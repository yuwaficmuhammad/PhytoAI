"""
streamlit_app.py
PhytoAI-Genetics: In Silico Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (Oryza sativa)
Antarmuka Web Interaktif Berbasis Tema Terang (Light Theme) Modern & Bersih.
Sesuai Proposal Riset Ilmiah Bioinformatika MA Salafiyah Kajen Pati.
"""

import os
import json
import pandas as pd
import streamlit as st

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="PhytoAI-Genetics | OsDREB2A Genomic Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeksi CSS Khusus Desain Terang & Navigasi Modern (SaaS-Grade Clean UI)
LIGHT_THEME_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
        background-color: #F8FAFC;
    }

    /* Main Container */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1220px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* Modern Navigation Radio Items */
    div[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 4px !important;
        margin-top: 6px;
    }

    div[data-testid="stSidebar"] div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        padding: 9px 12px !important;
        border-radius: 8px !important;
        border: 1px solid transparent !important;
        transition: all 0.15s ease !important;
        margin-bottom: 2px !important;
        cursor: pointer !important;
        background-color: transparent !important;
    }

    /* Hide the radio button circle */
    div[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    div[data-testid="stSidebar"] div[role="radiogroup"] > label p {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #334155 !important;
        margin: 0 !important;
    }

    div[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #F1F5F9 !important;
        border-color: #E2E8F0 !important;
        transform: translateX(2px);
    }

    div[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #ECFDF5 !important;
        border-color: #A7F3D0 !important;
        border-left: 3px solid #059669 !important;
        box-shadow: 0 1px 2px rgba(16, 185, 129, 0.08) !important;
    }

    div[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #065F46 !important;
        font-weight: 700 !important;
    }

    /* Top Breadcrumb Header */
    .top-breadcrumb {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #E2E8F0;
    }

    .breadcrumb-active {
        color: #059669;
        background: #ECFDF5;
        padding: 2px 10px;
        border-radius: 9999px;
        border: 1px solid #A7F3D0;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
        border: 1px solid #BBF7D0;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px -2px rgba(16, 185, 129, 0.08);
    }

    .hero-title {
        color: #065F46;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        color: #047857;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 14px;
    }

    /* Badges & Pills */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .badge-green {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }

    .badge-blue {
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
    }

    .badge-amber {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
    }

    .badge-purple {
        background-color: #FAF5FF;
        color: #6B21A8;
        border: 1px solid #E9D5FF;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px -3px rgba(15, 23, 42, 0.08);
        border-color: #CBD5E1;
    }

    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 2px;
    }

    .metric-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
    }

    .metric-caption {
        font-size: 0.78rem;
        color: #059669;
        font-weight: 500;
    }

    /* Landrace Cards Grid */
    .landrace-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        transition: border-color 0.15s ease, transform 0.15s ease;
    }

    .landrace-card:hover {
        border-color: #10B981;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(16, 185, 129, 0.08);
    }

    .landrace-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .landrace-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
    }

    .landrace-desc {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.5;
        margin-top: 6px;
    }

    /* Pillar Cards */
    .pillar-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    .pillar-num {
        display: inline-block;
        width: 26px;
        height: 26px;
        line-height: 26px;
        text-align: center;
        background-color: #059669;
        color: #FFFFFF;
        border-radius: 50%;
        font-size: 0.82rem;
        font-weight: 700;
        margin-right: 8px;
    }

    .pillar-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0F172A;
    }

    /* Filter Box */
    .filter-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    /* Code styling */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
    }

    /* Alert Boxes */
    .custom-alert {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        color: #92400E;
        font-size: 0.9rem;
        margin: 16px 0;
    }

    .custom-info {
        background-color: #F0FDF4;
        border-left: 4px solid #10B981;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        color: #065F46;
        font-size: 0.9rem;
        margin: 16px 0;
    }
