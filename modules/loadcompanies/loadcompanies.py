from services.utils import api_sleep
from services.http import api
import random
import string
import psycopg2
import psycopg2.extras
from services.pg import conn
from services.log import log
from time import sleep
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn, SpinnerColumn

def m_loadcompanies():
    # log.info(":hourglass: Loading companies")

    # r = api.get('companies')
    # companies = r.json()
    # m_upsert_companies(companies)
    # api_sleep()
    # log.info(":white_check_mark: Companies loaded successfully")


    m_upsert_tickers()
    log.info(":white_check_mark: Companies tickers loaded successfully")




def m_upsert_companies(companies):
    tmp = 'tmp_c_' + ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    log.debug(f'Temporary schema used for companies: [bold]{tmp}[/bold]')
    try:
        cur = conn.cursor()
        cur.execute(f'CREATE SCHEMA {tmp}')
        cur.execute(f'CREATE TABLE {tmp}.companies (LIKE public.companies INCLUDING ALL)')

        for company in companies:
            if company['cnpj']:
                cur.execute(f'INSERT INTO {tmp}.companies (name, trade_name,  cvm_code, cnpj, founding_date, main_activity, website, controlling_interest, is_state_owned, is_foreign, is_b3_listed, b3_issuer_code, b3_listing_segment, b3_sector, b3_subsector, b3_segment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(
                    company['name'],
                    company['trade_name'],
                    company['cvm_code'],
                    company['cnpj'],
                    company['founding_date'],
                    company['main_activity'],
                    company['website'],
                    company['controlling_interest'],
                    company['is_state_owned'],
                    company['is_foreign'],
                    company['is_b3_listed'],
                    company['b3_issuer_code'],
                    company['b3_listing_segment'],
                    company['b3_sector'],
                    company['b3_subsector'],
                    company['b3_segment']
                    )
                )
        cur.execute(f'''INSERT INTO public.companies (name, trade_name,  cvm_code, cnpj, founding_date, main_activity, website, controlling_interest, is_state_owned, is_foreign, is_b3_listed, b3_issuer_code, b3_listing_segment, b3_sector, b3_subsector, b3_segment)
        SELECT tmp.name, tmp.trade_name, tmp.cvm_code, tmp.cnpj, tmp.founding_date, tmp.main_activity, tmp.website, tmp.controlling_interest, tmp.is_state_owned, tmp.is_foreign, tmp.is_b3_listed, tmp.b3_issuer_code, tmp.b3_listing_segment, tmp.b3_sector, tmp.b3_subsector, tmp.b3_segment
        FROM {tmp}.companies tmp
        LEFT JOIN public.companies c on c.cvm_code = tmp.cvm_code
        WHERE c.cvm_code isnull''')

        cur.execute(f'DROP SCHEMA {tmp} CASCADE')
        conn.commit()
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.rollback()
            cur.close()


def m_upsert_tickers():

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('''SELECT c.* 
                   FROM companies c
                   LEFT JOIN tickers t on t.cvm_code = c.cvm_code
                   WHERE t.cvm_code isnull and c.is_b3_listed = true''')
    companies = cursor.fetchall()
    cursor.close()

    log.info(f":hourglass: Loading tickers for {len(companies)} companies")

    count = 0
    cur = conn.cursor()
    tmp = 'tmp_ct_' + ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    insert_query = f'''INSERT INTO public.tickers (ticker, type, cvm_code, market_type, market, issuer_code, currency, isin)
            SELECT tmp.ticker, tmp.type, tmp.cvm_code, tmp.market_type, tmp.market, tmp.issuer_code, tmp.currency, tmp.isin
            FROM {tmp}.tickers tmp
            LEFT JOIN public.tickers t on t.cvm_code = tmp.cvm_code and t.ticker = tmp.ticker
            WHERE t.cvm_code isnull
            '''
    try:
        log.debug(f'Temporary schema used for companies tickers: [bold]{tmp}[/bold]')

        cur.execute(f'CREATE SCHEMA {tmp}')
        cur.execute(f'CREATE TABLE {tmp}.tickers (LIKE public.tickers INCLUDING ALL)')

        with Progress(SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            MofNCompleteColumn(),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan] Companies processed: ", total=len(companies))

            for company in companies:
                cvm_code = company['cvm_code']
                name = company['name']
                website = company['website']
                log.debug(f"Loading tickers for {name}", extra={'style': f"link {website}"})
                if count > 10:
                    log.debug(':heavy_plus_sign: Commiting insertion of tickers of 10 more companies')
                    cur.execute(insert_query)
                    cur.execute(f'DELETE FROM {tmp}.tickers')
                    conn.commit()
                    cur = conn.cursor()
                    count = 0


                r = api.get(f'companies/{cvm_code}/tickers')
                api_sleep()
                ct = r.json()

                for t in ct:
                    cur.execute(f'INSERT INTO {tmp}.tickers (ticker, type, cvm_code, market_type, market, issuer_code, currency, isin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',(
                        t['ticker'],
                        t['type'],
                        cvm_code,
                        t['market_type'],
                        t['market'],
                        t['issuer_code'],
                        t['currency'],
                        t['isin'],
                        )
                    )
                count = count + 1
                progress.update(task, advance=1)

        cur.execute(insert_query)

        cur.execute(f'DROP SCHEMA {tmp} CASCADE')
        conn.commit()
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.rollback()


