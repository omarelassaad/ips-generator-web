from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ---------------------------------------------------------------------------
# Fee Schedule
# ---------------------------------------------------------------------------

class FeeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Fee Category"
        verbose_name_plural = "Fee Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class FeeTier(models.Model):
    category    = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name='tiers')
    lower       = models.BigIntegerField(help_text="Lower AUM bound (inclusive, $)")
    upper       = models.BigIntegerField(help_text="Upper AUM bound (inclusive, $). Use 999999999 for no limit.")
    max_fee     = models.DecimalField(max_digits=5, decimal_places=2, help_text="Max total fee %")
    max_trailer = models.DecimalField(max_digits=5, decimal_places=2, help_text="Max trailer fee %")
    min_fee     = models.DecimalField(max_digits=5, decimal_places=2, help_text="Min total fee %")
    min_trailer = models.DecimalField(max_digits=5, decimal_places=2, help_text="Min trailer fee %")
    admin_fee   = models.DecimalField(max_digits=5, decimal_places=2, help_text="Admin/platform fee %")
    order       = models.PositiveSmallIntegerField(default=0, help_text="Display order within category")

    class Meta:
        verbose_name = "Fee Tier"
        verbose_name_plural = "Fee Tiers"
        ordering = ['category', 'order', 'lower']

    def __str__(self):
        return f"{self.category.name}: ${self.lower:,} – ${self.upper:,}"

    def to_dict(self):
        return {
            "lower":      self.lower,
            "upper":      self.upper,
            "maxFee":     float(self.max_fee),
            "maxTrailer": float(self.max_trailer),
            "minFee":     float(self.min_fee),
            "minTrailer": float(self.min_trailer),
            "adminFee":   float(self.admin_fee),
        }


# ---------------------------------------------------------------------------
# Mandates (investment strategies)
# ---------------------------------------------------------------------------

class Mandate(models.Model):
    name                 = models.CharField(max_length=200, unique=True)
    fee_category         = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, related_name='mandates')
    # Asset allocations
    cash                 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fixed_income         = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    canadian_equity      = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    us_equity            = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    international_equity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    alternatives         = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Supporting documents
    fact_sheet           = models.FileField(upload_to='fact_sheets/', blank=True, null=True,
                                            help_text="PDF fact sheet for this mandate")
    disclaimer           = models.TextField(blank=True, default='',
                                            help_text="Strategy-specific disclaimer (HTML allowed). Leave blank if none.")
    # Minimum investment
    minimum_investment   = models.PositiveIntegerField(default=0,
                                                       help_text="Minimum investment amount ($) enforced in the IPS form")
    # Status
    is_active            = models.BooleanField(default=True,
                                               help_text="Inactive mandates are hidden from the IPS form")
    display_order        = models.PositiveSmallIntegerField(default=0,
                                                            help_text="Order in dropdown lists (lower = first)")

    class Meta:
        verbose_name = "Mandate"
        verbose_name_plural = "Mandates"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def asset_allocation(self):
        """Return allocation as a dict matching the legacy strategyData format."""
        return {
            "Cash":                 float(self.cash),
            "Fixed Income":         float(self.fixed_income),
            "Canadian Equity":      float(self.canadian_equity),
            "U.S. Equity":          float(self.us_equity),
            "International Equity": float(self.international_equity),
            "Alternatives":         float(self.alternatives),
        }


# ---------------------------------------------------------------------------
# Portfolio profiles (asset mix allocations + descriptions)
# ---------------------------------------------------------------------------

