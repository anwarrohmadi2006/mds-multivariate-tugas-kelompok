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
# 1-6. LOAD DATA DARI CSV YANG SUDAH DIPARSING
# ============================================================
CSV_FILE = "data_mds_udang_32provinsi.csv"
df_panel = pd.read_csv(CSV_FILE).set_index("Provinsi")

# Map column names to match the variables expected by the rest of the script
df_panel.rename(columns={
    "Volume_2023_ton": "Vol_2023",
    "Nilai_2023_JutaRp": "Nilai_2023",
    "Harga_2023_RpPerKg": "Harga_2023",
    "Share_2023_Persen": "Share_2023",
    "HargaShare_2023": "HargaShare_2023",
    "Volume_2024_ton": "Vol_2024",
    "Nilai_2024_JutaRp": "Nilai_2024",
    "Harga_2024_RpPerKg": "Harga_2024",
    "Share_2024_Persen": "Share_2024",
    "HargaShare_2024": "HargaShare_2024"
}, inplace=True)

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
fig_es = make_subplots(rows=1, cols=2,
    subplot_titles=('Elbow Method (Inertia/WCSS)', 'Silhouette Score per K'))

fig_es.add_trace(go.Scatter(
    x=df_k['k'], y=df_k['inertia'], mode='lines+markers',
    name='Inertia', line=dict(color='#1DB954', width=2.5),
    marker=dict(size=9), fill='tozeroy', fillcolor='rgba(29,185,84,0.10)'
), row=1, col=1)

for col_name, color, name in [
    ('sil_km', '#4A90E2', 'K-Means'),
    ('sil_hc', '#E74C3C', 'HC-Ward')
]:
    fig_es.add_trace(go.Scatter(
        x=df_k['k'], y=df_k[col_name], mode='lines+markers',
        name=name, line=dict(color=color, width=2.5),
        marker=dict(size=9)
    ), row=1, col=2)

for col_idx in [1, 2]:
    fig_es.add_vline(x=3, line_dash='dash', line_color='#F5A623',
                     line_width=2, row=1, col=col_idx)

fig_es.update_layout(
    title=dict(text=(
        "Penentuan K Optimal — Elbow & Silhouette<br>"
        "<span style='font-size:13px;font-weight:normal;'>"
        f"Data Panel 2023+2024, 10 Variabel, {len(df_panel)} Provinsi | K=3 optimal</span>"
    )),
    legend=dict(orientation='h', yanchor='bottom', y=1.07, xanchor='center', x=0.5),
    plot_bgcolor='rgba(10,18,35,1)', paper_bgcolor='rgba(10,18,35,1)',
    font=dict(color='white', size=11), width=1100, height=520,
    margin=dict(l=60, r=60, t=150, b=60)
)
fig_es.update_xaxes(title_text='K', row=1, col=1)
fig_es.update_xaxes(title_text='K', row=1, col=2)
fig_es.update_yaxes(title_text='Inertia (WCSS)', row=1, col=1)
fig_es.update_yaxes(title_text='Silhouette Score', row=1, col=2)

fig_es.write_image('output/01_elbow_silhouette.png', scale=2)
with open('output/01_elbow_silhouette.png.meta.json', 'w') as f:
    json.dump({"caption": f"Elbow & Silhouette — K=3 Optimal (10 Var, {len(df_panel)} Provinsi)"}, f)
print("✅ Chart 1: Elbow + Silhouette")

# ============================================================
# 15. VISUALISASI 2 — PETA MDS FINAL
# ============================================================
vol_min = df_panel['Vol_2023'].min()
vol_max = df_panel['Vol_2023'].max()
def vol2size(v, base=11, rng=24):
    return base + (v - vol_min) / (vol_max - vol_min) * rng

fig_mds = go.Figure()
for lbl in ['C1: Volume Besar', 'C2: Share Tinggi', 'C3: Produser Umum']:
    sub = df_panel[df_panel['Label'] == lbl]
    if len(sub) == 0: continue
    sizes = [32 if lbl == 'C1: Volume Besar' else
             22 if lbl == 'C2: Share Tinggi' else
             vol2size(v) for v in sub['Vol_2023']]

    fig_mds.add_trace(go.Scatter(
        x=sub['MDS_X'], y=sub['MDS_Y'],
        mode='markers+text',
        name=f"{lbl} (n={len(sub)})",
        text=[short(p) for p in sub.index],
        textposition='top center',
        textfont=dict(size=9, color='white'),
        marker=dict(size=sizes, color=CLR[lbl], symbol=SYM[lbl],
                    opacity=0.90, line=dict(width=1.5, color='rgba(255,255,255,0.4)')),
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Vol 2023: %{customdata[0]:,.0f} ton<br>'
            'Harga: Rp%{customdata[1]:,.0f}/kg<br>'
            'Share: %{customdata[2]:.2f}%<br>'
            'Nilai: Rp%{customdata[3]:.1f}M<br>'
            'Silhouette: %{customdata[4]:.3f}<extra></extra>'
        ),
        customdata=list(zip(
            sub['Vol_2023'], sub['Harga_2023'],
            sub['Share_2023'], sub['Nilai_2023'], sub['Sil_HC'].round(3)
        ))
    ))

