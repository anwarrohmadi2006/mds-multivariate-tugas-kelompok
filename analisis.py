"""
Analisis MDS + Clustering Udang
Data: Produksi Udang Budidaya BPS 2023-2024 (32 Provinsi)
End-to-End: XLSX -> MDS -> Hierarchical Clustering -> Visualisasi
"""

import numpy as np, pandas as pd, matplotlib.pyplot as plt, os, warnings
from sklearn.preprocessing import RobustScaler
from sklearn.manifold import MDS
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, silhouette_samples, davies_bouldin_score, pairwise_distances
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
warnings.filterwarnings('ignore')
os.makedirs('output', exist_ok=True)

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
    
    h23, h24 = (n23*1e6)/v23 if v23>0 else 0, (n24*1e6)/v24 if v24>0 else 0
    s23, s24 = (v23/t23)*100 if t23>0 else 0, (v24/t24)*100 if t24>0 else 0
    
    records.append({'Provinsi': p, 
        'Vol_2023': v23, 'Nilai_2023': n23, 'Harga_2023': h23, 'Share_2023': s23, 'HargaShare_2023': (h23*s23)/1000,
        'Vol_2024': v24, 'Nilai_2024': n24, 'Harga_2024': h24, 'Share_2024': s24, 'HargaShare_2024': (h24*s24)/1000
    })

df = pd.DataFrame(records).set_index('Provinsi')
df = df[(df.Vol_2023 > 0) & (df.Vol_2024 > 0)]

# 2. NORMALISASI & MDS
X = RobustScaler().fit_transform(df)
dist = pairwise_distances(X, metric='euclidean')
mds = MDS(2, dissimilarity='precomputed', random_state=42, n_init=50).fit_transform(dist)
stress = np.sqrt(MDS(2, dissimilarity='precomputed', random_state=42).fit(dist).stress_ / np.sum(dist**2)) * 100
rsq = pearsonr(dist[np.triu_indices(len(df),1)], pairwise_distances(mds)[np.triu_indices(len(df),1)])[0]**2

# 3. K-OPTIMAL (Elbow & Silhouette)
res = []
for k in range(2, 8):
    km = KMeans(k, random_state=42).fit_predict(mds)
    hc = AgglomerativeClustering(k, linkage='ward').fit_predict(X)
    res.append([k, KMeans(k, random_state=42).fit(mds).inertia_, silhouette_score(mds, km), silhouette_score(X, hc)])
df_k = pd.DataFrame(res, columns=['K', 'Inertia', 'Sil_KM', 'Sil_HC'])

# 4. CLUSTERING WARD K=3
Z = linkage(X, 'ward')
df['Cluster'] = fcluster(Z, 3, criterion='maxclust') - 1
lbl_map = {
    df.groupby('Cluster').Vol_2023.mean().sort_values(ascending=False).index[0]: 'C1: Volume Besar',
    df.groupby('Cluster').Vol_2023.mean().sort_values(ascending=False).index[1]: 'C2: Share Tinggi',
    df.groupby('Cluster').Vol_2023.mean().sort_values(ascending=False).index[2]: 'C3: Produser Umum'
}
df['Label'] = df['Cluster'].map(lbl_map)
df['MDS_X'], df['MDS_Y'], df['Sil'] = mds[:,0], mds[:,1], silhouette_samples(X, df['Cluster'])
df.to_csv('output/hasil_clustering.csv')

# 5. CETAK HASIL (Singkat)
print(f"✅ Data siap: {len(df)} Provinsi")
print(f"✅ MDS -> Stress: {stress:.2f}% (<10% Baik), RSQ: {rsq:.4f} (>0.6 Baik)")
print(f"✅ Ward K=3 -> Silhouette: {silhouette_score(X, df['Cluster']):.4f}, DB: {davies_bouldin_score(X, df['Cluster']):.4f}\n")
for l in sorted(df.Label.unique()):
    sub = df[df.Label == l]
    print(f" [{l}] {len(sub):2d} prov | Vol: {sub.Vol_2023.mean():>9,.0f} ton | Rp/kg: Rp {sub.Harga_2023.mean():>6,.0f} | Share: {sub.Share_2023.mean():>4.1f}%")

# 6. VISUALISASI
bg, txt = '#0a1223', 'white'
plt.style.use('dark_background')
colors = {'C1: Volume Besar':'#F5A623', 'C2: Share Tinggi':'#E74C3C', 'C3: Produser Umum':'#4A90E2'}

# Chart 1: K-Optimal
fig, ax = plt.subplots(1, 2, figsize=(12,4), facecolor=bg)
ax[0].plot(df_k.K, df_k.Inertia, 'o-', c='#1DB954'); ax[0].set_title("Elbow Method")
ax[1].plot(df_k.K, df_k.Sil_HC, 'o-', c='#E74C3C'); ax[1].set_title("Silhouette (HC-Ward)")
plt.savefig('output/01_elbow_silhouette.png', facecolor=bg); plt.close()

# Chart 2: MDS Scatter
fig, ax = plt.subplots(figsize=(10,6), facecolor=bg)
for l in df.Label.unique():
    sub = df[df.Label == l]
    ax.scatter(sub.MDS_X, sub.MDS_Y, s=np.clip(sub.Vol_2023/500, 100, 800), c=colors[l], label=l, alpha=0.8, edgecolor='w')
    for p, row in sub.iterrows(): ax.text(row.MDS_X, row.MDS_Y+0.1, p[:6], c=txt, fontsize=8, ha='center')
ax.legend(); ax.set_title(f"Peta MDS Udang (Stress {stress:.2f}%)")
plt.savefig('output/02_peta_mds_final.png', facecolor=bg); plt.close()

# Chart 3: Dendrogram
fig, ax = plt.subplots(figsize=(12,5), facecolor=bg)
dendrogram(Z, labels=df.index.tolist(), leaf_rotation=90, ax=ax)
ax.set_title("Dendrogram Hierarchical Ward K=3")
plt.savefig('output/03_dendrogram_hc_ward.png', facecolor=bg); plt.close()

# Chart 4: Silhouette Bar
fig, ax = plt.subplots(figsize=(10,8), facecolor=bg)
df_sil = df.sort_values(['Label','Sil'])
y = np.arange(len(df_sil))
ax.barh(y, df_sil.Sil, color=[colors[l] for l in df_sil.Label])
ax.set_yticks(y); ax.set_yticklabels(df_sil.index, fontsize=8)
ax.axvline(df_sil.Sil.mean(), color='w', ls='--')
ax.set_title(f"Silhouette Plot (Mean: {df_sil.Sil.mean():.4f})")
plt.savefig('output/04_silhouette_per_provinsi.png', facecolor=bg); plt.close()

print("\n✅ Chart 1-4 tersimpan di folder output/")
