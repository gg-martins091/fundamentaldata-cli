from services.log import log
import random
from time import sleep
from .pg import conn
import math

def api_sleep(is_retry = False):
    t = random.uniform(1.5, 2.8)
    log.debug(f":zzz:{' :arrows_counterclockwise:' if is_retry else ''} Sleeping for {round(t, 2)} seconds{' (retry)' if is_retry else ''}")
    sleep(t)


def get_cvm_code(ticker: str):
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT c.cvm_code
        FROM companies c
        INNER JOIN tickers t on t.cvm_code = c.cvm_code
        WHERE t.ticker = '{ticker}'
        LIMIT 1
    ''')

    res = cursor.fetchone()
    if res == None:
        raise Exception('ticker not found')

    return res[0]

def get_layout(tickers, indicators):

    if tickers == 1:
        return (3, math.ceil(indicators / 3))

    return (tickers, indicators)