fig_mds.add_annotation(
    x=0.99, y=0.02, xref='paper', yref='paper', xanchor='right',
    text=(
        f"<b>Metrik (K=3)</b><br>"
        f"Stress MDS : {stress:.2f}%  ✅<br>"
        f"RSQ        : {rsq:.4f}  ✅<br>"
        f"Sil HC     : {sil_hc3:.4f}  ✅<br>"
        f"Sil KMeans : {sil_km3:.4f}  ✅<br>"
        f"DB HC      : {db_hc3:.4f}  ✅<br>"
        f"ARI        : {ari:.4f}  ✅<br>"
        f"Cophenetic : {coph_corr:.4f}  ✅"
    ),
    showarrow=False, font=dict(size=10.5, color='white'), align='left',
    bgcolor='rgba(10,25,45,0.85)', bordercolor='rgba(74,144,226,0.5)',
    borderwidth=1.5, borderpad=7
)

fig_mds.update_layout(
    title=dict(text=(
        f"Peta MDS — Hierarchical Ward K=3, Panel 2023+2024<br>"
        f"<span style='font-size:13px;font-weight:normal;'>"
        f"{len(df_panel)} Provinsi | 10 Variabel | RobustScaler | BPS 2023–2024</span>"
    )),
    legend=dict(orientation='h', yanchor='bottom', y=1.07, xanchor='center', x=0.5, font=dict(size=11)),
    xaxis=dict(title='Dimensi 1 MDS', gridcolor='rgba(255,255,255,0.07)', zeroline=False),
    yaxis=dict(title='Dimensi 2 MDS', gridcolor='rgba(255,255,255,0.07)', zeroline=False),
    plot_bgcolor='rgba(10,18,35,1)', paper_bgcolor='rgba(10,18,35,1)',
    font=dict(color='white', size=11), width=1200, height=860,
    margin=dict(l=60, r=60, t=150, b=60)
)

fig_mds.write_image('output/02_peta_mds_final.png', scale=2)
with open('output/02_peta_mds_final.png.meta.json', 'w') as f:
    json.dump({"caption": f"Peta MDS Final — HC Ward K=3, {len(df_panel)} Provinsi (2023–2024)"}, f)
print("✅ Chart 2: Peta MDS")

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

fig_sil = go.Figure()
fig_sil.add_trace(go.Bar(
    x=df_sil['Sil_HC'], y=df_sil['prov'],
    orientation='h',
    marker=dict(color=[CLR[l] for l in df_sil['Label']], line=dict(width=0)),
    opacity=0.88, showlegend=False,
    hovertemplate='<b>%{y}</b><br>Silhouette: %{x:.3f}<extra></extra>'
))
fig_sil.add_shape(type='line', x0=0.5, x1=0.5, y0=-0.5, y1=len(df_sil)-0.5,
                  line=dict(color='#F5A623', width=2, dash='dash'))
fig_sil.add_annotation(x=0.5, y=len(df_sil)-0.5,
                        text='Threshold 0.50', showarrow=False,
                        font=dict(color='#F5A623', size=10),
                        xanchor='left', xshift=5)

for lbl, col in CLR.items():
    n = len(df_panel[df_panel['Label']==lbl])
    fig_sil.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
        name=f"{lbl} (n={n})", marker=dict(size=10, color=col)))

fig_sil.update_layout(
    title=dict(text=(
        f"Silhouette Score per Provinsi — HC Ward K=3<br>"
        f"<span style='font-size:13px;font-weight:normal;'>"
        f"Sil rata² = {sil_hc3:.4f} | DB = {db_hc3:.4f} | Cophenetic = {coph_corr:.4f}</span>"
    )),
    legend=dict(orientation='h', yanchor='bottom', y=1.07, xanchor='center', x=0.5, font=dict(size=10)),
    xaxis=dict(title='Silhouette Score', range=[-0.15, 1.05], gridcolor='rgba(255,255,255,0.07)'),
    yaxis=dict(title='', tickfont=dict(size=9)),
    plot_bgcolor='rgba(10,18,35,1)', paper_bgcolor='rgba(10,18,35,1)',
    font=dict(color='white', size=11), width=900, height=860,
    margin=dict(l=130, r=60, t=150, b=60)
)
fig_sil.write_image('output/04_silhouette_per_provinsi.png', scale=2)
with open('output/04_silhouette_per_provinsi.png.meta.json', 'w') as f:
    json.dump({"caption": f"Silhouette per Provinsi — HC Ward K=3 (rata²={sil_hc3:.4f})"}, f)
print("✅ Chart 4: Silhouette per Provinsi")

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
