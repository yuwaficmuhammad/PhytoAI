# SCOPE AUDIT: Penyelarasan PhytoAI-Genetics dengan Proposal Riset

> Dokumen inventaris aktual dan matriks keputusan cakupan berdasarkan proposal:
> *"PhytoAI-Genetics: Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (Oryza sativa)"*.

---

## 1. Ringkasan Eksekutif Inventaris

- **Total berkas diaudit**: 82 berkas
- **Ukuran total repositori (sebelum pemangkasan)**: ~45 MB (didominasi PDF redundan dan aset raster)
- **Komponen sesuai proposal (Butir 1–7)**:
  - `ncbi_client.py` & router `sequences.py` (Unduh sekuens GenBank FASTA)
  - Koordinat Domain AP2/ERF (Nukleotida)
  - Mutagenesis saturasi in silico (Level nukleotida via DNABERT-2)
  - Dual-prediction head (MLP di Colab / scripts)
  - API minimal (`/health`, baca varian) & Docker pendukung
- **Komponen di luar cakupan proposal (Harus Dihapus)**:
  - Modul CRISPR Base Editing & WebGL 3D simulation
  - Modul BNPB InaRISK GIS & peta Leaflet spasial
  - Modul Desainer Varietas (Gene Pyramiding) & Katalog Multi-Tanaman Pangan
  - Modul Katalog 10 Gen Regulon Padi
  - Chatbot Groq AI & kebocoran kunci API
  - Dashboard Web Studio (`index.html`, `studio_bundle.py`, `streamlit_app.py`)
  - Berkas PDF statis & gambar raster

---

## 2. Matriks Cakupan dan Keputusan Berkas Aktual

