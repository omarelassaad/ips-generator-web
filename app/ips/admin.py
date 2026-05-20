from django.contrib import admin
from django.utils.html import format_html
from django.core.cache import cache
from .models import (
    Profile, QuestionnaireResponse, ChooseMyselfData, LetPmChooseData,
    FeeCategory, FeeTier, Mandate, ReturnsUpload,
    PortfolioProfile, IPSCopyBlock, SiteDocument,
)


# ---------------------------------------------------------------------------
# Existing models
# ---------------------------------------------------------------------------

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'user__email')

class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'score')
    search_fields = ('user__username', 'question', 'answer')

class ChooseMyselfDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_owner', 'account_type', 'amount', 'strategy', 'version_number')
    search_fields = ('user__username', 'account_owner', 'account_type', 'strategy')

class LetPmChooseDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_owner', 'account_type', 'amount', 'timestamp', 'additional_info')
    search_fields = ('user__username', 'account_owner', 'account_type', 'additional_info')
    ordering = ('-timestamp',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(QuestionnaireResponse, QuestionnaireResponseAdmin)
admin.site.register(ChooseMyselfData, ChooseMyselfDataAdmin)
admin.site.register(LetPmChooseData, LetPmChooseDataAdmin)


# ---------------------------------------------------------------------------
# Fee Schedule
# ---------------------------------------------------------------------------

class FeeTierInline(admin.TabularInline):
    model = FeeTier
    extra = 1
    fields = ('order', 'lower', 'upper', 'max_fee', 'max_trailer', 'min_fee', 'min_trailer', 'admin_fee')
    ordering = ('order', 'lower')


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'tier_count')
    search_fields = ('name',)
    inlines       = [FeeTierInline]

    def tier_count(self, obj):
        return obj.tiers.count()
    tier_count.short_description = "# Tiers"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('fee_data')
        cache.delete('strategy_fee_map')

    def save_formset(self, request, form, formset, change):
        """Also clear cache when fee tiers are added/edited/deleted inline."""
        super().save_formset(request, form, formset, change)
        cache.delete('fee_data')
        cache.delete('strategy_fee_map')


# ---------------------------------------------------------------------------
# Mandates
# ---------------------------------------------------------------------------

@admin.register(Mandate)
class MandateAdmin(admin.ModelAdmin):
    list_display  = ('name', 'fee_category', 'allocation_summary', 'has_fact_sheet', 'has_disclaimer', 'is_active', 'display_order')
    list_filter   = ('is_active', 'fee_category')
    search_fields = ('name',)
    list_editable = ('is_active', 'display_order')
    ordering      = ('display_order', 'name')
    fieldsets = (
        (None, {
            'fields': ('name', 'fee_category', 'minimum_investment', 'is_active', 'display_order'),
        }),
        ('Asset Allocation (%)', {
            'fields': (
                ('cash', 'fixed_income'),
                ('canadian_equity', 'us_equity'),
                ('international_equity', 'alternatives'),
            ),
        }),
        ('Documents', {
            'fields': ('fact_sheet', 'disclaimer'),
        }),
    )

    def allocation_summary(self, obj):
        return (
            f"Cash {obj.cash}% | FI {obj.fixed_income}% | "
            f"CA {obj.canadian_equity}% | US {obj.us_equity}% | "
            f"Intl {obj.international_equity}% | Alt {obj.alternatives}%"
        )
    allocation_summary.short_description = "Allocation"

    def has_fact_sheet(self, obj):
        return bool(obj.fact_sheet)
    has_fact_sheet.boolean = True
    has_fact_sheet.short_description = "Fact Sheet"

    def has_disclaimer(self, obj):
        return bool(obj.disclaimer)
    has_disclaimer.boolean = True
    has_disclaimer.short_description = "Disclaimer"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('strategy_data')
        cache.delete('fee_data')
        cache.delete('strategy_fee_map')
        cache.delete('mandates')


# ---------------------------------------------------------------------------
# Returns Uploads
# ---------------------------------------------------------------------------

@admin.register(ReturnsUpload)
class ReturnsUploadAdmin(admin.ModelAdmin):
    list_display  = ('as_of_date', 'uploaded_at', 'is_active', 'file_link')
    list_filter   = ('is_active',)
    readonly_fields = ('uploaded_at',)
    ordering      = ('-uploaded_at',)

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return "—"
    file_link.short_description = "File"

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            ReturnsUpload.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
        cache.delete('performance_data')


# ---------------------------------------------------------------------------
# Portfolio Profiles
# ---------------------------------------------------------------------------

@admin.register(PortfolioProfile)
class PortfolioProfileAdmin(admin.ModelAdmin):
    list_display  = ('name', 'allocation_summary', 'order')
    list_editable = ('order',)
    ordering      = ('order', 'name')
    fieldsets = (
        (None, {
            'fields': ('name', 'order', 'description'),
        }),
        ('Standard Allocations % (liquidity not important)', {
            'fields': (
                ('cash', 'fixed_income'),
                ('canadian_equity', 'us_equity'),
                ('international_equity', 'alternatives'),
            ),
        }),
        ('Liquidity-Adjusted Allocations % (liquidity very/somewhat important)', {
            'classes': ('collapse',),
            'fields': (
                ('liq_cash', 'liq_fixed_income'),
                ('liq_canadian_equity', 'liq_us_equity'),
                ('liq_international_equity', 'liq_alternatives'),
            ),
        }),
    )

    def allocation_summary(self, obj):
        return (f"Cash {obj.cash}% | FI {obj.fixed_income}% | "
                f"CA {obj.canadian_equity}% | US {obj.us_equity}% | "
                f"Intl {obj.international_equity}% | Alt {obj.alternatives}%")
    allocation_summary.short_description = "Standard Allocation"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('portfolio_profiles')


# ---------------------------------------------------------------------------
# IPS Copy Blocks
# ---------------------------------------------------------------------------

@admin.register(IPSCopyBlock)
class IPSCopyBlockAdmin(admin.ModelAdmin):
    list_display  = ('category', 'key', 'title', 'body_preview', 'order')
    list_filter   = ('category',)
    list_editable = ('order',)
    search_fields = ('key', 'title', 'body')
    ordering      = ('category', 'order', 'key')
    fieldsets = (
        (None, {
            'fields': ('category', 'key', 'order'),
        }),
        ('Content', {
            'fields': ('title', 'body'),
            'description': 'HTML tags are supported in the body field (e.g. <b>, <i>).',
        }),
    )

    def body_preview(self, obj):
        return obj.body[:80] + '…' if len(obj.body) > 80 else obj.body
    body_preview.short_description = "Body (preview)"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete(f'copy_blocks_{obj.category}')


# ---------------------------------------------------------------------------
# Site Documents
# ---------------------------------------------------------------------------

@admin.register(SiteDocument)
class SiteDocumentAdmin(admin.ModelAdmin):
    list_display    = ('label', 'key', 'file_link', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return "No file uploaded"
    file_link.short_description = "Current File"
