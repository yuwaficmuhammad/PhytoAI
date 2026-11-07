"""
streamlit_app.py
PhytoAI-Genetics: In Silico Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (Oryza sativa)
Antarmuka Web Interaktif untuk Streamlit Community Cloud.
Sesuai Proposal Riset Ilmiah Bioinformatika MA Salafiyah Kajen Pati.
"""

import os
import csv
import json
import pandas as pd
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="PhytoAI-Genetics | OsDREB2A Genomics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Jalur Berkas Data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_SATURATION = os.path.join(DATA_DIR, "processed", "saturation_mutagenesis_results.csv")
CSV_ACCESSIONS = os.path.join(DATA_DIR, "accessions.csv")
JSON_PREPROCESS = os.path.join(DATA_DIR, "processed", "preprocessing_summary.json")
DEVIATIONS_MD = os.path.join(BASE_DIR, "DEVIATIONS.md")

COLAB_URL = "https://colab.research.google.com/github/yuwaficmuhammad/ncbi/blob/align-with-proposal/notebooks/phytoai_colab.ipynb"
MODEL_HF_URL = "https://huggingface.co/zhihan1996/DNABERT-2-117M"


@st.cache_data
def load_saturation_data():
    """Memuat data hasil evaluasi mutagenesis saturasi domain AP2/ERF."""
    if os.path.exists(CSV_SATURATION):
        df = pd.read_csv(CSV_SATURATION)
        return df
    return pd.DataFrame()


@st.cache_data
def load_accessions_data():
    """Memuat daftar aksesi landrace padi lokal dan acuan."""
    if os.path.exists(CSV_ACCESSIONS):
        return pd.read_csv(CSV_ACCESSIONS)
    return pd.DataFrame()


