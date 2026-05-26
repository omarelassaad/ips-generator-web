from django import forms
from decimal import Decimal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class QuestionnaireForm(forms.Form):
    advisor_name = forms.CharField(max_length=100, required=True, label='Investment Advisor Name')
    client_identifier = forms.CharField(max_length=100, required=True, label='Client Identifier')

    INVESTMENT_GOALS = [
        ('Retirement', 'Retirement'),
        ('Wealth accumulation', 'Wealth accumulation'),
        ('Legacy planning', 'Legacy planning'),
        ('Philanthropy', 'Philanthropy'),
        ('Major asset purchase', 'Major asset purchase'),
        ('Education', 'Education'),
        ('Health care', 'Health care'),
        ('Travel', 'Travel'),
        ('Other', 'Other'),
    ]
    investment_goals = forms.MultipleChoiceField(choices=INVESTMENT_GOALS, widget=forms.CheckboxSelectMultiple, required=True, label='Primary Investment Goals')

    # Ability to Tolerate Risk
    ANNUAL_INCOME = [
        ('1', 'Less than $50000'),
        ('2', '$50000 - $100000'),
        ('3', '$100000 - $200000'),
        ('4', '$200000 - $500000'),
        ('5', 'More than $500000'),
    ]
    annual_income = forms.ChoiceField(choices=ANNUAL_INCOME, required=True, label='What is your current annual income from all sources?')

    INCOME_SAVINGS = [
        ('1', 'Less than 5%'),
        ('2', '5% - 10%'),
        ('3', '10% - 20%'),
        ('4', '20% - 30%'),
        ('5', 'More than 30%'),
    ]
    income_savings = forms.ChoiceField(choices=INCOME_SAVINGS, required=True, label='What percentage of your income do you currently save or invest?')

    SPENDING_NEEDS = [
        ('1', 'More than 90% of your income'),
        ('2', '75% - 90% of your income'),
        ('3', '50% - 75% of your income'),
        ('4', '25% - 50% of your income'),
        ('5', 'Less than 25% of your income'),
    ]
    spending_needs = forms.ChoiceField(choices=SPENDING_NEEDS, required=True, label='What are your monthly spending needs (including fixed and variable expenses)?')

    EMERGENCY_FUND = [
        ('1', 'Less than 1 month'),
        ('2', '1-3 months'),
        ('3', '3-6 months'),
        ('4', '6-12 months'),
        ('5', 'More than 12 months'),
    ]
    emergency_fund = forms.ChoiceField(choices=EMERGENCY_FUND, required=True, label='How many months of living expenses do you have saved in an emergency fund?')

    # Willingness to Tolerate Risk
    RISK_TOLERANCE = [
        ('1', 'Conservative: Prefer minimal risk willing to accept lower returns to avoid potential losses.'),
        ('2', 'Moderate: Willing to take some risk for potential moderate returns. Comfortable with occasional fluctuations.'),
        ('3', 'Aggressive: Comfortable with high risk and significant fluctuations for the chance of higher returns.'),
    ]
    risk_tolerance = forms.ChoiceField(choices=RISK_TOLERANCE, required=True, label='How would you describe your risk tolerance for your overall investment portfolio?')

    INVESTMENT_LOSS = [
        ('1', '5% loss'),
        ('2', '10% loss'),
        ('3', '15% loss'),
        ('4', '20% loss'),
        ('5', 'More than 20% loss'),
    ]
    investment_loss = forms.ChoiceField(choices=INVESTMENT_LOSS, required=True, label='What level of investment loss in a year would make you uncomfortable?')

    RECOVERY_PERIOD = [
        ('1', 'Less than 1 year'),
        ('2', '1-2 years'),
        ('3', '3-5 years'),
        ('4', 'More than 5 years'),
    ]
    recovery_period = forms.ChoiceField(choices=RECOVERY_PERIOD, required=True, label='How long are you willing to wait for your investments to recover after a market downturn?')

    REACTION_TO_DROP = [
        ('1', 'Sell: Prefer to cut losses and avoid further declines.'),
        ('3', 'Hold: Prefer to wait and expect recovery over time.'),
        ('5', 'Buy More: See it as an opportunity to invest more at lower prices.'),
    ]
    reaction_to_drop = forms.ChoiceField(choices=REACTION_TO_DROP, required=True, label='How would you react to a significant drop in your portfolio value?')

    HIGH_RISK_OPPORTUNITIES = [
        ('1', 'Very uncomfortable: Avoid high-risk investments and prefer stable low-risk options.'),
        ('2', 'Somewhat uncomfortable: Accept slight risk but mainly prefer safer investments.'),
        ('3', 'Neutral: Open to a balanced mix of risk and reward opportunities.'),
        ('4', 'Somewhat comfortable: Willing to take on higher risk for the chance of higher returns including speculative investments.'),
        ('5', 'Very comfortable: Seek high-risk investments with the potential for substantial rewards such as speculative stocks or startups.'),
    ]
    high_risk_opportunities = forms.ChoiceField(choices=HIGH_RISK_OPPORTUNITIES, required=True, label='How comfortable are you with investing in high-risk/high-reward opportunities such as speculative stocks or startups?')

    VOLATILITY = [
        ('1', 'Very uncomfortable: Prefer stable and consistent returns avoiding significant fluctuations.'),
        ('2', 'Uncomfortable: Tolerate minor fluctuations but generally prefer stable returns.'),
        ('3', 'Neutral: Accept volatility as a part of investing and can handle moderate fluctuations.'),
        ('4', 'Comfortable: Willing to endure significant fluctuations for the possibility of higher returns.'),
        ('5', 'Very comfortable: Expect and accept high volatility in pursuit of the highest possible returns.'),
    ]
    volatility = forms.ChoiceField(choices=VOLATILITY, required=True, label='How do you feel about the volatility in your investment returns considering scenarios like market downturns or sudden gains?')

    # Investment Knowledge
    INVESTMENT_KNOWLEDGE = [
        ('1', 'None: You have no experience with investments and rely entirely on professional advice.'),
        ('2', 'Basic: You have a basic understanding of stocks, bonds, and mutual funds but limited experience in making investment decisions.'),
        ('3', 'Intermediate: You have a good understanding of various investment products (stocks, bonds, mutual funds, ETFs) and have made several investment decisions on your own.'),
        ('4', 'Advanced: You have extensive knowledge of investments including complex instruments (options, futures, derivatives) and frequently make your own investment decisions.'),
    ]
    investment_knowledge = forms.ChoiceField(choices=INVESTMENT_KNOWLEDGE, required=True, label='How would you rate your knowledge of investments?')

    # Time Horizon
    TIME_HORIZON = [
        ('1', 'Less than 1 year'),
        ('2', '1-3 years'),
        ('3', '3-5 years'),
        ('4', '5-10 years'),
        ('5', 'More than 10 years'),
    ]
    time_horizon = forms.ChoiceField(choices=TIME_HORIZON, required=True, label='For your primary investment goal, indicate the approximate time frame:')

    # Liquidity Needs
    LIQUIDITY_NEEDS = [
        ('1', 'Very important: Need to access cash quickly for emergencies or opportunities.'),
        ('2', 'Somewhat important: Need some access to cash but can afford to wait for a short period.'),
        ('3', 'Not important: Comfortable with long-term investments without needing quick access to cash.'),
    ]
    liquidity_needs = forms.ChoiceField(choices=LIQUIDITY_NEEDS, required=True, label='Importance of having access to cash for your investments:')

    annual_withdrawal = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        required=False,
        label='Annual Withdrawal Amount'
    )

    def clean_annual_withdrawal(self):
        data = self.cleaned_data.get('annual_withdrawal')
        if data:
            data = str(data).replace('$', '').replace(',', '')
            try:
                data = Decimal(data)
            except ValueError:
                raise forms.ValidationError("Please enter a valid dollar amount.")
        return data
    
    RESPONSIBLE_INVESTING = [
        ('RI', 'An all responsible investing portfolio, if possible'),
        ('Neutral', 'Neutral, no bias')
    ]
    responsible_investing = forms.ChoiceField(choices=RESPONSIBLE_INVESTING, required=True, label='Responsible Investing Preference')

    ASSET_MIX = {
        'Income': {
            'Cash': '2%',
            'Fixed Income': '68%',
            'Canadian Equity': '10%',
            'U.S. Equity': '5%',
            'International Equity': '5%',
            'Alternatives': '10%',
            'Total': '100%',
        },
        'Income & Growth': {
            'Cash': '2%',
            'Fixed Income': '58%',
            'Canadian Equity': '12%',
            'U.S. Equity': '10%',
            'International Equity': '8%',
            'Alternatives': '10%',
            'Total': '100%',
        },
        'Balanced': {
            'Cash': '2%',
            'Fixed Income': '43%',
            'Canadian Equity': '20%',
            'U.S. Equity': '14%',
            'International Equity': '11%',
            'Alternatives': '10%',
            'Total': '100%',
        },
        'Growth & Income': {
            'Cash': '2%',
            'Fixed Income': '28%',
            'Canadian Equity': '25%',
            'U.S. Equity': '20%',
            'International Equity': '15%',
            'Alternatives': '10%',
            'Total': '100%',
        },
        'Growth': {
            'Cash': '2%',
            'Fixed Income': '18%',
            'Canadian Equity': '27%',
            'U.S. Equity': '23%',
            'International Equity': '20%',
            'Alternatives': '10%',
            'Total': '100%',
        },
        'Maximum Growth': {
            'Cash': '2%',
            'Fixed Income': '0%',
            'Canadian Equity': '31%',
            'U.S. Equity': '31%',
            'International Equity': '26%',
            'Alternatives': '10%',
            'Total': '100%',
        },
    }

    def calculate_ability_to_tolerate_risk_score(self):
        score_fields = [
            'annual_income', 'income_savings', 'spending_needs', 'emergency_fund',
            'time_horizon', 'liquidity_needs'
        ]
        return sum(int(self.cleaned_data[field]) for field in score_fields)



    def calculate_willingness_to_tolerate_risk_score(self):
        score_fields = [
            'risk_tolerance', 'investment_loss', 'recovery_period',
            'reaction_to_drop', 'high_risk_opportunities', 'volatility'
        ]
        return sum(int(self.cleaned_data[field]) for field in score_fields)


    def calculate_total_score(self):
        ability_to_tolerate_risk_score = self.calculate_ability_to_tolerate_risk_score()
        willingness_to_tolerate_risk_score = self.calculate_willingness_to_tolerate_risk_score()
        knowledge_score = int(self.cleaned_data['investment_knowledge'])
        return (ability_to_tolerate_risk_score + willingness_to_tolerate_risk_score + 
                knowledge_score)


    def get_portfolio_recommendation(self):
        total_score = self.calculate_total_score()
        time_horizon_score = int(self.cleaned_data['time_horizon'])
    
        # Define the recommendation table
        recommendations = [
            ['Income', 'Income', 'Income', 'Income', 'Income'],
            ['Income', 'Income & Growth', 'Income & Growth', 'Income & Growth', 'Income & Growth'],
            ['Income & Growth', 'Balanced', 'Balanced', 'Balanced', 'Balanced'],
            ['Balanced', 'Growth & Income', 'Growth & Income', 'Growth & Income', 'Growth & Income'],
            ['Growth & Income', 'Growth', 'Growth', 'Growth', 'Growth'],
            ['Growth', 'Maximum Growth', 'Maximum Growth', 'Maximum Growth', 'Maximum Growth'],
        ]
    
        risk_ranges = [10.67, 21.33, 32, 42.67, 53.33, 64]
        time_horizon_ranges = [1, 2, 3, 4, 5]
    
        # Determine the row index for the total score
        risk_index = next((i for i, v in enumerate(risk_ranges) if total_score <= v), len(risk_ranges) - 1)
        # Determine the column index for the time horizon score
        time_horizon_index = next((i for i, v in enumerate(time_horizon_ranges) if time_horizon_score <= v), len(time_horizon_ranges) - 1)
    
        recommendation = recommendations[risk_index][time_horizon_index]
    
        # Append (RI) if Responsible Investing is selected
        if self.cleaned_data['responsible_investing'] == 'RI':
            recommendation += " (RI)"
    
        return recommendation

    
        # Determine the row index for the total score
        risk_index = next((i for i, v in enumerate(risk_ranges) if total_score <= v), len(risk_ranges) - 1)
        # Determine the column index for the time horizon score
        time_horizon_index = next((i for i, v in enumerate(time_horizon_ranges) if time_horizon_score <= v), len(time_horizon_ranges) - 1)
    
        recommendation = recommendations[risk_index][time_horizon_index]
    
        # Append (RI) if Responsible Investing is selected
        if self.cleaned_data['responsible_investing'] == 'RI':
            recommendation += " (RI)"
    
        return recommendation



    def get_asset_mix(self, portfolio_recommendation, asset_mix_db=None, liq_asset_mix_db=None):
        """Return the asset allocation dict for a given portfolio recommendation.

        When asset_mix_db / liq_asset_mix_db are provided (built from
        PortfolioProfile DB records) those take precedence over the hardcoded
        fallbacks below.  Views should pass these in so that the admin-managed
        PortfolioProfile table is the single source of truth.
        """
        liquidity_needs = int(self.cleaned_data.get('liquidity_needs'))
        key = portfolio_recommendation.replace(" (RI)", "")

        if liquidity_needs == 3:  # Not important: use the liquidity profile (liq_* fields) from the DB
            if liq_asset_mix_db:
                return liq_asset_mix_db.get(key, {})
            # Hardcoded fallback (used only when DB has no PortfolioProfile records)
            return self.ASSET_MIX.get(key, {})
        else:  # Important or somewhat important: use the standard (liquidity-adjusted) fields from DB
            if asset_mix_db:
                return asset_mix_db.get(key, {})
            # Hardcoded fallback (used only when DB has no PortfolioProfile records)
            return {
                'Income': {'Cash': '2%', 'Fixed Income': '78%', 'Canadian Equity': '10%', 'U.S. Equity': '5%', 'International Equity': '5%', 'Alternatives': '0%', 'Total': '100%'},
                'Income & Growth': {'Cash': '2%', 'Fixed Income': '63%', 'Canadian Equity': '16%', 'U.S. Equity': '11%', 'International Equity': '8%', 'Alternatives': '0%', 'Total': '100%'},
                'Balanced': {'Cash': '2%', 'Fixed Income': '48%', 'Canadian Equity': '23%', 'U.S. Equity': '15%', 'International Equity': '13%', 'Alternatives': '0%', 'Total': '100%'},
                'Growth & Income': {'Cash': '2%', 'Fixed Income': '33%', 'Canadian Equity': '27%', 'U.S. Equity': '20%', 'International Equity': '18%', 'Alternatives': '0%', 'Total': '100%'},
                'Growth': {'Cash': '2%', 'Fixed Income': '18%', 'Canadian Equity': '32%', 'U.S. Equity': '26%', 'International Equity': '22%', 'Alternatives': '0%', 'Total': '100%'},
                'Maximum Growth': {'Cash': '2%', 'Fixed Income': '0%', 'Canadian Equity': '35%', 'U.S. Equity': '35%', 'International Equity': '28%', 'Alternatives': '0%', 'Total': '100%'}
            }.get(key, {})
        
    def get_risk_profile(self):
        total_score = self.calculate_total_score()
        if total_score <= 10.67:
            return 'Low Risk'
        elif total_score <= 21.33:
            return 'Low Medium Risk'
        elif total_score <= 32:
            return 'Medium Risk'
        elif total_score <= 42.67:
            return 'Medium High Risk'
        elif total_score <= 53.33:
            return 'High Risk'
        else:
            return 'Very High Risk'


       
