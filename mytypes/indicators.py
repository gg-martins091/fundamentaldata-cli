from enum import Enum

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
