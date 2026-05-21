from django.core.management.base import BaseCommand
from ips.models import FeeCategory, FeeTier, Mandate, PortfolioProfile, IPSCopyBlock


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


COPY_BLOCKS = [
    # ── Risk Profiles ────────────────────────────────────────────────────────
    {
        "category": "risk_profile", "key": "Low Risk", "order": 1,
        "title": "Low Risk",
        "body": (
            "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Low Risk. "
            "Investors with this profile generally prioritize capital preservation and prefer to minimize the possibility of losses. They tend to seek stability and security, even if it means accepting lower returns. "
            "This risk profile is ideal for those who are more risk-averse or have a shorter investment horizon. Therefore, an 'Income' asset mix is considered suitable for clients with this risk profile."
        ),
    },
    {
        "category": "risk_profile", "key": "Low Medium Risk", "order": 2,
        "title": "Low Medium Risk",
        "body": (
            "After reviewing your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Low Medium Risk. "
            "This profile suits investors who are comfortable with a moderate level of risk in exchange for the potential of modest returns. They seek a balance between preserving capital and achieving some growth. "
            "These investors are prepared for minor fluctuations in their portfolio value. As such, an 'Income & Growth' asset mix is considered appropriate for clients with this risk profile."
        ),
    },
    {
        "category": "risk_profile", "key": "Medium Risk", "order": 3,
        "title": "Medium Risk",
        "body": (
            "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Medium Risk. "
            "Investors with this profile are open to accepting some risk to achieve better returns. They understand that their portfolio may experience occasional fluctuations in value but are comfortable with this in pursuit of higher gains. "
            "This risk profile is suitable for investors with a moderate investment horizon. Therefore, a 'Balanced' asset mix is considered appropriate for clients with this risk profile."
        ),
    },
    {
        "category": "risk_profile", "key": "Medium High Risk", "order": 4,
        "title": "Medium High Risk",
        "body": (
            "After carefully considering your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Medium High Risk. "
            "Investors with this profile are willing to accept some fluctuations in their portfolio value in exchange for the potential of higher returns. While they aim for capital appreciation, they also value some income from their investments. "
            "This risk profile is suitable for those with a longer investment horizon. Consequently, a 'Growth & Income' asset mix is considered appropriate for clients with this risk profile."
        ),
    },
    {
        "category": "risk_profile", "key": "High Risk", "order": 5,
        "title": "High Risk",
        "body": (
            "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is High Risk. "
            "Investors with this profile are comfortable with more significant fluctuations in their portfolio value in pursuit of high returns. They are prepared to accept considerable risk in exchange for the potential of substantial gains. "
            "This risk profile is appropriate for those with a long-term investment horizon and a strong appetite for risk. Therefore, a 'Growth' asset mix is considered suitable for clients with this risk profile."
        ),
    },
    {
        "category": "risk_profile", "key": "Very High Risk", "order": 6,
        "title": "Very High Risk",
        "body": (
            "After reviewing your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is Very High Risk. "
            "Investors with this profile are willing to accept significant volatility and fluctuations in their portfolio value for the potential of maximum returns. They focus on high-growth opportunities and are comfortable with a high level of risk. "
            "This risk profile is most appropriate for those with a long-term investment horizon and a strong focus on growth. As such, a 'Maximum Growth' asset mix is considered appropriate for clients with this risk profile."
        ),
    },

    # ── Investment Goals ──────────────────────────────────────────────────────
    {
        "category": "investment_goal", "key": "Education", "order": 1,
        "title": "Education",
        "body": "Investing for education encompasses funding private schooling, higher education, and advanced degrees for children and grandchildren. It may also involve endowing educational institutions or creating scholarship funds.",
    },
    {
        "category": "investment_goal", "key": "Health care", "order": 2,
        "title": "Health care",
        "body": "Planning for healthcare needs includes ensuring access to high-quality medical care, funding long-term care insurance, and creating healthcare trusts. This ensures that you can maintain your health and well-being without financial constraints.",
    },
    {
        "category": "investment_goal", "key": "Legacy planning", "order": 3,
        "title": "Legacy planning",
        "body": "Legacy planning involves creating trusts, establishing family offices, and planning for wealth transfer to future generations. This goal ensures that your wealth supports not just immediate family but also future generations and philanthropic causes.",
    },
    {
        "category": "investment_goal", "key": "Major asset purchase", "order": 4,
        "title": "Major asset purchase",
        "body": "Planning for major asset purchases includes setting aside funds for significant acquisitions such as primary residences, vacation homes, luxury vehicles, or valuable collectibles. This goal involves strategic financial planning to ensure these purchases are aligned with your overall wealth strategy and do not impact long-term financial goals.",
    },
    {
        "category": "investment_goal", "key": "Other", "order": 5,
        "title": "Other",
        "body": "Custom financial goals unique to your personal situation. This might include investments in private businesses, art collections, or supporting entrepreneurial activities within the family, all aligned with your overall wealth management strategy.",
    },
    {
        "category": "investment_goal", "key": "Philanthropy", "order": 6,
        "title": "Philanthropy",
        "body": "Charitable giving involves creating philanthropic foundations, making endowments, and engaging in impactful giving. This goal includes tax-efficient giving and ensuring long-term sustainability of charitable efforts.",
    },
    {
        "category": "investment_goal", "key": "Retirement", "order": 7,
        "title": "Retirement",
        "body": "Ensuring a comfortable and financially secure retirement involves creating a portfolio that supports your desired lifestyle. This includes planning for living expenses, luxury travel, healthcare, and legacy planning.",
    },
    {
        "category": "investment_goal", "key": "Travel", "order": 8,
        "title": "Travel",
        "body": "Planning for travel involves setting aside funds for luxury travel, owning vacation properties, and participating in exclusive experiences. This ensures financial flexibility for both planned and spontaneous trips.",
    },
    {
        "category": "investment_goal", "key": "Wealth accumulation", "order": 9,
        "title": "Wealth accumulation",
        "body": "Growing your assets involves strategic investments in various asset classes, including stocks, bonds, real estate, and alternative investments. The goal is to maximize returns while managing risk and preserving wealth.",
    },

    # ── Time Horizon ──────────────────────────────────────────────────────────
    {
        "category": "time_horizon", "key": "1", "order": 1,
        "title": "Less than 1 year",
        "body": "Your investment portfolio is designed for a very short-term time horizon of less than one year. This means that the focus will be on preserving capital and maintaining liquidity. The strategy will prioritize investments that are stable and easily convertible to cash to meet your immediate financial needs.",
    },
    {
        "category": "time_horizon", "key": "2", "order": 2,
        "title": "1-3 years",
        "body": "Your investment portfolio is designed with a short-to-medium term time horizon of 1 to 3 years. The strategy will balance between stability and modest growth, emphasizing relatively safe investments that offer some potential for appreciation while minimizing risk. The approach aims to achieve a balance of stability and growth to meet your investment goals within the specified time frame.",
    },
    {
        "category": "time_horizon", "key": "3", "order": 3,
        "title": "3-5 years",
        "body": "Your investment portfolio is structured with a medium-term time horizon of 3 to 5 years. This allows for a more balanced approach to risk and return, with the objective of achieving moderate growth while preserving capital. The strategy aims to strike a balance between stability and growth, aligning with your financial goals over this period.",
    },
    {
        "category": "time_horizon", "key": "4", "order": 4,
        "title": "5-10 years",
        "body": "Your investment portfolio is tailored for a long-term time horizon of 5 to 10 years. With a focus on growth and capital appreciation, the investment strategy will be more aggressive. The approach will aim to optimize growth potential and manage risk, achieving significant appreciation over the extended period.",
    },
    {
        "category": "time_horizon", "key": "5", "order": 5,
        "title": "More than 10 years",
        "body": "Your investment portfolio is planned with a long-term time horizon of more than 10 years. This extended duration allows for a more aggressive growth strategy, focusing on maximizing capital appreciation over the long run. The approach will take advantage of the compounding growth potential over the long term, aligning with your long-term financial objectives and risk tolerance.",
    },

    # ── Liquidity Needs ───────────────────────────────────────────────────────
    {
        "category": "liquidity_needs", "key": "1", "order": 1,
        "title": "Very Important",
        "body": "You have indicated that having access to cash quickly is very important for your investment strategy. This suggests that you may need to respond rapidly to emergencies or opportunities. Therefore, your investment portfolio will prioritize liquidity to ensure that funds are readily available when needed, without significant delays or penalties. This approach will help you maintain the flexibility required to meet your short-term financial needs and unexpected expenses.",
    },
    {
        "category": "liquidity_needs", "key": "2", "order": 2,
        "title": "Somewhat Important",
        "body": "You have indicated that having some access to cash is somewhat important, but you can afford to wait for a short period. This implies a balance between liquidity and potential returns. Your investment portfolio will be structured to provide moderate liquidity, allowing for access to funds within a reasonable timeframe while still aiming for growth. This approach will help you meet occasional cash needs without sacrificing long-term investment goals.",
    },
    {
        "category": "liquidity_needs", "key": "3", "order": 3,
        "title": "Not Important",
        "body": "You have indicated that having access to cash quickly is not important for your investment strategy. This suggests that you are comfortable with long-term investments and do not anticipate needing quick access to cash. Therefore, your investment portfolio can focus on growth and capital appreciation, with less emphasis on liquidity. This approach allows for potentially higher returns over the long term, aligning with your comfort level and investment horizon.",
    },

    # ── Responsible Investing ─────────────────────────────────────────────────
    {
        "category": "responsible_investing", "key": "Neutral", "order": 1,
        "title": "Neutral",
        "body": "You have indicated a neutral stance with no specific bias towards responsible investing. This means that your investment strategy will focus on optimizing returns without particular consideration for environmental, social, and governance (ESG) criteria. The portfolio will be designed to achieve your financial objectives based on traditional investment principles, ensuring that performance and risk management are prioritized according to your overall investment goals.",
    },
    {
        "category": "responsible_investing", "key": "RI", "order": 2,
        "title": "Emphasis on Responsible Investing",
        "body": "You have indicated a preference for an all responsible investing portfolio, if possible. This means that your investment strategy will prioritize selecting investments that meet certain environmental, social, and governance (ESG) criteria. The portfolio will aim to align with your values by investing in companies and funds that are committed to sustainable and ethical practices. This approach reflects your commitment to making a positive impact through your investment choices while pursuing your financial goals.",
    },

    # ── Risk Override – Downward ──────────────────────────────────────────────
    {
        "category": "risk_override_downward", "key": "default", "order": 1,
        "title": "Risk Profile Override – Downward Adjustment",
        "body": (
            "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is {questionnaire_result}. "
            "However, following a review of your personal preferences and investment objectives, you have expressed a preference for a more conservative approach than your questionnaire result indicates. "
            "As a result, your portfolio will be constructed in accordance with a {override_result} profile. "
            "Investors with this profile prioritize the preservation of capital and are willing to accept lower potential returns in exchange for greater stability. "
            "They are generally more comfortable with modest, stable returns and less comfortable with significant fluctuations in portfolio value.\n\n"
            "This downward adjustment has been made at your request and with your full understanding that your assessed risk capacity and tolerance support a {questionnaire_result} profile. "
            "A '{override_portfolio}' asset mix is therefore considered appropriate and will be applied to your portfolio accordingly.\n\n"
            "<strong>Client Acknowledgment:</strong> By signing this IPS, you confirm that you have requested this adjustment, understand the implications of a more conservative investment approach, and agree to the investment strategy outlined above."
        ),
    },

    # ── Risk Override – Upward ────────────────────────────────────────────────
    {
        "category": "risk_override_upward", "key": "default", "order": 1,
        "title": "Risk Profile Override – Upward Adjustment",
        "body": (
            "Based on your responses to the risk questionnaire, which helps us understand your ability to withstand losses (risk capacity) and your willingness to take on risk (risk tolerance), we have determined that your risk profile is {questionnaire_result}. "
            "However, following a review of your personal preferences and investment objectives, you have expressed a preference for a more growth-oriented approach than your questionnaire result indicates. "
            "After discussion with your advisor, and taking into consideration factors beyond the scope of the questionnaire — including your broader financial situation, investment experience, and long-term objectives — your portfolio will be constructed in accordance with a {override_result} profile. "
            "Investors with this profile seek strong long-term capital growth and are comfortable accepting significant fluctuations in portfolio value in pursuit of higher returns.\n\n"
            "This upward adjustment has been made at your request and with your full understanding that your portfolio may experience greater volatility than what your assessed risk profile would typically suggest. "
            "A '{override_portfolio}' asset mix is therefore considered appropriate and will be applied to your portfolio accordingly.\n\n"
            "<strong>Client Acknowledgment:</strong> By signing this IPS, you confirm that you have requested this adjustment, that your advisor has discussed the associated risks with you, that you understand your portfolio may experience a higher degree of volatility than your assessed risk profile would indicate, and that you agree to the investment approach outlined above."
        ),
    },
]


class Command(BaseCommand):
    help = 'Seed fee categories, fee tiers, mandates, portfolio profiles, and IPS copy blocks'

    def handle(self, *args, **kwargs):
        self.seed_fee_categories()
        self.seed_mandates()
        self.seed_portfolio_profiles()
        self.seed_copy_blocks()
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

    def seed_copy_blocks(self):
        for b in COPY_BLOCKS:
            IPSCopyBlock.objects.update_or_create(
                category=b['category'],
                key=b['key'],
                defaults={
                    'title': b['title'],
                    'body':  b['body'],
                    'order': b['order'],
                }
            )
        self.stdout.write('  IPS copy blocks: done')
