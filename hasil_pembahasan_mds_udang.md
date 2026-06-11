# Hasil dan Pembahasan: Pemetaan Provinsi Berdasarkan Produksi Udang Budidaya Menggunakan Multidimensional Scaling dan Hierarchical Clustering

## 4. Hasil dan Pembahasan

### 4.1 Deskripsi Data

Data yang digunakan dalam penelitian ini adalah data produksi udang budidaya dari Badan Pusat Statistik (BPS) tahun 2023 dan 2024 yang mencakup 32 provinsi di Indonesia. Lima variabel digunakan dalam analisis, yaitu volume produksi (ton), nilai produksi (juta rupiah), harga implisit (Rp/kg), share udang terhadap total produksi budidaya (%), dan indeks kontribusi premium (HargaShare). Dengan menggabungkan data dua tahun secara panel, total dimensi analisis menjadi 10 variabel. Sebelum analisis dilakukan, seluruh variabel distandarisasi menggunakan *RobustScaler* untuk meminimalkan pengaruh pencilan (*outlier*).

Secara agregat, total produksi udang budidaya dari 32 provinsi pada tahun 2023 mencapai **941.637 ton** dengan total nilai produksi sebesar **Rp 62.700,7 miliar**. Rata-rata harga implisit nasional adalah Rp 68.449/kg dan rata-rata share udang terhadap total produksi budidaya sebesar 12,83%. Sebaran antar provinsi sangat heterogen: volume tertinggi dipegang oleh NTB (194.648 ton) dan terendah oleh Jambi (19 ton), sehingga normalisasi data menjadi syarat mutlak sebelum analisis jarak dilakukan.

### 4.2 Hasil Multidimensional Scaling (MDS)

Analisis Multidimensional Scaling dilakukan menggunakan matriks jarak Euclidean dari 10 variabel yang telah distandarisasi, kemudian direduksi ke dalam ruang dua dimensi. Goodness-of-fit MDS dievaluasi menggunakan dua metrik utama, yaitu Stress Kruskal dan koefisien determinasi RSQ.

**Tabel 1. Metrik Goodness-of-Fit MDS**

| Metrik | Nilai | Threshold | Interpretasi |
|---|---|---|---|
| Stress Kruskal | **7,19%** | < 10% (Baik) | Baik [cite:129] |
| RSQ (R²) | **0,9749** | > 0,60 (Baik) | Sangat Baik [cite:17] |

Nilai Stress sebesar 7,19% termasuk dalam kategori *"Baik"* menurut kriteria Kruskal (1964), yaitu pada rentang 5–10% [cite:129]. Nilai RSQ sebesar 0,9749 menunjukkan bahwa 97,49% variasi jarak asli antarprovinsi dalam ruang 10 dimensi berhasil direpresentasikan dalam peta dua dimensi. Hasil ini mengindikasikan bahwa konfigurasi MDS dua dimensi mampu mempertahankan struktur kedekatan antarprovinsi secara memuaskan [cite:17].

### 4.3 Penentuan Jumlah Cluster Optimal

Penentuan jumlah cluster (*K*) dilakukan menggunakan kombinasi *Elbow Method* berdasarkan inertia (WCSS) dan analisis *Silhouette Score* pada koordinat MDS untuk nilai *K* = 2 hingga 7. Hasil menunjukkan bahwa *K* = 3 menghasilkan Silhouette Score tertinggi sebesar **0,6337** untuk *K-Means* dan **0,6171** untuk *Hierarchical Ward* [cite:132].

**Tabel 2. Perbandingan Silhouette Score per Nilai K (Koordinat MDS Panel)**

| K | Sil K-Means | Sil H-Ward | DB K-Means | Distribusi Cluster |
|---|---|---|---|---|
| 2 | 0,5623 | 0,5709 | 1,0751 | [27, 5] |
| **3** | **0,6337** | **0,6171** | **0,5152** | **[27, 3, 2]** |
| 4 | 0,3756 | 0,2841 | 0,7787 | [15, 12, 3, 2] |
| 5 | 0,3588 | 0,2892 | 0,6631 | [15, 12, 2, 2, 1] |

