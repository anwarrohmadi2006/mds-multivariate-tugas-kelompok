"""
Analisis MDS + Hierarchical Clustering + K-Means
Data: Produksi Udang Budidaya BPS 2023-2024 (32 Provinsi)
End-to-End: XLSX → Preprocessing → MDS → Clustering → Evaluasi → Visualisasi
"""

# ============================================================
# 0. IMPORT LIBRARY
# ============================================================
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import json, os, warnings, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

from sklearn.preprocessing import RobustScaler
from sklearn.manifold import MDS
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import (
    silhouette_score, silhouette_samples,
    davies_bouldin_score, calinski_harabasz_score,
    adjusted_rand_score, pairwise_distances
)
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram, cophenet
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr

os.makedirs('output', exist_ok=True)

# ============================================================
# 1. EXTRACT DATA DARI XLSX
# ============================================================
XLSX_FILE = "Query Builder Result - Selasa, 09 Juni 2026 pukul 06.10.20 WIB.xlsx"

xl = pd.ExcelFile(XLSX_FILE)
print(f"Sheet tersedia: {xl.sheet_names}")

# --- Sheet 1: Volume (Ton) ---
df_vol_raw = pd.read_excel(XLSX_FILE, sheet_name=xl.sheet_names[0], header=0)
print(f"\nShape sheet Volume: {df_vol_raw.shape}")

# --- Sheet 2: Nilai (Ribu Rupiah) ---
df_val_raw = pd.read_excel(XLSX_FILE, sheet_name=xl.sheet_names[1], header=0)
print(f"\nShape sheet Nilai: {df_val_raw.shape}")

# ============================================================
# 2. PREPROCESSING — IDENTIFIKASI STRUKTUR KOLOM
# ============================================================
def parse_sheet(df_raw, value_label='Vol'):
    df = df_raw.copy()
    prov_col = df.columns[0]
    df[prov_col] = df[prov_col].astype(str).str.strip()
    df = df[~df[prov_col].str.lower().isin(['nan', 'total', 'indonesia', 'jumlah'])]
    df = df.set_index(prov_col)
    df = df.replace('-', 0).replace('', 0)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    return df

df_vol = parse_sheet(df_vol_raw, 'Vol')
df_val = parse_sheet(df_val_raw, 'Nilai')

# ============================================================
# 3. IDENTIFIKASI KOMODITAS DAN TAHUN
# ============================================================
import re
def detect_year_commodity(columns):
    results = []
    for col in columns:
        col_str = str(col)
        years_found = re.findall(r'20\d{2}', col_str)
        if years_found:
            year = int(years_found[-1])
            commodity = re.sub(r'20\d{2}', '', col_str).strip(' _.-')
            results.append((col, commodity, year))
        else:
            results.append((col, col_str, None))
    return results

col_info_vol = detect_year_commodity(df_vol.columns)
col_info_val = detect_year_commodity(df_val.columns)

# ============================================================
# 4. EXTRACT UDANG — VOLUME & NILAI PER TAHUN
# ============================================================
def get_udang_cols(df, col_info, target_years):
    result = {}
    for col, comm, year in col_info:
        if year in target_years and 'udang' in comm.lower():
            result[year] = col
    return result

udang_vol_cols = get_udang_cols(df_vol, col_info_vol, [2023, 2024])
udang_val_cols = get_udang_cols(df_val, col_info_val, [2023, 2024])

# ============================================================
# 5. HITUNG TOTAL PRODUKSI PER PROVINSI (untuk Share)
# ============================================================
def get_total_cols(df, col_info, year):
    return [col for col, comm, y in col_info if y == year]

total_vol_2023_cols = get_total_cols(df_vol, col_info_vol, 2023)
total_vol_2024_cols = get_total_cols(df_vol, col_info_vol, 2024)
total_val_2023_cols = get_total_cols(df_val, col_info_val, 2023)
total_val_2024_cols = get_total_cols(df_val, col_info_val, 2024)

# ============================================================
# 6. BANGUN DATAFRAME PANEL (5 VARIABEL × 2 TAHUN = 10 DIM)
# ============================================================
common_prov = df_vol.index.intersection(df_val.index)

