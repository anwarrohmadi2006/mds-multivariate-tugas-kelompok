import pandas as pd
import re

XLSX_FILE = "Query Builder Result - Selasa, 09 Juni 2026 pukul 06.10.20 WIB.xlsx"
xl = pd.ExcelFile(XLSX_FILE)
df_vol_raw = pd.read_excel(XLSX_FILE, sheet_name="Data 2", header=3)
df_val_raw = pd.read_excel(XLSX_FILE, sheet_name="Data 1", header=3)

def parse_sheet(df_raw):
    df = df_raw.copy()
    prov_col = df.columns[0]
    df[prov_col] = df[prov_col].astype(str).str.strip()
    df = df[~df[prov_col].str.lower().isin(['nan', 'total', 'indonesia', 'jumlah'])]
    df = df.set_index(prov_col)
    df = df.replace('-', 0).replace('', 0)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    return df

df_vol = parse_sheet(df_vol_raw)
df_val = parse_sheet(df_val_raw)

import re
def get_udang_cols(df, target_years):
    res = {}
    for col in df.columns:
        col_str = str(col)
        years_found = re.findall(r'20\d{2}', col_str)
        if years_found:
            year = int(years_found[-1])
            if year in target_years and 'udang' in col_str.lower():
                res[year] = col
    return res

udang_vol_cols = get_udang_cols(df_vol, [2023, 2024])
udang_val_cols = get_udang_cols(df_val, [2023, 2024])

common_prov = df_vol.index.intersection(df_val.index)
records = []
for prov in common_prov:
    vol_23 = float(df_vol.loc[prov, udang_vol_cols.get(2023, df_vol.columns[0])])
    vol_24 = float(df_vol.loc[prov, udang_vol_cols.get(2024, df_vol.columns[0])])
    
    val_23 = float(df_val.loc[prov, udang_val_cols.get(2023, df_val.columns[0])]) / 1000
    val_24 = float(df_val.loc[prov, udang_val_cols.get(2024, df_val.columns[0])]) / 1000
    
    records.append({
        'Provinsi': prov,
        'Vol_2023': vol_23, 'Nilai_2023': val_23,
        'Vol_2024': vol_24, 'Nilai_2024': val_24,
    })

df_panel = pd.DataFrame(records).set_index('Provinsi')

# Filter: hanya provinsi yang punya data udang di KEDUA tahun
df_panel = df_panel[(df_panel['Vol_2023'] > 0) & (df_panel['Vol_2024'] > 0)]
print(f"\nJumlah provinsi valid: {len(df_panel)}")
print(df_panel.describe().round(1))
