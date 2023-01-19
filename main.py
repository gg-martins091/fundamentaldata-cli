from modules.getinfos.getinfos import m_getinfos
from mytypes.mytypes import InfoType
from modules.loadcompanies.loadcompanies import m_loadcompanies
import typer
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn, SpinnerColumn
from services.pg import conn
from services.utils import get_cvm_code
import psycopg2.extras
import plotext as plt

app = typer.Typer()

@app.command()
def loadcompanies():
    m_loadcompanies()

@app.command()
def getinfos(infotype: InfoType, ticker: str):
    if infotype == "all":
        with Progress(SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            MofNCompleteColumn(),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan] Infos processed: ", total=len(InfoType) -1)
            for data in InfoType:
                if data.value != "all":
                    m_getinfos(data.value, ticker)
                    progress.update(task, advance=1)
                    print()
    else:
        m_getinfos(infotype, ticker)

@app.command()
def plot(ticker: str):
    # cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor = conn.cursor()
    cvm_code = get_cvm_code(ticker)

    cursor.execute(f"SELECT earnings_per_share FROM market_ratios where cvm_code = {cvm_code} and earnings_per_share is not null")

    eps = [float(r[0]) for r in cursor.fetchall()]


    cursor.execute(f"SELECT earnings_per_share FROM market_ratios where cvm_code = 3980 and earnings_per_share is not null")

    eps2 = [float(r[0]) for r in cursor.fetchall()]

    plt.plot(eps, label = "ETER3")
    plt.plot(eps2, label = "GGBR4")

    plt.title("Multiple Data Set")
    plt.show()


if __name__ == "__main__":
    app()
