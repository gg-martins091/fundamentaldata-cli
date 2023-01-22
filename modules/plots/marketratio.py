
import datetime
from mytypes.indicators import MarketRatioIndicator, MarketRatioIndicatorColumns
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn, SpinnerColumn
from services.pg import conn
import pandas as pd
import pandas.io.sql as sqlio
import datetime

def m_create_marketratio_df(indicators, tickers, price):
    start_time = datetime.datetime(2015, 10, 1)
    # end_time = datetime.datetime(2018, 6, 20)
    today = datetime.datetime.now().date().isoformat()
    dates = pd.date_range(start_time, today)
    df = pd.DataFrame(index=dates)

    if len(indicators) == 1 and indicators[0] == "all":
        indicators = [i for i in MarketRatioIndicator if i != "all"]

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
            all_indicators = ' '.join([f'{MarketRatioIndicatorColumns[i]} as "{ticker}_{MarketRatioIndicatorColumns[i]}",' for i in indicators])
            only_aliases = [f"{ticker}_{MarketRatioIndicatorColumns[i]}" for i in indicators]
            dfquery = sqlio.read_sql_query(f"""
                SELECT DISTINCT reference_date, {all_indicators} price as "{ticker}" FROM market_ratios mr
                INNER JOIN tickers t on t.cvm_code = mr.cvm_code and t.ticker = mr.ticker
                WHERE t.ticker = '{ticker}'
            """, conn)
            dfquery = dfquery.reset_index()
            dfquery.set_index('reference_date', inplace=True, drop=False)

            df = df.join(dfquery[only_aliases + ([ticker] if price else [])])
            progress.update(task, advance=1)

    df = df.dropna()
    return df
