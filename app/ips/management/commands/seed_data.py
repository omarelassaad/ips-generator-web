from django.core.management.base import BaseCommand
from ips.models import FeeCategory, FeeTier, Mandate, PortfolioProfile


FEE_DATA = {
    "Equity & Balanced": [
        {"lower": 0,       "upper": 250000,    "maxFee": 2.35, "maxTrailer": 1.25, "minFee": 1.85, "minTrailer": 0.75, "adminFee": 1.10, "order": 1},
        {"lower": 250001,  "upper": 500000,    "maxFee": 2.25, "maxTrailer": 1.15, "minFee": 1.75, "minTrailer": 0.65, "adminFee": 1.10, "order": 2},
        {"lower": 500001,  "upper": 1000000,   "maxFee": 2.00, "maxTrailer": 1.20, "minFee": 1.70, "minTrailer": 0.90, "adminFee": 0.80, "order": 3},
        {"lower": 1000001, "upper": 2000000,   "maxFee": 1.95, "maxTrailer": 1.20, "minFee": 1.55, "minTrailer": 0.80, "adminFee": 0.75, "order": 4},
        {"lower": 2000001, "upper": 5000000,   "maxFee": 1.90, "maxTrailer": 1.20, "minFee": 1.25, "minTrailer": 0.55, "adminFee": 0.70, "order": 5},
        {"lower": 5000001, "upper": 999999999, "maxFee": 1.90, "maxTrailer": 1.20, "minFee": 1.25, "minTrailer": 0.55, "adminFee": 0.70, "order": 6},
    ],
    "Structured Bond": [
        {"lower": 0,       "upper": 250000,    "maxFee": 1.00, "maxTrailer": 0.50, "minFee": 0.80, "minTrailer": 0.30, "adminFee": 0.50, "order": 1},
        {"lower": 250001,  "upper": 500000,    "maxFee": 1.00, "maxTrailer": 0.50, "minFee": 0.80, "minTrailer": 0.30, "adminFee": 0.50, "order": 2},
        {"lower": 500001,  "upper": 1000000,   "maxFee": 1.00, "maxTrailer": 0.50, "minFee": 0.80, "minTrailer": 0.30, "adminFee": 0.50, "order": 3},
        {"lower": 1000001, "upper": 2000000,   "maxFee": 0.90, "maxTrailer": 0.50, "minFee": 0.75, "minTrailer": 0.35, "adminFee": 0.40, "order": 4},
        {"lower": 2000001, "upper": 5000000,   "maxFee": 0.90, "maxTrailer": 0.50, "minFee": 0.70, "minTrailer": 0.30, "adminFee": 0.40, "order": 5},
        {"lower": 5000001, "upper": 999999999, "maxFee": 0.90, "maxTrailer": 0.50, "minFee": 0.70, "minTrailer": 0.30, "adminFee": 0.40, "order": 6},
    ],
    "Fixed Income": [
        {"lower": 0,       "upper": 250000,    "maxFee": 1.15, "maxTrailer": 0.50, "minFee": 0.95, "minTrailer": 0.30, "adminFee": 0.65, "order": 1},
        {"lower": 250001,  "upper": 500000,    "maxFee": 1.15, "maxTrailer": 0.50, "minFee": 0.95, "minTrailer": 0.30, "adminFee": 0.65, "order": 2},
        {"lower": 500001,  "upper": 1000000,   "maxFee": 1.15, "maxTrailer": 0.50, "minFee": 0.95, "minTrailer": 0.30, "adminFee": 0.65, "order": 3},
        {"lower": 1000001, "upper": 2000000,   "maxFee": 1.10, "maxTrailer": 0.60, "minFee": 0.90, "minTrailer": 0.40, "adminFee": 0.50, "order": 4},
        {"lower": 2000001, "upper": 5000000,   "maxFee": 1.00, "maxTrailer": 0.50, "minFee": 0.70, "minTrailer": 0.20, "adminFee": 0.50, "order": 5},
        {"lower": 5000001, "upper": 999999999, "maxFee": 1.00, "maxTrailer": 0.50, "minFee": 0.70, "minTrailer": 0.20, "adminFee": 0.50, "order": 6},
    ],
    "Bond Ladder": [
        {"lower": 0,       "upper": 1000000,   "maxFee": 0.90, "maxTrailer": 0.60, "minFee": 0.60, "minTrailer": 0.30, "adminFee": 0.30, "order": 1},
        {"lower": 1000001, "upper": 2000000,   "maxFee": 0.85, "maxTrailer": 0.60, "minFee": 0.55, "minTrailer": 0.30, "adminFee": 0.25, "order": 2},
        {"lower": 2000001, "upper": 999999999, "maxFee": 0.80, "maxTrailer": 0.60, "minFee": 0.50, "minTrailer": 0.30, "adminFee": 0.20, "order": 3},
    ],
    "Conservative Balanced": [
        {"lower": 0,       "upper": 250000,    "maxFee": 1.75, "maxTrailer": 0.95, "minFee": 1.40, "minTrailer": 0.60, "adminFee": 0.80, "order": 1},
        {"lower": 250001,  "upper": 500000,    "maxFee": 1.75, "maxTrailer": 0.95, "minFee": 1.40, "minTrailer": 0.60, "adminFee": 0.80, "order": 2},
        {"lower": 500001,  "upper": 1000000,   "maxFee": 1.75, "maxTrailer": 0.95, "minFee": 1.40, "minTrailer": 0.60, "adminFee": 0.80, "order": 3},
        {"lower": 1000001, "upper": 2000000,   "maxFee": 1.65, "maxTrailer": 0.90, "minFee": 1.35, "minTrailer": 0.60, "adminFee": 0.75, "order": 4},
        {"lower": 2000001, "upper": 5000000,   "maxFee": 1.50, "maxTrailer": 0.80, "minFee": 1.25, "minTrailer": 0.55, "adminFee": 0.70, "order": 5},
        {"lower": 5000001, "upper": 999999999, "maxFee": 1.50, "maxTrailer": 0.80, "minFee": 1.25, "minTrailer": 0.55, "adminFee": 0.70, "order": 6},
    ],
    "Alternative": [
        {"lower": 0,       "upper": 999999,    "maxFee": 1.00, "maxTrailer": 0.50, "minFee": 0.80, "minTrailer": 0.30, "adminFee": 0.50, "order": 1},
        {"lower": 1000000, "upper": 999999999, "maxFee": 0.90, "maxTrailer": 0.45, "minFee": 0.75, "minTrailer": 0.30, "adminFee": 0.45, "order": 2},
    ],
}

