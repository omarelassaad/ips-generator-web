from django.db import migrations

AR_RISK_PROFILE = [
    ('Low Risk',          0, '', 'Your risk profile, determined based on your responses to the risk questionnaire, is classified as Low Risk. Investors with this profile generally prioritize capital preservation and prefer to minimize the possibility of losses. They tend to seek stability and security, even if it means accepting lower returns. This risk profile is ideal for those who are more risk-averse or have a shorter investment horizon. Therefore, an \'Income\' asset mix is considered suitable for clients with this risk profile.'),
    ('Low Medium Risk',   1, '', 'Your risk profile, determined based on your responses to the risk questionnaire, is classified as Low Medium Risk. This profile suits investors who are comfortable with a moderate level of risk in exchange for the potential of modest returns. They seek a balance between preserving capital and achieving some growth. These investors are prepared for minor fluctuations in their portfolio value. As such, an \'Income & Growth\' asset mix is considered appropriate for clients with this risk profile.'),
    ('Medium Risk',       2, '', 'Your risk profile, determined based on your responses to the risk questionnaire, is classified as Medium Risk. This profile indicates that you are open to accepting some risk in pursuit of better returns. You understand that your portfolio may experience occasional fluctuations in value and are comfortable with this as you seek higher gains. This risk profile is suitable for investors with a moderate investment horizon, making a \'Balanced\' asset mix an appropriate choice for your investment strategy.'),
    ('Medium High Risk',  3, '', 'Your risk profile, determined based on your responses to the risk questionnaire, is classified as Medium High Risk. Investors with this profile are willing to accept some fluctuations in their portfolio value in exchange for the potential of higher returns. While they aim for capital appreciation, they also value some income from their investments. This risk profile is suitable for those with a longer investment horizon. Consequently, a \'Growth & Income\' asset mix is considered appropriate for clients with this risk profile.'),
    ('High Risk',         4, '', 'Your risk profile, determined based on your responses to the risk questionnaire, is classified as High Risk. Investors with this profile are comfortable with more significant fluctuations in their portfolio value in pursuit of high returns. They are prepared to accept considerable risk in exchange for the potential of substantial gains. This risk profile is appropriate for those with a long-term investment horizon and a strong appetite for risk. Therefore, a \'Growth\' asset mix is considered suitable for clients with this risk profile.'),
    ('Very High Risk',    5, '', 'Your risk profile, determined based on your responses to the risk questionnaire, is classified as Very High Risk. Investors with this profile are willing to accept significant volatility and fluctuations in their portfolio value for the potential of maximum returns. They focus on high-growth opportunities and are comfortable with a high level of risk. This risk profile is most appropriate for those with a long-term investment horizon and a strong focus on growth. As such, a \'Maximum Growth\' asset mix is considered appropriate for clients with this risk profile.'),
]

AR_ASSET_MIX = [
    ('Income',          0, '', 'The Income asset mix is designed to generate steady returns through investments primarily in bonds and fixed-income securities, with minimal equities.'),
    ('Income & Growth', 1, '', 'The Income & Growth asset mix offers a combination of bonds and some equities, focusing on stable returns while providing the potential for modest growth. This mix aims to generate income through fixed-income securities and achieve some capital appreciation through equities.'),
    ('Balanced',        2, '', 'The Balanced asset mix consists of an equal mix of equities and bonds, providing moderate exposure to both asset classes. This combination aims to achieve a balance between income generation and capital growth, offering a moderate risk-return profile. It is ideal for investors seeking a diversified approach to investing.'),
    ('Growth & Income', 3, '', 'The Growth & Income asset mix emphasizes equities more than bonds, focusing on capital appreciation while maintaining some income generation. This mix is suitable for investors seeking growth with a medium-high risk tolerance.'),
    ('Growth',          4, '', 'The Growth asset mix is primarily composed of equities, offering higher volatility with a focus on capital appreciation. It is ideal for investors seeking higher growth opportunities with a long-term horizon.'),
    ('Maximum Growth',  5, '', 'The Maximum Growth asset mix is almost entirely made up of equities or high-risk assets, providing maximum exposure to market fluctuations. It targets the highest possible returns and is suitable for investors willing to accept very high risk.'),
]