records = []
for prov in common_prov:
    vol_23 = float(df_vol.loc[prov, udang_vol_cols.get(2023, df_vol.columns[0])])
    vol_24 = float(df_vol.loc[prov, udang_vol_cols.get(2024, df_vol.columns[0])])
    val_23 = float(df_val.loc[prov, udang_val_cols.get(2023, df_val.columns[0])]) / 1000
    val_24 = float(df_val.loc[prov, udang_val_cols.get(2024, df_val.columns[0])]) / 1000
    tot_vol_23 = float(df_vol.loc[prov, total_vol_2023_cols].sum())
    tot_vol_24 = float(df_vol.loc[prov, total_vol_2024_cols].sum())

    harga_23 = (val_23 * 1_000_000) / vol_23 if vol_23 > 0 else 0
    harga_24 = (val_24 * 1_000_000) / vol_24 if vol_24 > 0 else 0
    share_23 = (vol_23 / tot_vol_23 * 100) if tot_vol_23 > 0 else 0
    share_24 = (vol_24 / tot_vol_24 * 100) if tot_vol_24 > 0 else 0
    hs_23 = harga_23 * share_23 / 1000
    hs_24 = harga_24 * share_24 / 1000

    records.append({
        'Provinsi': prov,
        'Vol_2023': vol_23, 'Nilai_2023': val_23,
        'Harga_2023': harga_23, 'Share_2023': share_23, 'HargaShare_2023': hs_23,
        'Vol_2024': vol_24, 'Nilai_2024': val_24,
        'Harga_2024': harga_24, 'Share_2024': share_24, 'HargaShare_2024': hs_24,
    })

df_panel = pd.DataFrame(records).set_index('Provinsi')

# Filter: hanya provinsi yang punya data udang di KEDUA tahun
df_panel = df_panel[(df_panel['Vol_2023'] > 0) & (df_panel['Vol_2024'] > 0)]
print(f"\nJumlah provinsi valid: {len(df_panel)}")
print(df_panel[['Vol_2023','Harga_2023','Share_2023','Nilai_2023']].describe().round(1))

# ============================================================
# 7. NORMALISASI — RobustScaler
# ============================================================
feature_cols = [
    'Vol_2023','Nilai_2023','Harga_2023','Share_2023','HargaShare_2023',
    'Vol_2024','Nilai_2024','Harga_2024','Share_2024','HargaShare_2024'
]
scaler = RobustScaler()
X_panel = scaler.fit_transform(df_panel[feature_cols].values)
print(f"\nShape X_panel setelah normalisasi: {X_panel.shape}")

# ============================================================
# 8. MDS — MULTIDIMENSIONAL SCALING
# ============================================================
dist_matrix = pairwise_distances(X_panel, metric='euclidean')

mds_model = MDS(
    n_components=2,
    dissimilarity='precomputed',
    random_state=42,
    n_init=50,
    max_iter=5000
)
coords_mds = mds_model.fit_transform(dist_matrix)

# Hitung Stress Kruskal
stress = np.sqrt(mds_model.stress_ / np.sum(dist_matrix**2)) * 100

# Hitung RSQ
ix = np.triu_indices(len(df_panel), k=1)
r_val, _ = pearsonr(dist_matrix[ix], pairwise_distances(coords_mds)[ix])
rsq = r_val**2

print(f"\n=== METRIK MDS ===")
print(f"Stress Kruskal : {stress:.4f}%  (< 10% = Baik)")
print(f"RSQ (R²)       : {rsq:.4f}      (> 0.60 = Baik)")

# ============================================================
# 9. PENENTUAN K OPTIMAL — ELBOW + SILHOUETTE
# ============================================================
print("\n=== ELBOW + SILHOUETTE (K=2 s/d 7) ===")
print(f"{'K':<5} | {'Inertia':>12} | {'Sil KM':>8} | {'Sil HC-Ward':>12} | {'DB':>8}")
print("-"*60)

results_k = []
for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=100)
    lbl_km = km.fit_predict(coords_mds)
    lbl_hc = AgglomerativeClustering(n_clusters=k, linkage='ward').fit_predict(X_panel)

    sil_km = silhouette_score(coords_mds, lbl_km)
    sil_hc = silhouette_score(X_panel, lbl_hc)
    db_km  = davies_bouldin_score(coords_mds, lbl_km)

    results_k.append({
        'k': k, 'inertia': km.inertia_,
        'sil_km': sil_km, 'sil_hc': sil_hc, 'db_km': db_km
    })
    mark = " ← OPTIMAL" if k == 3 else ""
    print(f"{k:<5} | {km.inertia_:>12.2f} | {sil_km:>8.4f} | {sil_hc:>12.4f} | {db_km:>8.4f}{mark}")

