from enum import Enum

class AllIndicators(str, Enum):
    lpa = "lpa"
    vpa = "vpa"
    ebitpa = "ebitpa"
    apa = "apa"
    rlpa = "rlpa"
    pl = "pl"
    pvp = "pvp"
    psr = "psr"
    pcf = "pcf"
    gm = "gm"
    nm = "nm"
    em = "em"
    om = "om"
    roe = "roe"
    roa = "roa"
    at = "at"
    cl = "cl"
    ql = "ql"
    csl = "csl"
    wc = "wc"
    gd = "gd"
    nd = "nd"
    td = "td"
    ebitda = "ebitda"
    ebitdam = "ebitdam"

AllIndicatorsColumns = {
    "lpa": "earnings_per_share",
    "vpa": "equity_per_share",
    "ebitpa": "ebit_per_share",
    "apa": "assets_per_share",
    "rlpa": "net_sales_per_share",
    "pl": "price_earnings",
    "pvp": "price_to_book",
    "psr": "price_to_sales",
    "pcf": "price_to_cash_flow",
    "gm": "gross_margin",
    "nm": "net_margin",
    "em": "ebit_margin",
    "om": "operating_margin",
    "roe": "return_on_equity",
    "roa": "return_on_assets",
    "at": "asset_turnover",
    "cl": "current_liquidity",
    "ql": "quick_liquidity",
    "csl": "cash_liquidity",
    "wc": "working_capital",
    "gd": "gross_debt",
    "nd": "net_debt",
    "td": "total_debt",
    "ebitda": "ebitda",
    "ebitdam": "ebitda_margin"
}
class MarketRatioIndicator(str, Enum):
    lpa = "lpa"
    vpa = "vpa"
    ebitpa = "ebitpa"
    apa = "apa"
    rlpa = "rlpa"
    pl = "pl"
    pvp = "pvp"
    psr = "psr"
    pcf = "pcf"
    all = "all"


MarketRatioIndicatorColumns = {
    "lpa": "earnings_per_share",
    "vpa": "equity_per_share",
    "ebitpa": "ebit_per_share",
    "apa": "assets_per_share",
    "rlpa": "net_sales_per_share",
    "pl": "price_earnings",
    "pvp": "price_to_book",
    "psr": "price_to_sales",
    "pcf": "price_to_cash_flow"
}

class RatioIndicator(str, Enum):
    gm = "gm"
    nm = "nm"
    em = "em"
    om = "om"
    roe = "roe"
    roa = "roa"
    at = "at"
    cl = "cl"
    ql = "ql"
    csl = "csl"
    wc = "wc"
    gd = "gd"
    nd = "nd"
    td = "td"
    ebitda = "ebitda"
    ebitdam = "ebitdam"
    all = "all"


RatioIndicatorColumns = {
    "gm": "gross_margin",
    "nm": "net_margin",
    "em": "ebit_margin",
    "om": "operating_margin",
    "roe": "return_on_equity",
    "roa": "return_on_assets",
    "at": "asset_turnover",
    "cl": "current_liquidity",
    "ql": "quick_liquidity",
    "csl": "cash_liquidity",
    "wc": "working_capital",
    "gd": "gross_debt",
    "nd": "net_debt",
    "td": "total_debt",
    "ebitda": "ebitda",
    "ebitdam": "ebitda_margin"
}
