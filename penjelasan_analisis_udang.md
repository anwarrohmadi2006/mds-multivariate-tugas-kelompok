# Penjelasan Analisis Clustering MDS Produksi Udang Budidaya (2023-2024)

Dokumen ini memuat hasil komprehensif dari proses **Multidimensional Scaling (MDS)** dan **Hierarchical Clustering** terhadap data produksi perikanan budidaya (fokus komoditas udang) dari 32 provinsi di Indonesia untuk tahun 2023 dan 2024.

---

## 1. Persiapan Data dan Variabel (Data Panel)

Data mentah bersumber dari BPS (Volume dan Nilai Produksi Perikanan Budidaya). Kami memfilter data menjadi **32 provinsi valid** yang memiliki pencatatan udang di kedua tahun tersebut.
Model MDS dan Clustering menggunakan **10 variabel panel** hasil ekstraksi:
1. `Volume 2023` & `Volume 2024` (Ton)
2. `Nilai 2023` & `Nilai 2024` (Juta Rupiah)
3. `Harga 2023` & `Harga 2024` (Rupiah/Kg, didapatkan dari Nilai / Volume)
4. `Share 2023` & `Share 2024` (% kontribusi volume udang terhadap total volume budidaya di provinsi tersebut)
5. `HargaShare 2023` & `HargaShare 2024` (Indeks premi harga × share)

Variabel-variabel tersebut dinormalisasi menggunakan **RobustScaler** agar tahan terhadap pencilan (outlier) seperti produksi super besar di provinsi tertentu (Jabar/Jatim).

---

## 2. Hasil Multidimensional Scaling (MDS)

Data 10 dimensi dari 32 provinsi diproyeksikan menjadi 2 dimensi (Peta Jarak) dengan algoritma Euclidean MDS. Hal ini dilakukan untuk memetakan jarak kedekatan struktur produksi antarprovinsi.

**Metrik Kualitas Pemetaan MDS:**
- **Stress Kruskal**: `7.1930%` (Tergolong Baik karena < 10%). Artinya proyeksi 2D kehilangan informasi jarak kurang dari 8% dibanding jarak asli 10 dimensi.
- **RSQ (R²)**: `0.9749` (Sangat Baik karena > 0.60). Artinya varians dalam data dapat terwakili 97.49% di ruang dimensi baru.

---

## 3. Penentuan K Optimal (Jumlah Cluster)

Evaluasi jumlah cluster (*Elbow Method* dan *Silhouette Score*) dilakukan untuk rentang $K = 2$ hingga $K = 7$:
- $K = 2$: Silhouette 0.5709, DB Index 1.07
- $K = 3$: Silhouette **0.6171**, DB Index **0.5144** (Terbaik)
- $K = 4$: Silhouette 0.2841, DB Index 0.7786

Berdasarkan puncak Silhouette Score dan nilai *Davies-Bouldin (DB)* Index terendah, **K=3** ditetapkan sebagai jumlah cluster optimal. 
Kami menggunakan algoritma **Hierarchical Clustering (Ward linkage)** yang lebih stabil dibanding K-Means untuk dataset dengan ukuran kecil (32 observasi).

**Metrik Evaluasi Hierarchical Ward K=3:**
- **Silhouette Score**: `0.6171` (> 0.50, pemisahan antar cluster sangat baik dan jelas).
- **Davies-Bouldin Index**: `0.5424` (< 1.00, kepadatan cluster tergolong baik).
- **Cophenetic Correlation**: `0.8427` (> 0.75, dendrogram Ward merepresentasikan jarak Euclidean asli dengan sangat akurat).

---

## 4. Profil dan Komposisi Cluster

Berikut adalah penjabaran profil dari 3 cluster yang terbentuk beserta anggotanya:

### [C1] Cluster Volume Besar (3 Provinsi)
Karakteristik: Sentra produksi utama nasional secara nominal dengan rata-rata volume sangat fantastis, namun secara *share* komoditas bukan mayoritas (banyak komoditas lain).
- **Rata-rata Volume (2023)**: 148.525 ton
- **Rata-rata Share (2023)**: 13.74%
- **Rata-rata Nilai (2023)**: Rp 9,6 Triliun
- **Anggota**: Nusa Tenggara Barat, Jawa Barat, Jawa Timur.

### [C2] Cluster Share Tinggi / Sentra Spesialis Udang (2 Provinsi)
Karakteristik: Provinsi yang budidaya perikanannya sangat difokuskan/didominasi oleh komoditas udang. Volume medium-besar, namun persentase share udang-nya sangat dominan (>60% dari total perikanan budidaya mereka).
- **Rata-rata Volume (2023)**: 27.150 ton
- **Rata-rata Share (2023)**: 63.38% *(Sangat Tinggi)*
- **Rata-rata Nilai (2023)**: Rp 1,94 Triliun
- **Harga Rata-rata**: Rp 70.290 / kg *(Harga cenderung premium)*
- **Anggota**: Aceh, Kep. Bangka Belitung.

### [C3] Cluster Produser Umum (27 Provinsi)
Karakteristik: Provinsi mayoritas dengan volume produksi skala menengah hingga kecil, dan share udang yang tidak mendominasi total produksi akuakultur mereka (rata-rata share ~9%).
- **Rata-rata Volume (2023)**: 16.361 ton
- **Rata-rata Share (2023)**: 8.98%
- **Rata-rata Nilai (2023)**: Rp 1,11 Triliun
- **Anggota**: Sulawesi Selatan, Lampung, Sulawesi Tenggara, Jawa Tengah, Sumatera Utara, Sumatera Selatan, Kalimantan Timur, dan 20 provinsi lainnya.

---

## 5. Kesimpulan
1. **Validitas Model**: Model memiliki tingkat validitas yang sangat baik terbukti dari Stress MDS (7.19%) dan Silhouette Score Clustering (0.6171).
2. **Polarisasi:** Budidaya Udang terpolarisasi pada dua jenis sentra produksi: **Sentra Volume Agregat** (C1 - Jabar, Jatim, NTB) yang menghasilkan udang masif bersama komoditas lain, dan **Sentra Spesialis** (C2 - Aceh, Babel) yang perekonomian akuakulturnya bergantung sangat besar pada komoditas udang (premium & dominan).
3. Hasil label dari setiap provinsi beserta metrik individunya telah disimpan di file `output/hasil_clustering.csv`.