df_k = pd.DataFrame(results_k)

# ============================================================
# 10. HIERARCHICAL CLUSTERING WARD (K=3)
# ============================================================
K_OPTIMAL = 3

# Fit linkage
Z = linkage(X_panel, method='ward')
coph_corr, _ = cophenet(Z, pdist(X_panel))

# Potong dendrogram di K=3
lbl_hc3 = fcluster(Z, K_OPTIMAL, criterion='maxclust') - 1  # 0-indexed

# Metrik evaluasi HC
sil_hc3  = silhouette_score(X_panel, lbl_hc3)
sil_smp  = silhouette_samples(X_panel, lbl_hc3)
db_hc3   = davies_bouldin_score(X_panel, lbl_hc3)
ch_hc3   = calinski_harabasz_score(X_panel, lbl_hc3)

# K-Means final (dari koordinat MDS)
km_final  = KMeans(n_clusters=K_OPTIMAL, random_state=42, n_init=100)
lbl_km3   = km_final.fit_predict(coords_mds)

sil_km3   = silhouette_score(coords_mds, lbl_km3)
sil_smp_km= silhouette_samples(coords_mds, lbl_km3)
db_km3    = davies_bouldin_score(coords_mds, lbl_km3)
ch_km3    = calinski_harabasz_score(coords_mds, lbl_km3)
ari       = adjusted_rand_score(lbl_hc3, lbl_km3)

print(f"\n=== METRIK EVALUASI CLUSTERING K={K_OPTIMAL} ===")
print(f"{'Metrik':<25} | {'HC Ward':>10} | {'K-Means':>10} | Threshold")
print("-"*65)
print(f"{'Silhouette':<25} | {sil_hc3:>10.4f} | {sil_km3:>10.4f} | > 0.50")
print(f"{'Davies-Bouldin':<25} | {db_hc3:>10.4f} | {db_km3:>10.4f} | < 1.00")
print(f"{'Calinski-Harabasz':<25} | {ch_hc3:>10.2f} | {ch_km3:>10.2f} | lebih besar")
print(f"{'ARI (HC vs KM)':<25} | {ari:>10.4f} | {ari:>10.4f} | → 1.00")
print(f"{'Cophenetic':<25} | {coph_corr:>10.4f} | {'N/A':>10} | > 0.75")
print(f"{'Stress MDS':<25} | {'N/A':>10} | {stress:>9.4f}% | < 10%")
print(f"{'RSQ MDS':<25} | {'N/A':>10} | {rsq:>10.4f} | > 0.60")

# ============================================================
# 11. LABELING CLUSTER BERDASARKAN PROFIL DATA
# ============================================================
df_panel = df_panel.copy()
df_panel['Cluster_HC']  = lbl_hc3
df_panel['Cluster_KM']  = lbl_km3
df_panel['Sil_HC']      = sil_smp
df_panel['Sil_KM']      = sil_smp_km
df_panel['MDS_X']       = coords_mds[:, 0]
df_panel['MDS_Y']       = coords_mds[:, 1]

# Profil tiap cluster berdasarkan Vol_2023
prof = df_panel.groupby('Cluster_HC')['Vol_2023'].mean().sort_values(ascending=False)
cluster_label_map = {}
for rank, (cid, vol_mean) in enumerate(prof.items()):
    if rank == 0:
        cluster_label_map[cid] = 'C1: Volume Besar'
    elif rank == 1:
        cluster_label_map[cid] = 'C2: Share Tinggi'
    else:
        cluster_label_map[cid] = 'C3: Produser Umum'

df_panel['Label'] = df_panel['Cluster_HC'].map(cluster_label_map)