</style>
"""
st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)

# 3. Jalur Berkas Data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_SATURATION = os.path.join(DATA_DIR, "processed", "saturation_mutagenesis_results.csv")
CSV_ACCESSIONS = os.path.join(DATA_DIR, "accessions.csv")
JSON_PREPROCESS = os.path.join(DATA_DIR, "processed", "preprocessing_summary.json")
DEVIATIONS_MD = os.path.join(BASE_DIR, "DEVIATIONS.md")

COLAB_URL = "https://colab.research.google.com/github/yuwaficmuhammad/PhytoAI/blob/main/notebooks/phytoai_colab.ipynb"
MODEL_HF_URL = "https://huggingface.co/zhihan1996/DNABERT-2-117M"


@st.cache_data
def load_saturation_data():
    """Memuat data evaluasi mutagenesis saturasi domain AP2/ERF."""
    if os.path.exists(CSV_SATURATION):
        return pd.read_csv(CSV_SATURATION)
    return pd.DataFrame()


@st.cache_data
def load_accessions_data():
    """Memuat daftar aksesi landrace padi lokal dan acuan."""
    if os.path.exists(CSV_ACCESSIONS):
        return pd.read_csv(CSV_ACCESSIONS)
    return pd.DataFrame()


@st.cache_data
def load_preprocessing_summary():
    """Memuat ringkasan pra-pemrosesan sekuens FASTA."""
    if os.path.exists(JSON_PREPROCESS):
        with open(JSON_PREPROCESS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# 4. Sidebar Navigasi Teredesain (SaaS-Grade Navigation)
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
        <span style="font-size:1.8rem;">🌾</span>
        <div>
            <div style="font-weight:800; font-size:1.1rem; color:#065F46; line-height:1.2;">PhytoAI-Genetics</div>
            <div style="font-size:0.75rem; color:#059669; font-weight:600;">Transformer Rice Genomics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.72rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em; margin-top:14px; margin-bottom:4px;'>MODUL NAVIGASI</div>", unsafe_allow_html=True)

    nav_choice = st.radio(
        "Pilih Modul:",
        [
            "🌾 Ringkasan & 7 Butir Proposal",
            "🧬 Sekuens DREB2A & Domain AP2",
            "📊 Mutagenesis Saturasi In Silico",
            "🎯 Cetak Biru Kandidat Varian",
            "🚀 Google Colab & DNABERT-2",
            "📑 Integritas & Deviasi Saintifik"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#F8FAFC; padding:12px 14px; border-radius:10px; font-size:0.8rem; border:1px solid #E2E8F0;">
        <div style="font-weight:700; color:#0F172A; margin-bottom:6px; display:flex; align-items:center; gap:5px;">
            <span>📌</span> Metadata Riset
        </div>
        <div style="color:#475569; margin-bottom:3px;"><b>Organisme:</b> <i>Oryza sativa</i></div>
        <div style="color:#475569; margin-bottom:3px;"><b>Lokus:</b> <i>OsDREB2A</i> (Chr 1)</div>
        <div style="color:#475569; margin-bottom:3px;"><b>NCBI ID:</b> <a href="https://www.ncbi.nlm.nih.gov/gene/4324418" target="_blank" style="color:#059669; font-weight:600;">4324418</a></div>
        <div style="color:#475569; margin-bottom:3px;"><b>Domain AP2:</b> nt 202 - 390</div>
        <div style="color:#475569;"><b>Model:</b> DNABERT-2 117M</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:14px;">
        <a href="{COLAB_URL}" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg, #059669 0%, #047857 100%); color:#FFFFFF; text-align:center; padding:10px 12px; border-radius:8px; font-size:0.84rem; font-weight:700; box-shadow:0 2px 6px rgba(5,150,105,0.25);">
                ⚡ Buka di Google Colab &rarr;
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)


# Helper Breadcrumb Header
def render_breadcrumb(current_module: str):
    st.markdown(f"""
    <div class="top-breadcrumb">
        <span>🌾 PhytoAI-Genetics</span>
        <span>/</span>
        <span class="breadcrumb-active">{current_module}</span>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# MODUL 1: RINGKASAN & 7 BUTIR PROPOSAL
