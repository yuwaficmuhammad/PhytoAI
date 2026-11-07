# PhytoAI-Genetics

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-DNABERT--2--117M-yellow)](https://huggingface.co/zhihan1996/DNABERT-2-117M)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuwaficmuhammad/ncbi/blob/align-with-proposal/notebooks/phytoai_colab.ipynb)

> **PhytoAI-Genetics: Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (*Oryza sativa*)**  
> Penelitian Bioinformatika & Pemodelan Genomik MA Salafiyah Kajen Pati

---

## 1. Latar Belakang & Cakupan Riset

Cekaman kekeringan merupakan tantangan abiotik utama pada budidaya padi sawah dan lahan kering di Indonesia. Faktor transkripsi **OsDREB2A** (*Dehydration-Responsive Element-Binding Protein 2A*; NCBI Gene ID: 4324418) memainkan peran sentral dalam mengaktivasi ekspresi gen-gen hilir toleransi dehidrasi melalui pengikatan elemen cis DRE/CRT (*A/GCCGAC*) pada promotor target.

Proyek ini mengimplementasikan alur kerja komputasi ilmiah yang **selaras 100% dengan proposal riset**:
1. **Data Genomik:** Pengambilan sekuens nukleotida gen *DREB2A* dari minimal 5 landrace padi lokal Indonesia + genom referensi (*Nipponbare*) dari NCBI GenBank.
2. **Pra-Pemrosesan Sekuens:** Pembersihan FASTA, validasi reading frame CDS (ATG start, TAA/TAG/TGA stop), translasi asam amino, dan tokenisasi.
3. **Model Genomik Transformer:** Pemanfaatan model pondasi DNA **DNABERT-2** (117M parameter; `zhihan1996/DNABERT-2-117M`) untuk mengekstraksi representasi embedding 768-dimensi via mean pooling pada hidden state terakhir encoder.
4. **Mutagenesis Saturasi *In Silico*:** Penggantian sistematis nukleotida pada koordinat domain **AP2/ERF** pengikat DNA (koordinat CDS: bp 202 - 390; $189\text{ bp} \times 3\text{ alternatif} = 567\text{ varian}$).
5. **Skor Pergeseran Pseudo-Log-Likelihood:** Evaluasi keselarasan varian mutan melalui pergeseran $\Delta\text{PLL} = \text{PLL}(S_{mut}) - \text{PLL}(S_{wt})$ dan *pseudo-perplexity*.
6. **Dual-Prediction Head (MLP):** Arsitektur multi-task untuk klasifikasi varian (3 kelas: *Benign*, *Deleterious*, *Beneficial*) dan regresi *Leaf Rolling Index* (LRI, $0.0 - 1.0$) dengan **Scientific Data Gating** (hanya dilatih bila data fenotipe basah riil tersedia).
7. **Cetak Biru Varian Rekayasa Genom:** Penyusunan kandidat varian berpeluang tinggi sebagai cetak biru rekomendasi rekayasa CRISPR-Cas9 **di masa depan**.

---

## 2. Struktur Repositori

```
ncbi/
├── app/                      # Layanan REST API minimal (FastAPI)
│   ├── core/                 # Konfigurasi aplikasi & konstanta koordinat AP2
│   ├── data/                 # Database lokal SQLite (phytoai_local.db)
│   ├── middleware/           # Rate limiting per-IP (sliding window)
│   ├── models/               # Skema data Pydantic (varian, sekuens, respon)
│   ├── routers/              # Endpoint minimal (/phytoai, /database, /sequences)
│   ├── services/             # Klien NCBI Datasets & layanan database SQLite
│   └── main.py               # Titik masuk aplikasi FastAPI
├── data/
│   ├── accessions.csv        # Tabel nomor aksesi landrace & referensi NCBI
│   ├── raw/                  # Berkas FASTA asli unduhan NCBI
│   └── processed/            # Sekuens FASTA bersih, summary JSON, & CSV saturasi
├── notebooks/
│   └── phytoai_colab.ipynb   # Notebook Google Colab 7 langkah end-to-end
├── phytoai/                  # Modul inti komputasi ilmiah PhytoAI-Genetics
│   ├── embedding.py          # Ekstraksi representasi 768-D via DNABERT-2
│   ├── heads.py              # Arsitektur PyTorch DualPredictionHead MLP
│   ├── scoring.py            # Analisis kodon biologis, delta PLL, & pseudo-perplexity
│   └── tokenization.py       # Utilitas 6-mer & integrasi BPE AutoTokenizer
├── scripts/
│   ├── fetch_dreb2a_fasta.py # Unduh sekuens DREB2A dari NCBI E-utilities
│   ├── preprocess.py         # Pembersihan FASTA & translasi CDS
│   ├── run_saturation.py     # Mutagenesis saturasi AP2 & evaluasi PLL
│   └── train_heads.py        # Pelatihan dual-head dengan Scientific Data Gating
├── tests/                    # Pengujian unit otomatis (pytest)
├── DEVIATIONS.md             # Dokumentasi deviasi ilmiah (D1, D2, D3)
├── Dockerfile                # Lingkungan kontainer minimal
├── docker-compose.yml        # Orkestrasi Docker lokal
├── requirements.txt          # Dependensi server API inti
├── requirements-dev.txt      # Dependensi pengujian pengembang
└── requirements-ml.txt       # Dependensi pemodelan ML (PyTorch, Transformers)
```

---

## 3. Cara Penggunaan

### Opsi A: Google Colab (Lingkungan Utama Proposal Butir 7)

Jalankan notebook interaktif lengkap dengan akselerasi GPU:
1. Buka [notebooks/phytoai_colab.ipynb](notebooks/phytoai_colab.ipynb) atau klik tautan **Open In Colab** di atas.
2. Pilih runtime GPU: **Runtime > Change runtime type > T4 GPU**.
3. Jalankan sel berurutan dari Langkah 1 hingga Langkah 7.

### Opsi B: Pipeline CLI Lokal

1. **Setup Virtual Environment & Dependensi:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   # Opsional (untuk inferensi lokal DNABERT-2 dengan PyTorch):
   pip install -r requirements-ml.txt
   ```

2. **Konfigurasi Variabel Lingkungan (`.env`):**
   ```env
   NCBI_API_KEY=isi_kunci_anda
   ```

3. **Unduh Sekuens dari NCBI:**
   ```bash
   python scripts/fetch_dreb2a_fasta.py --csv-path data/accessions.csv
   ```

4. **Pra-Pemrosesan Sekuens:**
   ```bash
   python scripts/preprocess.py --input-dir data/raw --output-dir data/processed
   ```

5. **Jalankan Mutagenesis Saturasi In Silico:**
   ```bash
   # Modus dry-run (memetakan kodon & konsekuensi asam amino tanpa unduh bobot 400MB)
   python scripts/run_saturation.py --dry-run

   # Modus inferensi neural penuh (memerlukan PyTorch & transformers):
   python scripts/run_saturation.py
   ```

6. **Pelatihan Dual-Prediction Head (Terproteksi Pintu Pengaman):**
   ```bash
   # Skrip ini akan menolak melatih jika data fenotipe riil belum disediakan
   python scripts/train_heads.py
   ```

---

## 4. Layanan REST API Minimal

Jalankan server API FastAPI lokal:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Dokumentasi interaktif OpenAPI tersedia di:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Endpoint Utama:
- `GET /health`: Status server dan penegasan metodologi saintifik.
- `GET /info`: Informasi organisme acuan (*Oryza sativa*) dan lokus gen acuan (*OsDREB2A*).
- `GET /api/v1/phytoai/variants`: Membaca varian hasil mutagenesis saturasi dari database lokal SQLite.
- `GET /api/v1/phytoai/methods`: Penjelasan transparansi model DNABERT-2 dan batas validitas ilmiah.
- `GET /api/v1/db/status`: Status operasional dan statistik tabel database lokal.

---

## 5. Pengujian Unit Otomatis

Jalankan seluruh rangkaian pengujian unit dengan pytest:
```bash
pytest tests/ -v
```

Semua pengujian dirancang deterministik, terisolasi dari jaringan eksternal, dan memverifikasi batas validitas biokimia serta integritas data gating.

---

## 6. Metode & Keterbatasan Saintifik (Integritas Akademik)

Sesuai komitmen etika penelitian ilmiah:
1. **Sifat Skor Zero-Shot:** Nilai pergeseran pseudo-log-likelihood ($\Delta\text{PLL}$) adalah ukuran keselarasan tata bahasa urutan menurut model representasi bahasa genomik DNABERT-2, **bukan bukti langsung fenotipe toleransi kekeringan di sawah/laboratorium**.
2. **Pencegahan Fabrikasi Data (Data Gating):** Repositori ini tidak mengarang data latih sintetis. Regresi Leaf Rolling Index (LRI) dan klasifikasi varian menguntungkan (*Beneficial*) hanya akan dilatih apabila peneliti telah memasukkan data fenotipe empiris terukur.
3. **Cakupan CRISPR:** Rekayasa penyuntingan genom CRISPR-Cas9 merupakan sasaran penelitian masa depan (*future work*) di laboratorium basah dan bukan bagian dari pekerjaan komputasi repositori saat ini.
4. **Deviasi Proposal:** Seluruh perbedaan antara naskah awal proposal dan implementasi teknis terdokumentasi secara transparan di [DEVIATIONS.md](DEVIATIONS.md).