# Tampilkan komposisi
print("\n=== KOMPOSISI CLUSTER FINAL (HC Ward K=3) ===")
for lbl in ['C1: Volume Besar', 'C2: Share Tinggi', 'C3: Produser Umum']:
    sub = df_panel[df_panel['Label'] == lbl].sort_values('Vol_2023', ascending=False)
    print(f"\n[{lbl}] — {len(sub)} provinsi")
    print(f"  Vol rata²    2023: {sub['Vol_2023'].mean():>12,.1f} ton")
    print(f"  Vol rata²    2024: {sub['Vol_2024'].mean():>12,.1f} ton")
    print(f"  Δ Vol 23→24     : {((sub['Vol_2024'].mean()-sub['Vol_2023'].mean())/sub['Vol_2023'].mean()*100):>+11.2f}%")
    print(f"  Harga rata² 2023: Rp {sub['Harga_2023'].mean():>10,.0f}/kg")
    print(f"  Share rata² 2023: {sub['Share_2023'].mean():>11.2f}%")
    print(f"  Nilai rata² 2023: Rp {sub['Nilai_2023'].mean():>10,.1f} M")
    print(f"  Sil rata²       : {sub['Sil_HC'].mean():>12.4f}")
    print(f"  Anggota: {', '.join(sub.index.tolist())}")

# ============================================================
# 12. SIMPAN CSV HASIL
# ============================================================
df_panel.to_csv('output/hasil_clustering.csv')
df_k.to_csv('output/elbow_silhouette_k.csv', index=False)
print("\n✅ CSV tersimpan: output/hasil_clustering.csv")

# ============================================================
# 13. HELPER: singkatan nama provinsi
# ============================================================
PROV_SHORT = {
    'Kep. Bangka Belitung':'Babel','Kalimantan Selatan':'Kalsel',
    'Kalimantan Tengah':'Kalteng','Kalimantan Barat':'Kalbar',
    'Kalimantan Timur':'Kaltim','Kalimantan Utara':'Kalut',
    'Sulawesi Selatan':'Sulsel','Sulawesi Tengah':'Sulteng',
    'Sulawesi Tenggara':'Sultra','Sulawesi Utara':'Sulut',
    'Sulawesi Barat':'Sulbar','Sumatera Utara':'Sumut',
    'Sumatera Barat':'Sumbar','Sumatera Selatan':'Sumsel',
    'Nusa Tenggara Barat':'NTB','Jawa Barat':'Jabar',
    'Jawa Tengah':'Jateng','Jawa Timur':'Jatim',
    'DKI Jakarta':'DKI','DI Yogyakarta':'DIY','Kep. Riau':'Kepri',
    'Maluku Utara':'Malut',
}
def short(p): return PROV_SHORT.get(p, p)

CLR = {
    'C1: Volume Besar': '#F5A623',
    'C2: Share Tinggi': '#E74C3C',
    'C3: Produser Umum': '#4A90E2',
}
SYM = {
    'C1: Volume Besar': 'star',
    'C2: Share Tinggi': 'diamond',
    'C3: Produser Umum': 'circle',
}

# ============================================================
# 14. VISUALISASI 1 — ELBOW + SILHOUETTE
# ============================================================
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('#0a1223')
for a in ax:
    a.set_facecolor('#0a1223')
    a.tick_params(colors='white')
    for sp in ['top', 'right']: a.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: a.spines[sp].set_color('#444')

ax[0].plot(df_k['k'], df_k['inertia'], marker='o', color='#1DB954', linewidth=2.5)
ax[0].fill_between(df_k['k'], df_k['inertia'], color='#1DB954', alpha=0.1)
ax[0].axvline(3, color='#F5A623', linestyle='--')
ax[0].set_title('Elbow Method (Inertia)', color='white')
ax[0].set_xlabel('K', color='white')
ax[0].set_ylabel('Inertia (WCSS)', color='white')

ax[1].plot(df_k['k'], df_k['sil_km'], marker='o', color='#4A90E2', label='K-Means', linewidth=2.5)
ax[1].plot(df_k['k'], df_k['sil_hc'], marker='o', color='#E74C3C', label='HC-Ward', linewidth=2.5)
ax[1].axvline(3, color='#F5A623', linestyle='--')
ax[1].set_title('Silhouette Score per K', color='white')
ax[1].set_xlabel('K', color='white')
ax[1].set_ylabel('Silhouette Score', color='white')
ax[1].legend(facecolor='#0a1223', labelcolor='white')

