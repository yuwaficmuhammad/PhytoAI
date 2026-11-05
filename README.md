# 🌾 PhytoAI-Genetics: Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (Oryza sativa)
### *Bioinformatics & Machine Learning Platform for DREB2A Mutation Modeling, CRISPR Base Editing, and Spatial InaRISK BNPB Integration across Indonesian Rice Agroecosystems consuming NCBI Datasets v2 REST API*

> 🏛️ **Atribusi Riset**: Proyek penelitian, platform pemodelan genomik, dan AI PhytoAI ini adalah hasil karya orisinal **Periset MA Salafiyah Kajen Pati** (Madrasah Aliyah Salafiyah Kajen, Margoyoso, Kabupaten Pati, Jawa Tengah).

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![NCBI Datasets](https://img.shields.io/badge/NCBI%20Datasets-v2%20API-0071bc.svg)](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/api/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Platform ini mengintegrasikan pemodelan kecerdasan buatan berbasis **Protein Language Model (Transformer pLM)** dengan data resmi **NCBI Datasets v2 REST API** dan sistem spasial **BNPB InaRISK ImageServer 100m** untuk memodelkan mutasi titik pada **OsDREB2A** (NCBI Gene ID: `4324418`), merancang panduan *CRISPR Base Editing* (CBE/ABE), serta mengevaluasi adaptasi kultivar padi lokal (*Oryza sativa*) di seluruh agroekosistem terdampak kekeringan di Indonesia.

---

## 🎯 Fokus Utama Proyek

1. **🤖 Pemodelan Transformer OsDREB2A (ΔLLR)**:
   - Evaluasi efek mutasi titik pada faktor transkripsi kunci kekeringan (*Dehydration-Responsive Element-Binding Protein 2A*, 274 AA).
   - Pemetaan 4 domain fungsional: **NLS** (13-22), **AP2/ERF DNA-Binding** (68-130), **NRD / Degron PEST** (136-192, proteasom 26S), dan **TAD** (200-274).
   - Identifikasi mutasi konstitutif aktif **DREB2A-CA** (`P168L`) yang meniadakan degradasi proteasom, serta mutasi afinitas pengikatan promoter (`V79I`).
2. **🗺️ Integrasi Spasial BNPB InaRISK & Sampling Koordinat Dinamis**:
   - Seluruh data diambil dinamis dari endpoint API tanpa *hardcoded value*.
   - **Sampling Koordinat Real-Time**: Pengguna dapat mengklik titik mana saja di seluruh kepulauan Indonesia pada peta Leaflet untuk mengambil skor risiko kekeringan BNPB secara instan (`/api/v1/phytoai/assess-coordinates`).
   - Cakupan klaster nasional meliputi Jawa Tengah (Demak, Pati, Grobogan), Jawa Timur (Bojonegoro, Madura, Tapal Kuda), Jawa Barat & Banten, NTT (Timor, Sumba, Flores), NTB (Sistem GORA), D.I. Yogyakarta (Karst Gunungkidul), Bali, Sulawesi (Palu, Jeneponto, Wajo), Sumatera (Lampung, Ogan Ilir, Pidie), dan Kalimantan Selatan.
3. **🌾 Basis Data Kultivar Padi Lokal Indonesia**:
   - Profil alel alami dan keragaman haplotip DREB2A pada varietas lokal (*Inpari 32 HDB*, *Padi Gogo Merah NTT*, *Segreng Handayani*, *Salumpikit*, *Gogo Jatiluhur*, *Limboto*, *Situ Bagendit*, *Inpari 42 Agritan GSR*, *Padi Hitam Sumba*, *Rojolele*, *Mentik Wangi*, *IR64*).
4. **✂️ Desain CRISPR Base Editing (CBE / ABE)**:
   - Desain gRNA presisi untuk memasukkan mutasi transisi (C-ke-T via CBE atau A-ke-G via ABE) ke dalam sekuens coding *OsDREB2A* tanpa membuat *double-strand break* (DSB).
   - Analisis PAM SpCas9 / Cas12a, kadar GC, dan eliminasi motif terminasi dini Pol III (`TTTT`).
5. **📡 Konsumsi Langsung NCBI Datasets v2 REST API**:
   - Mengambil sekuens genomik, CDS (825 bp), dan protein (274 AA) untuk gen target *OsDREB2A* dan jejaring regulon kekeringan secara otomatis dengan autentikasi API Key.

---

## 🧬 Katalog Regulon Toleransi Kekeringan Padi Terkurasi

Semua target difokuskan secara ketat pada jejaring transkripsi dan toleransi dehidrasi padi:

| Simbol Gen | NCBI Gene ID | Kromosom | Kategori Sifat | Peran Biologis & Strategi Rekayasa |
| :--- | :--- | :--- | :--- | :--- |
| **OsDREB2A** | `4324418` | 1 | Master Regulator Cekaman | AP2/ERF TF; delesi NRD/P168L menghasilkan DREB2A-CA tahan kemarau ekstrem |
| **OsDREB1A** | `4341490` | 6 | Toleransi Cekaman Suhu/Kering | Regulon DREB1/CBF aktivasi cepat penurunan potensial osmotik |
| **OsDREB2B** | `4338981` | 5 | Alternative Splicing Regulator | Saklar transkrip aktif fungsional saat dehidrasi jaringan sel |
| **OsLEA3-1** | `4337666` | 5 | Proteksi Membran Sel | Efektor hilir DREB2A penstabil protein & membran plasma |
| **OsAREB1** | `4340578` | 6 | Sinyal ABA-Dependent | bZIP TF bekerja komplementer dengan DREB2A pada fase reproduktif |
| **OsP5CS1** | `4338302` | 5 | Biosintesis Osmolit Prolin | Biosintesis asam amino prolin pencegah plasmolisis sel |
| **OsSKIPa** | `4331776` | 2 | Viabilitas Seluler & ROS | Menekan akumulasi radikal bebas saat kekeringan perakaran |
| **SNAC1** | `4334002` | 3 | Penutupan Stomata | Menekan laju transpirasi air daun saat kemarau |
| **OsDST** | `4334341` | 3 | Kerapatan Stomata | Target knockout untuk menurunkan kerapatan stomata dan evaporasi daun |
| **OsERF71** | `4330107` | 2 | Arsitektur Perakaran | Merombak akar padi lebih tebal dan dalam menembus lapisan akuifer tanah |

---

## 🚀 Panduan Menjalankan

### Menggunakan Virtual Environment Lokal

1. **Masuk ke Direktori Proyek**:
   ```bash
   cd /Users/yuwaficmuhammad/Desktop/ncbi
   ```

2. **Aktifkan Virtual Environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Lingkungan (`.env`)**:
   ```env
   NCBI_API_KEY=b1930592bae2f149001d2768b0faad3f0d08
   ```

5. **Jalankan Server API**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Buka di Browser**:
   - 🌾 **Studio Web UI Interaktif**: [http://localhost:8000](http://localhost:8000)
   - 📖 **Dokumentasi Interaktif (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - 📑 **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Pengujian Komprehensif

Rangkaian 36 pengujian unit test dan live integration test:

```bash
# Menjalankan seluruh 36 tes
pytest -v

# Menjalankan unit test model PhytoAI & asesmen koordinat dinamis
pytest tests/test_phytoai.py -v

# Menjalankan pengujian koneksi live NCBI Datasets v2
pytest tests/test_live_integration.py -v
```

---

## 📡 Daftar Endpoint REST API Utama

### 1. 🤖 PhytoAI-Genetics & GIS Spasial BNPB InaRISK (`/api/v1/phytoai`)
- `GET /api/v1/phytoai/dreb2a/domains`: Anotasi struktur domain OsDREB2A (NLS, AP2/ERF, NRD/Degron PEST, TAD).
- `POST /api/v1/phytoai/dreb2a/predict-mutation`: Prediksi dampak mutasi titik (mis. `P168L`, `V79I`, `S167A`) terhadap toleransi kekeringan menggunakan model Transformer pLM (ΔLLR).
- `GET /api/v1/phytoai/dreb2a/deep-mutational-scan`: In silico Deep Mutational Scanning (DMS) pada domain AP2 dan NRD untuk menemukan mutasi paling menguntungkan.
- `GET /api/v1/phytoai/dreb2a/local-cultivars`: Database profil alel alami OsDREB2A pada varietas padi lokal Indonesia.
- `POST /api/v1/phytoai/dreb2a/design-base-editing`: Desain gRNA CRISPR Base Editor (ABE/CBE) untuk memasukkan mutasi DREB2A-CA tanpa double-strand break.
- `GET /api/v1/phytoai/drought-regions`: Katalog dinamis wilayah sentra padi terdampak kekeringan di Indonesia dengan filter `province`, `min_hazard`, dan `search`.
- `GET /api/v1/phytoai/assess-coordinates?lat=...&lon=...`: **Sampling Spasial Titik Koordinat Dinamis Bebas** di seluruh Indonesia untuk mendeteksi indeks bahaya kekeringan InaRISK, agroekosistem, kultivar adaptif, dan strategi mutasi DREB2A.
- `POST /api/v1/phytoai/assess-coordinates`: Versi POST penilaian titik koordinat untuk integrasi payload JSON.
- `GET /api/v1/phytoai/inarisk/metadata`: Verifikasi koneksi metadata resmi ArcGIS ImageServer BNPB InaRISK (`inarisk/layer_risiko_kekeringan`).

### 2. 🎯 Regulon Toleransi Kekeringan Padi (`/api/v1/targets`)
- `GET /api/v1/targets`: Daftar gen regulon toleransi kekeringan padi (*OsDREB2A*, *OsDREB1A*, *OsDREB2B*, dll.).
- `GET /api/v1/targets/{identifier}`: Detail gen target dengan penggabungan data live anotasi NCBI Datasets.

### 3. ✂️ Perancangan CRISPR Base Editing (`/api/v1/crispr`)
- `POST /api/v1/crispr/find-targets`: Pemindaian situs target gRNA dari sekuens DNA dengan analisis PAM SpCas9/Cas12a, %GC, dan peringatan terminasi `TTTT`.

### 4. 📥 Ekstraksi Sekuens DNA/Protein NCBI (`/api/v1/sequences`)
- `GET /api/v1/sequences/gene/{gene_id}`: Ekstraksi sekuens Genomik, CDS, dan Protein langsung dari arsip resmi NCBI secara in-memory.
- `GET /api/v1/sequences/gene/{gene_id}/download-package`: Unduh arsip ZIP resmi NCBI Datasets.

---

## 📜 Lisensi & Atribusi

- **Karya Orisinal**: Periset **MA Salafiyah Kajen Pati** (Pati, Jawa Tengah).
- **Data Genomika**: Bersumber langsung dari **National Center for Biotechnology Information (NCBI) Datasets v2 REST API**.
- **Data Spasial Kekeringan**: Bersumber dari **BNPB InaRISK Indonesia** (`gis.bnpb.go.id`).
- Didedikasikan untuk mendukung riset bioteknologi, ketahanan pangan nasional, dan pemuliaan tanaman padi modern berketahanan iklim ekstrem di Indonesia.
