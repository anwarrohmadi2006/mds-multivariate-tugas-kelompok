# Analisis Pemetaan Potensi Ekonomi Budidaya Udang Nasional

Repositori ini memuat landasan kode dan dokumentasi untuk riset **Pemetaan Potensi Ekonomi Budidaya Udang Nasional Berbasis *Multidimensional Scaling* (MDS) dan *Spectral Clustering***. Penelitian ini dikembangkan dengan kerangka kerja CRISP-DM (*Cross-Industry Standard Process for Data Mining*) guna memberikan landasan strategis (*evidence-based*) bagi ekspansi distribusi teknologi akuakultur JALA Tech.

## 📖 Latar Belakang
Indonesia merupakan salah satu produsen akuakultur terbesar di dunia. Namun, distribusi produksi dan pemanfaatan teknologi di sektor budidaya udang masih sangat terkonsentrasi di beberapa wilayah sentra seperti Jawa Timur, Jawa Barat, dan Nusa Tenggara Barat. Ketimpangan ini menuntut adanya sebuah model analisis spasial yang mampu mengelompokkan wilayah berdasarkan tingkat kemiripan karakteristik ekonominya secara utuh, sehingga perumusan kebijakan distribusi teknologi tidak lagi menggunakan pendekatan pukul rata (*one-size-fits-all*).

## 🔬 Metodologi (CRISP-DM)
Proses analisis pada repositori ini dijalankan secara komprehensif melalui enam tahapan standar industri:
1. **Business Understanding**: Memetakan potensi ekonomi udang per provinsi untuk kebijakan ekspansi presisi JALA Tech.
2. **Data Understanding**: Ekstraksi dan evaluasi data sekunder BPS 2023–2024 terkait parameter Volume (Ton), Nilai (Juta Rupiah), dan Harga (Rupiah/kg).
3. **Data Preparation**: Pembersihan data, penghapusan anomali (*missing values*), serta normalisasi rentang menggunakan algoritma `RobustScaler`.
4. **Modeling**: Reduksi kompleksitas dimensi multivariat dengan *Multidimensional Scaling* (MDS) dan penetapan partisi wilayah menggunakan *Spectral Clustering* berbasis jarak *Euclidean*.
5. **Evaluation**: Penentuan presisi jumlah klaster (K) dengan optimalisasi *Silhouette Score*, serta pengujian keandalan representasi spasial menggunakan metrik *Stress* dan *R-Squared* (RSQ).
6. **Deployment**: Pengejawantahan temuan menjadi kebijakan terapan, pencetakan peta sebaran wilayah, dan perumusan dokumen cetak biru (*blueprint*) bisnis JALA.

![Diagram Alir CRISP-DM](output/00_flowchart_crispdm.png)

## 🗂 Struktur Repositori
- `analisis.py` — Skrip komputasi utama berisikan lintasan algoritma mulai dari normalisasi matriks data mentah hingga perenderan grafik *output*.
- `penjelasan_analisis_udang.md` — Laporan komprehensif berformat Markdown mengenai latar belakang fenomena, argumentasi metodologi, dan konklusi kebijakan.
- `to_docx.py` — Skrip utilitas untuk merender laporan dari basis Markdown secara utuh menjadi dokumen *Microsoft Word* (*Native Table & Formatting*).
- `create_flowchart.py` — Skrip pembangun ilustrasi hierarki diagram alir proses CRISP-DM dengan basis *library* `matplotlib`.
- `output/` — Direktori sentral yang memuat artefak visual hasil eksekusi algoritma, di antaranya:
  - `00_flowchart_crispdm.png`: Visualisasi tahapan analisis secara struktural.
  - `01_elbow_silhouette.png`: Kurva validasi nilai *Silhouette Score* untuk penentuan titik K-optimal.
  - `02_peta_mds_final.png`: Representasi titik-titik spasial dari 33 provinsi hasil reduksi MDS pada K=4.
  - `03_silhouette_per_provinsi.png`: Diagram palang (bar) untuk mengukur tingkat kohesi klasifikasi setiap provinsi.
  - `hasil_clustering.csv`: Basis data agregasi klaster beserta himpunan metrik finansialnya.

## 🚀 Cara Menjalankan Modul (How to Run)
Pastikan sistem Anda telah terinstal lingkungan Python versi 3.x dan modul komputasi saintifik bawaan. Untuk instalasi ketergantungan paket (*dependencies*), silakan jalankan perintah ini di dalam terminal:
```bash
pip install numpy pandas matplotlib scikit-learn scipy python-docx
```

Setelah konfigurasi utilitas sistem selesai, Anda dapat memicu eksekusi pemodelan utama dengan perintah:
```bash
python analisis.py
```
Seluruh perputaran algoritma akan memakan waktu kurang dari sepuluh detik, dan hasil visualisasi grafik spasial serta metrik matematis akan otomatis disimpan ke dalam folder `output/`.

## 📌 Ringkasan Temuan Algoritma
Melalui ketajaman pendekatan *Spectral Clustering*, peta dominasi ekonomi udang nasional sukses divalidasi secara matematis ke dalam 4 klaster spasial:
- **[C1] Sentra Produksi Raksasa** (3 Provinsi): Dominasi absolut atas suplai volume panen dan putaran kas nasional.
- **[C2] Wilayah Berskala Besar** (8 Provinsi): Area krusial yang tengah melalui masa transisi masif menuju fase budidaya padat modal.
- **[C3] Wilayah Menengah** (6 Provinsi): Menyuplai volume dalam batas menengah, namun menduduki titik rata-rata harga jual premium tertinggi secara mutlak.
- **[C4] Wilayah Skala Kecil** (16 Provinsi): Kawasan pembudidaya gurem tradisional yang paling mendesak untuk disokong dengan permodalan subsidi serta dorongan literasi teknologi dasar.

---
*Laporan komprehensif ini didesain secara dedikatif untuk menyongsong pembangunan tata kelola agritech di perairan Indonesia secara presisi.*
