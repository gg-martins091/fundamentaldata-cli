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



class IncomeIndicator(str, Enum):
    ns = "ns"
    costs = "costs"
    gi = "gi"
    oe = "oe"
    ebit = "ebit"
    noi = "noi"
    pbt = "pbt"
    taxes = "taxes"
    co = "co"
    do = "do"
    ni = "ni"
    nic = "nic"
    ninc = "ninc"

IncomeIndicatorColumns = {
    "ns" : "net_sales",
    "costs" : "costs",
    "gi" : "gross_income",
    "oe" : "operating_expenses",
    "ebit" : "ebit",
    "noi" : "non_operating_income",
    "pbt" : "profit_before_taxes",
    "taxes" : "taxes",
    "co" : "continued_operations",
    "do" : "discontinued_operations",
    "ni" : "net_income",
    "nic" : "net_income_controlling",
    "ninc" : "net_income_non_controlling"
}



class BalanceIndicator(str, Enum):
    assets = "assets"
    ca = "ca"
    cash = "cash"
    fi = "fi"
    rec = "rec"
    inv = "inv"
    nca = "nca"
    invest = "invest"
    fa = "fa"
    ia = "ia"
    lia = "lia"
    clia = "clia"
    sup = "sup"
    loans = "loans"
    ltl = "ltl"
    equity = "equity"
    enc = "enc"

BalanceIndicatorColumns = {
    "assets" : "assets",
    "ca" : "current_assets",
    "cash" : "cash",
    "fi" : "financial_investments",
    "rec" : "receivables",
    "inv" : "inventories",
    "nca" : "noncurrent_assets",
    "invest" : "investments",
    "fa" : "fixed_assets",
    "ia" : "intangible_assets",
    "lia" : "liabilities",
    "clia" : "current_liabilities",
    "sup" : "suppliers",
    "loans" : "loans",
    "ltl" : "long_term_loans",
    "equity" : "equity",
    "enc" : "equity_non_controlling"
}
