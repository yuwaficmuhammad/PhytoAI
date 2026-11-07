# Dokumentasi Deviasi Saintifik: PhytoAI-Genetics

Dokumen ini mencatat seluruh deviasi teknis dan metodologis antara teks proposal riset (*"PhytoAI-Genetics: Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (Oryza sativa)"*) dengan implementasi komputasi aktual pada repositori ini.

Pencatatan ini dilakukan secara terbuka demi menjunjung tinggi integritas ilmiah, transparansi akademik, dan reproduktibilitas penelitian.

---

## Ringkasan Deviasi

| Kode | Aspek Metodologi | Pernyataan Proposal | Implementasi Aktual Repositori | Alasan Saintifik & Rekomendasi Revisi Proposal |
|---|---|---|---|---|
| **D1** | **Tokenisasi Sekuens** | k-mer (k=6, stride=1) | Byte Pair Encoding (BPE) bawaan DNABERT-2 + Utilitas k-mer deskriptif | Model DNABERT-2 tidak menggunakan k-mer 6 overlapping melainkan BPE (~4096 token). |
| **D2** | **Metrik Perplexity** | Pergeseran Perplexity | Pseudo-Log-Likelihood (PLL) & Pseudo-Perplexity | DNABERT-2 adalah Masked Language Model (MLM), bukan autoregresif kausal. Perplexity standar tidak valid secara matematis. |
| **D3** | **Prediksi LRI & Klasifikasi** | Dual-prediction head terlatih untuk varian & LRI | Arsitektur MLP dibangun; Pelatihan dikunci ketat (Gating) hingga data fenotipe riil tersedia | Proposal tidak menyertakan dataset fenotipe empiris. Menolak melatih dengan data fiktif. |

---

## Rincian Deviasi & Usulan Perbaikan Naskah Proposal

### D1. Tokenisasi: BPE vs k-mer 6-mer Overlapping

- **Pernyataan dalam Proposal:**  
  *"Sekuens nukleotida dipotong menjadi token-token k-mer dengan panjang k=6 dan pergeseran stride=1 sebelum diinputkan ke dalam model bahasa genomik..."*
- **Realitas Teknis Model Card:**  
  Model pondasi yang dipilih (`zhihan1996/DNABERT-2-117M`, Zhou et al., 2023) secara resmi menggunakan **Byte Pair Encoding (BPE)** melalui `PreTrainedTokenizerFast` dengan kosakata ~4096 token. Tokenisasi k-mer $k=6$ overlapping adalah karakteristik model DNABERT generasi pertama (Ji et al., 2021) yang memiliki redundansi spasial tinggi dan efisiensi komputasi lebih rendah.
- **Implementasi dalam Repositori:**  
  1. Untuk inferensi dan ekstraksi embedding DNABERT-2, pipeline menggunakan `AutoTokenizer` bawaan model (`phytoai/tokenization.py`).
  2. Fungsi k-mer overlapping (`kmerize(seq, k=6, stride=1)`) tetap disediakan sebagai modul analisis deskriptif tersendiri guna menjawab Rumusan Masalah 1 terkait variasi komposisi oligonukleotida antar landrace.
- **Usulan Revisi Kalimat Proposal:**  
  > *"Urutan nukleotida DREB2A ditokenisasi menggunakan Byte-Pair Encoding (BPE) bawaan arsitektur DNABERT-2 dengan kosakata 4.096 token sub-kata genomik. Sebagai komparasi deskriptif pada Rumusan Masalah 1, profil distribusi frekuensi 6-mer overlapping (k=6, stride=1) dihitung secara komplementer."*

---

### D2. Metrik Pergeseran Perplexity pada Masked Language Model (MLM)

- **Pernyataan dalam Proposal:**  
  *"Mutagenesis saturasi dievaluasi dengan menghitung pergeseran perplexity dari urutan mutan dibandingkan wildtype..."*
- **Realitas Bioinformatika & NLP:**  
  DNABERT-2 adalah *Masked Language Model* (MLM) dua-arah (bidirectional), bukan model bahasa kausal satu-arah (seperti GPT). Pada model MLM, perhitungan *perplexity* autoregresif standar $\exp(-\frac{1}{N} \sum \log P(x_t \mid x_{<t}))$ secara teoretis tidak terdefinisi karena token di masa depan dapat dilihat oleh representasi tersembunyi.
- **Implementasi dalam Repositori:**  
  Repositori menerapkan standar ilmiah konsensus bioinformatika dan NLP (Salazar et al., ACL 2020; Meier et al., PNAS 2021) menggunakan **Pseudo-Log-Likelihood (PLL)**:
  $$\text{PLL}(S) = \sum_{i \in W} \log P(x_i \mid S_{\setminus i})$$
  $$\Delta \text{PLL} = \text{PLL}(S_{mut}) - \text{PLL}(S_{wt})$$
  $$\text{Pseudo-Perplexity} = \exp\left(-\frac{1}{|W|} \text{PLL}(S)\right)$$
  Pergeseran $\Delta\text{PLL} > 0$ menandakan substitusi basa meningkatkan keselarasan sekuens lokal menurut representasi DNABERT-2.
- **Usulan Revisi Kalimat Proposal:**  
  > *"Evaluasi in silico mutasi titik pada domain AP2/ERF diukur melalui pergeseran Pseudo-Log-Likelihood (ΔPLL) dan pseudo-perplexity yang dihitung dari distribusi probabilitas kondisional model bertopeng DNABERT-2 pada jendela token target."*

---

### D3. Data Gating: Pelatihan Dual-Prediction Head (LRI & Klasifikasi)

- **Pernyataan dalam Proposal:**  
  *"Dual-prediction head (MLP) memprediksi klasifikasi varian (Benign/Deleterious/Beneficial) dan regresi Leaf Rolling Index (LRI) skala 0.0 sampai 1.0 di bawah cekaman osmotik..."*
- **Realitas Ketersediaan Data:**  
  Proposal tidak mencantumkan sitasi, lampiran tabel, atau basis data repositori terbuka untuk nilai Leaf Rolling Index (LRI) per mutasi nukleotida DREB2A, maupun ground truth label mutasi menguntungkan (*Beneficial*) pada landrace lokal Indonesia.
- **Implementasi dalam Repositori:**  
  1. Arsitektur PyTorch `DualPredictionHead` telah dibangun secara lengkap di `phytoai/heads.py` dengan cabang linear untuk klasifikasi 3-kelas dan regresi LRI bertopeng fungsi aktivasi `Sigmoid` (memastikan interval ketat $[0.0, 1.0]$).
  2. Skrip pelatihan `scripts/train_heads.py` dilengkapi **Scientific Data Gating**: proses pelatihan akan MENOLAK dieksekusi jika berkas `data/labels_variant_class.csv` dan `data/phenotype_lri.csv` belum disediakan oleh peneliti dengan data eksperimental riil.
  3. Dalam mode inferensi tanpa data latih riil, repositori menyajikan skor sebagai pergeseran likelihood *zero-shot* murni, dengan penandaan jujur: `"kandidat zero-shot (bukan Beneficial terverifikasi)"`, dan nilai LRI diset `None` (*null*).
- **Usulan Revisi Kalimat Proposal:**  
  > *"Arsitektur dual-prediction head (MLP) dibangun di atas representasi 768-dimensi DNABERT-2 untuk menerima data kalibrasi fenotipe basah (Leaf Rolling Index hasil uji PEG/osmotik laboratorium) di masa depan. Pada tahap in silico awal tanpa data basah, penyaringan kandidat mutasi mengandalkan skor zero-shot ΔPLL."*