| Komponen / Berkas | Jalur Berkas Aktual | Ukuran (Bytes) | Baris | Keterkaitan Proposal | Keputusan Default | Alasan / Tindakan |
|---|---|:---:|:---:|:---:|:---:|---|
| **NCBI Client** | `app/services/ncbi_client.py` | 9,514 | 236 | Butir 1 | **PERTAHANKAN** | Dirampingkan khusus untuk ekstraksi DREB2A FASTA |
| **Router Sequences** | `app/routers/sequences.py` | 4,572 | 108 | Butir 1 | **PERTAHANKAN** | Sederhanakan tanpa unduhan ZIP |
| **Router Genes** | `app/routers/genes.py` | 5,402 | 122 | Parsial | **HAPUS** | Tidak dibutuhkan langsung oleh pipeline data proposal |
| **Router Genomes** | `app/routers/genomes.py` | 3,306 | 78 | Parsial | **HAPUS** | Tidak dibutuhkan oleh proposal (hanya fokus lokus DREB2A) |
| **Router Targets** | `app/routers/targets.py` | 2,574 | 68 | Tidak Ada | **HAPUS** | Proposal hanya meneliti gen DREB2A, bukan 10 regulon |
| **Data Targets** | `app/data/rice_targets.py` | 9,211 | 202 | Tidak Ada | **HAPUS** | Katalog 10 target di luar ruang lingkup |
| **Router CRISPR** | `app/routers/crispr.py` | 4,021 | 90 | Tidak Ada | **HAPUS** | CRISPR adalah pekerjaan masa depan, bukan saat ini |
| **Service CRISPR** | `app/services/crispr_service.py` | 6,955 | 181 | Tidak Ada | **HAPUS** | Algoritma sgRNA/PAM tidak ada dalam proposal |
| **Model CRISPR** | `app/models/crispr.py` | 2,156 | 54 | Tidak Ada | **HAPUS** | Skema Pydantic CRISPR dihapus |
| **Simulasi 3D** | `app/static/crispr_3d.html` | 31,309 | 832 | Tidak Ada | **HAPUS** | Simulasi WebGL di luar cakupan |
| **Service InaRISK** | `app/services/inarisk_service.py` | 5,474 | 101 | Tidak Ada | **HAPUS** | Data spasial kebencanaan tidak ada dalam proposal |
| **Service Variety** | `app/services/variety_designer_service.py` | 35,090 | 740 | Tidak Ada | **HAPUS** | Gene pyramiding & katalog jagung/kedelai/sorgum di luar proposal |
| **Chatbot Router** | `app/routers/chat.py` | 11,828 | 176 | Tidak Ada | **HAPUS** | Chatbot tidak ada di proposal; hilangkan sumber kebocoran kunci |
| **Studio Bundle** | `app/services/studio_bundle.py` | 29,419 | 621 | Tidak Ada | **HAPUS** | Generator bundel web SPA di luar cakupan proposal |
| **Web Studio SPA** | `app/static/index.html` | 338,400 | 6,538 | Tidak Ada | **HAPUS** | Proposal bekerja di lingkungan Colab |
| **Streamlit App** | `streamlit_app.py` | 90,496 | 1,599 | Tidak Ada | **HAPUS** | Digantikan oleh Colab notebook & skrip CLI |
| **Service PhytoAI** | `app/services/phytoai_service.py` | 44,896 | 892 | Butir 4 (Parsial) | **HAPUS / TULIS ULANG** | Hapus logika protein rule-based, ganti ke level nukleotida |
| **Router PhytoAI** | `app/routers/phytoai.py` | 18,072 | 394 | Butir 4, 6 | **RAMPINGKAN** | Pertahankan hanya endpoint baca hasil varian & methods |
| **Database Router** | `app/routers/database.py` | 3,282 | 88 | Parsial | **RAMPINGKAN** | Simpan hanya pembacaan tabel varian dan skor |
| **Database Service** | `app/services/db_service.py` | 38,419 | 783 | Parsial | **RAMPINGKAN** | Rampingkan ke tabel landrace, varian, dan saturation_scores |
| **Database SQLite** | `app/data/phytoai_local.db` | 61,440 | - | Parsial | **RAMPINGKAN** | Simpan DB lama sebagai cadangan, buat skema ramping baru |
| **FastAPI Core** | `app/main.py` | 8,462 | 194 | Pendukung | **RAMPINGKAN** | Hanya `/health`, `/api/v1/variants`, `/api/v1/methods` |
| **Config Core** | `app/core/config.py` | 2,219 | 56 | Pendukung | **RAMPINGKAN** | Hapus GROQ_*, simpan NCBI_* dan method_note |
| **Exceptions Core**| `app/core/exceptions.py` | 822 | 23 | Pendukung | **PERTAHANKAN** | Error handling HTTP |
| **Rate Limiter** | `app/middleware/rate_limit.py` | 4,159 | 105 | Pendukung | **PERTAHANKAN** | Pertahankan sliding-window limiter |
| **Model PhytoAI** | `app/models/phytoai.py` | 4,479 | 105 | Butir 4, 5 | **RAMPINGKAN** | Sesuaikan dengan model nukleotida, LRI, dan varian |
| **Model Gene** | `app/models/gene.py` | 2,040 | 45 | Butir 1 | **PERTAHANKAN** | Skema data gen NCBI |
| **Model Genome** | `app/models/genome.py` | 1,804 | 45 | Butir 1 | **HAPUS** | Tidak dipakai langsung |
| **Model Target** | `app/models/target.py` | 1,298 | 25 | Tidak Ada | **HAPUS** | Dihapus bersama `rice_targets` |
| **PDF Panduan 1** | `Panduan_Alur_Penelitian_Step_by_Step_A4.pdf` | 4,954,873 | - | Tidak Ada | **HAPUS** | Dokumen non-kode di luar proposal |
| **PDF Panduan 2** | `Panduan_Lengkap_PhytoAI_Genetics_A4.pdf` | 8,474,783 | - | Tidak Ada | **HAPUS** | Dokumen non-kode di luar proposal |
| **PDF di app/static**| `app/static/*.pdf` | 13,429,656 | - | Tidak Ada | **HAPUS** | Salinan duplikat berkas PDF |
| **PDF di static/** | `static/*.pdf` | 13,429,656 | - | Tidak Ada | **HAPUS** | Salinan duplikat berkas PDF |
| **Gambar app/static**| `app/static/images/*.png, *.jpg` | 9,141,850 | - | Tidak Ada | **HAPUS** | Aset visual web studio |
| **Gambar static/** | `static/*` | 1,749,437 | - | Tidak Ada | **HAPUS** | Aset visual duplikat |
| **Favicon & Icon** | `app/static/fav*`, `app/static/apple*` | 91,408 | - | Tidak Ada | **HAPUS** | Aset visual web |
| **Favicon di static**| `static/fav*`, `static/apple*` | 91,408 | - | Tidak Ada | **HAPUS** | Aset visual web |
| **Script PDF 1** | `build_tutorial_pdf.py` | 72,013 | 1,197 | Tidak Ada | **HAPUS** | Skrip pembuatan PDF |
| **Script PDF 2** | `generate_step_by_step_pdf.py` | 38,180 | 778 | Tidak Ada | **HAPUS** | Skrip pembuatan PDF |
| **Dockerfile** | `Dockerfile` | 924 | 32 | Infrastruktur | **PERTAHANKAN** | Disesuaikan dengan berkas tersisa |
| **Docker Compose** | `docker-compose.yml` | 425 | 18 | Infrastruktur | **PERTAHANKAN** | Hapus `version:`, sesuaikan env |
| **Requirements** | `requirements.txt` | 236 | 15 | Infrastruktur | **BERSIHKAN** | Hapus streamlit, pillow, dll. |
| **Test Targets** | `tests/test_targets.py` | 985 | 34 | Tidak Ada | **HAPUS** | Fitur targets dihapus |
| **Test CRISPR** | `tests/test_crispr.py` | 2,884 | 84 | Tidak Ada | **HAPUS** | Fitur CRISPR dihapus |
| **Test Chat** | `tests/test_chat.py` | 1,785 | 57 | Tidak Ada | **HAPUS** | Fitur Chatbot dihapus |
| **Test Variety** | `tests/test_variety_designer.py` | 4,744 | 135 | Tidak Ada | **HAPUS** | Fitur variety designer dihapus |
| **Test PhytoAI** | `tests/test_phytoai.py` | 6,841 | 199 | Parsial | **RAMPINGKAN** | Hapus tes InaRISK & hardcoded protein scores |
| **Test Database** | `tests/test_database.py` | 3,927 | 133 | Parsial | **RAMPINGKAN** | Sesuaikan dengan skema tabel baru |
| **Test API** | `tests/test_api.py` | 2,314 | 70 | Parsial | **RAMPINGKAN** | Sesuaikan dengan endpoint minimal |
| **Test Live NCBI**| `tests/test_live_integration.py` | 1,865 | 48 | Butir 1 | **PERTAHANKAN** | Tes koneksi NCBI GenBank |

---

## 3. Komponen Baru yang Akan Dibuat (Sesuai Proposal)

| Komponen Baru | Jalur Berkas Target | Keterkaitan Proposal | Deskripsi |
|---|---|:---:|---|
| **Daftar Aksesi** | `data/accessions.csv` | Butir 1 | Landrace padi lokal Indonesia (templat kosong bertanda `[ISI MANUAL]`) |
| **Skrip Unduh FASTA** | `scripts/fetch_dreb2a_fasta.py` | Butir 1 | Mengunduh urutan FASTA GenBank untuk tiap aksesi |
| **Skrip Preprocessing**| `scripts/preprocess.py` | Butir 2 | Pembersihan FASTA, validasi alfabet A/C/G/T/N, pemotongan sekuens |
| **Modul Tokenizer** | `phytoai/tokenization.py` | Butir 2 & Deviasi D1 | Utilitas k-mer (k=6, stride=1) + adapter BPE DNABERT-2 |
| **Modul Embedding** | `phytoai/embedding.py` | Butir 3 | Ekstraksi representasi 768-dimensi via `zhihan1996/DNABERT-2-117M` |
| **Modul Scoring PLL** | `phytoai/scoring.py` | Butir 4 & Deviasi D2 | Pseudo-log-likelihood (PLL) masking & pseudo-perplexity |
| **Skrip Mutagenesis** | `scripts/run_saturation.py` | Butir 4 | Saturasi substitusi nukleotida domain AP2/ERF |
| **Modul Dual Heads** | `phytoai/heads.py` | Butir 5 | MLP 3-class classification + LRI sigmoid regression |
| **Skrip Latih Heads** | `scripts/train_heads.py` | Butir 5 | Gerbang data fenotipe: menolak melatih jika data nyata belum ada |
| **Notebook Colab** | `notebooks/phytoai_colab.ipynb` | Butir 7 | Notebook interaktif end-to-end lingkungan Google Colab |
| **Dokumen Deviasi** | `DEVIATIONS.md` | Deviasi D1–D3 | Dokumentasi transparan perbedaan teknis proposal vs arsitektur model |
| **Requirements ML** | `requirements-ml.txt` | Lingkungan Colab | Dependensi `torch`, `transformers`, `einops`, `triton` khusus lingkungan komputasi |
| **Requirements Dev** | `requirements-dev.txt` | Pengembangan | `pytest`, `httpx` untuk pengujian lokal tanpa bloatware |
