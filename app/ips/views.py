# Configure matplotlib first
import matplotlib
matplotlib.use('Agg', force=True)  # Force Agg backend for production

# Cache font manager to prevent repeated initialization
import matplotlib.font_manager as fm
# Clear and rebuild the font cache only once at startup
fm.findfont('Liberation Sans', rebuild_if_missing=True)

import os
import pandas as pd
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from .models import QuestionnaireResponse, ChooseMyselfData, LetPmChooseData, Profile, ReturnsUpload, Mandate, FeeCategory, FeeTier, PortfolioProfile, IPSCopyBlock, SiteDocument, SavedProposal
from .forms import QuestionnaireForm, ChooseMyselfForm, LetPmChooseForm, RegisterForm
from django.template.loader import render_to_string
from django.templatetags.static import static
from weasyprint import HTML, CSS
from PyPDF2 import PdfMerger, PdfReader
import logging
import io
from decimal import Decimal
from django.views.decorators.http import require_POST
import matplotlib.pyplot as plt  # Import plt after setting backend
import matplotlib.font_manager as fm
import json
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from datetime import datetime
import glob
from urllib.parse import urljoin
from pathlib import Path
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.cache import never_cache

# Configure logging
logger = logging.getLogger(__name__)

# Set up matplotlib to use system fonts in order of preference - simplified for memory
FONT_PREFERENCES = ['Liberation Sans', 'sans-serif']  # Reduced list to essential fonts

# Find the first available font and use it consistently - simplified check
available_font = 'sans-serif'  # Default fallback
try:
    if fm.findfont('Liberation Sans') is not None:
        available_font = 'Liberation Sans'
        logger.info("Using Liberation Sans font")
    else:
        logger.info("Falling back to sans-serif font")
except Exception as e:
    logger.warning(f"Font detection error: {str(e)}, falling back to sans-serif")

# Configure matplotlib with minimal font settings
plt.rcParams.update({
    'font.family': available_font,
    'font.size': 10
})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure a profile is created only if it doesn't exist
            Profile.objects.get_or_create(user=user)
            messages.success(request, 'Registration successful. Your account needs to be approved by an administrator before you can log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.profile.is_approved:
                login(request, user)
                return redirect('questionnaire')  # Redirect to the questionnaire page
            else:
                messages.error(request, 'Your account is not approved yet.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def load_performance_data():
    """Load the active returns Excel from the DB upload, falling back to the
    static file if no upload exists yet."""
    cached = cache.get('performance_data')
    if cached is not None:
        return cached

    try:
        upload = ReturnsUpload.objects.filter(is_active=True).latest('uploaded_at')
        excel_path = upload.file.path
        logger.info(f"Loading performance data from upload: {excel_path}")
    except Exception:
        excel_path = os.path.join(settings.BASE_DIR, 'static', 'returns', 'returns.xlsx')
        logger.info(f"No active upload found, falling back to: {excel_path}")

    if not os.path.exists(excel_path):
        logger.error(f"Returns file not found: {excel_path}")
        return None

    df = pd.read_excel(excel_path, sheet_name='Sheet1')
    cache.set('performance_data', df, 60 * 60 * 24)
    return df


def get_returns_as_of_date():
    """Return the as-of date string from the active ReturnsUpload."""
    try:
        upload = ReturnsUpload.objects.filter(is_active=True).latest('uploaded_at')
        return upload.as_of_date
    except Exception:
        return ""


try:
    performance_data = load_performance_data()
except Exception:
    performance_data = None


# ---------------------------------------------------------------------------
# DB-backed data helpers (replace all hardcoded dicts)
# ---------------------------------------------------------------------------

def get_strategy_data():
    """Return {mandate_name: asset_allocation_dict} from the DB, cached."""
    cached = cache.get('strategy_data')
    if cached is not None:
        return cached
    try:
        data = {m.name: m.asset_allocation() for m in Mandate.objects.filter(is_active=True)}
        cache.set('strategy_data', data, 60 * 60 * 24)
    except Exception:
        data = {}
    return data


def get_fee_data():
    """Return {category_name: [tier_dict, ...]} from the DB, cached."""
    cached = cache.get('fee_data')
    if cached is not None:
        return cached
    try:
        data = {}
        for tier in FeeTier.objects.select_related('category').order_by('category__name', 'order', 'lower'):
            data.setdefault(tier.category.name, []).append(tier.to_dict())
        cache.set('fee_data', data, 60 * 60 * 24)
    except Exception:
        data = {}
    return data


def get_strategy_fee_map():
    """Return {mandate_name: fee_category_name} from the DB, cached."""
    cached = cache.get('strategy_fee_map')
    if cached is not None:
        return cached
    try:
        data = {
            m.name: m.fee_category.name
            for m in Mandate.objects.filter(is_active=True).select_related('fee_category')
        }
        cache.set('strategy_fee_map', data, 60 * 60 * 24)
    except Exception:
        data = {}
    return data


def get_mandates():
    """Return {mandate_name: Mandate} ordered by display_order, cached."""
    cached = cache.get('mandates')
    if cached is not None:
        return cached
    try:
        data = {m.name: m for m in Mandate.objects.filter(is_active=True).order_by('display_order', 'name')}
        cache.set('mandates', data, 60 * 60 * 24)
    except Exception:
        data = {}
    return data


def get_copy_blocks(category):
    """Return {key: (title, body)} for a given IPSCopyBlock category, cached."""
    cache_key = f'copy_blocks_{category}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        data = {b.key: (b.title, b.body) for b in IPSCopyBlock.objects.filter(category=category).order_by('order', 'key')}
        cache.set(cache_key, data, 60 * 60 * 24)
    except Exception:
        data = {}
    return data


def get_site_document_path(key, fallback_static_path):
    """Return the filesystem path for a SiteDocument, falling back to the static file."""
    try:
        doc = SiteDocument.objects.get(key=key)
        if doc.file and os.path.exists(doc.file.path):
            return doc.file.path
    except Exception:
        pass
    return fallback_static_path


def get_portfolio_profiles():
    """Return {name: PortfolioProfile} ordered by display order, cached."""
    cached = cache.get('portfolio_profiles')
    if cached is not None:
        return cached
    try:
        data = {p.name: p for p in PortfolioProfile.objects.all().order_by('order')}
        cache.set('portfolio_profiles', data, 60 * 60 * 24)
    except Exception:
        data = {}
    return data


def get_calendar_years():
    """Return list of calendar year strings from the active ReturnsUpload."""
    try:
        upload = ReturnsUpload.objects.filter(is_active=True).latest('uploaded_at')
        return [y.strip() for y in upload.calendar_years.split(',') if y.strip()]
    except Exception:
        return ['2025', '2024', '2023', '2022', '2021', '2020', '2019']

@require_POST
def calculate_fees(request):
    try:
        data = json.loads(request.body)
        strategies = data.get('strategies', [])
        amounts = data.get('amounts', [])

        if not strategies or not amounts or len(strategies) != len(amounts):
            return JsonResponse({
                'error': 'Invalid input: strategies and amounts must be non-empty and of equal length'
            }, status=400)

        fee_categories = {}
        for strategy, amount in zip(strategies, amounts):
            if not isinstance(amount, (int, float)) or amount < 0:
                return JsonResponse({
                    'error': 'Invalid amount: amounts must be non-negative numbers'
                }, status=400)

            category = get_strategy_fee_map().get(strategy, "Equity & Balanced")
            if category not in fee_categories:
                fee_categories[category] = 0
            fee_categories[category] += amount

        total_assets = sum(amounts)
        if total_assets <= 0:
            return JsonResponse({
                'error': 'Total assets must be greater than 0'
            }, status=400)

        overall_min_fee = 0
        overall_min_trailer = 0
        overall_max_fee = 0
        overall_max_trailer = 0
        overall_admin_fee = 0

        for category, category_assets in fee_categories.items():
            fee_ranges = get_fee_data().get(category, [])
            fee_range_found = False
            for range_data in fee_ranges:
                if range_data["lower"] <= category_assets <= range_data["upper"]:
                    overall_min_fee += range_data["minFee"] * category_assets
                    overall_min_trailer += range_data["minTrailer"] * category_assets
                    overall_max_fee += range_data["maxFee"] * category_assets
                    overall_max_trailer += range_data["maxTrailer"] * category_assets
                    overall_admin_fee += range_data["adminFee"] * category_assets
                    fee_range_found = True
                    break

            if not fee_range_found:
                return JsonResponse({
                    'error': f'No valid fee range found for category {category} with assets {category_assets}'
                }, status=400)

        overall_min_fee /= total_assets
        overall_min_trailer /= total_assets
        overall_max_fee /= total_assets
        overall_max_trailer /= total_assets
        overall_admin_fee /= total_assets

        return JsonResponse({
            'min_fee': round(overall_min_fee, 2),
            'min_trailer': round(overall_min_trailer, 2),
            'max_fee': round(overall_max_fee, 2),
            'max_trailer': round(overall_max_trailer, 2),
            'admin_fee': round(overall_admin_fee, 2),
        })
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred while calculating fees: {str(e)}'
        }, status=500)

def calculate_fees_for_ips(strategies, amounts):
    fee_categories = {}
    for strategy, amount in zip(strategies, amounts):
        category = get_strategy_fee_map().get(strategy, "Equity & Balanced")
        if category not in fee_categories:
            fee_categories[category] = 0
        fee_categories[category] += amount

    total_assets = sum(amounts)
    overall_min_fee = 0
    overall_min_trailer = 0
    overall_max_fee = 0
    overall_max_trailer = 0
    overall_admin_fee = 0
    category_fees = {}

    for category, category_assets in fee_categories.items():
        fee_ranges = get_fee_data().get(category, [])
        category_min_fee = float('inf')
        category_max_fee = 0
        for range_data in fee_ranges:
            if range_data["lower"] <= category_assets <= range_data["upper"]:
                overall_min_fee += range_data["minFee"] * category_assets
                overall_min_trailer += range_data["minTrailer"] * category_assets
                overall_max_fee += range_data["maxFee"] * category_assets
                overall_max_trailer += range_data["maxTrailer"] * category_assets
                overall_admin_fee += range_data["adminFee"] * category_assets
                category_min_fee = min(category_min_fee, range_data["minFee"])
                category_max_fee = max(category_max_fee, range_data["maxFee"])
                break
        category_fees[category] = {
            'min_fee': category_min_fee,
            'max_fee': category_max_fee
        }

    if total_assets > 0:
        overall_min_fee /= total_assets
        overall_min_trailer /= total_assets
        overall_max_fee /= total_assets
        overall_max_trailer /= total_assets
        overall_admin_fee /= total_assets

    return {
        'min_fee': round(overall_min_fee, 2),
        'min_trailer': round(overall_min_trailer, 2),
        'max_fee': round(overall_max_fee, 2),
        'max_trailer': round(overall_max_trailer, 2),
        'admin_fee': round(overall_admin_fee, 2),
        'category_fees': category_fees
    }