AR_TIME_HORIZON = [
    ('1', 0, 'Less than 1 year',   'Your investment portfolio is designed for a very short-term time horizon of less than one year. The focus will be on preserving capital and maintaining liquidity, prioritizing investments that are stable and easily convertible to cash.'),
    ('2', 1, '1–3 years',      'Your investment portfolio is designed with a short-to-medium term time horizon of 1 to 3 years. The strategy will balance between stability and modest growth, emphasizing relatively safe investments that offer some potential for appreciation while minimizing risk.'),
    ('3', 2, '3–5 years',      'Your investment portfolio is structured with a medium-term time horizon of 3 to 5 years. This allows for a balanced approach to risk and return, with the objective of achieving moderate growth while preserving capital.'),
    ('4', 3, '5–10 years',     'Your investment portfolio is tailored for a long-term time horizon of 5 to 10 years. With a focus on growth and capital appreciation, the investment strategy will be more aggressive. The approach will aim to optimize growth potential and manage risk, achieving significant appreciation over the extended period.'),
    ('5', 4, 'More than 10 years', 'Your investment portfolio is planned with a long-term time horizon of more than 10 years. This extended duration allows for a more aggressive growth strategy, taking advantage of compounding growth potential and maximizing capital appreciation over the long run.'),
]

AR_LIQUIDITY = [
    ('1', 0, 'Very Important',     'You have indicated that having access to cash quickly is very important for your investment strategy. Your investment portfolio will prioritize liquidity to ensure that funds are readily available when needed, without significant delays or penalties.'),
    ('2', 1, 'Somewhat Important', 'You have indicated that having some access to cash is somewhat important, but you can afford to wait for a short period. This implies a balance between liquidity and potential returns. Your investment portfolio will be structured to provide moderate liquidity, allowing for access to funds within a reasonable timeframe while still aiming for growth. This approach will help you meet occasional cash needs without sacrificing long-term investment goals.'),
    ('3', 2, 'Not Important',      'You have indicated that having access to cash quickly is not important for your investment strategy. Your investment portfolio can therefore focus on growth and capital appreciation, with less emphasis on liquidity, allowing for potentially higher long-term returns.'),
]

AR_RI = [
    ('RI',      0, 'Responsible Investing', 'You have indicated a preference for an all responsible investing portfolio. Your investment strategy will prioritize selecting investments that meet environmental, social, and governance (ESG) criteria, aligning with your values by investing in companies committed to sustainable and ethical practices.'),
    ('Neutral', 1, 'Neutral',               'You have indicated a neutral stance with no specific bias towards responsible investing. This means that your investment strategy will focus on optimizing returns without particular consideration for environmental, social, and governance (ESG) criteria. The portfolio will be designed to achieve your financial objectives based on traditional investment principles, ensuring that performance and risk management are prioritized according to your overall investment goals.'),
]

AR_INCOME_NEEDS = [
    ('default', 0, 'Income Needs', 'You have indicated that you plan to withdraw $0 annually from your portfolio in the coming years. This amount will be considered in the management of your investment portfolio to ensure that your liquidity needs are met while pursuing your long-term investment goals. The strategy will aim to generate sufficient income and maintain the necessary liquidity to accommodate these annual withdrawals.'),
]

ALL_BLOCKS = [
    ('ar_risk_profile',          AR_RISK_PROFILE),
    ('ar_asset_mix',             AR_ASSET_MIX),
    ('ar_time_horizon',          AR_TIME_HORIZON),
    ('ar_liquidity',             AR_LIQUIDITY),
    ('ar_responsible_investing', AR_RI),
    ('ar_income_needs',          AR_INCOME_NEEDS),
]


def seed_ar_copy_blocks(apps, schema_editor):
    IPSCopyBlock = apps.get_model('ips', 'IPSCopyBlock')
    for category, rows in ALL_BLOCKS:
        for key, order, title, body in rows:
            IPSCopyBlock.objects.get_or_create(
                category=category,
                key=key,
                defaults={'title': title, 'body': body, 'order': order},
            )


def remove_ar_copy_blocks(apps, schema_editor):
    IPSCopyBlock = apps.get_model('ips', 'IPSCopyBlock')
    categories = [cat for cat, _ in ALL_BLOCKS]
    IPSCopyBlock.objects.filter(category__in=categories).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0010_ar_first_page_site_document'),
    ]

    operations = [
        migrations.RunPython(seed_ar_copy_blocks, reverse_code=remove_ar_copy_blocks),
    ]