class PortfolioProfile(models.Model):
    name        = models.CharField(max_length=100, unique=True,
                                   help_text="e.g. Income, Balanced, Growth")
    description = models.TextField(help_text="Narrative shown in the IPS document")
    order       = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower = first)")

    # Standard allocations (when liquidity needs are Not Important)
    cash                 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fixed_income         = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    canadian_equity      = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    us_equity            = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    international_equity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    alternatives         = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Liquidity-adjusted allocations (when liquidity needs are Very / Somewhat Important)
    liq_cash                 = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                   verbose_name="Cash (liquidity-adjusted)")
    liq_fixed_income         = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                   verbose_name="Fixed Income (liquidity-adjusted)")
    liq_canadian_equity      = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                   verbose_name="Canadian Equity (liquidity-adjusted)")
    liq_us_equity            = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                   verbose_name="U.S. Equity (liquidity-adjusted)")
    liq_international_equity = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                   verbose_name="Intl Equity (liquidity-adjusted)")
    liq_alternatives         = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                   verbose_name="Alternatives (liquidity-adjusted)")

    class Meta:
        verbose_name = "Portfolio Profile"
        verbose_name_plural = "Portfolio Profiles"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def to_form_dict(self, liquidity_adjusted=False):
        """Return allocation dict in the format expected by views/templates."""
        if liquidity_adjusted:
            return {
                'Cash': f'{self.liq_cash:.0f}%',
                'Fixed Income': f'{self.liq_fixed_income:.0f}%',
                'Canadian Equity': f'{self.liq_canadian_equity:.0f}%',
                'U.S. Equity': f'{self.liq_us_equity:.0f}%',
                'International Equity': f'{self.liq_international_equity:.0f}%',
                'Alternatives': f'{self.liq_alternatives:.0f}%',
                'Total': '100%',
            }
        return {
            'Cash': f'{self.cash:.0f}%',
            'Fixed Income': f'{self.fixed_income:.0f}%',
            'Canadian Equity': f'{self.canadian_equity:.0f}%',
            'U.S. Equity': f'{self.us_equity:.0f}%',
            'International Equity': f'{self.international_equity:.0f}%',
            'Alternatives': f'{self.alternatives:.0f}%',
            'Total': '100%',
        }


# ---------------------------------------------------------------------------
# IPS narrative copy blocks
# ---------------------------------------------------------------------------

class IPSCopyBlock(models.Model):
    CATEGORY_CHOICES = [
        ('risk_profile',              'Risk Profile'),
        ('risk_override_downward',    'Risk Override – Downward'),
        ('risk_override_upward',      'Risk Override – Upward'),
        ('investment_goal',           'Investment Goal'),
        ('time_horizon',              'Time Horizon'),
        ('liquidity_needs',           'Liquidity Needs'),
        ('responsible_investing',     'Responsible Investing'),
        ('risk_analytics_disclaimer', 'Risk Analytics Disclaimer'),
        # Annual Review narratives
        ('ar_risk_profile',          'AR – Risk Profile'),
        ('ar_asset_mix',             'AR – Asset Mix'),
        ('ar_time_horizon',          'AR – Time Horizon'),
        ('ar_liquidity',             'AR – Liquidity'),
        ('ar_responsible_investing', 'AR – Responsible Investing'),
        ('ar_income_needs',          'AR – Income Needs'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    key      = models.CharField(max_length=100,
                                help_text="Lookup key used in code (e.g. 'Low Risk', 'Retirement', '1', 'RI')")
    title    = models.CharField(max_length=200, blank=True, default='',
                                help_text="Short label shown as a heading (leave blank if not needed)")
    body     = models.TextField(help_text="Main paragraph text. HTML tags allowed.")
    order    = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "IPS Copy Block"
        verbose_name_plural = "IPS Copy Blocks"
        unique_together = [['category', 'key']]
        ordering = ['category', 'order', 'key']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.key}"


# ---------------------------------------------------------------------------
# Site-wide documents (cover page, back page)
# ---------------------------------------------------------------------------

class SiteDocument(models.Model):
    KEY_CHOICES = [
        ('ips_first_page', 'IPS Cover Page'),
        ('ips_last_page',  'IPS Back Page'),
        ('ar_first_page',  'Annual Review Cover Page'),
        ('cds_form_3',     'CDS Form 3 (Client-directed Sleeve Request)'),
    ]
    key         = models.CharField(max_length=50, unique=True, choices=KEY_CHOICES)
    label       = models.CharField(max_length=100)
    file        = models.FileField(upload_to='site_documents/', blank=True, null=True,
                                   help_text="Upload a PDF to replace the current file")
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Document"
        verbose_name_plural = "Site Documents"

    def __str__(self):
        return self.label


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    can_override_fee = models.BooleanField(default=False, help_text="Allow this user to override the calculated fee and trailer")
    can_use_master_proposals = models.BooleanField(default=False, help_text="Allow this user to load master/template proposals defined in the admin portal")
    can_import_ifms = models.BooleanField(default=False, help_text="Allow this user to import client data from the IFMS upload into Annual Review")

    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.is_approved else 'Not Approved'}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure a profile is created if it doesn't exist for existing users
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class QuestionnaireResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=255, default="Unknown")  # Provide a default value
    answer = models.CharField(max_length=255, blank=True, null=True)  # Allowing null values
    score = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.question}"

