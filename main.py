import typer
from modules.getinfos.getinfos import m_getinfos
from modules.loadcompanies.loadcompanies import m_loadcompanies

app = typer.Typer()

@app.command()
def loadcompanies():
    m_loadcompanies()


@app.command()
def getinfos():
    m_getinfos()

if __name__ == "__main__":
    app()