class ChooseMyselfForm(forms.Form):
    account_owner = forms.CharField(max_length=100)
    account_type = forms.ChoiceField(choices=[
        ('Cash', 'Cash'),
        ('Corporate', 'Corporate'),
        ('RRSP', 'RRSP'),
        ('RRIF', 'RRIF'),
        ('LIF', 'LIF'),
        ('TFSA', 'TFSA'),
        ('SRSP', 'SRSP'),
        ('SRIF', 'SRIF'),
        ('LIRA', 'LIRA'),
        ('IPP', 'IPP'),
        ('Non-profit', 'Non-profit'),
        ('PRIF', 'PRIF'),
        ('RESP', 'RESP'),
        ('FHSA', 'FHSA'),
        ('LRIF', 'LRIF'),
    ])
    amount = forms.DecimalField(decimal_places=2, max_digits=10)
    strategy = forms.ChoiceField(choices=[
        ('Aviso 5-year Bond Ladder (Income)', 'Aviso 5-year Bond Ladder (Income)'),
        ('Aviso 5-year Bond Ladder (Taxable)', 'Aviso 5-year Bond Ladder (Taxable)'),
        ('Beutel Goodman Conservative Balanced', 'Beutel Goodman Conservative Balanced'),
        ('Beutel Goodman Structured Bond', 'Beutel Goodman Structured Bond'),
        ('Brookfield Private Real Assets Fund', 'Brookfield Private Real Assets Fund'),
        ('Dixon Mitchell Total Equity', 'Dixon Mitchell Total Equity'),
        ('NEI Global Total Return Bond Fund', 'NEI Global Total Return Bond Fund'),
        ('GMO US Equity', 'GMO US Equity'),
        ('Guardian Balanced Fund', 'Guardian Balanced Fund'),
        ('Guardian Canadian Balanced (RI)', 'Guardian Canadian Balanced (RI)'),
        ('Guardian Canadian Bond (RI)', 'Guardian Canadian Bond (RI)'),
        ('Guardian Canadian Bond Fund', 'Guardian Canadian Bond Fund'),
        ('Guardian Canadian Equity (RI)', 'Guardian Canadian Equity (RI)'),
        ('Guardian Canadian Equity Fund', 'Guardian Canadian Equity Fund'),
        ('Guardian Canadian Equity Income', 'Guardian Canadian Equity Income'),
        ('Guardian Global Dividend', 'Guardian Global Dividend'),
        ('Guardian Global Dividend Fund', 'Guardian Global Dividend Fund'),
        ('Guardian Global Equity (RI)', 'Guardian Global Equity (RI)'),
        ('Jarislowsky Fraser North American Balanced', 'Jarislowsky Fraser North American Balanced'),
        ('Jarislowsky Fraser North American Equity', 'Jarislowsky Fraser North American Equity'),
        ('Lazard Global Equity', 'Lazard Global Equity'),
        ('Lazard International Equity', 'Lazard International Equity'),
        ('Mawer EAFE Large Cap Fund', 'Mawer EAFE Large Cap Fund'),
        ('Manning & Napier US Equity (RI)', 'Manning & Napier US Equity (RI)'),
        ('QV Dividend Income (RI)', 'QV Dividend Income (RI)'),
        ('QV Small Cap (RI)', 'QV Small Cap (RI)'),
        ('Scheer Rowlett Canadian Equity', 'Scheer Rowlett Canadian Equity'),
        ('Sagard Private Credit Fund', 'Sagard Private Credit Fund'),
        ('Sionna Canadian Equity', 'Sionna Canadian Equity'),
    ])

class ClientManagedHoldingsForm(forms.Form):
    cmh_account_owner = forms.CharField(max_length=100, label='Account Owner')
    cmh_account_type = forms.ChoiceField(choices=[
        ('Cash', 'Cash'),
        ('Corporate', 'Corporate'),
        ('RRSP', 'RRSP'),
        ('RRIF', 'RRIF'),
        ('LIF', 'LIF'),
        ('TFSA', 'TFSA'),
        ('SRSP', 'SRSP'),
        ('SRIF', 'SRIF'),
        ('LIRA', 'LIRA'),
        ('IPP', 'IPP'),
        ('Non-profit', 'Non-profit'),
        ('PRIF', 'PRIF'),
        ('RESP', 'RESP'),
        ('FHSA', 'FHSA'),
        ('LRIF', 'LRIF'),
    ], label='Account Type')
    cmh_amount = forms.DecimalField(decimal_places=2, max_digits=10, label='Amount')

class CMSFeeForm(forms.Form):
    cms_fee = forms.DecimalField(decimal_places=2, max_digits=5, label='CMS Fee')

class LetPmChooseForm(forms.Form):
    desired_trailer_rate = forms.DecimalField(decimal_places=2, max_digits=5)