class ChooseMyselfData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=255)
    account_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    strategy = models.TextField()  # Changed from CharField to TextField
    version_number = models.CharField(max_length=50, default='N/A')

    def __str__(self):
        return f"{self.user.username} - {self.account_owner} - {self.account_type}"

class LetPmChooseData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=255)
    account_type = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    additional_info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['timestamp']


class ReturnsUpload(models.Model):
    file = models.FileField(upload_to='returns/', help_text="Excel file (.xlsx) with Sheet1 performance data")
    as_of_date = models.CharField(max_length=50, help_text='e.g. "March 31, 2026"')
    calendar_years = models.CharField(
        max_length=200,
        default='2025,2024,2023,2022,2021,2020,2019',
        help_text='Comma-separated list of calendar years to show in the performance table, most recent first.'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Only one upload should be active at a time. "
                  "Saving a new active upload automatically deactivates the previous one."
    )

    class Meta:
        verbose_name = "Returns Upload"
        verbose_name_plural = "Returns Uploads"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Returns as of {self.as_of_date} (uploaded {self.uploaded_at.strftime('%Y-%m-%d') if self.uploaded_at else '—'})"


class IFMSUpload(models.Model):
    """Monthly IFMS Excel export uploaded by admin. Advisors with permission can
    search it from the Annual Review form to pre-fill the strategy table."""
    file       = models.FileField(upload_to='ifms/', help_text="Excel file (.xlsx) exported from IFMS")
    label      = models.CharField(max_length=100, help_text='Descriptive label, e.g. "IFMS 05-21-2026"')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(
        default=True,
        help_text="Only one upload should be active at a time. "
                  "Saving a new active upload automatically deactivates the previous one."
    )

    class Meta:
        verbose_name = "IFMS Upload"
        verbose_name_plural = "IFMS Uploads"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.label} (uploaded {self.uploaded_at.strftime('%Y-%m-%d') if self.uploaded_at else '—'})"

    def save(self, *args, **kwargs):
        if self.is_active:
            IFMSUpload.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class MasterProposal(models.Model):
    """Admin-defined template proposals that permitted users can load."""
    label = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, default='', help_text="Short description shown to advisors")
    data = models.TextField(help_text="JSON list of account rows (same format as SavedProposal.data)")
    risk_profile_override = models.CharField(max_length=100, blank=True, default='')
    portfolio_override = models.CharField(max_length=100, blank=True, default='')
    is_active = models.BooleanField(default=True, help_text="Inactive proposals are hidden from advisors")
    display_order = models.PositiveSmallIntegerField(default=0, help_text="Lower = displayed first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Master Proposal"
        verbose_name_plural = "Master Proposals"
        ordering = ['display_order', 'label']

    def __str__(self):
        return self.label


class SavedProposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_proposals')
    label = models.CharField(max_length=200)
    data = models.TextField()  # JSON snapshot of all ChooseMyselfData rows
    risk_profile_override = models.CharField(max_length=100, blank=True, default='')
    portfolio_override = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} — {self.label}"
