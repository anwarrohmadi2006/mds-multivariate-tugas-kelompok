import pandas as pd

# 1. BACA & EKSTRAK DATA DARI EXCEL (Langsung pakai index kolom BPS yang valid)
FILE = "Query Builder Result - Selasa, 09 Juni 2026 pukul 06.10.20 WIB.xlsx"
df_val = pd.read_excel(FILE, sheet_name=0, skiprows=3, header=None)
df_vol = pd.read_excel(FILE, sheet_name=1, skiprows=3, header=None)

def clean_df(df):
    df.rename(columns={0: 'Provinsi'}, inplace=True)
    df = df[~df['Provinsi'].astype(str).str.lower().isin(['nan','total','indonesia','jumlah'])]
    return df.set_index('Provinsi').replace(['-',''], 0).apply(pd.to_numeric, errors='coerce').fillna(0)

df_vol, df_val = clean_df(df_vol), clean_df(df_val)

# Indeks Kolom Udang: Volume(59,60), Nilai(39,40)
records = []
for p in df_vol.index.intersection(df_val.index):
    v23, v24 = float(df_vol.loc[p, 59]), float(df_vol.loc[p, 60])
    n23, n24 = float(df_val.loc[p, 39])/1000, float(df_val.loc[p, 40])/1000
    t23, t24 = float(df_vol.loc[p, [5,11,17,23,29,35,41,47,53,59,65]].sum()), float(df_vol.loc[p, [6,12,18,24,30,36,42,48,54,60,66]].sum())
    
    h23, h24 = (n23*1e3)/v23 if v23>0 else 0, (n24*1e3)/v24 if v24>0 else 0
    s23, s24 = (v23/t23)*100 if t23>0 else 0, (v24/t24)*100 if t24>0 else 0
    
    records.append({'Provinsi': p, 
        'Vol_2023': v23, 'Nilai_2023': n23, 'Harga_2023': h23, 'Share_2023': s23, 'HargaShare_2023': (h23*s23)/1000,
        'Vol_2024': v24, 'Nilai_2024': n24, 'Harga_2024': h24, 'Share_2024': s24, 'HargaShare_2024': (h24*s24)/1000
    })

df = pd.DataFrame(records).set_index('Provinsi')
df = df[(df.Vol_2023 > 0) & (df.Vol_2024 > 0)]

import os
os.makedirs('output', exist_ok=True)
output_path = 'output/hasil_preprocessing.csv'
df.to_csv(output_path)
print(f"Preprocessing selesai. Data ({len(df)} provinsi) telah disimpan ke {output_path}")
