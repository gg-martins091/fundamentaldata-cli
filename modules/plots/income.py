

import datetime
from mytypes.indicators import IncomeIndicator, IncomeIndicatorColumns
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn, SpinnerColumn
from services.pg import conn
import pandas as pd
import pandas.io.sql as sqlio
import datetime


def m_create_income_df(indicators, tickers, price):
    start_time = datetime.datetime(2010, 10, 1)
    # end_time = datetime.datetime(2018, 6, 20)
    today = datetime.datetime.now().date().isoformat()
    dates = pd.date_range(start_time, today)
    df = pd.DataFrame(index=dates)

    if len(indicators) == 1 and indicators[0] == "all":
        indicators = [i for i in IncomeIndicator if i != "all"]



    with Progress(SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan] Loading data: ", total=len(tickers) -1)
        for ticker in tickers:
            all_indicators = ' '.join([f'{IncomeIndicatorColumns[i]} as "{ticker}_{IncomeIndicatorColumns[i]}",' for i in indicators])
            only_aliases = [f"{ticker}_{IncomeIndicatorColumns[i]}" for i in indicators]
            dfquery = sqlio.read_sql_query(f"""
                SELECT DISTINCT period_end as reference_date, {all_indicators} 0 as "{ticker}" FROM incomes mr
                INNER JOIN companies c on c.cvm_code = mr.cvm_code
                INNER JOIN tickers t on t.cvm_code = mr.cvm_code
                WHERE t.ticker = '{ticker}'
            """, conn)

            dfquery = dfquery.reset_index()
            dfquery.set_index('reference_date', inplace=True, drop=False)

            df = df.join(dfquery[only_aliases + ([ticker] if price else [])])
            progress.update(task, advance=1)

    df = df.dropna()

    return df
