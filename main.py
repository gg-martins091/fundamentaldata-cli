from modules.getinfos.getinfos import m_getinfos
from mytypes.indicators import MarketRatioIndicator, MarketRatioIndicatorColumns
from mytypes.mytypes import InfoType
from modules.loadcompanies.loadcompanies import m_loadcompanies
import typer
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn, SpinnerColumn
from services.pg import conn
from services.utils import get_cvm_code
from services.log import log
import psycopg2.extras
import matplotlib.pyplot as plt
import matplotlib
from typing import List
import pandas as pd
import pandas.io.sql as sqlio
import datetime
import mplcursors
from rich import prompt
from rich.live import Live
from rich.table import Table
import time
from rich import print
from rich.layout import Layout

layout = Layout()
app = typer.Typer()

@app.command()
def loadcompanies():
    m_loadcompanies()

@app.command()
def getinfos(infotype: InfoType, tickers: List[str]):
    with Progress(SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task1 = progress.add_task(f"[cyan] Tickers processed: ", total=len(tickers))
        for ticker in tickers:
            if infotype == "all":
                task2 = progress.add_task(f"[cyan] ({ticker}) Infos processed: ", total=len(InfoType) -1)
                for data in InfoType:
                    if data.value != "all":
                        m_getinfos(data.value, ticker)
                        progress.update(task2, advance=1)
                        print()
            else:
                m_getinfos(infotype, ticker)

            progress.update(task1, advance=1)


@app.command()
def marketratio(indicators: List[MarketRatioIndicator], price: bool = False):
    tickers = prompt.Prompt.ask("Tickers ")
    tickers = tickers.upper().split(' ')
    start_time = datetime.datetime(2020, 10, 1)
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
            print(f"""
                SELECT DISTINCT reference_date, {all_indicators} price as "{ticker}" FROM market_ratios mr
                INNER JOIN tickers t on t.cvm_code = mr.cvm_code and t.ticker = mr.ticker
                WHERE t.ticker = '{ticker}'
            """, conn)
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
    ax = df.plot(title='market ratio', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    ax.set_xlabel("Date")
    # ax.set_ylabel(indicator)
    
    mplcursors.cursor(ax)
    # plt.title('Relative price change')
    # plt.legend(loc='upper left', fontsize=12)
    plt.tight_layout()
    plt.style.use('bmh')
    plt.grid(True)
    plt.show(block=False)
    plt.pause(1)
    with Live(layout, refresh_per_second=4, screen=True):  # update 4 times a second to feel fluid
        print(layout.tree)
        # prompt.Prompt.ask("eai")
        # for row in range(12):
        #     time.sleep(0.4)  # arbitrary delay
        #     # update the renderable internally
        #     table.add_row(f"{row}", f"description {row}", "[red]ERROR")

    plt.show()
    # plt.title(indicator)
    # plt.savefig(f'{"_".join(tickers)}.pdf')

    # plt.show()

    # matplotlib.use('TkAgg')

    # plt.show()

if __name__ == "__main__":
    app()
