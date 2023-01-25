
from services.http import api
import pandas as pd

def m_create_gringos_df():

    r = api.get('investors')
    investors = r.json()
    df = pd.DataFrame(investors)

    df = df.reset_index()
    df.set_index('date', inplace=True, drop=False)
    df['index'] = 0
    df['sum'] = df['flow'].cumsum()
    df = df.reindex(index=df.index[::-1])
    return df