Penurunan tajam Silhouette Score dari *K* = 3 ke *K* = 4 (dari 0,6337 menjadi 0,3756) mengkonfirmasi bahwa *K* = 3 merupakan jumlah cluster yang paling optimal dan bermakna secara statistik [cite:177]. Selain itu, analisis *Elbow Method* menunjukkan penurunan inertia paling signifikan terjadi pada transisi *K* = 2 ke *K* = 3, setelah itu kurva mulai mendatar.

### 4.4 Hasil Clustering Hierarchical Ward

Clustering dilakukan menggunakan metode *Hierarchical Agglomerative Clustering* dengan *linkage Ward* pada data asli 10 variabel (panel 2023–2024). Kualitas dendrogram divalidasi dengan *Cophenetic Correlation Coefficient* (CCC) sebesar **0,8427**, yang termasuk kategori sangat baik (> 0,75) dan menunjukkan bahwa struktur hierarki dendrogram merepresentasikan data dengan baik [cite:133].

**Tabel 3. Metrik Evaluasi Clustering Hierarchical Ward K=3**

| Metrik | Nilai | Threshold | Status |
|---|---|---|---|
| Silhouette Score | **0,6171** | > 0,50 | ✅ Baik [cite:132] |
| Davies-Bouldin Index | **0,5424** | < 1,00 | ✅ Baik [cite:132] |
| Calinski-Harabasz Index | **31,11** | Lebih besar lebih baik | ✅ |
| Cophenetic Correlation | **0,8427** | > 0,75 | ✅ Sangat Baik [cite:133] |
| ARI vs K-Means | **1,0000** | → 1,00 | ✅ Identik [cite:132] |

Nilai *Adjusted Rand Index* (ARI) antara hasil *Hierarchical Ward* dan *K-Means* sebesar **1,0000** membuktikan bahwa kedua algoritma menghasilkan partisi yang identik — setiap provinsi dikelompokkan ke dalam cluster yang sama oleh kedua metode. Hal ini mengindikasikan bahwa struktur tiga cluster yang terbentuk sangat kuat dan tidak sensitif terhadap pemilihan algoritma [cite:135].

### 4.5 Profil dan Interpretasi Tiga Cluster

Berdasarkan hasil *Hierarchical Clustering Ward* dengan *K* = 3, terbentuk tiga cluster dengan karakteristik yang berbeda secara substansial.

**Tabel 4. Profil Tiga Cluster Provinsi (Data Panel 2023–2024)**

| Variabel | C1: Volume Besar (n=3) | C2: Share Tinggi (n=2) | C3: Produser Umum (n=27) |
|---|---|---|---|
| Anggota | NTB, Jawa Barat, Jawa Timur | Aceh, Kep. Bangka Belitung | 27 provinsi lainnya |
| Vol rata² 2023 (ton) | **148.526** | 27.150 | 16.362 |
| Vol rata² 2024 (ton) | 148.100 | 27.103 | **17.035** |
| Δ Volume 23→24 | −0,29% | −0,17% | **+4,12%** |
| Harga rata² 2023 (Rp/kg) | 63.550 | **70.290** | 68.857 |
| Share rata² 2023 (%) | 13,73% | **63,39%** | 8,98% |
| Nilai rata² 2023 (Rp M) | **9.609,3** | 1.947,0 | 1.110,3 |
| Silhouette rata² | 0,5111 | 0,3115 | **0,6515** |

#### 4.5.1 Cluster 1 — Provinsi dengan Volume Produksi Besar

