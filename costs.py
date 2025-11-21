from pathlib import Path
import pandas as pd

def get_costs(excel_path, sheet_name=0):
    df_ = pd.read_excel('0_EP_runs/' + excel_path, sheet_name=sheet_name)

    # 1. get relevant rows
    df = df_[(df_.index >= 53) & (df_.index < 67)].copy()
    df = df[['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 3']]

    # keep only the rows you want
    df = df.loc[[53, 54, 60, 62, 64, 66]]

    # make numeric before filling -> no FutureWarning
    df['Unnamed: 1'] = pd.to_numeric(df['Unnamed: 1'], errors='coerce')
    df['Unnamed: 3'] = pd.to_numeric(df['Unnamed: 3'], errors='coerce')

    # fill NaNs in Unnamed: 1 with Unnamed: 3
    df['Unnamed: 1'] = df['Unnamed: 1'].fillna(df['Unnamed: 3'])

    # drop helper column
    df = df[['Unnamed: 0', 'Unnamed: 1']]

    # 2. rename
    df = df.rename(columns={
        'Unnamed: 0': 'Case (M EUR)',
        'Unnamed: 1': Path(excel_path).stem
    })

    # 3. transpose
    df = df.set_index('Case (M EUR)').T
    return df