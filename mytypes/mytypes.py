from enum import Enum

class InfoType(str, Enum):
    balances = "balances"
    incomes = "incomes"
    cashflows = "cashflows"
    marketratios = "marketratios"
    ratios = "ratios"
    all = "all"

endpoints = {"balances": "balances", "incomes": "incomes", "cashflows": "cash_flows", "marketratios": "market_ratios", "ratios": "ratios"}