Cluster 1 terdiri dari tiga provinsi, yaitu **NTB, Jawa Barat, dan Jawa Timur**, dengan volume rata-rata sebesar 148.526 ton pada tahun 2023. NTB menjadi produser terbesar dengan volume 194.648 ton (2023), diikuti Jawa Barat (132.599 ton) dan Jawa Timur (118.330 ton). Ketiganya menghasilkan nilai produksi rata-rata sebesar Rp 9.609,3 miliar per provinsi — jauh melampaui dua cluster lainnya. Meskipun volume cenderung stabil antara 2023 dan 2024 (perubahan −0,29%), nilai produksi justru sedikit meningkat menjadi Rp 9.683,7 miliar pada 2024, mengindikasikan peningkatan efisiensi nilai meskipun volume stagnan.

Ketiga provinsi ini terposisikan jauh dari kelompok lain dalam peta MDS, mencerminkan jarak Euclidean yang besar dalam ruang multidimensi. Share udang terhadap total produksi budidaya relatif moderat (rata-rata 13,73%), menunjukkan bahwa ketiga provinsi ini juga memiliki diversifikasi komoditas budidaya yang tinggi di luar udang.

#### 4.5.2 Cluster 2 — Provinsi dengan Share Udang Tinggi

Cluster 2 terdiri dari dua provinsi, yaitu **Aceh dan Kepulauan Bangka Belitung**. Karakteristik pembeda cluster ini bukan volume produksi absolut, melainkan dominasi udang terhadap total produksi budidaya. Kepulauan Bangka Belitung memiliki share sebesar **82,28%** — artinya udang menyumbang lebih dari empat per lima total volume budidaya provinsi tersebut. Aceh memiliki share sebesar **44,49%**, jauh di atas rata-rata nasional 12,83%. Kedua nilai ini merupakan dua tertinggi di antara seluruh 32 provinsi.

Pemisahan cluster ini murni merupakan hasil matematis dari algoritma *Hierarchical Ward*: jarak Euclidean dari 10 variabel menempatkan kedua provinsi ini lebih jauh dari cluster manapun dibandingkan satu sama lain. Harga implisit kedua provinsi (Rp 72.396/kg untuk Aceh dan Rp 68.183/kg untuk Kep. Babel) juga relatif lebih tinggi dibandingkan C1, mengindikasikan orientasi pasar udang dengan nilai jual kompetitif. Nilai Silhouette cluster ini (0,3115) lebih rendah dari dua cluster lainnya, yang mencerminkan kemiripan relatif antara kedua provinsi dengan C3 pada beberapa variabel non-share.

#### 4.5.3 Cluster 3 — Provinsi Produser Umum

Cluster 3 adalah kelompok terbesar, mencakup **27 provinsi** yang tersebar di seluruh wilayah Indonesia, meliputi Sulawesi Selatan, Lampung, Aceh [catatan: lihat C2], Sulawesi Tenggara, Jawa Tengah, Sumatera Utara, Sumatera Selatan, Kalimantan Timur, dan provinsi-provinsi lainnya. Rata-rata volume produksi 2023 sebesar 16.362 ton dengan share 8,98% mengindikasikan bahwa udang bukan komoditas dominan di sebagian besar provinsi kelompok ini.

Meskipun demikian, cluster ini mencatat pertumbuhan volume tertinggi antarcluster, yaitu **+4,12%** dari 2023 ke 2024 (dari 16.362 ton menjadi 17.035 ton per provinsi), serta kenaikan harga rata-rata dari Rp 68.857/kg menjadi Rp 70.376/kg. Nilai Silhouette rata-rata cluster ini adalah 0,6515 — tertinggi di antara tiga cluster — menunjukkan kohesivitas internal yang baik. Dinamika pertumbuhan positif pada cluster ini membuka peluang intervensi kebijakan untuk mendorong peningkatan kapasitas produksi di 27 provinsi tersebut.

### 4.6 Validasi dengan K-Means pada Koordinat MDS