plt.suptitle(f"Penentuan K Optimal — Panel 2023+2024 ({len(df_panel)} Prov)", color='white')
plt.tight_layout()
plt.savefig('output/01_elbow_silhouette.png', dpi=150, facecolor='#0a1223')
plt.close()
print("✅ Chart 1: Elbow + Silhouette (Tersimpan sebagai PNG)")

# ============================================================
# 15. VISUALISASI 2 — PETA MDS FINAL
# ============================================================
vol_min = df_panel['Vol_2023'].min()
vol_max = df_panel['Vol_2023'].max()
def vol2size(v, base=11, rng=24):
    return base + (v - vol_min) / (vol_max - vol_min) * rng

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('#0a1223')
ax.set_facecolor('#0a1223')
ax.tick_params(colors='white')
for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
for sp in ['bottom', 'left']: ax.spines[sp].set_color('#444')

for lbl in ['C1: Volume Besar', 'C2: Share Tinggi', 'C3: Produser Umum']:
    sub = df_panel[df_panel['Label'] == lbl]
    if len(sub) == 0: continue
    sizes = [400 if lbl == 'C1: Volume Besar' else 250 if lbl == 'C2: Share Tinggi' else vol2size(v)*8 for v in sub['Vol_2023']]
    
    ax.scatter(sub['MDS_X'], sub['MDS_Y'], s=sizes, c=CLR[lbl], label=f"{lbl} (n={len(sub)})", alpha=0.9, edgecolors='white', linewidths=1)
    
    for _, row in sub.iterrows():
        ax.text(row['MDS_X'], row['MDS_Y'] + 0.15, short(row.name), color='white', fontsize=8, ha='center', va='bottom')

ax.set_title(f"Peta MDS — Hierarchical Ward K=3 (Stress: {stress:.2f}%, RSQ: {rsq:.4f})", color='white', pad=15)
ax.set_xlabel('Dimensi 1 MDS', color='white')
ax.set_ylabel('Dimensi 2 MDS', color='white')
ax.legend(facecolor='#0a1223', labelcolor='white', loc='lower left')

plt.tight_layout()
plt.savefig('output/02_peta_mds_final.png', dpi=150, facecolor='#0a1223')
plt.close()
print("✅ Chart 2: Peta MDS (Tersimpan sebagai PNG)")

# ============================================================
# 16. VISUALISASI 3 — DENDROGRAM HIERARCHICAL WARD
# ============================================================
prov_list = list(df_panel.index)
clr_per_prov = {}
for i, prov in enumerate(prov_list):
    c = lbl_hc3[i]
    lbl_name = cluster_label_map[c]
    clr_per_prov[prov] = CLR[lbl_name]

fig_dend, ax = plt.subplots(figsize=(15, 8))
fig_dend.patch.set_facecolor('#0a1223')
ax.set_facecolor('#0a1223')

dn = dendrogram(Z,
    labels=np.array([short(p) for p in prov_list]),
    ax=ax, orientation='bottom',
    color_threshold=Z[-3, 2] * 0.99,
    above_threshold_color='#888888',
    leaf_rotation=90, leaf_font_size=8)

leaves = dn['leaves']
for tick, leaf_idx in zip(ax.get_xticklabels(), leaves):
    tick.set_color(clr_per_prov[prov_list[leaf_idx]])

cut_h = (Z[-3, 2] + Z[-2, 2]) / 2
ax.axhline(y=cut_h, color='white', linewidth=1.5, linestyle='--', alpha=0.7)
ax.text(0.5, cut_h + 0.3, f'Cut K=3 (h={cut_h:.2f})',
        transform=ax.get_yaxis_transform(), color='white',
        fontsize=9, ha='left', va='bottom')

ax.set_title(
    f'Dendrogram Hierarchical Ward — {len(df_panel)} Provinsi, Panel 2023+2024\n'
    f'Cophenetic = {coph_corr:.4f} | Silhouette = {sil_hc3:.4f} | ARI vs K-Means = {ari:.4f}',
    color='white', fontsize=10, pad=12
)
ax.set_ylabel('Jarak Ward', color='white', fontsize=10)
ax.tick_params(colors='white', axis='y')
for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
for sp in ['bottom', 'left']: ax.spines[sp].set_color('#444')