# Sorted alphabetically — display_order assigned by position
MANDATES = sorted([
    {"name": "Aviso 5-year Bond Ladder (Income)",          "fee_category": "Bond Ladder",          "cash": 2.00,  "fixed_income": 98.00, "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Aviso 5-year Bond Ladder (Taxable)",         "fee_category": "Bond Ladder",          "cash": 2.00,  "fixed_income": 98.00, "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Beutel Goodman Conservative Balanced",       "fee_category": "Conservative Balanced","cash": 1.50,  "fixed_income": 68.50, "canadian_equity": 22.50, "us_equity": 7.50,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Beutel Goodman Structured Bond",             "fee_category": "Structured Bond",      "cash": 5.00,  "fixed_income": 95.00, "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Brookfield Private Real Assets Fund",        "fee_category": "Alternative",          "cash": 5.00,  "fixed_income": 0.00,  "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 95.00, "minimum_investment": 0},
    {"name": "Dixon Mitchell Total Equity",                "fee_category": "Equity & Balanced",    "cash": 2.00,  "fixed_income": 0.00,  "canadian_equity": 64.00, "us_equity": 34.00, "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Balanced Fund",                     "fee_category": "Equity & Balanced",    "cash": 2.00,  "fixed_income": 38.00, "canadian_equity": 35.00, "us_equity": 20.00, "international_equity": 5.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Canadian Balanced (RI)",            "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 39.00, "canadian_equity": 58.50, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Canadian Bond (RI)",                "fee_category": "Fixed Income",         "cash": 2.50,  "fixed_income": 97.50, "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Canadian Bond Fund",                "fee_category": "Fixed Income",         "cash": 2.00,  "fixed_income": 98.00, "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Canadian Equity (RI)",              "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 97.50, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Canadian Equity Fund",              "fee_category": "Equity & Balanced",    "cash": 2.00,  "fixed_income": 0.00,  "canadian_equity": 98.00, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Canadian Equity Income",            "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 97.50, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Global Dividend",                   "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 3.50,  "us_equity": 62.00, "international_equity": 32.00, "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Global Dividend Fund",              "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 3.50,  "us_equity": 62.00, "international_equity": 32.00, "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Guardian Global Equity (RI)",                "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 3.50,  "us_equity": 62.00, "international_equity": 32.00, "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Hamilton Lane Global Private Assets Fund",   "fee_category": "Alternative",          "cash": 5.00,  "fixed_income": 0.00,  "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 95.00, "minimum_investment": 0},
    {"name": "Jarislowsky Fraser North American Balanced", "fee_category": "Equity & Balanced",    "cash": 10.00, "fixed_income": 45.00, "canadian_equity": 20.00, "us_equity": 25.00, "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Jarislowsky Fraser North American Equity",   "fee_category": "Equity & Balanced",    "cash": 10.00, "fixed_income": 0.00,  "canadian_equity": 45.00, "us_equity": 45.00, "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Lazard Global Equity",                       "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 3.50,  "us_equity": 62.00, "international_equity": 32.00, "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Lazard International Equity",                "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 97.50, "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Manning & Napier US Equity (RI)",            "fee_category": "Equity & Balanced",    "cash": 5.00,  "fixed_income": 0.00,  "canadian_equity": 0.00,  "us_equity": 95.00, "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Mawer EAFE Large Cap Fund",                  "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 97.50, "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "QV Dividend Income (RI)",                    "fee_category": "Equity & Balanced",    "cash": 10.00, "fixed_income": 0.00,  "canadian_equity": 90.00, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "QV Small Cap (RI)",                          "fee_category": "Equity & Balanced",    "cash": 5.00,  "fixed_income": 0.00,  "canadian_equity": 95.00, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Sagard Private Credit Fund",                 "fee_category": "Alternative",          "cash": 5.00,  "fixed_income": 0.00,  "canadian_equity": 0.00,  "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 95.00, "minimum_investment": 0},
    {"name": "Scheer Rowlett Canadian Equity",             "fee_category": "Equity & Balanced",    "cash": 3.00,  "fixed_income": 0.00,  "canadian_equity": 97.00, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
    {"name": "Sionna Canadian Equity",                     "fee_category": "Equity & Balanced",    "cash": 2.50,  "fixed_income": 0.00,  "canadian_equity": 97.50, "us_equity": 0.00,  "international_equity": 0.00,  "alternatives": 0.00,  "minimum_investment": 0},
], key=lambda m: m['name'])

# Portfolio profiles — asset allocations are placeholders until confirmed
PORTFOLIO_PROFILES = [
    {
        "name": "Income", "order": 1,
        "description": "The Income asset mix is designed to generate steady returns through investments primarily in bonds and fixed-income securities, minimal equities.",
        "cash": 5.00,  "fixed_income": 75.00, "canadian_equity": 10.00, "us_equity": 5.00,  "international_equity": 5.00,  "alternatives": 0.00,
        "liq_cash": 10.00, "liq_fixed_income": 70.00, "liq_canadian_equity": 10.00, "liq_us_equity": 5.00, "liq_international_equity": 5.00, "liq_alternatives": 0.00,
    },
    {
        "name": "Income & Growth", "order": 2,
        "description": "The Income & Growth asset mix offers a combination of bonds and some equities, focusing on stable returns while providing the potential for growth. This mix is designed to generate income through fixed-income securities and achieve some capital appreciation through equities, making it suitable for those looking for a balanced approach with low medium risk.",
        "cash": 5.00,  "fixed_income": 55.00, "canadian_equity": 20.00, "us_equity": 10.00, "international_equity": 10.00, "alternatives": 0.00,
        "liq_cash": 10.00, "liq_fixed_income": 50.00, "liq_canadian_equity": 20.00, "liq_us_equity": 10.00, "liq_international_equity": 10.00, "liq_alternatives": 0.00,
    },
    {
        "name": "Balanced", "order": 3,
        "description": "The Balanced asset mix consists of an equal mix of equities and bonds, providing moderate exposure to both asset classes. This combination aims to achieve a balance between income generation and capital growth, offering a moderate risk-return profile. It is ideal for investors seeking a diversified approach to investing.",
        "cash": 5.00,  "fixed_income": 40.00, "canadian_equity": 25.00, "us_equity": 15.00, "international_equity": 15.00, "alternatives": 0.00,
        "liq_cash": 10.00, "liq_fixed_income": 35.00, "liq_canadian_equity": 25.00, "liq_us_equity": 15.00, "liq_international_equity": 15.00, "liq_alternatives": 0.00,
    },
    {
        "name": "Growth & Income", "order": 4,
        "description": "The Growth & Income asset mix emphasizes equities more than bonds, focusing on capital appreciation while maintaining some income generation. This mix is designed to provide higher returns through equity investments, supplemented by the relative stability of fixed-income securities. It is suitable for investors seeking growth with a medium high risk.",
        "cash": 5.00,  "fixed_income": 25.00, "canadian_equity": 30.00, "us_equity": 20.00, "international_equity": 20.00, "alternatives": 0.00,
        "liq_cash": 10.00, "liq_fixed_income": 20.00, "liq_canadian_equity": 30.00, "liq_us_equity": 20.00, "liq_international_equity": 20.00, "liq_alternatives": 0.00,
    },
    {
        "name": "Growth", "order": 5,
        "description": "The Growth asset mix is primarily composed of equities, offering higher volatility with focus on capital appreciation. This mix aims to achieve substantial returns through investments in equities, accepting the added risk associated with market fluctuations. It is ideal for investors seeking higher growth opportunities.",
        "cash": 5.00,  "fixed_income": 10.00, "canadian_equity": 35.00, "us_equity": 25.00, "international_equity": 25.00, "alternatives": 0.00,
        "liq_cash": 10.00, "liq_fixed_income": 5.00,  "liq_canadian_equity": 35.00, "liq_us_equity": 25.00, "liq_international_equity": 25.00, "liq_alternatives": 0.00,
    },
    {
        "name": "Maximum Growth", "order": 6,
        "description": "The Maximum Growth asset mix is almost entirely made up of equities or high-risk assets, providing maximum exposure to market fluctuations. This mix targets the highest possible returns through investments in high-growth equities and other volatile assets. It is suitable for investors looking for the highest growth potential and willing to accept very high risk.",
        "cash": 5.00,  "fixed_income": 0.00,  "canadian_equity": 40.00, "us_equity": 30.00, "international_equity": 25.00, "alternatives": 0.00,
        "liq_cash": 10.00, "liq_fixed_income": 0.00,  "liq_canadian_equity": 40.00, "liq_us_equity": 25.00, "liq_international_equity": 25.00, "liq_alternatives": 0.00,
    },
]


class Command(BaseCommand):
    help = 'Seed fee categories, fee tiers, mandates, and portfolio profiles'

    def handle(self, *args, **kwargs):
        self.seed_fee_categories()
        self.seed_mandates()
        self.seed_portfolio_profiles()
        self.stdout.write(self.style.SUCCESS('Seed data loaded successfully.'))

    def seed_fee_categories(self):
        for category_name, tiers in FEE_DATA.items():
            category, _ = FeeCategory.objects.get_or_create(name=category_name)
            for tier in tiers:
                FeeTier.objects.update_or_create(
                    category=category,
                    lower=tier['lower'],
                    upper=tier['upper'],
                    defaults={
                        'max_fee':     tier['maxFee'],
                        'max_trailer': tier['maxTrailer'],
                        'min_fee':     tier['minFee'],
                        'min_trailer': tier['minTrailer'],
                        'admin_fee':   tier['adminFee'],
                        'order':       tier['order'],
                    }
                )
        self.stdout.write('  Fee categories and tiers: done')

    def seed_mandates(self):
        for i, m in enumerate(MANDATES):
            category = FeeCategory.objects.get(name=m['fee_category'])
            Mandate.objects.update_or_create(
                name=m['name'],
                defaults={
                    'fee_category':         category,
                    'cash':                 m['cash'],
                    'fixed_income':         m['fixed_income'],
                    'canadian_equity':      m['canadian_equity'],
                    'us_equity':            m['us_equity'],
                    'international_equity': m['international_equity'],
                    'alternatives':         m['alternatives'],
                    'minimum_investment':   m['minimum_investment'],
                    'display_order':        (i + 1) * 10,
                    'is_active':            True,
                }
            )
        self.stdout.write('  Mandates: done')

    def seed_portfolio_profiles(self):
        for p in PORTFOLIO_PROFILES:
            PortfolioProfile.objects.update_or_create(
                name=p['name'],
                defaults={
                    'description':         p['description'],
                    'order':               p['order'],
                    'cash':                p['cash'],
                    'fixed_income':        p['fixed_income'],
                    'canadian_equity':     p['canadian_equity'],
                    'us_equity':           p['us_equity'],
                    'international_equity':p['international_equity'],
                    'alternatives':        p['alternatives'],
                    'liq_cash':                p['liq_cash'],
                    'liq_fixed_income':        p['liq_fixed_income'],
                    'liq_canadian_equity':     p['liq_canadian_equity'],
                    'liq_us_equity':           p['liq_us_equity'],
                    'liq_international_equity':p['liq_international_equity'],
                    'liq_alternatives':        p['liq_alternatives'],
                }
            )
        self.stdout.write('  Portfolio profiles: done')