Sebagai validasi silang, *K-Means Clustering* juga diterapkan pada koordinat MDS dua dimensi (Skenario D). Hasilnya identik sempurna dengan *Hierarchical Ward* (ARI = 1,0000), dengan Silhouette Score K-Means sebesar 0,6337, Davies-Bouldin Index 0,5152, dan Calinski-Harabasz Index 34,07. Konsistensi hasil antara dua algoritma yang berbeda secara fundamental — *K-Means* berbasis centroid dan *Hierarchical Ward* berbasis jarak hierarkis — memberikan keyakinan tinggi bahwa struktur tiga cluster yang terbentuk merupakan representasi genuine dari pola dalam data, bukan artefak algoritmik [cite:195].

**Tabel 5. Perbandingan Metrik K-Means vs Hierarchical Ward (K=3)**

| Metrik | K-Means (Skenario D) | Hierarchical Ward | Threshold |
|---|---|---|---|
| Silhouette | **0,6337** | 0,6171 | > 0,50 ✅ |
| Davies-Bouldin | **0,5152** | 0,5424 | < 1,00 ✅ |
| Calinski-Harabasz | **34,07** | 31,11 | Lebih besar ✅ |
| ARI (satu sama lain) | **1,0000** | 1,0000 | → 1,00 ✅ |
| Cophenetic | — | **0,8427** | > 0,75 ✅ |

### 4.7 Peta MDS dan Interpretasi Spasial

Peta MDS dua dimensi memvisualisasikan jarak relatif antarprovinsi berdasarkan kesamaan profil 10 variabel. Tiga kelompok terlihat terpisah jelas di peta: C1 (Volume Besar) berada di kuadran kanan atas, C2 (Share Tinggi) di kuadran kiri atas, dan C3 (Produser Umum) tersebar di bagian tengah-bawah. Jarak antara C1 dan C2 yang besar di peta mencerminkan perbedaan mendasar: C1 didominasi oleh volume absolut yang sangat tinggi, sementara C2 dicirikan oleh dominasi relatif udang dalam struktur budidaya provinsi.

Interpretasi dimensi MDS dalam penelitian ini bersifat deskriptif — sumbu MDS tidak memiliki makna tunggal yang dapat didefinisikan secara langsung, melainkan merupakan representasi linier terbaik dari kompleksitas jarak multidimensi. Penempatan provinsi yang berdekatan di peta MDS mengindikasikan kemiripan profil produksi udang yang tinggi, sedangkan provinsi yang berjauhan menunjukkan perbedaan struktural yang signifikan [cite:198].

### 4.8 Implikasi Kebijakan

Temuan penelitian ini memiliki beberapa implikasi kebijakan yang relevan bagi pengembangan sektor perikanan budidaya udang di Indonesia.

- **Cluster 1 (Volume Besar — NTB, Jabar, Jatim):** Strategi kebijakan difokuskan pada peningkatan efisiensi dan kualitas produksi mengingat volume sudah besar namun pertumbuhan stagnan (−0,29%). Intervensi berupa sertifikasi produk, peningkatan teknologi pascapanen, dan akses pasar ekspor perlu diprioritaskan untuk meningkatkan nilai tambah tanpa harus menambah volume secara signifikan.

- **Cluster 2 (Share Tinggi — Aceh, Kep. Babel):** Kedua provinsi ini memiliki ketergantungan tinggi pada udang sebagai komoditas budidaya utama. Kebijakan yang tepat adalah diversifikasi komoditas untuk mengurangi risiko, sekaligus penguatan rantai pasok udang mengingat harga implisit yang kompetitif (Rp 70.290/kg rata-rata).

- **Cluster 3 (Produser Umum — 27 provinsi):** Kelompok ini menunjukkan potensi pertumbuhan paling menjanjikan (+4,12% volume, 2023→2024). Dukungan berupa penyediaan benih berkualitas, pelatihan teknis budidaya udang intensif, dan akses permodalan dapat mendorong transisi provinsi-provinsi dalam cluster ini ke tingkat produksi yang lebih tinggi.