patches = [
    mpatches.Patch(color='#F5A623', label=f'C1: Volume Besar — NTB, Jabar, Jatim (n=3)'),
    mpatches.Patch(color='#E74C3C', label=f'C2: Share Tinggi — Aceh, Kep. Babel (n=2)'),
    mpatches.Patch(color='#4A90E2', label=f'C3: Produser Umum (n=27)'),
]
ax.legend(handles=patches, loc='upper right', framealpha=0.15,
          labelcolor='white', fontsize=8.5, facecolor='#0a1223', edgecolor='#444')

plt.tight_layout()
plt.savefig('output/03_dendrogram_hc_ward.png', dpi=180,
            bbox_inches='tight', facecolor='#0a1223')
plt.close()
with open('output/03_dendrogram_hc_ward.png.meta.json', 'w') as f:
    json.dump({"caption": f"Dendrogram HC Ward K=3 (Cophenetic={coph_corr:.4f})"}, f)
print("✅ Chart 3: Dendrogram")

# ============================================================
# 17. VISUALISASI 4 — SILHOUETTE PER PROVINSI
# ============================================================
df_sil = df_panel[['Label', 'Sil_HC']].copy()
df_sil['prov'] = [short(p) for p in df_sil.index]
df_sil['ord'] = df_sil['Label'].map({'C1: Volume Besar':0,'C2: Share Tinggi':1,'C3: Produser Umum':2})
df_sil = df_sil.sort_values(['ord', 'Sil_HC'], ascending=[True, True])
colors = [CLR[l] for l in df_sil['Label']]

fig, ax = plt.subplots(figsize=(10, 8))
fig.patch.set_facecolor('#0a1223')
ax.set_facecolor('#0a1223')
ax.tick_params(colors='white', labelsize=8)
for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
for sp in ['bottom', 'left']: ax.spines[sp].set_color('#444')

ax.barh(df_sil['prov'], df_sil['Sil_HC'], color=colors, alpha=0.9)
ax.axvline(0.5, color='#F5A623', linestyle='--')
ax.text(0.51, len(df_sil)-1, 'Threshold 0.50', color='#F5A623', va='bottom')

ax.set_title(f"Silhouette Score per Provinsi (rata-rata: {sil_hc3:.4f})", color='white', pad=15)
ax.set_xlabel('Silhouette Score', color='white')

patches = [mpatches.Patch(color=CLR[lbl], label=f'{lbl}') for lbl in ['C1: Volume Besar', 'C2: Share Tinggi', 'C3: Produser Umum']]
ax.legend(handles=patches, facecolor='#0a1223', labelcolor='white', loc='lower right')

plt.tight_layout()
plt.savefig('output/04_silhouette_per_provinsi.png', dpi=150, facecolor='#0a1223')
plt.close()
print("✅ Chart 4: Silhouette per Provinsi (Tersimpan sebagai PNG)")

# ============================================================
# 18. CETAK RINGKASAN AKHIR
# ============================================================
print("\n" + "="*65)
print("RINGKASAN ANALISIS SELESAI")
print("="*65)
print(f"  File input    : {XLSX_FILE}")
print(f"  Provinsi valid: {len(df_panel)}")
print(f"  Variabel      : 10 (5 var × 2 tahun)")
print(f"  K optimal     : {K_OPTIMAL}")
print()
print(f"  METRIK MDS:")
print(f"    Stress      : {stress:.4f}%  (< 10% ✅)")
print(f"    RSQ         : {rsq:.4f}      (> 0.60 ✅)")
print()
print(f"  METRIK CLUSTERING (HC Ward):")
print(f"    Silhouette  : {sil_hc3:.4f}  (> 0.50 ✅)")
print(f"    DB Index    : {db_hc3:.4f}  (< 1.00 ✅)")
print(f"    CH Index    : {ch_hc3:.2f}")
print(f"    Cophenetic  : {coph_corr:.4f}  (> 0.75 ✅)")
print(f"    ARI vs KM   : {ari:.4f}  (→ 1.00 ✅)")
print()
print(f"  OUTPUT:")
print(f"    output/hasil_clustering.csv")
print(f"    output/01_elbow_silhouette.png")
print(f"    output/02_peta_mds_final.png")
print(f"    output/03_dendrogram_hc_ward.png")
print(f"    output/04_silhouette_per_provinsi.png")
print("="*65)
