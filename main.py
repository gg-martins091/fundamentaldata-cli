from modules.getinfos.getinfos import m_getinfos
from modules.plots.gringos import m_create_gringos_df
from modules.plots.income import m_create_income_df
from modules.plots.marketratio import m_create_marketratio_df
from modules.plots.ratio import m_create_ratio_df
from modules.plots.cashflow import m_create_cashflow_df
from modules.plots.balance import m_create_balance_df
from mytypes.indicators import BalanceIndicator, CashflowIndicator, IncomeIndicator, MarketRatioIndicator, MarketRatioIndicatorColumns, RatioIndicator, RatioIndicatorColumns, AllIndicators, AllIndicatorsColumns, IncomeIndicator, BalanceIndicator, CashflowIndicator
from mytypes.mytypes import InfoType
from modules.loadcompanies.loadcompanies import m_loadcompanies
import typer
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn, SpinnerColumn
from services.pg import conn
from services.utils import get_cvm_code, get_layout
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

console = Console()

#prompt-toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop.inputhook import set_eventloop_with_inputhook
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

def inputhook(inputhook_context):
    while not inputhook_context.input_is_ready():
        try:
            plt.pause(0.1)
        except Exception as exp:
            log.exception("%s", type(exp).__name__)
            continue
    return False


# history_file = os.path.join(os.path.expanduser("~"), ".fundamentals.his")

session = PromptSession(
    history=FileHistory("./.history")
)
set_eventloop_with_inputhook(inputhook)

#prompt-toolkit

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
    df = m_create_marketratio_df(indicators, tickers, price)
    df = df.dropna()
    # o interpolate aqui faz com que, caso tenhamos 2 graficos, 
    #um com dados desde 2010 e um desde 2015, o grafico que comeca 
    #em 2015 ainda mostra 2010 ate 2015 sem linha nenhuma
    #sem isso, todos os graficos comecariam quando o menor grafico comeca.
    #nesse exemplo, ambos graficos comecariam em 2015.
    ax = df.interpolate(method='linear').plot(title='market ratio', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    mplcursors.cursor(ax)
    plt.show()


@app.command()
def ratio(indicators: List[RatioIndicator], price: bool = False):
    tickers = prompt.Prompt.ask("Tickers ")
    tickers = tickers.upper().split(' ')
    df = m_create_ratio_df(indicators, tickers, price)
    ax = df.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(indicators))), title='ratio', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for a in ax:
        mplcursors.cursor(a)

    plt.show()

@app.command()
def income(indicators: List[IncomeIndicator], price: bool = False):
    tickers = prompt.Prompt.ask("Tickers ")
    tickers = tickers.upper().split(' ')
    df = m_create_income_df(indicators, tickers, price)
    ax = df.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(indicators))), title='ratio', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for a in ax:
        mplcursors.cursor(a)

    plt.show()

@app.command()
def balance(indicators: List[BalanceIndicator], price: bool = False):
    tickers = prompt.Prompt.ask("Tickers ")
    tickers = tickers.upper().split(' ')
    df = m_create_balance_df(indicators, tickers, price)
    ax = df.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(indicators))), title='ratio', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for a in ax:
        mplcursors.cursor(a)

    plt.show()

@app.command()
def plot(tickers: List[str], price: bool = False):

    # TODO: prompt pra saber quais types e quais indicators vai querer, alem dos tickers claro
    # TODO: criar as funcoes de criacao de df de incomes, balances e cashflows
    plt.tight_layout()
    ratioindicators = ('nm','em','roe','cl','ql','wc','gd','nd','td')
    dfratio = m_create_ratio_df(ratioindicators, tickers, False)
    ratiox = dfratio.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(ratioindicators))), title='ratios', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for rx in ratiox:
        mplcursors.cursor(rx)

    plt.tight_layout()
    incomeindicators = ('ns', 'costs', 'gi', 'ebit', 'taxes', 'ni')
    dfincome = m_create_income_df(incomeindicators, tickers, False)
    incomex = dfincome.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(incomeindicators))), title='income', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for ix in incomex:
        mplcursors.cursor(ix)

    plt.tight_layout()
    marketratioindicators = ('pl','pvp','pcf',)
    marketratiodf = m_create_marketratio_df(marketratioindicators, tickers, False)
    mrx = marketratiodf.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(marketratioindicators))), title='market ratio', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for mr in mrx:
        mplcursors.cursor(mr)

    plt.tight_layout()
    #balance +
    balanceindicators = ('cash', 'inv', 'invest', 'assets', 'ca', 'nca', 'fa', 'equity')
    balancedf = m_create_balance_df(balanceindicators, tickers, False)
    bx = balancedf.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(balanceindicators))), title='balance o que tem', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for b in bx:
        mplcursors.cursor(b)

    plt.tight_layout()
    #balance -
    balance2indicators = ('lia', 'clia', 'ia', 'sup', 'loans')
    balance2df = m_create_balance_df(balance2indicators, tickers, False)
    bxx = balance2df.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(balance2indicators))), title='balance devedor', fontsize=12, figsize=(20, 10), secondary_y=tickers if price else None)
    for bb in bxx:
        mplcursors.cursor(bb)

    plt.tight_layout()
    plt.show()

@app.command()
def gringos():
    df = m_create_gringos_df()
    fig,ax = plt.subplots()
    ax.bar(df.index, df['flow'], label="flow")
    ax.plot(df.index, df['sum'], color="green")
    ax.set_xticklabels(df.index)
    
    # ax = df[['date','sum']].plot(use_index=False, x='date', kind='line', title='fluxo gringo', fontsize=12, figsize=(20, 10))
    # df[['date','flow']].plot(x='date', kind='bar',ax=ax)
    mplcursors.cursor(ax)

    plt.tight_layout()
    plt.show()

@app.command()
def cashflow(indicators: List[CashflowIndicator]):
    tickers = prompt.Prompt.ask("Tickers ")
    tickers = tickers.upper().split(' ')
    df = m_create_cashflow_df(indicators, tickers)
    ax = df.interpolate(method='linear').plot(subplots=True, layout=(get_layout(len(tickers),len(indicators))), title='ratio', fontsize=12, figsize=(20, 10))
    for a in ax:
        mplcursors.cursor(a)

    plt.show()

@app.command()
def terminal():
    console.clear()
    ret = 1
    while ret:
        an_input = session.prompt(
            f"fundamentals / > ",
            # completer=t_controller.completer,
            search_ignore_case=True,
            bottom_toolbar=HTML(
                '<style bg="ansiblack" fg="ansiwhite">[h]</style> help menu    '
                '<style bg="ansiblack" fg="ansiwhite">[q]</style> return to previous menu    '
                '<style bg="ansiblack" fg="ansiwhite">[e]</style> exit terminal    '
                '<style bg="ansiblack" fg="ansiwhite">[cmd -h]</style> '
                "see usage and available options    "
                '<style bg="ansiblack" fg="ansiwhite">[about]</style> Getting Started Documentation'
            ),
            style=Style.from_dict(
                {
                    "bottom-toolbar": "#ffffff bg:#333333",
                }
            ),
        )
        print(an_input)

if __name__ == "__main__":
    app()