@login_required
@csrf_protect
def questionnaire_view(request):
    if request.method == 'POST':
        logger.debug("POST data: %s", request.POST)
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            total_score = form.calculate_total_score()
            portfolio_recommendation = form.get_portfolio_recommendation()
            asset_mix = form.get_asset_mix(portfolio_recommendation)
            risk_rating, portfolio_definition = get_risk_and_definition(portfolio_recommendation)
            user = request.user
            QuestionnaireResponse.objects.filter(user=user).delete()
            for field, value in form.cleaned_data.items():
                if field == 'investment_goals':
                    for goal in value:
                        QuestionnaireResponse.objects.create(user=user, question=field, answer=goal, score=0)
                else:
                    score = int(value) if field in [
                        'annual_income', 'income_savings', 'spending_needs',
                        'risk_tolerance', 'investment_loss', 'recovery_period',
                        'reaction_to_drop', 'high_risk_opportunities', 'volatility',
                        'investment_knowledge', 'time_horizon', 'liquidity_needs'
                    ] else 0
                    QuestionnaireResponse.objects.create(user=user, question=field, answer=value, score=score)
            return JsonResponse({
                'total_score': total_score,
                'portfolio_recommendation': portfolio_recommendation,
                'asset_mix': asset_mix,
                'risk_rating': risk_rating,
                'portfolio_definition': portfolio_definition
            })
        else:
            logger.debug("Form errors: %s", form.errors)
            errors = form.errors.get_json_data()
            return JsonResponse({'errors': errors}, status=400)
    else:
        form = QuestionnaireForm()
    return render(request, 'questionnaire.html', {'form': form})

@login_required
def generate_ips_questionnaire_responses(request):
    try:
        responses = QuestionnaireResponse.objects.filter(user=request.user)
        total_score = sum(response.score for response in responses if response.question in [
            'annual_income', 'income_savings', 'spending_needs',
            'risk_tolerance', 'investment_loss', 'recovery_period',
            'reaction_to_drop', 'high_risk_opportunities', 'volatility',
            'investment_knowledge', 'time_horizon', 'liquidity_needs'
        ])

        form_data = {response.question: response.answer for response in responses}
        form_data['investment_goals'] = [response.answer for response in responses.filter(question='investment_goals')]

        form = QuestionnaireForm(data=form_data)

        if form.is_valid():
            portfolio_recommendation = form.get_portfolio_recommendation()
            asset_mix = form.get_asset_mix(portfolio_recommendation)
            risk_rating, portfolio_definition = get_risk_and_definition(portfolio_recommendation)
        else:
            portfolio_recommendation = "Invalid data"
            asset_mix = {}
            risk_rating = "N/A"
            portfolio_definition = "N/A"

        context = {
            'responses': responses,
            'user': request.user,
            'total_score': total_score,
            'portfolio_recommendation': portfolio_recommendation,
            'asset_mix': asset_mix,
            'risk_rating': risk_rating,
            'portfolio_definition': portfolio_definition,
            'advisor_name': form.cleaned_data.get('advisor_name', 'N/A'),
            'annual_withdrawal': form.cleaned_data.get('annual_withdrawal', 'N/A')
        }

        html_string = render_to_string('ips_pcq.html', context)

        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="ips_questionnaire.pdf"'
        return response
    except Exception as e:
        logger.error("Error generating IPS PDF: %s", e)
        return HttpResponse("An error occurred while generating the PDF.", status=500)