@st.cache_data
def load_preprocessing_summary():
    """Memuat ringkasan pra-pemrosesan sekuens."""
    if os.path.exists(JSON_PREPROCESS):
        with open(JSON_PREPROCESS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# Sidebar Navigasi
st.sidebar.image("https://img.shields.io/badge/PhytoAI--Genetics-DNABERT--2-brightgreen?style=for-the-badge&logo=dna", use_container_width=True)
st.sidebar.title("🌾 PhytoAI-Genetics")
st.sidebar.caption("Transformer Modeling of DREB2A Mutations & Drought Tolerance in Local Rice")

nav_choice = st.sidebar.radio(
    "Navigasi Modul:",
    [
        "1. 🌾 Ringkasan & 7 Butir Proposal",
        "2. 🧬 Sekuens DREB2A & Domain AP2",
        "3. 📊 Mutagenesis Saturasi In Silico",
        "4. 🎯 Cetak Biru Kandidat Varian",
        "5. 🚀 Google Colab & DNABERT-2",
        "6. 📑 Integritas & Deviasi Saintifik"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Metadata Riset")
st.sidebar.markdown("""
- **Organisme:** *Oryza sativa* (Padi)
- **Lokus Target:** *OsDREB2A*
- **NCBI Gene ID:** [4324418](https://www.ncbi.nlm.nih.gov/gene/4324418)
- **Koordinat Domain AP2:** nt 202 - 390
- **Model Fondasi:** [DNABERT-2 117M](https://huggingface.co/zhihan1996/DNABERT-2-117M)
- **Institusi:** MA Salafiyah Kajen Pati
""")

st.sidebar.markdown(f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB_URL})")

# ==============================================================================
# HALAMAN 1: RINGKASAN & 7 BUTIR PROPOSAL
# ==============================================================================
if nav_choice.startswith("1."):
    st.title("🌾 PhytoAI-Genetics")
    st.subheader("Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (*Oryza sativa*)")

    st.markdown("""
    Selamat datang di platform bioinformatika komputasi **PhytoAI-Genetics**.
    Platform ini dirancang khusus untuk memodelkan dan mengevaluasi varian mutasi gen **OsDREB2A**
    pada padi lokal Indonesia secara *in silico* menggunakan model pondasi bahasa DNA **DNABERT-2 (117M)**.
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gen Target", "OsDREB2A", "Gene ID: 4324418")
    col2.metric("Panjang CDS Acuan", "825 bp", "274 Asam Amino")
    col3.metric("Domain Kritis", "AP2/ERF", "bp 202 - 390 (189 bp)")
    col4.metric("Mutasi Saturasi", "567 Varian", "189 Posisi × 3 Basa")

    st.markdown("---")
    st.header("📋 7 Pilar Utama Cakupan Proposal")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **1. Data Sekuens Nukleotida:**
        Urutan nukleotida gen *DREB2A* dari minimal 5 landrace padi lokal Indonesia + genom referensi (*Nipponbare*), diunduh dari NCBI GenBank (format FASTA).

        **2. Pra-pemrosesan Sekuens:**
        Parsing header FASTA, validasi reading frame (ATG start, TAA/TAG/TGA stop), pembersihan karakter non-DNA, translasi kodon, dan tokenisasi.

        **3. Model Genomik Transformer:**
        DNABERT-2 (117M parameter; `zhihan1996/DNABERT-2-117M`) via PyTorch + Hugging Face; ekstraksi embedding 768 dimensi dari hidden state terakhir encoder via mean pooling.

        **4. Mutagenesis Saturasi *In Silico*:**
        Substitusi sistematis seluruh kemungkinan basa nukleotida alternatif pada domain AP2/ERF pengikat DNA (*bp 202 - 390*).
        """)
    with c2:
        st.markdown("""
        **5. Skor Mutasi (Pseudo-Log-Likelihood Shift):**
        Perhitungan pergeseran *pseudo-log-likelihood* ($\Delta\text{PLL}$) dan *pseudo-perplexity* untuk menyaring kelayakan tata bahasa sekuens varian menurut model bahasa genomik.

        **6. Dual-Prediction Head (MLP) & Data Gating:**
        Arsitektur multi-task untuk klasifikasi varian (*Benign* / *Deleterious* / *Beneficial*) dan regresi *Leaf Rolling Index* (LRI, $0.0 - 1.0$) dengan proteksi data gating ketat (tidak dilatih tanpa data fenotipe riil).

        **7. Cetak Biru Rekayasa Genom Masa Depan:**
        Penyusunan koordinat varian kandidat sebagai cetak biru (*blueprint*) rekomendasi rekayasa CRISPR-Cas9 **di masa depan** diuji di lingkungan Python Google Colab.
        """)

    st.info("""
    💡 **Komitmen Integritas Akademik:**
    Seluruh inferensi neural mendalam (PyTorch & Hugging Face) dirancang berjalan di Google Colab dengan akselerasi GPU.
    Aplikasi Streamlit ini berfungsi sebagai dasbor eksplorasi hasil pemetaan biologis, penyaringan varian, dan keterbukaan metodologi.
    """)

# ==============================================================================
# HALAMAN 2: SEKUEN DREB2A & DOMAIN AP2
# ==============================================================================
elif nav_choice.startswith("2."):
    st.title("🧬 Sekuens Gen DREB2A & Domain AP2/ERF")
    st.markdown("Eksplorasi urutan nukleotida CDS *OsDREB2A* acuan (*Nipponbare*, LOC_Os01g07120) dan katalog landrace padi lokal Indonesia.")

    tab_seq, tab_landraces, tab_kmer = st.tabs(["Urutan CDS Acuan", "Katalog Landrace Lokal", "Analisis 6-mer Deskriptif"])

    with tab_seq:
        summary_list = load_preprocessing_summary()
        if summary_list:
            s = summary_list[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Panjang Nukleotida", f"{s['nt_length']} bp")
            c2.metric("Kandungan GC", f"{s['gc_percent']} %")
            c3.metric("Panjang Protein", f"{s['protein_length']} aa")
            c4.metric("Start & Stop Codon", "Valid (ATG & TAG)")

            st.markdown("#### Sekuens Domain AP2/ERF (bp 202 - 390)")
            st.code(s.get("ap2_domain_aa", "GPENSNCAYRGVRQRTWGKWVAEIREPNRGRRLWLGSFPTALEAAHAYDEAARAMYGPTARVN"), language="text")
            st.caption("Residu YRGVR (pengikat DNA inti) dan WGKWVA terletak di dalam domain ini.")

        st.markdown("#### Sekuens Lengkap CDS OsDREB2A (825 bp)")
        fasta_path = os.path.join(DATA_DIR, "processed", "Nipponbare_NM_001051515.2_cleaned.fasta")
        if os.path.exists(fasta_path):
            with open(fasta_path, "r", encoding="utf-8") as f:
                st.code(f.read(), language="fasta")

    with tab_landraces:
        st.markdown("#### Daftar Landrace Padi Lokal Indonesia (Proposal Butir 1)")
        df_acc = load_accessions_data()
        if not df_acc.empty:
            st.dataframe(df_acc, use_container_width=True, hide_index=True)
            st.caption("Sesuai etika saintifik: Aksesi yang belum terkonfirmasi di GenBank diberi tanda `[DATA BELUM TERSEDIA]` tanpa fabrikasi nomor palsu.")

    with tab_kmer:
        st.markdown("#### Analisis Tokenisasi 6-mer Overlapping (Deviasi D1)")
        st.markdown("""
        Sesuai Rumusan Masalah 1 dalam proposal, analisis oligonukleotida k-mer ($k=6, \text{stride}=1$)
        digunakan untuk memetakan frekuensi kata genomik pada lokus DREB2A.
        """)
        from phytoai.tokenization import kmerize, kmer_frequencies
        fasta_path = os.path.join(DATA_DIR, "processed", "Nipponbare_NM_001051515.2_cleaned.fasta")
        if os.path.exists(fasta_path):
            with open(fasta_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                seq = "".join(l.strip() for l in lines if not l.startswith(">"))
            kmers = kmerize(seq, k=6, stride=1)
            freqs = kmer_frequencies(kmers)
            df_kmer = pd.DataFrame(list(freqs.items()), columns=["6-mer Token", "Frekuensi"]).sort_values(by="Frekuensi", ascending=False)

            c_k1, c_k2 = st.columns([1, 2])
            with c_k1:
                st.dataframe(df_kmer.head(15), use_container_width=True, hide_index=True)
            with c_k2:
                try:
                    st.bar_chart(df_kmer.head(15).set_index("6-mer Token"))
                except Exception:
                    st.dataframe(df_kmer.head(15), use_container_width=True, hide_index=True)

# ==============================================================================
# HALAMAN 3: MUTAGENESIS SATURASI IN SILICO
# ==============================================================================
elif nav_choice.startswith("3."):
    st.title("📊 Mutagenesis Saturasi In Silico Domain AP2/ERF")
    st.markdown("""
    Evaluasi komprehensif seluruh varian substitusi nukleotida tunggal (*Single Nucleotide Variants*)
    pada domain AP2/ERF gen *OsDREB2A* (**nt 202 sampai 390**).
    Setiap posisi nukleotida memiliki 3 varian alternatif ($189 \times 3 = 567$ varian mutan).
    """)

    df_sat = load_saturation_data()
    if df_sat.empty:
        st.warning("Data hasil mutagenesis saturasi belum ditemukan. Jalankan: `python scripts/run_saturation.py --dry-run`")
    else:
        # Ringkasan Metrik
        col1, col2, col3, col4 = st.columns(4)
        total_muts = len(df_sat)
        missense_cnt = (df_sat["mutation_type"] == "missense").sum()
        synonymous_cnt = (df_sat["mutation_type"] == "synonymous").sum()
        nonsense_cnt = (df_sat["mutation_type"] == "nonsense").sum()

        col1.metric("Total Mutasi Dievaluasi", f"{total_muts} varian")
        col2.metric("Missense (Ganti AA)", f"{missense_cnt} ({missense_cnt/total_muts*100:.1f}%)")
        col3.metric("Synonymous (Basa Diam)", f"{synonymous_cnt} ({synonymous_cnt/total_muts*100:.1f}%)")
        col4.metric("Nonsense (Stop Kodon)", f"{nonsense_cnt} ({nonsense_cnt/total_muts*100:.1f}%)")

        st.markdown("---")
        st.subheader("🔍 Filter & Eksplorasi Varian Interaktif")

        f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
        with f_col1:
            mtypes = st.multiselect(
                "Tipe Mutasi:",
                options=["missense", "synonymous", "nonsense"],
                default=["missense", "synonymous", "nonsense"]
            )
        with f_col2:
            pos_range = st.slider("Rentang Koordinat Nukleotida CDS:", 202, 390, (202, 390))
        with f_col3:
            alt_filter = st.multiselect("Basa Alternatif (Mutan):", ["A", "C", "G", "T"], default=["A", "C", "G", "T"])

        # Filter Data
        filtered_df = df_sat[
            (df_sat["mutation_type"].isin(mtypes)) &
            (df_sat["position_nt"] >= pos_range[0]) &
            (df_sat["position_nt"] <= pos_range[1]) &
            (df_sat["alt"].isin(alt_filter))
        ]

        st.markdown(f"**Menampilkan {len(filtered_df)} dari {total_muts} varian:**")

        # Grafik Distribusi
        chart_col1, chart_col2 = st.columns([1, 2])
        with chart_col1:
            st.markdown("##### Komposisi Tipe Mutasi")
            type_counts = filtered_df["mutation_type"].value_counts()
            try:
                st.bar_chart(type_counts)
            except Exception:
                st.dataframe(pd.DataFrame(type_counts), use_container_width=True)

        with chart_col2:
            st.markdown("##### Sebaran Mutasi Sepanjang Koordinat Domain AP2")
            try:
                st.scatter_chart(
                    filtered_df,
                    x="position_nt",
                    y="mutation_type",
                    color="mutation_type"
                )
            except Exception:
                st.info("Visualisasi grafik interaktif memerlukan modul Altair yang kompatibel.")

        # Tabel Data
        st.dataframe(
            filtered_df[["position_nt", "ref", "alt", "mutation_type", "wt_codon", "mut_codon", "wt_aa", "mut_aa", "delta_pll"]],
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Unduh Data Varian Tersaring (CSV)",
            data=csv_data,
            file_name="phytoai_saturation_variants_filtered.csv",
            mime="text/csv"
        )

# ==============================================================================
# HALAMAN 4: CETAK BIRU KANDIDAT VARIAN
# ==============================================================================
elif nav_choice.startswith("4."):
    st.title("🎯 Cetak Biru Varian Rekayasa Genom (Candidate Blueprint)")
    st.markdown("""
    Sesuai **Proposal Butir 6**, sistem menyusun kandidat varian mutasi genetik sebagai
    cetak biru (*blueprint*) rekomendasi untuk rekayasa penyuntingan genom (*CRISPR-Cas9*) **di masa depan**.
    """)

    st.warning("""
    ⚠️ **Pernyataan Integritas Ilmiah (Deviasi D3):**
    Skor pergeseran $\Delta\text{PLL}$ adalah ukuran keselarasan tata bahasa sekuens menurut model bahasa DNA DNABERT-2 (zero-shot).
    **Bukan bukti fenotipe toleransi kekeringan riil di lapangan.**
    Nilai *Leaf Rolling Index* (LRI) tidak dikarang fiktif dan diberi status `null` sampai data eksperimen basah tersedia.
    """)

    df_sat = load_saturation_data()
    if not df_sat.empty:
        # Tampilkan kandidat missense non-disruptif pada residu kritis
        missense_df = df_sat[df_sat["mutation_type"] == "missense"].copy()
        missense_df["status_saintifik"] = "kandidat zero-shot (bukan Beneficial terverifikasi)"
        missense_df["predicted_lri"] = "[BELUM DILATIH: butuh data fenotipe basah]"

        st.subheader("📋 Daftar Varian Kandidat Missense Domain AP2/ERF")
        st.dataframe(
            missense_df[["position_nt", "ref", "alt", "wt_codon", "mut_codon", "wt_aa", "mut_aa", "status_saintifik", "predicted_lri"]].head(25),
            use_container_width=True,
            hide_index=True
        )

        st.info("""
        🔬 **Protokol Validasi Lanjutan yang Direkomendasikan:**
        1. **Wet-Lab Validation:** Pengujian kultur jaringan bibit padi di bawah cekaman PEG-6000 (0%, 10%, 20%) untuk mengukur LRI aktual.
        2. **Target Base Editing CRISPR:** Desain sgRNA dan seleksi jendela penyuntingan basa (Adenine / Cytosine Base Editor) pada koordinat di atas.
        """)

# ==============================================================================
# HALAMAN 5: GOOGLE COLAB & DNABERT-2
# ==============================================================================
elif nav_choice.startswith("5."):
    st.title("🚀 Google Colab & Pemodelan DNABERT-2")
    st.markdown("""
    Sesuai **Proposal Butir 7**, lingkungan kerja komputasi utama untuk model pondasi transformer
    adalah **Python di Google Colab** dengan akselerasi GPU NVIDIA (T4/V100/A100).
    """)

    st.success(f"""
    **Notebook Riset Resmi Telah Tersedia!**
    Seluruh 7 langkah pipeline proposal dapat dijalankan secara interaktif dan mandiri:
    👉 [**Buka Notebook di Google Colab**]({COLAB_URL})
    """)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Mengapa GPU Google Colab?")
        st.markdown("""
        - **Bobot Model 117 Juta Parameter:** DNABERT-2 memerlukan memori VRAM GPU untuk operasi tensor multi-head attention.
        - **Bypass Limitasi Streamlit Cloud:** Streamlit Community Cloud berjalan pada kontainer CPU standar (RAM ~1GB) yang tidak didesain untuk beban inferensi neural berat.
        - **Skoring PLL Cepat:** Komputasi pergeseran pseudo-log-likelihood untuk 567 mutasi selesai dalam hitungan detik pada GPU T4 Colab.
        """)
    with c2:
        st.markdown("#### Alur Eksekusi di Colab:")
        st.markdown("""
        1. **Langkah 1:** Instalasi dependensi PyTorch & Transformers + GPU check
        2. **Langkah 2:** Pemuatan sekuens acuan *OsDREB2A* (825 bp CDS)
        3. **Langkah 3:** Translasi asam amino & tokenisasi k-mer 6-mer
        4. **Langkah 4:** Pemuatan DNABERT-2 & ekstraksi embedding 768-D
        5. **Langkah 5:** Mutagenesis saturasi AP2 & kalkulasi $\Delta\text{PLL}$
        6. **Langkah 6:** Visualisasi scatter plot pergeseran pseudo-perplexity
        7. **Langkah 7:** Penyusunan cetak biru varian kandidat
        """)

    st.markdown("---")
    st.markdown("#### Cuplikan Kode Notebook Colab (Langkah 4 & 5)")
    st.code("""
# Memuat model transformer DNABERT-2 117M
from transformers import AutoTokenizer, AutoModelForMaskedLM

MODEL_NAME = "zhihan1996/DNABERT-2-117M"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME, trust_remote_code=True).to("cuda")

# Menghitung delta PLL pada posisi target domain AP2/ERF
# delta_pll = PLL(sekuens_mutan) - PLL(sekuens_wildtype)
    """, language="python")

# ==============================================================================
# HALAMAN 6: INTEGRITAS & DEVIASI SAINTIFIK
# ==============================================================================
elif nav_choice.startswith("6."):
    st.title("📑 Integritas Ilmiah & Deviasi Saintifik")
    st.markdown("""
    Dokumentasi resmi seluruh deviasi metodologis antara naskah awal proposal dengan implementasi
    komputasi aktual (tercantum lengkap di `DEVIATIONS.md`).
    """)

    st.markdown("""
    | Kode | Aspek Metodologi | Pernyataan Proposal | Implementasi Aktual Repositori | Alasan Saintifik & Rekomendasi Revisi Proposal |
    |---|---|---|---|---|
    | **D1** | **Tokenisasi Sekuens** | k-mer (k=6, stride=1) | Byte Pair Encoding (BPE) bawaan DNABERT-2 + Utilitas k-mer deskriptif | Model DNABERT-2 tidak menggunakan k-mer 6 overlapping melainkan BPE (~4096 token). |
    | **D2** | **Metrik Perplexity** | Pergeseran Perplexity | Pseudo-Log-Likelihood (PLL) & Pseudo-Perplexity | DNABERT-2 adalah Masked Language Model (MLM), bukan autoregresif kausal. Perplexity standar tidak valid secara matematis. |
    | **D3** | **Prediksi LRI & Klasifikasi** | Dual-prediction head terlatih untuk varian & LRI | Arsitektur MLP dibangun; Pelatihan dikunci ketat (Gating) hingga data fenotipe riil tersedia | Proposal tidak menyertakan dataset fenotipe empiris. Menolak melatih dengan data fiktif. |
    """)

    st.markdown("---")
    st.markdown("#### Isi Lengkap `DEVIATIONS.md`")
    if os.path.exists(DEVIATIONS_MD):
        with open(DEVIATIONS_MD, "r", encoding="utf-8") as f:
            st.markdown(f.read())

st.markdown("---")
st.caption("🌾 **PhytoAI-Genetics v2.0** | Penelitian Kolaborasi Sains MA Salafiyah Kajen Pati | Berbasis Model Fondasi DNABERT-2")
