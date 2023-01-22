from mytypes.mytypes import InfoType, endpoints
import random
import string
import psycopg2
import psycopg2.extras
from services.pg import conn
from services.log import log
from services.utils import api_sleep, get_cvm_code
from services.http import api

Parameters = {
    "balances": "",
    "incomes": "?period_type=quarter",
    "cashflows": "?period_type=quarter",
    "marketratios": "?period_type=quarter",
    "ratios": ""
}

def m_getinfos(infotype: InfoType, ticker: str):
    log.info(f":hourglass: Loading {infotype}")

    cvm_code = get_cvm_code(ticker)
    r = api.get(f'companies/{cvm_code}/{endpoints[infotype]}{Parameters[infotype]}')
    infos = r.json()
    m_upsert_info(infos, endpoints[infotype], ticker)
    api_sleep()
    log.info(f":white_check_mark: {infotype} loaded successfully")


columns = {
    "balances": ("cvm_code",
"statement_type",
"reference_date",
"assets",
"current_assets",
"cash",
"financial_investments",
"receivables",
"inventories",
"biological_assets",
"noncurrent_assets",
"investments",
"fixed_assets",
"intangible_assets",
"liabilities",
"current_liabilities",
"suppliers",
"loans",
"noncurrent_liabilities",
"long_term_loans",
"equity",
"equity_non_controlling",),
    "incomes": ("cvm_code",
"statement_type",
"period_init",
"period_end",
"period_type",
"net_sales",
"costs",
"gross_income",
"operating_expenses",
"ebit",
"non_operating_income",
"profit_before_taxes",
"taxes",
"continued_operations",
"discontinued_operations",
"net_income",
"net_income_controlling",
"net_income_non_controlling",),
    "cash_flows": ("cvm_code",
"statement_type",
"period_init",
"period_end",
"period_type",
"operating",
"investing",
"financing",),
    "market_ratios": ("cvm_code",
"ticker",
"reference_date",
"shares",
"price",
"earnings_per_share",
"equity_per_share",
"ebit_per_share",
"assets_per_share",
"net_sales_per_share",
"price_earnings",
"price_to_book",
"price_to_sales",
"price_to_cash_flow",),
    "ratios": ("cvm_code",
"statement_type",
"period_init",
"period_end",
"period_type",
"gross_margin",
"net_margin",
"ebit_margin",
"operating_margin",
"return_on_equity",
"return_on_assets",
"asset_turnover",
"current_liquidity",
"quick_liquidity",
"cash_liquidity",
"working_capital",
"gross_debt",
"net_debt",
"total_debt",
"ebitda",
"ebitda_margin",)
}

date_column = {"balances": "reference_date", "incomes": "period_end", "cash_flows": "period_end", "market_ratios": "reference_date", "ratios": "period_end"}

def m_get_insert_select(infotype, tmp, columns_string) -> str:
    columns_string_alias = 'tmp.' + ', tmp.'.join(columns[infotype])
    return f'''
        INSERT INTO public.{infotype} ({columns_string})
        SELECT {columns_string_alias}
        FROM {tmp}.{infotype} as tmp
        LEFT JOIN public.{infotype} as p on p.cvm_code = tmp.cvm_code and p.{date_column[infotype]} = tmp.{date_column[infotype]}
        WHERE p.cvm_code isnull
    '''

def m_get_insert_array(info, infotype):
    ret = [];

    for column in columns[infotype]:
        ret.append(info[column])

    return ret

def m_upsert_info(infos, infotype, ticker):
    tmp = f'tmp_{ticker}_{infotype}_' + ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    log.debug(f'Temporary schema used for info {infotype} for ticker {ticker}: [bold]{tmp}[/bold]')
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(f'CREATE SCHEMA {tmp}')
        cur.execute(f'CREATE TABLE {tmp}.{infotype} (LIKE public.{infotype} INCLUDING ALL)')

        values_string = ("%s, " * len(columns[infotype])).rstrip(', ')
        columns_string = ','.join(columns[infotype])
        for info in infos:
            cur.execute(f"INSERT INTO {tmp}.{infotype} ({columns_string}) VALUES ({values_string})", m_get_insert_array(info, infotype))

        cur.execute(m_get_insert_select(infotype, tmp, columns_string))

        cur.execute(f'DROP SCHEMA {tmp} CASCADE')
        conn.commit()
        cur.close()
    except psycopg2.DatabaseError as error:
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()