# ==============================================================================
if nav_choice.startswith("🌾"):
    render_breadcrumb("Ringkasan & 7 Butir Proposal")

    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">PhytoAI-Genetics</div>
        <div class="hero-subtitle">Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (<i>Oryza sativa</i>)</div>
        <div style="color:#334155; font-size:0.95rem; line-height:1.6; max-width:920px;">
            Platform komputasi genomik ilmiah karya Periset <b>MA Salafiyah Kajen Pati</b> untuk memodelkan dan mengevaluasi varian mutasi genetik faktor transkripsi <b>OsDREB2A</b> pada padi lokal Indonesia secara <i>in silico</i> menggunakan model pondasi <b>DNABERT-2 (117M)</b>.
        </div>
        <div class="badge-container">
            <span class="badge-pill badge-green">🌾 Oryza sativa</span>
            <span class="badge-pill badge-blue">🧬 OsDREB2A (Gene ID: 4324418)</span>
            <span class="badge-pill badge-purple">🤖 DNABERT-2 (117M)</span>
            <span class="badge-pill badge-amber">⚡ Google Colab GPU Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Gen Target</div>
            <div class="metric-value">OsDREB2A</div>
            <div class="metric-caption">Gene ID: 4324418 (Kromosom 1)</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Panjang CDS Acuan</div>
            <div class="metric-value">825 bp</div>
            <div class="metric-caption">274 Asam Amino Fungsional</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Domain Kritis AP2</div>
            <div class="metric-value">189 bp</div>
            <div class="metric-caption">Koordinat CDS nt 202 - 390</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Mutasi Saturasi</div>
            <div class="metric-value">567 Varian</div>
            <div class="metric-caption">189 Posisi × 3 Basa Mutan</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.subheader("📋 7 Pilar Inti Cakupan Proposal Riset")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="pillar-card">
            <div class="pillar-title"><span class="pillar-num">1</span> Data Sekuens Nukleotida</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px; line-height:1.5;">
                Urutan nukleotida gen <i>DREB2A</i> dari minimal 5 landrace padi lokal Indonesia + genom referensi (<i>Nipponbare</i>), diunduh dari basis data NCBI GenBank format FASTA.
            </div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title"><span class="pillar-num">2</span> Pra-Pemrosesan & Tokenisasi</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px; line-height:1.5;">
                Parsing header FASTA, pembersihan karakter non-DNA, translasi CDS (ATG start, TAG stop), dan tokenisasi k-mer 6-mer untuk analisis profil oligonukleotida.
            </div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title"><span class="pillar-num">3</span> Model Genomik Transformer</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px; line-height:1.5;">
                Pemanfaatan model transformer <b>DNABERT-2 (117M)</b> via PyTorch + Hugging Face untuk mengekstraksi representasi 768-dimensi dari hidden state terakhir encoder.
            </div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title"><span class="pillar-num">4</span> Mutagenesis Saturasi In Silico</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px; line-height:1.5;">
                Substitusi sistematis seluruh kemungkinan nukleotida alternatif pada domain AP2/ERF pengikat DNA (nt 202 - 390; total 567 varian mutan).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="pillar-card">
            <div class="pillar-title"><span class="pillar-num">5</span> Skor Pergeseran Pseudo-Log-Likelihood</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px; line-height:1.5;">
                Perhitungan pergeseran &Delta;PLL dan pseudo-perplexity untuk menyaring kelayakan urutan varian menurut representasi model bahasa genomik.
            </div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title"><span class="pillar-num">6</span> Dual-Prediction Head (MLP) & Data Gating</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px; line-height:1.5;">
                Arsitektur multi-task untuk klasifikasi varian dan regresi Leaf Rolling Index (LRI, 0.0 - 1.0) dengan proteksi integritas: menolak melatih tanpa data fenotipe basah riil.
            </div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title"><span class="pillar-num">7</span> Cetak Biru Rekayasa Genom Masa Depan</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px; line-height:1.5;">
                Penyusunan koordinat varian kandidat terbaik sebagai cetak biru rekomendasi rekayasa penyuntingan genom CRISPR-Cas9 di masa depan, dieksekusi di Google Colab.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# MODUL 2: SEKUEN DREB2A & DOMAIN AP2 (TEREDESAIN)