@login_required
def generate_ips(request):
    try:
        # Retrieve account details from the database
        account_details = list(ChooseMyselfData.objects.filter(user=request.user).exclude(
            account_owner__in=['Client-directed Holdings ', 'Comments', 'Desired Rate', 'CMS Fee', 'IPS Changes', 'Risk Profile Override', 'Portfolio Override']
        ).values(
            'account_owner', 'account_type', 'amount', 'strategy', 'version_number'
        ))
        # Sort the account details
        account_details.sort(key=lambda x: (x['account_owner'], x['account_type']))
        if not account_details:
            raise ValueError("No account details found in database.")

        logger.info(f"Retrieved {len(account_details)} account details for user {request.user.username}")

        amounts = [float(detail['amount']) for detail in account_details]
        strategies = [detail['strategy'] for detail in account_details]

        cms_fee = ChooseMyselfData.objects.filter(user=request.user, account_owner='CMS Fee').first()
        desired_rate = ChooseMyselfData.objects.filter(user=request.user, account_owner='Desired Rate').first()
        version_number = account_details[0]['version_number'] if account_details else "N/A"

        attach_fact_sheets = request.POST.get('attach_fact_sheets', 'No')

        # Calculate fees
        fee_data = calculate_fees_for_ips(strategies, amounts)
        overall_max_fee = fee_data['max_fee']
        overall_min_fee = fee_data['min_fee']
        fee_discount = overall_max_fee - float(desired_rate.amount) if desired_rate else 0
        fee_range = overall_max_fee - overall_min_fee
        discount_percentage = fee_discount / fee_range if fee_range != 0 else 0

        client_managed_holdings = list(ChooseMyselfData.objects.filter(
            user=request.user,
            account_owner='Client-directed Holdings '
        ).values('account_type', 'amount'))

        filtered_client_managed_holdings = []
        for holding in client_managed_holdings:
            amount = float(holding['amount'])
            if amount > 0:
                account_info = holding['account_type'].split(' - ')
                if len(account_info) == 2:
                    holding['account_owner'] = account_info[0]
                    holding['account_type'] = account_info[1]
                else:
                    holding['account_owner'] = 'Unknown'
                    holding['account_type'] = holding['account_type']
                holding['amount'] = amount
                filtered_client_managed_holdings.append(holding)

        comments = ChooseMyselfData.objects.filter(
            user=request.user,
            account_owner='Comments'
        ).first()

        # Calculate totals
        total_amount = sum(amounts)
        total_client_managed = sum(holding['amount'] for holding in filtered_client_managed_holdings)
        grand_total = total_amount + total_client_managed

        # Calculate weights for account details and Client-directed Holdings
        for detail in account_details:
            detail['weight'] = (float(detail['amount']) / grand_total * 100) if grand_total else 0
        for holding in filtered_client_managed_holdings:
            holding['weight'] = (holding['amount'] / grand_total * 100) if grand_total else 0

        # Step 1: Create fee_transparency_data
        fee_transparency_data = []
        for detail in account_details:
            fee_transparency_data.append({
                'account_owner': detail['account_owner'],
                'account_type': detail['account_type'],
                'strategy': detail['strategy'],
                'amount': float(detail['amount']),
                'weight': (float(detail['amount']) / grand_total * 100) if grand_total else 0,
            })

        # Add Client-directed Holdings  to fee_transparency_data
        for holding in filtered_client_managed_holdings:
            fee_transparency_data.append({
                'account_owner': holding['account_owner'],
                'account_type': holding['account_type'],
                'strategy': 'Client-directed Holdings ',
                'amount': float(holding['amount']),
                'weight': (float(holding['amount']) / grand_total * 100) if grand_total else 0,
            })

        # Step 2: Calculate fees for each item in fee_transparency_data
        for item in fee_transparency_data:
            if item['strategy'] == 'Client-directed Holdings ':
                item['fee'] = f"{float(cms_fee.amount):.2f}%" if cms_fee else "N/A"
            else:
                category = get_strategy_fee_map().get(item['strategy'], "Equity & Balanced")
                category_fee_data = fee_data['category_fees'].get(category, {})
                category_min_fee = category_fee_data.get('min_fee', 0)
                category_max_fee = category_fee_data.get('max_fee', 0)
                category_fee_range = category_max_fee - category_min_fee
                category_fee = category_min_fee + (category_fee_range * (1 - discount_percentage))
                item['fee'] = f"{category_fee:.2f}%"

        # Step 3: Calculate the total weighted fee
        total_weighted_fee = 0
        for item in fee_transparency_data:
            if item['fee'] != 'N/A':
                fee_percentage = float(item['fee'].rstrip('%'))
                weight_percentage = item['weight'] / 100
                weighted_fee = fee_percentage * weight_percentage
                total_weighted_fee += weighted_fee

        total_overall_fee = round(total_weighted_fee, 2)

        total_fee = sum(float(item['amount']) * float(item['fee'].rstrip('%')) / 100 for item in fee_transparency_data if item['fee'] != 'N/A')
        total_fee_percentage = (total_fee / grand_total) * 100 if grand_total > 0 else 0


        comments_record = ChooseMyselfData.objects.filter(user=request.user, account_owner='Comments').first()
        comments = comments_record.strategy if comments_record and comments_record.strategy.strip() else ''

        # Normalize asset class names
        def normalize_asset_class_name(name):
            return name.replace(' ', '_').replace('.', '')

        # Calculate weights and proposed asset class weights
        proposed_weights = {
            "Cash": 0,
            "Fixed_Income": 0,
            "Canadian_Equity": 0,
            "US_Equity": 0,
            "International_Equity": 0,
            "Alternatives": 0
        }

        for detail in account_details:
            amount = float(detail['amount'])
            detail['weight'] = (amount / total_amount * 100) if total_amount else 0
            strategy = detail['strategy']
            _strategy_data = get_strategy_data()
            if strategy in _strategy_data:
                strategy_weights = _strategy_data[strategy]
                for asset_class, weight in strategy_weights.items():
                    normalized_asset_class = normalize_asset_class_name(asset_class)
                    if normalized_asset_class in proposed_weights:
                        proposed_weights[normalized_asset_class] += (weight / 100) * (amount / total_amount * 100)

        # Round the proposed weights for display
        for asset_class in proposed_weights:
            proposed_weights[asset_class] = round(proposed_weights[asset_class],1)

        # Ensure the media directory exists
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            os.makedirs(media_root)

        # Set the font family to Arial
        plt.rcParams['font.family'] = 'Arial'

        # Normalize asset class names and update US Equity to US Equities, and replace US with U.S.
        labels = [name.replace('_', ' ').replace('Equity', 'Equities').replace('US', 'U.S.') for name in proposed_weights.keys()]


        sizes = list(proposed_weights.values())
        colors = ['#D60D8C','#205098', '#85BE00', '#112055', '#5948AD', '#E56919']  # Updated colors based on the legend
        explode = (0.02, 0.02, 0.02, 0.02, 0.02, 0.02)  # Slight explode for all slices

        # Filter out labels and sizes with zero values
        filtered_labels_sizes_colors_explode = [
            (label, size, color, exp) for label, size, color, exp in zip(labels, sizes, colors, explode) if size > 0
        ]

        if filtered_labels_sizes_colors_explode:
            filtered_labels, filtered_sizes, filtered_colors, filtered_explode = zip(*filtered_labels_sizes_colors_explode)
        else:
            filtered_labels, filtered_sizes, filtered_colors, filtered_explode = [], [], [], []

        # Set figure size (reduced from 4x4 to 3x3)
        plt.figure(figsize=(6, 6))

        # Create the pie chart without values
        wedges, texts = plt.pie(
            filtered_sizes,
            explode=filtered_explode,
            labels=None,  # Hide labels
            colors=filtered_colors,
            autopct=None,  # Remove values from the pie chart
            startangle=120,
            textprops={'fontsize': 12},  # Reduced font size
            pctdistance=0.7
        )

        # Prepare labels with values for the legend
        legend_labels = [f'{label}: {size:.1f}%' for label, size in zip(filtered_labels, filtered_sizes)]

        # Add a legend and adjust its size and position
        plt.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(-2, 0.5), fontsize=24, frameon=False)

        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Save the pie chart to the media directory
        pie_chart_filename = 'pie_chart.png'
        pie_chart_path = os.path.join(settings.MEDIA_ROOT, pie_chart_filename)
        plt.savefig(pie_chart_path, bbox_inches='tight', pad_inches=0.3, dpi=300)  # Reduced pad_inches
        plt.close()

        # Construct an absolute file URL for the pie chart
        pie_chart_url = Path(pie_chart_path).as_uri()


        # Collect data from the questionnaire responses
        questionnaire_responses = QuestionnaireResponse.objects.filter(user=request.user)

        # Extract client household name and investment advisor name
        client_household_name = next((resp.answer for resp in questionnaire_responses if resp.question == 'client_identifier'), 'N/A')
        investment_advisor_name = next((resp.answer for resp in questionnaire_responses if resp.question == 'advisor_name'), 'N/A')

        # Construct an absolute file URL for the logo
        if settings.DEBUG:
            logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo.png'
        else:
            logo_path = Path(settings.STATIC_ROOT) / 'images' / 'logo.png'
        logo_url = logo_path.as_uri()

        # Get portfolio recommendation and asset mix
        form_data = {response.question: response.answer for response in questionnaire_responses}
        form_data['investment_goals'] = [response.answer for response in questionnaire_responses.filter(question='investment_goals')]

        form = QuestionnaireForm(data=form_data)
        if form.is_valid():
            portfolio_recommendation = form.get_portfolio_recommendation()
            asset_mix = form.get_asset_mix(portfolio_recommendation)
            risk_rating, portfolio_definition = get_risk_and_definition(portfolio_recommendation)


            RISK_PROFILES = {

                'Low Risk': (
                    "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Low Risk. "
                    "Investors with this profile generally prioritize capital preservation and prefer to minimize the possibility of losses. They tend to seek stability and security, even if it means accepting lower returns. "
                    "This risk profile is ideal for those who are more risk-averse or have a shorter investment horizon. Therefore, an 'Income' asset mix is considered suitable for clients with this risk profile."
                ),
                'Low Medium Risk': (
                    "After reviewing your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Low Medium Risk. "
                    "This profile suits investors who are comfortable with a moderate level of risk in exchange for the potential of modest returns. They seek a balance between preserving capital and achieving some growth. "
                    "These investors are prepared for minor fluctuations in their portfolio value. As such, an 'Income & Growth' asset mix is considered appropriate for clients with this risk profile."
                ),
                'Medium Risk': (
                    "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Medium Risk. "
                    "Investors with this profile are open to accepting some risk to achieve better returns. They understand that their portfolio may experience occasional fluctuations in value but are comfortable with this in pursuit of higher gains. "
                    "This risk profile is suitable for investors with a moderate investment horizon. Therefore, a 'Balanced' asset mix is considered appropriate for clients with this risk profile."
                ),
                'Medium High Risk': (
                    "After carefully considering your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Medium High Risk. "
                    "Investors with this profile are willing to accept some fluctuations in their portfolio value in exchange for the potential of higher returns. While they aim for capital appreciation, they also value some income from their investments. "
                    "This risk profile is suitable for those with a longer investment horizon. Consequently, a 'Growth & Income' asset mix is considered appropriate for clients with this risk profile."
                ),
                'High Risk': (
                    "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is High Risk. "
                    "Investors with this profile are comfortable with more significant fluctuations in their portfolio value in pursuit of high returns. They are prepared to accept considerable risk in exchange for the potential of substantial gains. "
                    "This risk profile is appropriate for those with a long-term investment horizon and a strong appetite for risk. Therefore, a 'Growth' asset mix is considered suitable for clients with this risk profile."
                ),
                'Very High Risk': (
                    "After reviewing your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Very High Risk. "
                    "Investors with this profile are willing to accept significant volatility and fluctuations in their portfolio value for the potential of maximum returns. They focus on high-growth opportunities and are comfortable with a high level of risk. "
                    "This risk profile is most appropriate for those with a long-term investment horizon and a strong focus on growth. As such, a 'Maximum Growth' asset mix is considered appropriate for clients with this risk profile."
                ),

            }


            risk_rating = form.get_risk_profile()

            # Read overrides from POST first to avoid Azure SQL write lag
            _risk_profile_override = request.POST.get('risk_profile_override') or None
            _portfolio_override = request.POST.get('portfolio_override') or None

            # Fall back to DB if not in POST
            if not _risk_profile_override:
                _rp_rec = ChooseMyselfData.objects.filter(
                    user=request.user, account_owner='Risk Profile Override').first()
                _risk_profile_override = _rp_rec.strategy if _rp_rec and _rp_rec.strategy else None

            if not _portfolio_override:
                _po_rec = ChooseMyselfData.objects.filter(
                    user=request.user, account_owner='Portfolio Override').first()
                _portfolio_override = _po_rec.strategy if _po_rec and _po_rec.strategy else None

            if _risk_profile_override:
                risk_rating = _risk_profile_override

            if _portfolio_override:
                try:
                    asset_mix = QuestionnaireForm.ASSET_MIX.get(_portfolio_override, asset_mix)
                except Exception:
                    pass

            risk_rating_paragraph = RISK_PROFILES.get(risk_rating, "")

            asset_mix_descriptions = {
                "Income": "The Income asset mix is designed to generate steady returns through investments primarily in bonds and fixed-income securities, minimal equities.",
                "Income & Growth": "The Income & Growth asset mix offers a combination of bonds and some equities, focusing on stable returns while providing the potential for growth. This mix is designed to generate income through fixed-income securities and achieve some capital appreciation through equities, making it suitable for those looking for a balanced approach with low medium risk.",
                "Balanced": "The Balanced asset mix consists of an equal mix of equities and bonds, providing moderate exposure to both asset classes. This combination aims to achieve a balance between income generation and capital growth, offering a moderate risk-return profile. It is ideal for investors seeking a diversified approach to investing.",
                "Growth & Income": "The Growth & Income asset mix emphasizes equities more than bonds, focusing on capital appreciation while maintaining some income generation. This mix is designed to provide higher returns through equity investments, supplemented by the relative stability of fixed-income securities. It is suitable for investors seeking growth with a medium high risk.",
                "Growth": "The Growth asset mix is primarily composed of equities, offering higher volatility with focus on capital appreciation. This mix aims to achieve substantial returns through investments in equities, accepting the added risk associated with market fluctuations. It is ideal for investors seeking higher growth opportunities.",
                "Maximum Growth": "The Maximum Growth asset mix is almost entirely made up of equities or high-risk assets, providing maximum exposure to market fluctuations. This mix targets the highest possible returns through investments in high-growth equities and other volatile assets. It is suitable for investors looking for the highest growth potential and willing to accept very high risk."
            }

            asset_mix_title = _portfolio_override or portfolio_recommendation.replace(" (RI)", "")
            recommended_asset_mix_paragraph = asset_mix_descriptions.get(asset_mix_title, "N/A")

            # Define the investment goals paragraphs
            investment_goals_paragraphs_dict = {
                "Retirement": "Ensuring a comfortable and financially secure retirement involves creating a portfolio that supports your desired lifestyle. This includes planning for living expenses, luxury travel, healthcare, and legacy planning.",
                "Wealth accumulation": "Growing your assets involves strategic investments in various asset classes, including stocks, bonds, real estate, and alternative investments. The goal is to maximize returns while managing risk and preserving wealth.",
                "Legacy planning": "Legacy planning involves creating trusts, establishing family offices, and planning for wealth transfer to future generations. This goal ensures that your wealth supports not just immediate family but also future generations and philanthropic causes.",
                "Philanthropy": "Charitable giving involves creating philanthropic foundations, making endowments, and engaging in impactful giving. This goal includes tax-efficient giving and ensuring long-term sustainability of charitable efforts.",
                "Major asset purchase": "Planning for major asset purchases includes setting aside funds for significant acquisitions such as primary residences, vacation homes, luxury vehicles, or valuable collectibles. This goal involves strategic financial planning to ensure these purchases are aligned with your overall wealth strategy and do not impact long-term financial goals.",
                "Education": "Investing for education encompasses funding private schooling, higher education, and advanced degrees for children and grandchildren. It may also involve endowing educational institutions or creating scholarship funds.",
                "Health care": "Planning for healthcare needs includes ensuring access to high-quality medical care, funding long-term care insurance, and creating healthcare trusts. This ensures that you can maintain your health and well-being without financial constraints.",
                "Travel": "Planning for travel involves setting aside funds for luxury travel, owning vacation properties, and participating in exclusive experiences. This ensures financial flexibility for both planned and spontaneous trips.",
                "Other": "Custom financial goals unique to your personal situation. This might include investments in private businesses, art collections, or supporting entrepreneurial activities within the family, all aligned with your overall wealth management strategy."
            }

            investment_goals_paragraphs = [
                (goal, investment_goals_paragraphs_dict[goal])
                for goal in form.cleaned_data['investment_goals']
                if goal in investment_goals_paragraphs_dict
            ]

            # Define the time horizon paragraphs
            time_horizon = form.cleaned_data['time_horizon']
            time_horizon_paragraphs_dict = {
                '1': ("Less than 1 year", "Your investment portfolio is designed for a very short-term time horizon of less than one year. This means that the focus will be on preserving capital and maintaining liquidity. The strategy will prioritize investments that are stable and easily convertible to cash to meet your immediate financial needs."),
                '2': ("1-3 years", "Your investment portfolio is designed with a short-to-medium term time horizon of 1 to 3 years. The strategy will balance between stability and modest growth, emphasizing relatively safe investments that offer some potential for appreciation while minimizing risk. The approach aims to achieve a balance of stability and growth to meet your investment goals within the specified time frame."),
                '3': ("3-5 years", "Your investment portfolio is structured with a medium-term time horizon of 3 to 5 years. This allows for a more balanced approach to risk and return, with the objective of achieving moderate growth while preserving capital. The strategy aims to strike a balance between stability and growth, aligning with your financial goals over this period."),
                '4': ("5-10 years", "Your investment portfolio is tailored for a long-term time horizon of 5 to 10 years. With a focus on growth and capital appreciation, the investment strategy will be more aggressive. The approach will aim to optimize growth potential and manage risk, achieving significant appreciation over the extended period."),
                '5': ("More than 10 years", "Your investment portfolio is planned with a long-term time horizon of more than 10 years. This extended duration allows for a more aggressive growth strategy, focusing on maximizing capital appreciation over the long run. The approach will take advantage of the compounding growth potential over the long term, aligning with your long-term financial objectives and risk tolerance.")
            }

            time_horizon_title, time_horizon_paragraph = time_horizon_paragraphs_dict.get(time_horizon, ("N/A", "N/A"))

            # Define the liquidity needs paragraphs
            liquidity_needs = form.cleaned_data['liquidity_needs']
            liquidity_needs_paragraphs_dict = {
                '1': ("Very Important", "You have indicated that having access to cash quickly is very important for your investment strategy. This suggests that you may need to respond rapidly to emergencies or opportunities. Therefore, your investment portfolio will prioritize liquidity to ensure that funds are readily available when needed, without significant delays or penalties. This approach will help you maintain the flexibility required to meet your short-term financial needs and unexpected expenses."),
                '2': ("Somewhat Important", "You have indicated that having some access to cash is somewhat important, but you can afford to wait for a short period. This implies a balance between liquidity and potential returns. Your investment portfolio will be structured to provide moderate liquidity, allowing for access to funds within a reasonable timeframe while still aiming for growth. This approach will help you meet occasional cash needs without sacrificing long-term investment goals."),
                '3': ("Not Important", "You have indicated that having access to cash quickly is not important for your investment strategy. This suggests that you are comfortable with long-term investments and do not anticipate needing quick access to cash. Therefore, your investment portfolio can focus on growth and capital appreciation, with less emphasis on liquidity. This approach allows for potentially higher returns over the long term, aligning with your comfort level and investment horizon.")
            }

            liquidity_needs_title, liquidity_needs_paragraph = liquidity_needs_paragraphs_dict.get(liquidity_needs, ("N/A", "N/A"))

            # Define the income needs paragraphs
            annual_withdrawal = form.cleaned_data.get('annual_withdrawal', None)

            if annual_withdrawal in [None, 0]:
                income_needs_paragraph = "You have indicated that you have no income requirements and do not plan to withdraw funds from your portfolio in the coming years. This allows for a focus on long-term growth and capital appreciation, as the investment strategy can prioritize higher-risk, higher-reward opportunities without the need for maintaining liquidity for withdrawals."
            else:
                income_needs_paragraph = f"You have indicated that you plan to withdraw ${int(annual_withdrawal):,} annually from your portfolio in the coming years. This amount will be considered in the management of your investment portfolio to ensure that your liquidity needs are met while pursuing your long-term investment goals. The strategy will aim to generate sufficient income and maintain the necessary liquidity to accommodate these annual withdrawals."

            # Check for specific account types
            registered_income_accounts = ['RRIF', 'LIF', 'SRIF', 'PRIF', 'LRIF']
            has_registered_income_account = any(account['account_type'] in registered_income_accounts for account in account_details)

            if annual_withdrawal in [None, 0] and has_registered_income_account:
                income_needs_paragraph += " As you have not indicated a specific income withdrawal amount in the risk questionnaire, this assessment does not account for any systematic withdrawals from your registered portfolio."

            responsible_investing = form.cleaned_data.get('responsible_investing', 'Neutral')
            responsible_investing_paragraphs_dict = {
                'RI': (
                    "Emphasis on Responsible Investing",
                    "You have indicated a preference for an all responsible investing portfolio, if possible. This means that your investment strategy will prioritize selecting investments that meet certain environmental, social, and governance (ESG) criteria. The portfolio will aim to align with your values by investing in companies and funds that are committed to sustainable and ethical practices. This approach reflects your commitment to making a positive impact through your investment choices while pursuing your financial goals."
                ),
                'Neutral': (
                    "Neutral",
                    "You have indicated a neutral stance with no specific bias towards responsible investing. This means that your investment strategy will focus on optimizing returns without particular consideration for environmental, social, and governance (ESG) criteria. The portfolio will be designed to achieve your financial objectives based on traditional investment principles, ensuring that performance and risk management are prioritized according to your overall investment goals."
                ),
            }

            responsible_investing_title, responsible_investing_paragraph = responsible_investing_paragraphs_dict.get(
                responsible_investing,
                (
                    "Responsible Investing Preference: Neutral",
                    "You have indicated a neutral stance with no specific bias towards responsible investing. This means that your investment strategy will focus on optimizing returns without particular consideration for environmental, social, and governance (ESG) criteria. The portfolio will be designed to achieve your financial objectives based on traditional investment principles, ensuring that performance and risk management are prioritized according to your overall investment goals."
                )
            )

        # Calculate performance data
        amounts = [float(detail['amount']) for detail in account_details]
        strategies = [detail['strategy'] for detail in account_details]

        total_amount = sum(amounts)
        weights = [amount / total_amount if total_amount != 0 else 0 for amount in amounts]

        # Aggregate weights for each strategy
        strategy_weights = {}
        for strategy, weight in zip(strategies, weights):
            if strategy in strategy_weights:
                strategy_weights[strategy] += weight
            else:
                strategy_weights[strategy] = weight

        # Convert weights to percentages
        strategy_weights = {strategy: weight * 100 for strategy, weight in strategy_weights.items()}

        # Prepare the performance table
        performance_table = []
        for strategy, weight in strategy_weights.items():
            if strategy in performance_data['Strategy'].values:
                row = performance_data[performance_data['Strategy'] == strategy].iloc[0].to_dict()
                row['Weight'] = f"{weight:.1f}%"
                # Format the values with percentage signs and two decimal places
                for period in ['1M', '3M', 'YTD', '1YR', '3YR', '5YR', '10YR', 'SI']:
                    row[period] = f"{float(row[period]) * 100:.2f}%" if pd.notnull(row[period]) else 'N/A'
                    row[f"{period}b"] = f"{float(row[f'{period}b']) * 100:.2f}%" if pd.notnull(row[f"{period}b"]) else 'N/A'
                performance_table.append(row)
            else:
                logger.warning(f"Strategy {strategy} not found in performance data.")

        # Calculate the portfolio and benchmark returns
        portfolio_return = {}
        benchmark_return = {}
        periods = ['1M', '3M', 'YTD', '1YR', '3YR', '5YR', '10YR', 'SI']
        for period in periods:
            portfolio_return[period] = sum(
                (float(row[period].replace('%', '')) if isinstance(row[period], str) and row[period] != 'N/A' else 0) * (float(row['Weight'].replace('%', '')) / 100)
                for row in performance_table
            )
            benchmark_return[period] = sum(
                (float(row[f'{period}b'].replace('%', '')) if isinstance(row[f'{period}b'], str) and row[f'{period}b'] != 'N/A' else 0) * (float(row['Weight'].replace('%', '')) / 100)
                for row in performance_table
            )

        # Add Portfolio and Benchmark rows to the performance table
        portfolio_row = {'Strategy': 'Portfolio', 'Weight': '100.0%'}
        benchmark_row = {'Strategy': 'Benchmark', 'Weight': '100.0%'}
        for period in periods:
            portfolio_row[period] = f"{portfolio_return[period]:.2f}%"
            benchmark_row[period] = f"{benchmark_return[period]:.2f}%"
        performance_table.append(portfolio_row)
        performance_table.append(benchmark_row)

        # Prepare the calendar year returns table
        calendar_year_table = []
        years = ['2025', '2024', '2023', '2022', '2021', '2020', '2019']
        for strategy, weight in strategy_weights.items():
            if strategy in performance_data['Strategy'].values:
                row = performance_data[performance_data['Strategy'] == strategy].iloc[0].to_dict()
                row['Weight'] = f"{weight:.1f}%"
                # Format the values with percentage signs and two decimal places
                for year in years:
                    row[year] = f"{float(row.get(f'{year}a', 0)) * 100:.2f}%" if pd.notnull(row.get(f'{year}a')) and row.get(f'{year}a') != 'N/A' else 'N/A'
                    row[f"{year}b"] = f"{float(row.get(f'{year}b', 0)) * 100:.2f}%" if pd.notnull(row.get(f'{year}b')) and row.get(f'{year}b') != 'N/A' else 'N/A'
                calendar_year_table.append(row)
            else:
                logger.warning(f"Strategy {strategy} not found in performance data.")

        # Calculate the portfolio and benchmark returns for calendar years
        calendar_year_portfolio_return = {year: 0 for year in years}
        calendar_year_benchmark_return = {year: 0 for year in years}

        for year in years:
            calendar_year_portfolio_return[year] = sum(
                (float(row[year].replace('%', '')) if isinstance(row[year], str) and row[year] != 'N/A' else 0) *
                (float(row['Weight'].replace('%', '')) / 100)
                for row in calendar_year_table
            )
            calendar_year_benchmark_return[year] = sum(
                (float(row[f'{year}b'].replace('%', '')) if isinstance(row[f'{year}b'], str) and row[f'{year}b'] != 'N/A' else 0) *
                (float(row['Weight'].replace('%', '')) / 100)
                for row in calendar_year_table
            )

        # Add Portfolio and Benchmark rows to the calendar year table
        portfolio_row = {'Strategy': 'Portfolio', 'Weight': '100.0%'}
        benchmark_row = {'Strategy': 'Benchmark', 'Weight': '100.0%'}
        for year in years:
            portfolio_row[year] = f"{calendar_year_portfolio_return[year]:.2f}%"
            benchmark_row[year] = f"{calendar_year_benchmark_return[year]:.2f}%"
        calendar_year_table.append(portfolio_row)
        calendar_year_table.append(benchmark_row)

        # Get disclaimers for the selected strategies
        disclaimer_text = get_disclaimer(strategy_weights)

        # Split the disclaimer text into a list of lines
        disclaimer_lines = disclaimer_text.split('\n')
        unique_account_owners = set(item['account_owner'] for item in fee_transparency_data)

        # Find the ips_changes record
        ips_changes_record = ChooseMyselfData.objects.filter(
            user=request.user,
            account_owner='IPS Changes'
        ).first()

        # Get current date
        creation_date = datetime.now().strftime("%Y-%m-%d")

        # Add it to the context dictionary
        context = {
            'questionnaire_responses': questionnaire_responses,
            'user': request.user,
            'client_household_name': client_household_name,
            'investment_advisor_name': investment_advisor_name,
            'logo_url': logo_url,
            'risk_rating': risk_rating,
            'risk_rating_paragraph': risk_rating_paragraph,
            'asset_mix_title': asset_mix_title,
            'recommended_asset_mix_paragraph': recommended_asset_mix_paragraph,
            'investment_goals_paragraphs': investment_goals_paragraphs,
            'time_horizon_title': time_horizon_title,
            'time_horizon_paragraph': time_horizon_paragraph,
            'liquidity_needs_title': liquidity_needs_title,
            'liquidity_needs_paragraph': liquidity_needs_paragraph,
            'income_needs_paragraph': income_needs_paragraph,
            'responsible_investing_title': responsible_investing_title,
            'responsible_investing_paragraph': responsible_investing_paragraph,
            'account_details': account_details,
            'proposed_weights': proposed_weights,
            'total_amount': total_amount,
            'pie_chart_url': pie_chart_url,
            'performance_summary': performance_table,
            'portfolio_return': {period: f"{value:.2f}%" for period, value in portfolio_return.items()},
            'benchmark_return': {period: f"{value:.2f}%" for period, value in benchmark_return.items()},
            'calendar_year_summary': calendar_year_table,
            'disclaimer_lines': disclaimer_lines,
            'selected_strategies': strategies,
            'version_number': version_number,
            'deviation_comments': comments,
            'fee_transparency_data': fee_transparency_data,
            'total_fee_transparency_amount': grand_total,
            'desired_rate': desired_rate.amount if desired_rate else None,
            'cms_fee': cms_fee.amount if cms_fee else None,
            'client_managed_holdings': filtered_client_managed_holdings,  # Keep this as it was
            'filtered_client_managed_holdings': filtered_client_managed_holdings,  # Add this new key
            'total_client_managed': total_client_managed,
            'total_overall_fee': f"{total_overall_fee:.2f}%",
            'unique_account_owners': unique_account_owners,
            'selected_strategies': strategies,
            'ips_changes': ips_changes_record.strategy if ips_changes_record and ips_changes_record.strategy.strip() else None,
            'creation_date': creation_date,
        }

        # Paths to the existing PDF files (DB-uploaded takes priority over static fallback)
        first_page_pdf_path = get_site_document_path(
            'ips_first_page',
            os.path.join(settings.BASE_DIR, 'static', 'intro', 'IPS_First_Page.pdf'),
        )
        last_page_pdf_path = get_site_document_path(
            'ips_last_page',
            os.path.join(settings.BASE_DIR, 'static', 'intro', 'IPS_Last_Page.pdf'),
        )

        # Check if the PDF files exist
        if not os.path.exists(first_page_pdf_path):
            logger.error(f"First page PDF not found: {first_page_pdf_path}")
            raise FileNotFoundError(f"First page PDF not found: {first_page_pdf_path}")

        if not os.path.exists(last_page_pdf_path):
            logger.error(f"Last page PDF not found: {last_page_pdf_path}")
            raise FileNotFoundError(f"Last page PDF not found: {last_page_pdf_path}")

        # Render the main content to a PDF
        main_content_html = render_to_string('ips_document.html', context)

        base_url = 'file://' + str(settings.BASE_DIR)
        main_content_pdf_bytes = HTML(string=main_content_html, base_url=base_url).write_pdf()

        # Use PyPDF2 to merge the PDFs
        merger = PdfMerger()

        # Add the first page PDF
        with open(first_page_pdf_path, 'rb') as first_page_file:
            merger.append(PdfReader(first_page_file))

        # Add the main content PDF
        main_content_pdf = io.BytesIO(main_content_pdf_bytes)
        merger.append(PdfReader(main_content_pdf))

        # Add the last page PDF
        with open(last_page_pdf_path, 'rb') as last_page_file:
            merger.append(PdfReader(last_page_file))

        # If user chose to attach fact sheets, add them
        if attach_fact_sheets == 'Yes':
            fact_sheets_dir = os.path.join(settings.BASE_DIR, 'static', 'strategies')
            logger.info(f"Looking for fact sheets in: {fact_sheets_dir}")

            # Use a set to keep track of added fact sheets
            added_fact_sheets = set()

            # Sanitize strategy to prevent path traversal
            for strategy in strategies:
                safe_strategy = os.path.basename(strategy)
                # Additional validation to prevent path traversal and unsafe names
                invalid_names = {'', '.', '..', 'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
                if (
                    safe_strategy in invalid_names or
                    any(sep in safe_strategy for sep in ('/', '\\')) or
                    safe_strategy.strip() == ''
                ):
                    logger.warning(f"Rejected unsafe strategy name: {strategy}")
                    continue
                if safe_strategy not in added_fact_sheets:
                    # Try DB-uploaded fact sheet first, fall back to static file
                    mandate_obj = get_mandates().get(strategy)
                    if mandate_obj and mandate_obj.fact_sheet and os.path.exists(mandate_obj.fact_sheet.path):
                        fact_sheet_path = mandate_obj.fact_sheet.path
                    else:
                        fact_sheet_path = os.path.join(fact_sheets_dir, f"{safe_strategy}.pdf")

                    logger.info(f"Checking for fact sheet: {fact_sheet_path}")
                    if os.path.exists(fact_sheet_path):
                        logger.info(f"Found fact sheet: {fact_sheet_path}")
                        with open(fact_sheet_path, 'rb') as fact_sheet_file:
                            merger.append(PdfReader(fact_sheet_file))
                        added_fact_sheets.add(safe_strategy)
                    else:
                        logger.warning(f"Fact sheet not found: {fact_sheet_path}")

        # Create the HTTP response with the merged PDF
        response = HttpResponse(content_type='application/pdf')

        current_date = datetime.now().strftime("%Y-%m-%d")

        # Create the custom filename with the current date
        custom_filename = f"{current_date} IPS for {client_household_name} Version {version_number}.pdf"
        # Ensure the filename is URL-safe
        custom_filename = custom_filename.replace(" ", "_")

        # Set the Content-Disposition header with the custom filename
        response['Content-Disposition'] = f'inline; filename="{custom_filename}"'

        merged_pdf = io.BytesIO()
        merger.write(merged_pdf)
        merger.close()
        response.write(merged_pdf.getvalue())

        return response

    except Exception as e:
        logger.error(f"Error generating IPS PDF: {e}", exc_info=True)
        return HttpResponse("An error occurred while generating the PDF.", status=500)


def get_risk_and_definition(portfolio_recommendation):
    risk_and_definitions = {
        "Income": ("Low Risk", "Income: Primarily bonds and fixed-income securities, minimal equities."),
        "Income & Growth": ("Low Medium Risk", "Income & Growth: Mix of bonds and some equities, with a focus on stable returns."),
        "Balanced": ("Medium Risk", "Balanced: Equal mix of equities and bonds, moderate exposure to both."),
        "Growth & Income": ("Medium High Risk", "Growth & Income: More equities than bonds, with a focus on capital appreciation and some income."),
        "Growth": ("High Risk", "Growth: Primarily equities, higher volatility with focus on capital appreciation."),
        "Maximum Growth": ("Very High Risk", "Maximum Growth: Almost entirely equities or high-risk assets, maximum exposure to market fluctuations.")
    }

    base_recommendation = portfolio_recommendation.replace(" (RI)", "")
    return risk_and_definitions.get(base_recommendation, ("N/A", "N/A"))

@login_required
@csrf_protect
def choose_myself_view(request):
    if request.method == 'POST':
        form = ChooseMyselfForm(request.POST)
        if form.is_valid():
            account_owners = request.POST.getlist('account_owner')
            account_types = request.POST.getlist('account_type')
            amounts = request.POST.getlist('amount')
            strategies = request.POST.getlist('strategy')
            weights = request.POST.getlist('percentage')

            # Store account details in session
            request.session['account_details'] = {
                'owners': account_owners,
                'types': account_types,
                'amounts': amounts,
                'strategies': strategies,
                'weights': weights,
            }

            # Redirect to the PDF generation view
            return redirect('generate_ips')
    else:
        form = ChooseMyselfForm()

    account_owners = QuestionnaireResponse.objects.filter(user=request.user, question='account_owner').values_list('answer', flat=True)
    account_types = QuestionnaireResponse.objects.filter(user=request.user, question='account_type').values_list('answer', flat=True)

    # Combine account owner and account type
    combined_accounts = [f"{owner} - {atype}" for owner, atype in zip(account_owners, account_types)]

    # Load saved overrides for risk profile and portfolio
    rp_rec = ChooseMyselfData.objects.filter(user=request.user, account_owner='Risk Profile Override').first()
    po_rec = ChooseMyselfData.objects.filter(user=request.user, account_owner='Portfolio Override').first()
    risk_profile_override = rp_rec.strategy if rp_rec else ''
    portfolio_override = po_rec.strategy if po_rec else ''

    # Load questionnaire results to show current recommendations
    questionnaire_qs = QuestionnaireResponse.objects.filter(user=request.user).order_by('-id').first()
    questionnaire_risk_profile = ''
    questionnaire_portfolio = ''
    effective_portfolio = ''
    if questionnaire_qs:
        responses = QuestionnaireResponse.objects.filter(user=request.user)
        q_data = {response.question: response.answer for response in responses}
        q_data['investment_goals'] = [response.answer for response in responses.filter(question='investment_goals')]
        q_form = QuestionnaireForm(q_data)
        if q_form.is_valid():
            questionnaire_risk_profile = q_form.get_risk_profile()
            portfolio_rec = q_form.get_portfolio_recommendation()
            questionnaire_portfolio = portfolio_rec.replace(' (RI)', '')
    portfolio_override_choices = list(QuestionnaireForm.ASSET_MIX.keys())
    portfolio_allocations_json = json.dumps(QuestionnaireForm.ASSET_MIX)

    # Compute single selected values for template — avoids |default: filter edge cases
    selected_risk_profile = risk_profile_override if risk_profile_override else questionnaire_risk_profile
    selected_portfolio = portfolio_override if portfolio_override else questionnaire_portfolio

    try:
        mandates = list(Mandate.objects.filter(is_active=True).order_by('display_order', 'name'))
    except Exception:
        mandates = []

    return render(request, 'choose_myself.html', {
        'form': form,
        'combined_accounts': combined_accounts,
        'risk_profile_override': risk_profile_override,
        'portfolio_override': portfolio_override,
        'questionnaire_risk_profile': questionnaire_risk_profile,
        'questionnaire_portfolio': questionnaire_portfolio,
        'selected_risk_profile': selected_risk_profile,
        'selected_portfolio': selected_portfolio,
        'portfolio_override_choices': portfolio_override_choices,
        'portfolio_allocations_json': portfolio_allocations_json,
        'mandates': mandates,
    })

@login_required
def let_pm_choose_view(request):
    if request.method == 'POST':
        form = LetPmChooseForm(request.POST)
        if form.is_valid():
            # Retrieve the stored data
            stored_data = LetPmChooseData.objects.filter(user=request.user)

            # Process the data and generate PDF
            # ... (implement your PDF generation logic here)

            return redirect('let_pm_choose_result')
    else:
        form = LetPmChooseForm()
    return render(request, 'let_pm_choose.html', {'form': form})

@login_required
def choose_myself_result(request):
    return render(request, 'choose_myself_result.html')

@login_required
def let_pm_choose_result(request):
    return render(request, 'let_pm_choose_result.html')

@login_required
def get_target_weights(request):
    responses = QuestionnaireResponse.objects.filter(user=request.user)
    form_data = {response.question: response.answer for response in responses}
    form_data['investment_goals'] = [response.answer for response in responses.filter(question='investment_goals')]

    form = QuestionnaireForm(data=form_data)
    if form.is_valid():
        portfolio_recommendation = form.get_portfolio_recommendation()
        asset_mix = form.get_asset_mix(portfolio_recommendation)
        risk_rating, portfolio_definition = get_risk_and_definition(portfolio_recommendation)
        return JsonResponse({
            'target_weights': asset_mix,
            'portfolio_recommendation': portfolio_recommendation,
            'risk_rating': risk_rating,
            'portfolio_definition': portfolio_definition
        })
    else:
        return JsonResponse({'error': 'Invalid form data'}, status=400)

@login_required
def choose_myself_performance(request):
    if request.method == 'POST':
        amounts = request.POST.getlist('amount')
        strategies = request.POST.getlist('strategy')

        # Clean the amount strings and convert to floats
        cleaned_amounts = []
        for amount in amounts:
            cleaned_amount = amount.replace('$', '').replace(',', '')
            try:
                cleaned_amounts.append(float(cleaned_amount))
            except ValueError:
                cleaned_amounts.append(0.0)  # Handle possible conversion error

        total_amount = sum(cleaned_amounts)
        weights = [amount / total_amount if total_amount != 0 else 0 for amount in cleaned_amounts]

        # Aggregate weights for each strategy
        strategy_weights = {}
        for strategy, weight in zip(strategies, weights):
            if strategy in strategy_weights:
                strategy_weights[strategy] += weight
            else:
                strategy_weights[strategy] = weight

        # Convert weights to percentages
        strategy_weights = {strategy: weight * 100 for strategy, weight in strategy_weights.items()}

        # Prepare the performance table
        performance_table = []
        for strategy, weight in strategy_weights.items():
            if strategy in performance_data['Strategy'].values:
                row = performance_data[performance_data['Strategy'] == strategy].iloc[0].to_dict()
                row['Weight'] = f"{weight:.1f}%"
                # Format the values with percentage signs and two decimal places
                for period in ['1M', '3M', 'YTD', '1YR', '3YR', '5YR', '10YR', 'SI']:
                    row[period] = f"{float(row[period]) * 100:.2f}%" if pd.notnull(row[period]) else 'N/A'
                    row[f"{period}b"] = f"{float(row[f'{period}b']) * 100:.2f}%" if pd.notnull(row[f"{period}b"]) else 'N/A'
                performance_table.append(row)
            else:
                logger.warning(f"Strategy {strategy} not found in performance data.")

        # Calculate the portfolio and benchmark returns
        portfolio_return = {}
        benchmark_return = {}
        periods = ['1M', '3M', 'YTD', '1YR', '3YR', '5YR', '10YR', 'SI']
        for period in periods:
            portfolio_return[period] = sum(
                (float(row[period].replace('%', '')) if isinstance(row[period], str) and row[period] != 'N/A' else 0) * (float(row['Weight'].replace('%', '')) / 100)
                for row in performance_table
            )
            benchmark_return[period] = sum(
                (float(row[f'{period}b'].replace('%', '')) if isinstance(row[f'{period}b'], str) and row[f'{period}b'] != 'N/A' else 0) * (float(row['Weight'].replace('%', '')) / 100)
                for row in performance_table
            )

        # Add Portfolio and Benchmark rows to the performance table
        portfolio_row = {'Strategy': 'Portfolio', 'Weight': '100.0%'}
        benchmark_row = {'Strategy': 'Benchmark', 'Weight': '100.0%'}
        for period in periods:
            portfolio_row[period] = f"{portfolio_return[period]:.2f}%"
            benchmark_row[period] = f"{benchmark_return[period]:.2f}%"
        performance_table.append(portfolio_row)
        performance_table.append(benchmark_row)

        # Prepare the calendar year returns table
        calendar_year_table = []
        years = ['2025', '2024', '2023', '2022', '2021', '2020', '2019']
        for strategy, weight in strategy_weights.items():
            if strategy in performance_data['Strategy'].values:
                row = performance_data[performance_data['Strategy'] == strategy].iloc[0].to_dict()
                row['Weight'] = f"{weight:.1f}%"
                # Format the values with percentage signs and two decimal places
                for year in years:
                    row[year] = f"{float(row.get(f'{year}a', 0)) * 100:.2f}%" if pd.notnull(row.get(f'{year}a')) and row.get(f'{year}a') != 'N/A' else 'N/A'
                    row[f"{year}b"] = f"{float(row.get(f'{year}b', 0)) * 100:.2f}%" if pd.notnull(row.get(f'{year}b')) and row.get(f'{year}b') != 'N/A' else 'N/A'
                calendar_year_table.append(row)
            else:
                logger.warning(f"Strategy {strategy} not found in performance data.")

        # Calculate the portfolio and benchmark returns for calendar years
        calendar_year_portfolio_return = {year: 0 for year in years}
        calendar_year_benchmark_return = {year: 0 for year in years}

        for year in years:
            calendar_year_portfolio_return[year] = sum(
                (float(row[year].replace('%', '')) if isinstance(row[year], str) and row[year] != 'N/A' else 0) *
                (float(row['Weight'].replace('%', '')) / 100)
                for row in calendar_year_table
            )
            calendar_year_benchmark_return[year] = sum(
                (float(row[f'{year}b'].replace('%', '')) if isinstance(row[f'{year}b'], str) and row[f'{year}b'] != 'N/A' else 0) *
                (float(row['Weight'].replace('%', '')) / 100)
                for row in calendar_year_table
            )

        # Add Portfolio and Benchmark rows to the calendar year table
        portfolio_row = {'Strategy': 'Portfolio', 'Weight': '100.0%'}
        benchmark_row = {'Strategy': 'Benchmark', 'Weight': '100.0%'}
        for year in years:
            portfolio_row[year] = f"{calendar_year_portfolio_return[year]:.2f}%"
            benchmark_row[year] = f"{calendar_year_benchmark_return[year]:.2f}%"
        calendar_year_table.append(portfolio_row)
        calendar_year_table.append(benchmark_row)

        # Get disclaimers for the selected strategies
        disclaimer_text = get_disclaimer(strategy_weights)

        # Split the disclaimer text into a list of lines
        disclaimer_lines = disclaimer_text.split('\n')

        context = {
            'performance_summary': performance_table,
            'portfolio_return': {period: f"{value:.2f}%" for period, value in portfolio_return.items()},
            'benchmark_return': {period: f"{value:.2f}%" for period, value in benchmark_return.items()},
            'calendar_year_summary': calendar_year_table,
            'disclaimer_lines': disclaimer_lines,
            'selected_strategies': strategies,
        }

        return render(request, 'choose_myself_performance.html', context)

    return render(request, 'choose_myself.html')

def get_disclaimer(strategy_weights):
    disclaimers = {
        "Aviso 5-year Bond Ladder (Taxable)": "The performance of the <b>Aviso 5-year Bond Ladder (Taxable)</b> is presented using the current yield to maturity as a proxy for reference purposes only. Due to the nature of this strategy, where bonds are held to maturity in a laddered structure, traditional historical return benchmarks are not applicable, and no actual historical returns are available for presentation. Consequently, the current yield to maturity serves as an illustrative proxy to approximate the expected returns of this strategy when calculating portfolio returns in conjunction with other strategies. This approach provides a forward-looking estimate based on current market conditions rather than historical performance data. However, this proxy does not account for potential interest rate changes, reinvestment risk, or other factors that may affect actual future returns. It should be noted that actual performance may differ from the projected yield to maturity depending on market conditions and timing of investments. Investors are advised that this performance representation is for illustrative purposes only and should not be relied upon as an indicator of future results.",
        "Aviso 5-year Bond Ladder (Income)": "The performance of the <b>Aviso 5-year Bond Ladder (Income)</b> is presented using the current yield to maturity as a proxy for reference purposes only. Due to the nature of this strategy, where bonds are held to maturity in a laddered structure, traditional historical return benchmarks are not applicable, and no actual historical returns are available for presentation. Consequently, the current yield to maturity serves as an illustrative proxy to approximate the expected returns of this strategy when calculating portfolio returns in conjunction with other strategies. This approach provides a forward-looking estimate based on current market conditions rather than historical performance data. However, this proxy does not account for potential interest rate changes, reinvestment risk, or other factors that may affect actual future returns. It should be noted that actual performance may differ from the projected yield to maturity depending on market conditions and timing of investments. Investors are advised that this performance representation is for illustrative purposes only and should not be relied upon as an indicator of future results.",
        "Brookfield Private Real Assets Fund": "The performance of the <b>Brookfield Private Real Assets Fund</b> is presented using a blended index approach for reference purposes only. Due to inherent delays associated with private fund reporting, the Fund's actual return calculations are typically available with a lag. Consequently, these indices serve as illustrative proxies to approximate the Fund's returns and to compensate for any data gaps when calculating portfolio returns in conjunction with other strategies. The Fund does not actively track these indices, nor does it seek to replicate or outperform them. Prior to 2016, a blended benchmark comprised of 50% MSCI World Real Estate Index (CAD) and 50% MSCI World Infrastructure Index (CAD) is used. Subsequent to 2016, the S&P Real Asset TR index (CAD) is used. These are widely recognized market benchmarks designed to reflect the general performance of real estate and infrastructure markets, consistent with the Fund's investment objectives and strategies. However, the indices do not account for fees, expenses, taxes, or other costs associated with investing in the Fund. It should be noted that the Fund's holdings, sector allocations, and risk profile may differ significantly from those of the indices, leading to substantial variances in performance across different time periods. Past performance is neither a guarantee nor a reliable indicator of future results. Investors are advised not to rely solely upon the benchmark indices to gauge the Fund's expected or potential returns, risk characteristics, or suitability for investment purposes.",
        "Hamilton Lane Global Private Assets Fund": "The performance of the <b>Hamilton Lane Global Private Assets Fund</b> is presented against the MSCI World NR Index (CAD) for reference purposes only. Due to inherent delays associated with private fund reporting, the Fund's actual return calculations are typically available with a lag. Consequently, this Index serves as an illustrative proxy to approximate the Fund's returns and to compensate for any data gaps when calculating portfolio returns in conjunction with other strategies. The Fund does not actively track the Index, nor does it seek to replicate or outperform it. The MSCI World NR Index (CAD) is a widely recognized market benchmark designed to reflect the general performance of global equity markets, providing a broad reference point for the Fund's diversified private market investments. However, the Index does not account for fees, expenses, taxes, or other costs associated with investing in the Fund. It should be noted that the Fund's holdings, sector allocations, and risk profile may differ significantly from those of the Index, leading to substantial variances in performance across different time periods. Private market investments typically have different risk and return characteristics compared to public markets. Past performance is neither a guarantee nor a reliable indicator of future results. Investors are advised not to rely solely upon the benchmark Index to gauge the Fund's expected or potential returns, risk characteristics, or suitability for investment purposes.",
        "Sagard Private Credit Fund": "The performance of the <b>Sagard Private Credit Fund</b> is presented against the Morningstar LSTA US Leveraged Loan Total Return (CAD hedged) Index for reference purposes only. Due to inherent delays associated with private fund reporting, the Fund's actual return calculations are typically available with a lag. Consequently, this Index serves as an illustrative proxy to approximate the Fund's returns and to compensate for any data gaps when calculating portfolio returns in conjunction with other strategies. The Fund does not actively track the Index, nor does it seek to replicate or outperform it. The Morningstar LSTA US Leveraged Loan Total Return (CAD hedged) Index is a widely recognized market benchmark designed to reflect the general performance of a broad segment of the leveraged loan asset class, consistent with the Fund's investment objectives and strategies. However, the Index does not account for fees, expenses, taxes, or other costs associated with investing in the Fund. It should be noted that the Fund's holdings, sector allocations, and risk profile may differ significantly from those of the Index, leading to substantial variances in performance across different time periods. Past performance is neither a guarantee nor a reliable indicator of future results. Investors are advised not to rely solely upon the benchmark Index to gauge the Fund's expected or potential returns, risk characteristics, or suitability for investment purposes.",
        "Mawer EAFE Large Cap Fund": "The performance of the <b>Mawer EAFE Large Cap Fund</b> is presented using a blended approach for reference purposes only. From May 2020 onwards, actual strategy returns are used. For the period from 2015 to April 2020, the MSCI EAFE NR index was used as a proxy to illustrate historical performance. This approach serves to provide a more comprehensive historical context when calculating portfolio returns in conjunction with other strategies. The MSCI EAFE NR index is a widely recognized market benchmark designed to measure the equity market performance of developed markets outside of North America. However, the index does not account for fees, expenses, taxes, or other costs associated with investing in the fund. It should be noted that the fund's holdings, sector allocations, and risk profile may differ significantly from those of the index, leading to substantial variances in performance across different time periods. Past performance is neither a guarantee nor a reliable indicator of future results. Investors are advised not to rely solely upon the benchmark index to gauge the fund's expected or potential returns, risk characteristics, or suitability for investment purposes."
    }

    relevant_disclaimers = [disclaimers[strategy] for strategy in strategy_weights.keys() if strategy in disclaimers]
    return "\n".join(relevant_disclaimers)


@transaction.atomic
@require_POST
def save_choose_myself_data(request):
    try:
        data = request.POST

        # Clear existing data for the user
        ChooseMyselfData.objects.filter(user=request.user).delete()

        # Collect data from the form
        account_owners = data.getlist('account_owner')
        account_types = data.getlist('account_type')
        amounts = data.getlist('amount')
        strategies = data.getlist('strategy')
        version_number = data.get('version_number', 'N/A')
        comments = data.get('comments', '')
        desired_rate = data.get('desired_rate', '')
        cms_fee = data.get('cms_fee', '')
        cmh_account_types = data.getlist('cmh_combined_account')
        cmh_amounts = data.getlist('cmh_amount')

        # Clean the amount strings and convert to floats
        cleaned_amounts = []
        for amount in amounts:
            cleaned_amount = amount.replace('$', '').replace(',', '')
            try:
                cleaned_amount = float(cleaned_amount)
                cleaned_amounts.append(cleaned_amount)
            except ValueError:
                cleaned_amounts.append(0)

        # Save account details
        for i in range(len(account_owners)):
            ChooseMyselfData.objects.create(
                user=request.user,
                account_owner=account_owners[i],
                account_type=account_types[i],
                amount=cleaned_amounts[i],
                strategy=strategies[i],
                version_number=version_number,
            )

        for i in range(len(cmh_account_types)):
            try:
                cmh_amount = float(cmh_amounts[i].replace('$', '').replace(',', ''))
            except ValueError:
                cmh_amount = 0

            ChooseMyselfData.objects.create(
                user=request.user,
                account_owner='Client-directed Holdings ',
                account_type=cmh_account_types[i],
                amount=cmh_amount,
                strategy='Client Managed',
                version_number=version_number,
            )

        # Save comments, desired rate, and CMS fee separately
        ChooseMyselfData.objects.create(
            user=request.user,
            account_owner='Comments',
            account_type='Comments',
            amount=0,
            strategy=comments,  # This will now be an empty string if comments were cleared
            version_number=version_number,
        )

        ChooseMyselfData.objects.create(
            user=request.user,
            account_owner='Desired Rate',
            account_type='Desired Rate',
            amount=float(desired_rate) if desired_rate else 0,
            strategy='Desired Rate',
            version_number=version_number,
        )

        ChooseMyselfData.objects.create(
            user=request.user,
            account_owner='CMS Fee',
            account_type='CMS Fee',
            amount=float(cms_fee) if cms_fee else 0,
            strategy='CMS Fee',
            version_number=version_number,
        )

        # Save IPS changes if provided
        ips_changes = data.get('ips_changes', '')
        ChooseMyselfData.objects.create(
            user=request.user,
            account_owner='IPS Changes',
            account_type='IPS Changes',
            amount=0,
            strategy=ips_changes,
            version_number=version_number,
        )

        # Save risk profile and portfolio overrides
        ChooseMyselfData.objects.create(
            user=request.user,
            account_owner='Risk Profile Override',
            account_type='Override',
            amount=0,
            strategy=data.get('risk_profile_override', ''),
            version_number=version_number,
        )
        ChooseMyselfData.objects.create(
            user=request.user,
            account_owner='Portfolio Override',
            account_type='Override',
            amount=0,
            strategy=data.get('portfolio_override', ''),
            version_number=version_number,
        )

        logger.info(f"Saved account details for user {request.user.username} with version number {version_number}")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error in save_choose_myself_data: {e}", exc_info=True)
        return JsonResponse({'status': 'failed', 'message': str(e)}, status=400)

@login_required
@require_POST
def save_let_pm_choose_data(request):
    try:
        user = request.user
        data = request.POST

        # Log received data for debugging
        logger.info(f"Received data: {data}")

        # Clear existing data for the user
        LetPmChooseData.objects.filter(user=user).delete()

        # Save account details
        index = 0
        while f'account_owner_{index}' in data:
            LetPmChooseData.objects.create(
                user=user,
                account_owner=data.get(f'account_owner_{index}'),
                account_type=data.get(f'account_type_{index}'),
                amount=float(data.get(f'amount_{index}', '0').replace('$', '').replace(',', ''))
            )
            index += 1

        # Save desired trailer rate
        LetPmChooseData.objects.create(
            user=user,
            account_owner='Desired Trailer Rate',
            account_type='Desired Trailer Rate',
            amount=float(data.get('desired_trailer_rate', 0))
        )

        # Save Client-directed Holdings  data
        client_managed_holdings = data.get('client_managed_holdings', 'No')
        LetPmChooseData.objects.create(
            user=user,
            account_owner='Client-directed Holdings ',
            account_type=client_managed_holdings,
            amount=0
        )

        if client_managed_holdings == 'Yes':
            index = 0
            while f'cmh_account_{index}' in data:
                LetPmChooseData.objects.create(
                    user=user,
                    account_owner='Client Managed Account',
                    account_type=data.get(f'cmh_account_{index}'),
                    amount=float(data.get(f'cmh_amount_{index}', '0').replace('$', '').replace(',', ''))
                )
                index += 1

            # Save CMS fee
            LetPmChooseData.objects.create(
                user=user,
                account_owner='CMS Fee',
                account_type='CMS Fee',
                amount=float(data.get('cms_fee', 0))
            )

        # Save version number
        version_number = data.get('version_number', 'N/A')
        logger.info(f"Saving version number: {version_number}")
        LetPmChooseData.objects.create(
            user=user,
            account_owner='Version Number',
            account_type='Version Number',
            amount=0,
            additional_info=version_number
        )

        # Save attach fact sheets preference
        attach_fact_sheets = data.get('attach_fact_sheets', 'No')
        logger.info(f"Saving attach fact sheets preference: {attach_fact_sheets}")
        LetPmChooseData.objects.create(
            user=user,
            account_owner='Attach Fact Sheets',
            account_type='Attach Fact Sheets',
            amount=0,
            additional_info=attach_fact_sheets
        )

        # Save PM comments
        pm_comments = data.get('pm_comments', '')
        logger.info(f"Saving PM comments: {pm_comments}")
        LetPmChooseData.objects.create(
            user=user,
            account_owner='PM Comments',
            account_type='PM Comments',
            amount=0,
            additional_info=pm_comments
        )

        logger.info("Data saved successfully")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error in save_let_pm_choose_data: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def generate_ips_details_for_pm(request):
    try:
        # Fetch all the data needed for the IPS PCQ
        responses = QuestionnaireResponse.objects.filter(user=request.user)
        total_score = sum(response.score for response in responses if response.question in [
            'annual_income', 'income_savings', 'spending_needs',
            'risk_tolerance', 'investment_loss', 'recovery_period',
            'reaction_to_drop', 'high_risk_opportunities', 'volatility',
            'investment_knowledge', 'time_horizon', 'liquidity_needs'
        ])

        form_data = {response.question: response.answer for response in responses}
        form_data['investment_goals'] = [response.answer for response in responses.filter(question='investment_goals')]

        form = QuestionnaireForm(data=form_data)

        if form.is_valid():
            portfolio_recommendation = form.get_portfolio_recommendation()
            asset_mix = form.get_asset_mix(portfolio_recommendation)
            risk_rating, portfolio_definition = get_risk_and_definition(portfolio_recommendation)
        else:
            portfolio_recommendation = "Invalid data"
            asset_mix = {}
            risk_rating = "N/A"
            portfolio_definition = "N/A"

        # Fetch the Let PM Choose data
        let_pm_choose_data = LetPmChooseData.objects.filter(user=request.user).exclude(
            account_owner__in=['Desired Trailer Rate', 'Client-directed Holdings ', 'CMS Fee', 'Client Managed Account', 'Version Number', 'Attach Fact Sheets', 'PM Comments']
        )
        desired_trailer_rate = LetPmChooseData.objects.filter(user=request.user, account_owner='Desired Trailer Rate').first()
        client_managed_holdings = LetPmChooseData.objects.filter(user=request.user, account_owner='Client-directed Holdings ').first()
        cms_fee = LetPmChooseData.objects.filter(user=request.user, account_owner='CMS Fee').first()

        # Fetch client managed accounts
        client_managed_accounts = LetPmChooseData.objects.filter(user=request.user, account_owner='Client Managed Account')

        # Fetch version number, attach fact sheets preference, and PM comments
        version_number = LetPmChooseData.objects.filter(user=request.user, account_owner='Version Number').first()
        attach_fact_sheets = LetPmChooseData.objects.filter(user=request.user, account_owner='Attach Fact Sheets').first()
        pm_comments = LetPmChooseData.objects.filter(user=request.user, account_owner='PM Comments').first()

        context = {
            'responses': responses,
            'user': request.user,
            'total_score': total_score,
            'portfolio_recommendation': portfolio_recommendation,
            'asset_mix': asset_mix,
            'risk_rating': risk_rating,
            'portfolio_definition': portfolio_definition,
            'advisor_name': form.cleaned_data.get('advisor_name', 'N/A'),
            'annual_withdrawal': form.cleaned_data.get('annual_withdrawal', 'N/A'),
            'let_pm_choose_data': let_pm_choose_data,
            'desired_trailer_rate': desired_trailer_rate.amount if desired_trailer_rate else 'N/A',
            'client_managed_holdings': client_managed_holdings.account_type if client_managed_holdings else 'No',
            'client_managed_accounts': client_managed_accounts,
            'cms_fee': cms_fee.amount if cms_fee else 'N/A',
            'version_number': version_number.additional_info if version_number else 'N/A',
            'attach_fact_sheets': attach_fact_sheets.additional_info if attach_fact_sheets else 'No',
            'pm_comments': pm_comments.additional_info if pm_comments else '',
        }

        html_string = render_to_string('ips_details_for_pm.html', context)
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="IPS_Details_for_PM_{request.user.username}.pdf"'
        return response
    except Exception as e:
        logger.error(f"Error generating IPS Details for PM PDF: {e}", exc_info=True)
        return HttpResponse("An error occurred while generating the PDF. Please try again or contact support.", status=500)

@login_required
def choose_myself_risk_analytics(request):
    if request.method == 'POST':
        # Get the strategies and amounts from the form
        strategies = request.POST.getlist('strategy')
        amounts = request.POST.getlist('amount')

        # Clean the amount strings and convert to floats
        cleaned_amounts = []
        for amount in amounts:
            cleaned_amount = amount.replace('$', '').replace(',', '')
            try:
                cleaned_amount = float(cleaned_amount)
                cleaned_amounts.append(cleaned_amount)
            except ValueError:
                cleaned_amounts.append(0)

        total_amount = sum(cleaned_amounts)
        weights = [amount / total_amount if total_amount != 0 else 0 for amount in cleaned_amounts]

        # Aggregate weights for each strategy
        strategy_weights = {}
        for strategy, weight in zip(strategies, weights):
            if strategy in strategy_weights:
                strategy_weights[strategy] += weight
            else:
                strategy_weights[strategy] = weight

        # Convert weights to percentages
        strategy_weights = {strategy: weight * 100 for strategy, weight in strategy_weights.items()}

        # TODO: Once you provide the risk analytics data, we'll populate these with real data
        # For now, using placeholder data
        risk_metrics = []
        var_analysis = []
        correlation_matrix = []
        correlation_headers = []
        disclaimer_lines = []

        for strategy, weight in strategy_weights.items():
            # Add placeholder risk metrics for each strategy
            risk_metrics.append({
                'Strategy': strategy,
                'Weight': f"{weight:.1f}%",
                'Sharpe': 'TBD',
                'Sortino': 'TBD',
                'MaxDrawdown': 'TBD',
                'StdDev': 'TBD',
                'Beta': 'TBD',
                'Alpha': 'TBD',
                'RSquared': 'TBD'
            })

            # Add placeholder VaR analysis for each strategy
            var_analysis.append({
                'Strategy': strategy,
                'Weight': f"{weight:.1f}%",
                'HistoricalVaR95': 'TBD',
                'HistoricalVaR99': 'TBD',
                'ParametricVaR95': 'TBD',
                'ParametricVaR99': 'TBD',
                'ConditionalVaR95': 'TBD',
                'ConditionalVaR99': 'TBD'
            })

        # Add Portfolio and Benchmark rows
        risk_metrics.append({
            'Strategy': 'Portfolio',
            'Weight': '100.0%',
            'Sharpe': 'TBD',
            'Sortino': 'TBD',
            'MaxDrawdown': 'TBD',
            'StdDev': 'TBD',
            'Beta': 'TBD',
            'Alpha': 'TBD',
            'RSquared': 'TBD'
        })

        var_analysis.append({
            'Strategy': 'Portfolio',
            'Weight': '100.0%',
            'HistoricalVaR95': 'TBD',
            'HistoricalVaR99': 'TBD',
            'ParametricVaR95': 'TBD',
            'ParametricVaR99': 'TBD',
            'ConditionalVaR95': 'TBD',
            'ConditionalVaR99': 'TBD'
        })

        # Placeholder correlation matrix data
        asset_classes = ['Cash', 'Fixed Income', 'Canadian Equity', 'U.S. Equity', 'International Equity', 'Alternatives']
        correlation_headers = asset_classes

        # Create a placeholder correlation matrix
        for asset_class in asset_classes:
            row_values = ['TBD' for _ in asset_classes]
            correlation_matrix.append({
                'AssetClass': asset_class,
                'Values': row_values
            })

        # Add placeholder disclaimer lines
        disclaimer_lines = [
            "Past performance is not indicative of future results.",
            "Risk metrics are calculated using historical data and may not reflect future risk.",
            "Value at Risk (VaR) calculations are based on historical data and specific confidence intervals.",
            "Correlation analysis is based on historical relationships which may change over time."
        ]

        context = {
            'risk_metrics': risk_metrics,
            'var_analysis': var_analysis,
            'correlation_matrix': correlation_matrix,
            'correlation_headers': correlation_headers,
            'disclaimer_lines': disclaimer_lines
        }

        return render(request, 'choose_myself_risk_analytics.html', context)

    return render(request, 'choose_myself.html')

@require_POST
def generate_account_summary(request):
    try:
        # Force matplotlib to use Agg backend for this request
        matplotlib.use('Agg', force=True)

        data = json.loads(request.body)
        accounts = []
        total_amount = 0

        # Process accounts data
        for account in data.get('accounts', []):
            accounts.append({
                'owner': account.get('owner', ''),
                'type': account.get('type', ''),
                'amount': float(account.get('amount', 0)),
                'strategy': account.get('strategy', '')
            })
            total_amount += float(account.get('amount', 0))

        # Get target and proposed weights
        target_weights = data.get('target_weights', {})
        proposed_weights = data.get('proposed_weights', {})
        fee_range_text = data.get('fee_range_text', '')
        deviation_comments = data.get('deviation_comments', '')

        # Get client info
        client_household_name = QuestionnaireResponse.objects.filter(
            user=request.user,
            question='client_identifier'
        ).first()

        version_number = ChooseMyselfData.objects.filter(
            user=request.user
        ).exclude(
            account_owner__in=['Client-directed Holdings ', 'Comments', 'Desired Rate', 'CMS Fee', 'IPS Changes']
        ).first()

        # Prepare logo URL using absolute file path
        if settings.DEBUG:
            logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo.png'
        else:
            logo_path = Path(settings.STATIC_ROOT) / 'images' / 'logo.png'
        logo_url = logo_path.as_uri()

        # Prepare context with absolute paths for static files
        context = {
            'accounts': accounts,
            'total_amount': total_amount,
            'target_weights': target_weights,
            'proposed_weights': proposed_weights,
            'fee_range_text': fee_range_text,
            'deviation_comments': deviation_comments,
            'creation_date': datetime.now().strftime('%Y-%m-%d'),
            'logo_url': logo_url,
            'version_number': version_number.version_number if version_number else "1"
        }

        # Render HTML
        html_string = render_to_string('account_summary.html', context)

        # Create response
        response = HttpResponse(content_type='application/pdf')

        # Set filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        client_name = client_household_name.answer if client_household_name else "Unknown"
        version = version_number.version_number if version_number else "1"
        custom_filename = f"{current_date} Proposal for {client_name} Version {version}.pdf"
        custom_filename = custom_filename.replace(" ", "_")
        response['Content-Disposition'] = f'attachment; filename="{custom_filename}"'

        # Get the absolute path to the static directory
        static_dir = settings.STATIC_ROOT if not settings.DEBUG else settings.STATICFILES_DIRS[0]

        # Create CSS to handle static files properly
        css = CSS(string='''
            @font-face {
                font-family: 'Liberation Sans';
                src: local('Liberation Sans');
            }
            body {
                font-family: 'Liberation Sans', sans-serif;
            }
        ''')

        # Generate PDF with proper static file handling
        base_url = os.path.join('file://', static_dir)
        html = HTML(string=html_string, base_url=base_url)
        result = html.write_pdf(stylesheets=[css])
        response.write(result)

        return response

    except Exception as e:
        logger.error(f"Account summary generation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Clean up resources
        plt.close('all')
        if 'html' in locals():
            del html
        if 'result' in locals():
            del result

def generate_pie_chart(data, request):
    try:
        # Create figure with explicit DPI setting
        plt.figure(figsize=(10, 8), dpi=300)

        # Create pie chart with explicit font settings
        plt.pie(data['sizes'],
                labels=data['labels'],
                autopct='%1.1f%%')
        plt.axis('equal')

        # Use media directory within static for production
        if not settings.DEBUG:
            target_dir = os.path.join(settings.STATIC_ROOT, 'images')  # Store in static/images instead of media
        else:
            target_dir = os.path.join(settings.MEDIA_ROOT)

        # Ensure directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pie_chart_filename = f'pie_chart_{timestamp}.png'
        pie_chart_path = os.path.join(target_dir, pie_chart_filename)

        # Save with explicit settings
        plt.savefig(pie_chart_path,
                   bbox_inches='tight',
                   dpi=300,
                   format='png',
                   optimize=True,
                   transparent=False,
                   facecolor='white',
                   edgecolor='none')

        # Clean up old files
        cleanup_old_pie_charts(target_dir)

        # Return the correct URL - always use absolute paths
        if settings.DEBUG:
            return f"{settings.MEDIA_URL}{pie_chart_filename}?v={timestamp}"
        else:
            return f"/static/images/{pie_chart_filename}?v={timestamp}"  # Use /static/images instead of /media

    except Exception as e:
        logger.error(f"Pie chart generation error: {str(e)}")
        raise
    finally:
        plt.close('all')

def cleanup_old_pie_charts(media_dir, max_files=5):
    """Clean up old pie chart files to prevent disk space issues."""
    try:
        files = glob.glob(os.path.join(media_dir, 'pie_chart_*.png'))
        if len(files) > max_files:
            # Sort by modification time, oldest first
            files.sort(key=os.path.getmtime)
            # Remove oldest files, keeping only max_files
            for f in files[:-max_files]:
                try:
                    os.remove(f)
                except OSError as e:
                    logger.warning(f"Failed to remove old pie chart {f}: {str(e)}")
    except Exception as e:
        logger.warning(f"Failed to cleanup old pie charts: {str(e)}")


# ---------------------------------------------------------------------------
# Save Proposal views
# ---------------------------------------------------------------------------

@login_required
@require_POST
def save_proposal(request):
    """Snapshot the current ChooseMyselfData rows and save as a named proposal."""
    try:
        rows = list(
            ChooseMyselfData.objects.filter(user=request.user).values(
                'account_owner', 'account_type', 'amount', 'strategy', 'version_number'
            )
        )

        label = request.POST.get('label', '').strip()
        if not label:
            # Auto-generate from first non-special account_owner
            special = {'CMS Fee', 'Desired Rate', 'Risk Profile Override',
                       'Portfolio Override', 'Comments', 'IPS Changes', 'Client-directed Holdings '}
            first_owner = next(
                (r['account_owner'] for r in rows if r['account_owner'] not in special),
                None
            )
            date_str = timezone.now().strftime('%Y-%m-%d')
            label = f"{first_owner} — {date_str}" if first_owner else f"Proposal — {date_str}"

        risk_profile_override = request.POST.get('risk_profile_override', '')
        portfolio_override = request.POST.get('portfolio_override', '')

        # Convert Decimal to str for JSON serialisation
        for r in rows:
            if hasattr(r['amount'], '__float__'):
                r['amount'] = str(r['amount'])

        SavedProposal.objects.create(
            user=request.user,
            label=label,
            data=json.dumps(rows),
            risk_profile_override=risk_profile_override,
            portfolio_override=portfolio_override,
        )
    except Exception as e:
        logger.error(f"save_proposal error: {e}")

    return redirect('proposals_list')


@login_required
def proposals_list(request):
    """Show all saved proposals for the current user."""
    try:
        proposals = SavedProposal.objects.filter(user=request.user)
    except Exception as e:
        logger.error(f"proposals_list error: {e}")
        proposals = []
    return render(request, 'proposals.html', {'proposals': proposals})


@login_required
@require_POST
def load_proposal(request, proposal_id):
    """Restore ChooseMyselfData from a saved proposal and redirect to choose_myself."""
    proposal = get_object_or_404(SavedProposal, id=proposal_id, user=request.user)
    try:
        rows = json.loads(proposal.data)
        with transaction.atomic():
            ChooseMyselfData.objects.filter(user=request.user).delete()
            for r in rows:
                ChooseMyselfData.objects.create(
                    user=request.user,
                    account_owner=r.get('account_owner', ''),
                    account_type=r.get('account_type', ''),
                    amount=r.get('amount', '0'),
                    strategy=r.get('strategy', ''),
                    version_number=r.get('version_number', 'N/A'),
                )
    except Exception as e:
        logger.error(f"load_proposal error: {e}")
    return redirect('choose_myself')


@login_required
@require_POST
def delete_proposal(request, proposal_id):
    """Delete a saved proposal."""
    proposal = get_object_or_404(SavedProposal, id=proposal_id, user=request.user)
    try:
        proposal.delete()
    except Exception as e:
        logger.error(f"delete_proposal error: {e}")
    return redirect('proposals_list')