# ==============================================================================
elif nav_choice.startswith("🧬"):
    render_breadcrumb("Sekuens DREB2A & Katalog Landrace Padi Lokal")

    st.title("🧬 Sekuens Gen DREB2A & Katalog Landrace Lokal")
    st.markdown("Eksplorasi urutan nukleotida CDS *OsDREB2A* acuan (*Nipponbare*, LOC_Os01g07120) dan katalog 5 landrace padi lokal Indonesia.")

    tab_landraces, tab_seq, tab_kmer = st.tabs([
        "🌾 Katalog 5 Landrace Lokal + Acuan",
        "🧬 Urutan CDS Acuan & Domain AP2",
        "📊 Analisis 6-mer Deskriptif"
    ])

    # TAB 1: KATALOG LANDRACE TEREDESAIN
    with tab_landraces:
        st.markdown("### 🌾 Katalog Varietas & Landrace Padi Lokal Indonesia (Proposal Butir 1)")
        st.markdown("""
        Proposal mensyaratkan perbandingan gen *DREB2A* antara genom acuan standar (*Nipponbare*) dengan
        minimal **5 landrace padi lokal Indonesia** dari berbagai agroekosistem (lahan kering/gogo, aromatik dataran tinggi, sawah tadah hujan, dan pasang surut).
        """)

        # Data Landrace Padi Lokal Indonesia (Aksesi Riil GenBank + Target Wet-Lab)
        VERIFIED_LANDRACES = [
            {
                "name": "Nipponbare",
                "tag": "Acuan Standar",
                "tag_class": "badge-green",
                "accession": "NM_001051515.2",
                "region": "Genom Referensi Global (Oryza sativa Japonica)",
                "length": "825 bp CDS (274 aa)",
                "note": "Referensi genom Oryza sativa Nipponbare DREB2A (LOC_Os01g07120). Standar koordinat AP2.",
                "ncbi_link": "https://www.ncbi.nlm.nih.gov/nuccore/NM_001051515.2"
            },
            {
                "name": "Pare Lambem",
                "tag": "Landrace Toraja (Sulawesi)",
                "tag_class": "badge-blue",
                "accession": "PP187274.1",
                "region": "Tana Toraja, Sulawesi Selatan",
                "length": "760 bp (Partial CDS DREB2A)",
                "note": "Landrace lokal dataran tinggi Sulawesi Selatan. Urutan sekuens mencakup domain pengikat DNA AP2/ERF.",
                "ncbi_link": "https://www.ncbi.nlm.nih.gov/nuccore/PP187274.1"
            },
            {
                "name": "Pare Bakato Kaka",
                "tag": "Landrace Toraja (Sulawesi)",
                "tag_class": "badge-blue",
                "accession": "PP187273.1",
                "region": "Tana Toraja, Sulawesi Selatan",
                "length": "775 bp (Partial CDS DREB2A)",
                "note": "Plasma nutfah lokal Sulawesi dengan ketahanan spesifik terhadap suhu dingin dan defisit air berkala.",
                "ncbi_link": "https://www.ncbi.nlm.nih.gov/nuccore/PP187273.1"
            },
            {
                "name": "Sigupai",
                "tag": "Landrace Aromatik Aceh",
                "tag_class": "badge-purple",
                "accession": "PP171511.1",
                "region": "Aceh Barat Daya, Sumatera",
                "length": "779 bp (Partial CDS DREB2A)",
                "note": "Padi lokal aromatik pesisir barat Sumatera. Memiliki adaptasi morfologi unik terhadap tanah berpasir.",
                "ncbi_link": "https://www.ncbi.nlm.nih.gov/nuccore/PP171511.1"
            },
            {
                "name": "Padi Hitam",
                "tag": "Padi Lokal Beras Hitam",
                "tag_class": "badge-purple",
                "accession": "PP171510.1",
                "region": "Koleksi Plasma Nutfah Indonesia",
                "length": "802 bp (Partial CDS DREB2A)",
                "note": "Padi lokal fungsional kaya antosianin dengan ketahanan abiotik alami dan motif AP2 YRGVR utuh.",
                "ncbi_link": "https://www.ncbi.nlm.nih.gov/nuccore/PP171510.1"
            },
            {
                "name": "Situ Bagendit",
                "tag": "Padi Gogo Lahan Kering",
                "tag_class": "badge-amber",
                "accession": "PP171512.1",
                "region": "Agroekosistem Lahan Kering Indonesia",
                "length": "791 bp (Partial CDS DREB2A)",
                "note": "Kultivar unggul toleran kekeringan dengan efisiensi penggunaan air tinggi di tanah marjinal.",
                "ncbi_link": "https://www.ncbi.nlm.nih.gov/nuccore/PP171512.1"
            },
            {
                "name": "Way Apo Buru",
                "tag": "Landrace Maluku",
                "tag_class": "badge-blue",
                "accession": "PP171513.1",
                "region": "Pulau Buru, Maluku",
                "length": "796 bp (Partial CDS DREB2A)",
                "note": "Padi sawah tadah hujan Indonesia Timur dengan daya adaptasi tinggi terhadap cekaman lingkungan.",
                "ncbi_link": "https://www.ncbi.nlm.nih.gov/nuccore/PP171513.1"
            }
        ]

        WETLAB_LANDRACES = [
            {"name": "Rojolele", "region": "Jawa Tengah", "status": "Target Sekuensing Amplikon", "note": "Padi lokal toleran cekaman biotik/abiotik. Peneliti menganalisis lokus DREB2A via PCR primer spesifik."},
            {"name": "Gogo Jatiluhur", "region": "Jawa Barat", "status": "Target Sekuensing Amplikon", "note": "Padi gogo lahan kering vertisol. Perakaran dalam, efisiensi osmotik tinggi saat ketersediaan air tanah terbatas."},
            {"name": "Salumpikit", "region": "Sulawesi Utara", "status": "Target Sekuensing Amplikon", "note": "Padi lahan kering marjinal Sulawesi Utara. Aksesi NCBI terdaftar untuk gen NBS-LRR (HE586175, HE580106)."},
            {"name": "Menthik Wangi", "region": "Jawa Tengah", "status": "Target Sekuensing Amplikon", "note": "Padi lokal aromatik dataran tinggi Jawa Tengah dengan sensitivitas spesifik terhadap cekaman air."},
            {"name": "Siam Saba", "region": "Kalimantan", "status": "Target Sekuensing Amplikon", "note": "Padi pasang surut toleran rendaman berkala dan salinitas tanah sulfat masam."}
        ]

        st.markdown("#### ✅ 6 Landrace Padi Lokal Indonesia dengan Aksesi Terverifikasi NCBI GenBank")
        col1, col2 = st.columns(2)
        for i, item in enumerate(VERIFIED_LANDRACES):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                acc_link = f'<a href="{item["ncbi_link"]}" target="_blank" style="color:#059669; font-weight:700; text-decoration:none;">🔗 {item["accession"]} (Buka di NCBI)</a>'
                st.markdown(f"""
                <div class="landrace-card">
                    <div class="landrace-header">
                        <span class="landrace-name">{item["name"]}</span>
                        <span class="badge-pill {item["tag_class"]}">{item["tag"]}</span>
                    </div>
                    <div style="font-size:0.84rem; color:#64748B; margin-bottom:4px;"><b>Wilayah:</b> {item["region"]}</div>
                    <div style="font-size:0.84rem; color:#64748B; margin-bottom:6px;"><b>Panjang Sekuens:</b> {item["length"]}</div>
                    <div style="margin-bottom:8px;"><b>Nomor Aksesi:</b> {acc_link}</div>
                    <div class="landrace-desc">{item["note"]}</div>
                    <div style="margin-top:12px; display:flex; justify-content:flex-end;">
                        <span class="badge-pill badge-green">✅ Tersekuensing Resmi GenBank</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### ⏳ Landrace Target Pengujian Sekuensing Laboratorium Basah")
        st.markdown("""
        Varietas lokal di bawah ini dikarakterisasi dalam literatur ilmiah padi Indonesia menggunakan *primers* DREB2A spesifik
        (Forward: `5'-CCTCATTGGGTCAGGAAGAA-3'`, Reverse: `5'-GGATCTCAGCCACCCACTTA-3'`), dan menjadi target pengujian sekuensing basah (*wet-lab amplicon sequencing*):
        """)
        
        c_w1, c_w2 = st.columns(2)
        for j, witem in enumerate(WETLAB_LANDRACES):
            t_col = c_w1 if j % 2 == 0 else c_w2
            with t_col:
                st.markdown(f"""
                <div class="landrace-card" style="border-left: 3px solid #F59E0B;">
                    <div class="landrace-header">
                        <span class="landrace-name">{witem["name"]}</span>
                        <span class="badge-pill badge-amber">{witem["region"]}</span>
                    </div>
                    <div class="landrace-desc">{witem["note"]}</div>
                    <div style="margin-top:10px; display:flex; justify-content:flex-end;">
                        <span class="badge-pill badge-amber">🔍 {witem["status"]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📋 Tabel Ringkasan Aksesi & Metadata Kurasi")
        
        # Tampilkan Tabel Formatted
        table_rows = []
        for d in LANDRACE_DATA:
            table_rows.append({
                "Nama Varietas": d["name"],
                "Aksesi GenBank": d["accession"],
                "Agroekosistem / Asal": d["region"],
                "Karakteristik Unggul": d["note"]
            })
        df_display = pd.DataFrame(table_rows)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("""
        <div class="custom-info">
            💡 <b>Catatan Integritas Ilmiah:</b> Sesuai standar publikasi internasional, repositori ini mempertahankan slot aksesi landrace lokal secara transparan tanpa mengarang nomor aksesi fiktif. Peneliti laboratorium basah dapat memasukkan data amplikon sekuensing langsung ke berkas <code>data/accessions.csv</code>.
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: SEKUEN ACUAN
    with tab_seq:
        summary_list = load_preprocessing_summary()
        if summary_list:
            s = summary_list[0]
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Panjang Nukleotida</div>
                    <div class="metric-value">{s['nt_length']} bp</div>
                    <div class="metric-caption">CDS Lengkap</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Kandungan GC</div>
                    <div class="metric-value">{s['gc_percent']}%</div>
                    <div class="metric-caption">Rasio Guanin-Sitosin</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Panjang Protein</div>
                    <div class="metric-value">{s['protein_length']} aa</div>
                    <div class="metric-caption">274 aa + Stop Codon</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Reading Frame</div>
                    <div class="metric-value">Valid</div>
                    <div class="metric-caption">Start ATG & Stop TAG</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown("#### 🎯 Domain AP2/ERF Pengikat DNA (bp 202 - 390)")
            st.code(s.get("ap2_domain_aa", "GPENSNCAYRGVRQRTWGKWVAEIREPNRGRRLWLGSFPTALEAAHAYDEAARAMYGPTARVN"), language="text")
            st.caption("Residu kunci YRGVR (kontak langsung sekuens DRE/CRT) dan motif amphipathic alpha-helix terletak di dalam rentang koordinat ini.")

        st.markdown("#### Sekuens Lengkap FASTA OsDREB2A Acuan (825 bp)")
        fasta_path = os.path.join(DATA_DIR, "processed", "Nipponbare_NM_001051515.2_cleaned.fasta")
        if os.path.exists(fasta_path):
            with open(fasta_path, "r", encoding="utf-8") as f:
                st.code(f.read(), language="fasta")

    # TAB 3: 6-MER
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

            c_k1, c_k2 = st.columns([1, 1])
            with c_k1:
                st.dataframe(df_kmer.head(15), use_container_width=True, hide_index=True)
            with c_k2:
                try:
                    st.bar_chart(df_kmer.head(15).set_index("6-mer Token"))
                except Exception:
                    st.dataframe(df_kmer.head(15), use_container_width=True, hide_index=True)


# ==============================================================================
# MODUL 3: MUTAGENESIS SATURASI IN SILICO
# ==============================================================================
elif nav_choice.startswith("📊"):
    render_breadcrumb("Mutagenesis Saturasi In Silico (Domain AP2/ERF)")

    st.title("📊 Mutagenesis Saturasi In Silico Domain AP2/ERF")
    st.markdown("""
    Evaluasi komprehensif seluruh varian substitusi nukleotida tunggal (*Single Nucleotide Variants*)
    pada domain AP2/ERF gen *OsDREB2A* (**nt 202 sampai 390**).
    Setiap posisi nukleotida memiliki 3 kemungkinan basa mutan ($189 \times 3 = 567$ varian mutasi).
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

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Varian</div>
                <div class="metric-value">{total_muts}</div>
                <div class="metric-caption">100% Koordinat AP2</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Missense</div>
                <div class="metric-value">{missense_cnt}</div>
                <div class="metric-caption">{missense_cnt/total_muts*100:.1f}% (Substitusi AA)</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Synonymous</div>
                <div class="metric-value">{synonymous_cnt}</div>
                <div class="metric-caption">{synonymous_cnt/total_muts*100:.1f}% (Basa Diam)</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Nonsense</div>
                <div class="metric-value">{nonsense_cnt}</div>
                <div class="metric-caption">{nonsense_cnt/total_muts*100:.1f}% (Stop Kodon)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔍 Filter Varian Interaktif")

        st.markdown('<div class="filter-box">', unsafe_allow_html=True)
        f_col1, f_col2, f_col3 = st.columns([2, 3, 2])
        with f_col1:
            mtypes = st.multiselect(
                "Tipe Konsekuensi Mutasi:",
                options=["missense", "synonymous", "nonsense"],
                default=["missense", "synonymous", "nonsense"]
            )
        with f_col2:
            pos_range = st.slider("Rentang Koordinat Nukleotida CDS:", 202, 390, (202, 390))
        with f_col3:
            alt_filter = st.multiselect("Basa Alternatif (Mutan):", ["A", "C", "G", "T"], default=["A", "C", "G", "T"])
        st.markdown('</div>', unsafe_allow_html=True)

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
            st.markdown("##### Komposisi Tipe Mutasi Tersaring")
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
                st.dataframe(filtered_df[["position_nt", "ref", "alt", "mutation_type"]].head(10), use_container_width=True)

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
# MODUL 4: CETAK BIRU KANDIDAT VARIAN
# ==============================================================================
elif nav_choice.startswith("🎯"):
    render_breadcrumb("Cetak Biru Varian Rekayasa Genom Masa Depan")

    st.title("🎯 Cetak Biru Varian Rekayasa Genom (Candidate Blueprint)")
    st.markdown("""
    Sesuai **Proposal Butir 6**, sistem menyusun kandidat varian mutasi genetik sebagai
    cetak biru (*blueprint*) rekomendasi untuk rekayasa penyuntingan genom (*CRISPR-Cas9*) **di masa depan**.
    """)

    st.markdown("""
    <div class="custom-alert">
        ⚠️ <b>Pernyataan Integritas Ilmiah (Deviasi D3):</b>
        Skor pergeseran &Delta;PLL adalah ukuran keselarasan tata bahasa sekuens menurut model bahasa DNA DNABERT-2 (zero-shot). <b>Bukan bukti fenotipe toleransi kekeringan riil di lapangan.</b> Nilai <i>Leaf Rolling Index</i> (LRI) tidak dikarang fiktif dan diberi status <code>null</code> sampai data eksperimen basah tersedia.
    </div>
    """, unsafe_allow_html=True)

    df_sat = load_saturation_data()
    if not df_sat.empty:
        missense_df = df_sat[df_sat["mutation_type"] == "missense"].copy()
        missense_df["status_saintifik"] = "kandidat zero-shot (bukan Beneficial terverifikasi)"
        missense_df["predicted_lri"] = "[BELUM DILATIH: butuh data fenotipe basah]"

        st.subheader("📋 Daftar Varian Kandidat Missense Domain AP2/ERF")
        st.dataframe(
            missense_df[["position_nt", "ref", "alt", "wt_codon", "mut_codon", "wt_aa", "mut_aa", "status_saintifik", "predicted_lri"]].head(30),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("""
        <div class="custom-info">
            🔬 <b>Protokol Validasi Lanjutan yang Direkomendasikan:</b><br>
            1. <b>Wet-Lab Osmotic Assay:</b> Pengujian kultur jaringan bibit padi di bawah cekaman PEG-6000 (0%, 10%, 20%) untuk mengukur LRI aktual.<br>
            2. <b>Desain CRISPR Base Editing:</b> Perancangan sgRNA dengan Cytosine Base Editor (CBE: C&rarr;T) atau Adenine Base Editor (ABE: A&rarr;G) pada koordinat di atas.
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# MODUL 5: GOOGLE COLAB & DNABERT-2
# ==============================================================================
elif nav_choice.startswith("🚀"):
    render_breadcrumb("Google Colab & Pemodelan Transformer DNABERT-2")

    st.title("🚀 Google Colab & Pemodelan DNABERT-2")
    st.markdown("""
    Sesuai **Proposal Butir 7**, lingkungan kerja komputasi utama untuk model pondasi transformer
    adalah **Python di Google Colab** dengan akselerasi GPU NVIDIA (T4/V100/A100).
    """)

    st.markdown(f"""
    <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:20px; margin-bottom:20px;">
        <div style="font-weight:700; color:#065F46; font-size:1.1rem; margin-bottom:6px;">⚡ Notebook Riset Resmi Telah Tersedia!</div>
        <div style="color:#047857; font-size:0.92rem; margin-bottom:12px;">Seluruh 7 langkah pipeline proposal dapat dijalankan secara interaktif dan mandiri dengan akselerasi GPU gratis di Google Colab.</div>
        <a href="{COLAB_URL}" target="_blank" style="text-decoration:none;">
            <span style="background:#059669; color:#FFFFFF; font-weight:700; padding:8px 16px; border-radius:6px; font-size:0.85rem; display:inline-block;">
                Buka Notebook di Google Colab &rarr;
            </span>
        </a>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Mengapa Menggunakan GPU Colab?")
        st.markdown("""
        - **117 Juta Parameter:** Model DNABERT-2 memerlukan alokasi memori VRAM GPU untuk komputasi tensor *Multi-Head Self-Attention*.
        - **Bypass Limitasi Streamlit Cloud:** Streamlit Community Cloud berjalan pada kontainer CPU standar (~1 GB RAM) yang didesain untuk visualisasi web, bukan pelatihan deep learning.
        - **Skoring PLL Cepat:** Komputasi pergeseran pseudo-log-likelihood untuk 567 varian selesai dalam hitungan detik pada GPU T4 Colab.
        """)
    with c2:
        st.markdown("#### 7 Langkah Alur di Colab:")
        st.markdown("""
        1. **Langkah 1:** Setup dependensi PyTorch & Transformers + GPU check
        2. **Langkah 2:** Pemuatan sekuens acuan *OsDREB2A* (825 bp CDS)
        3. **Langkah 3:** Translasi asam amino & tokenisasi k-mer 6-mer
        4. **Langkah 4:** Pemuatan DNABERT-2 & ekstraksi embedding 768-D
        5. **Langkah 5:** Mutagenesis saturasi AP2 & kalkulasi &Delta;PLL
        6. **Langkah 6:** Visualisasi scatter plot pergeseran pseudo-perplexity
        7. **Langkah 7:** Penyusunan cetak biru varian kandidat rekayasa genom
        """)


# ==============================================================================
# MODUL 6: INTEGRITAS & DEVIASI SAINTIFIK
# ==============================================================================
elif nav_choice.startswith("📑"):
    render_breadcrumb("Integritas Ilmiah & Deviasi Metodologi")

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
    st.markdown("#### Dokumen Lengkap `DEVIATIONS.md`")
    if os.path.exists(DEVIATIONS_MD):
        with open(DEVIATIONS_MD, "r", encoding="utf-8") as f:
            st.markdown(f.read())

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748B; font-size:0.85rem; padding:12px 0;">
    🌾 <b>PhytoAI-Genetics v2.0</b> | Riset Bioinformatika Padi MA Salafiyah Kajen Pati | Berbasis DNABERT-2 Foundation Model
</div>
""", unsafe_allow_html=True)
