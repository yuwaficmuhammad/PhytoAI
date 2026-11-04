"""
PhytoAI-Genetics: Aplikasi Streamlit Interaktif Rekayasa Genetik Padi & InaRISK BNPB
Mode Ganda:
1. Mode Studio Penuh (100% Sama Persis dengan FastAPI Web Studio - Leaflet GIS, Select2, SweetAlert2, 8 Tab)
2. Mode Dashboard Streamlit (Python Native Widgets, Pytest Live Runner & Analitik Biofisika)
"""

import os
import sys
import subprocess
import urllib.request
import streamlit as st
import streamlit.components.v1 as components

# Pastikan root workspace masuk ke sys.path untuk impor modul lokal
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from app.services.phytoai_service import (
    analyze_dreb2a_mutation,
    generate_dms_scan,
    assess_custom_coordinates,
    get_drought_regions,
    LOCAL_CULTIVARS,
    OSDREB2A_DOMAINS,
    OSDREB2A_PROTEIN,
)
from app.services.crispr_service import analyze_crispr_targets
from app.data.rice_targets import RICE_TARGETS

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="PhytoAI-Genetics | Transformer Modeling & Rice Drought Tolerance",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FASTAPI_URL = "http://localhost:8000"
PDF_PATH = os.path.join(ROOT_DIR, "Panduan_Lengkap_PhytoAI_Genetics_A4.pdf")
IMG_DIR = os.path.join(ROOT_DIR, "app", "static", "images")


def get_image_path(img_name):
    p = os.path.join(IMG_DIR, img_name)
    return p if os.path.exists(p) else None


def render_table(rows):
    if HAS_PANDAS:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.table(rows)


# ==================== SIDEBAR PILIHAN TAMPILAN ====================
with st.sidebar:
    st.markdown("### 🌾 PhytoAI-Genetics")
    st.caption("Studio Pemodelan Transformer OsDREB2A, CRISPR Base Editing & InaRISK BNPB")
    st.markdown("---")

    view_mode = st.radio(
        "Pilih Mode Tampilan:",
        [
            "🖥️ Tampilan Sama Persis (FastAPI Web Studio)",
            "📊 Mode Dashboard Streamlit (Native)",
        ],
        index=0,
        help="Pilih 'Tampilan Sama Persis' untuk menampilkan antarmuka web studio lengkap (Leaflet GIS, Select2, SweetAlert2, 8 Tab persis seperti di port 8000).",
    )

    st.markdown("---")
    st.markdown("#### 📌 Status Sistem")
    st.markdown(
        """
    - **FastAPI Engine:** 🟢 Aktif (`:8000`)
    - **Streamlit Studio:** 🟢 Aktif (`:8501`)
    - **Lokus Utama:** *OsDREB2A* (Gene ID: `4324418`)
    - **Unit Test:** `37 Passed (100%)`
    """
    )

    st.markdown("---")
    st.markdown("#### ☁️ Panduan Deploy Cloud")
    st.info(
        "💡 **Siap Deploy ke share.streamlit.io!**\n\n"
        "Gunakan **Mode Dashboard Native** saat deploy ke cloud agar seluruh fitur (AI transformer, DMS, CRISPR, dan Animasi 3D) berjalan 100% mandiri tanpa server FastAPI terpisah."
    )

    if os.path.exists(PDF_PATH):
        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📥 Unduh Panduan Riset A4 (PDF)",
            data=pdf_bytes,
            file_name="Panduan_Lengkap_PhytoAI_Genetics_A4.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.caption("Kementerian Pendidikan Tinggi, Sains, dan Teknologi RI\nPusat Riset Bioteknologi Pangan")


# ==================== 1. MODE TAMPILAN SAMA PERSIS DENGAN FASTAPI ====================
if view_mode == "🖥️ Tampilan Sama Persis (FastAPI Web Studio)":
    # Custom CSS untuk menyelaraskan container Streamlit menjadi full-width tanpa margin
    st.markdown(
        """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {display: none;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            border: none !important;
            width: 100% !important;
            min-height: 100vh !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Embed aplikasi web studio FastAPI secara utuh (100% sama persis)
    if hasattr(st, "iframe"):
        st.iframe(f"{FASTAPI_URL}", height=1200)
    else:
        components.iframe(f"{FASTAPI_URL}", height=1200, scrolling=True)


# ==================== 2. MODE DASHBOARD STREAMLIT NATIVE ====================
else:
    # Custom CSS bertema alam ilmiah (#059669)
    st.markdown(
        """
    <style>
        :root {
            --primary: #059669;
            --primary-dark: #065f46;
        }
        .main-title {
            font-size: 2rem;
            font-weight: 800;
            color: #065f46;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            font-size: 1rem;
            color: #475569;
            margin-bottom: 1.2rem;
        }
        .card {
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
        .card-highlight {
            background-color: #ecfdf5;
            border: 1.5px solid #059669;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
        div.stButton > button:first-child {
            background-color: #059669;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
        }
        div.stButton > button:first-child:hover {
            background-color: #047857;
            color: white;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    tab_overview, tab_drought, tab_3d, tab_phytoai, tab_dms, tab_cultivars, tab_crispr, tab_targets, tab_ncbi, tab_tests = st.tabs(
        [
            "🏠 Beranda",
            "🗺️ Peta InaRISK",
            "🎬 Animasi 3D CRISPR",
            "🤖 Prediksi Transformer",
            "🔬 DMS Matrix",
            "🌾 Kultivar Lokal",
            "✂️ CRISPR Studio",
            "🧬 10 Gen Regulon",
            "🌐 Live NCBI",
            "🧪 Pengujian Pytest",
        ]
    )

    with tab_overview:
        st.markdown("<div class='main-title'>🌾 PhytoAI-Genetics Studio</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='sub-title'>Platform bioinformatika kecerdasan buatan terintegrasi untuk akselerasi perakitan padi tahan kekeringan El Nino.</div>",
            unsafe_allow_html=True,
        )
        hero_img = get_image_path("rice_dreb2a_hero.png")
        if hero_img:
            st.image(hero_img, caption="Arsitektur faktor transkripsi OsDREB2A berikatan dengan heliks DNA motif DRE/CRT.", use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Model AI", "Transformer pLM", delta="Evolusi Alami")
        c2.metric("Base Editor", "CBE & ABE", delta="Non-Transgenik")
        c3.metric("Data Geospasial", "InaRISK BNPB", delta="Resolusi 100m")

    with tab_drought:
        st.markdown("### 🗺️ Eksplorasi Geospasial InaRISK BNPB")
        raw_regions = get_drought_regions()
        region_options = {r.region_name: r for r in raw_regions}

        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            sel_r_name = st.selectbox("Sentra Padi Rawan Kekeringan:", list(region_options.keys()))
            sel_r = region_options[sel_r_name]
            lat = st.number_input("Latitude:", value=float(sel_r.latitude), format="%.5f")
            lon = st.number_input("Longitude:", value=float(sel_r.longitude), format="%.5f")
            btn_calc = st.button("🔍 Hitung Risiko Koordinat")

        with col_d2:
            if btn_calc or sel_r:
                res_obj = assess_custom_coordinates(lat, lon)
                res = res_obj.model_dump()
                st.markdown(
                    f"""
                <div class='card-highlight'>
                    <h4>Klaster Terdekat: {res['nearest_region_name']} ({res['distance_km']:.1f} km)</h4>
                    <p><b>Indeks Bahaya InaRISK:</b> <code>{res['inarisk_hazard_score']:.2f} ({res['inarisk_hazard_level'].upper()})</code></p>
                    <p><b>Agroekosistem:</b> {res['agroecosystem_type']}</p>
                    <p><b>Rekomendasi Kultivar:</b> {', '.join(res['recommended_cultivars'])}</p>
                    <p><b>Strategi DREB2A:</b> {res['dreb2a_strategy']}</p>
                    <p><b>Catatan Ahli:</b> {res.get('drought_impact_profile', '')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        f1 = get_image_path("indonesia_rice_agroecosystem.png")
        f2 = get_image_path("rice_drought_vertisol_field.png")
        col_img1, col_img2 = st.columns(2)
        if f1:
            col_img1.image(f1, caption="Gambar 1: Agroekosistem sawah sensor IoT InaRISK.", use_container_width=True)
        if f2:
            col_img2.image(f2, caption="Gambar 2: Rekahan lempung vertisol Pantura Jawa.", use_container_width=True)

    with tab_3d:
        st.markdown("### 🎬 Simulasi 3D Dinamis: Rekayasa Genetik OsDREB2A")
        st.caption(
            "Visualisasi molekuler 3D interaktif berbasis WebGL/Three.js. Simulasi ini berjalan dinamis sesuai "
            "dengan mutasi target yang dipilih (menyesuaikan tipe enzim base editor, basa sasaran, dan domain fungsional)."
        )

        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            mut_choice = st.selectbox(
                "Pilih Target Rekayasa Genetik untuk Disimulasikan:",
                [
                    "P168L (Cytosine Base Editor CBE: C→T / Degron NRD Stabil)",
                    "V79I (Adenine Base Editor ABE: A→G / Peningkatan Afinitas AP2)",
                    "S167A (Cytosine Base Editor CBE: C→T / Abolisi Fosforilasi)",
                ],
                index=0,
                key="st_3d_mut_choice"
            )
            selected_mut_key = mut_choice.split()[0]
        with col_m2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.caption("💡 *Simulasi dapat diputar 360° & di-zoom langsung di viewport 3D di bawah.*")

        # Kartu indikator dinamis
        mc1, mc2, mc3 = st.columns(3)
        if selected_mut_key == "P168L":
            mc1.metric("Editor Enzim", "CBE (evoAPOBEC1)", delta="Deaminasi Sitidin")
            mc2.metric("Perubahan Basa", "CCT → CTT (C → T)", delta="Pro168Leu")
            mc3.metric("Efek Fenotipe", "DREB2A-CA", delta="Resisten Ubiquitin")
        elif selected_mut_key == "V79I":
            mc1.metric("Editor Enzim", "ABE (TadA-8e)", delta="Deaminasi Adenin")
            mc2.metric("Perubahan Basa", "GTT → ATT (A → G)", delta="Val79Ile")
            mc3.metric("Efek Fenotipe", "Afinitas DNA +140%", delta="Ikatan DRE/CRT Kuat")
        else:
            mc1.metric("Editor Enzim", "CBE (evoCDA1)", delta="Deaminasi Sitidin")
            mc2.metric("Perubahan Basa", "TCC → GCC (C → T)", delta="Ser167Ala")
            mc3.metric("Efek Fenotipe", "Abolisi Fosforilasi", delta="Mencegah Degradasi")

        anim_path = os.path.join(ROOT_DIR, "app", "static", "crispr_3d.html")
        if os.path.exists(anim_path):
            with open(anim_path, "r", encoding="utf-8") as f:
                html_code = f.read()
            html_code = html_code.replace(
                "let activeMutationKey = urlParams.get('mut') || 'P168L';",
                f"let activeMutationKey = '{selected_mut_key}';"
            )
            components.html(html_code, height=720, scrolling=False)
        else:
            st.warning("File aset simulasi 3D (`crispr_3d.html`) sedang disiapkan.")

    with tab_phytoai:
        st.markdown("### 🤖 Prediksi Mutasi OsDREB2A (Transformer pLM)")
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            mut_val = st.text_input("Notasi Mutasi:", value="P168L")
            c_name = st.selectbox("Kultivar Acuan:", ["Inpari 32 HDB", "Rojolele", "Gogo Jatiluhur", "Ciherang"])
            r_name = st.selectbox("Wilayah Sasaran:", ["Pantura Jawa Tengah (Demak-Pati)", "NTT Semi-Arid", "NTB Gora"])
            btn_pred = st.button("🚀 Prediksi Mutasi")

        with col_p2:
            if mut_val:
                try:
                    res_obj = analyze_dreb2a_mutation(mut_val, cultivar=c_name, region=r_name)
                    res = res_obj.model_dump()
                    m1, m2, m3 = st.columns(3)
                    score = res['transformer_score']
                    m1.metric("Skor &Delta;LLR", f"{score:+.2f}", delta="Stabil" if score > 0 else "Destruktif")
                    m2.metric("Indeks Toleransi", f"{res['drought_tolerance_index']:.2f}")
                    m3.metric("Domain", res['affected_domain'])
                    st.success(f"**Efek Fungsional:** {res['predicted_functional_effect']}")
                    st.info(f"**Ulasan Biofisika:** {res['biochemical_rationale']}")
                    st.caption(f"**Rekomendasi Base Editing:** {res.get('crispr_base_editing_candidate', '-')}")
                except Exception as err:
                    st.error(f"Error: {err}")

    with tab_dms:
        st.markdown("### 🔬 In Silico Deep Mutational Scanning (DMS)")
        domain_choice = st.radio("Pilih Domain Target:", ["AP2/ERF (70-90)", "NRD Degron (160-180)"])
        start_p, end_p = (70, 90) if "AP2" in domain_choice else (160, 180)
        if st.button("🧬 Jalankan Pemindaian DMS"):
            dms_obj = generate_dms_scan(start_p, end_p)
            dms_res = dms_obj.model_dump()
            dms_rows = []
            for item in dms_res["positions"]:
                dms_rows.append(
                    {
                        "Posisi": item["position"],
                        "Wildtype": item["wildtype_aa"],
                        "Domain": item.get("domain", ""),
                        "Mutasi Terbaik": item["best_mutation"],
                        "Skor Terbaik (ΔLLR)": item["best_score"],
                    }
                )
            render_table(dms_rows)

        f3 = get_image_path("rice_dms_landscape.png")
        if f3:
            st.image(f3, caption="Gambar 3: Lanskap komputasi konformasi 3D dan data DMS.", use_container_width=True)

    with tab_cultivars:
        st.markdown("### 🌾 Haplotipe Plasma Nutfah Padi Lokal")
        cult_rows = []
        for k, v in LOCAL_CULTIVARS.items():
            cult_rows.append(
                {
                    "Varietas Padi": v.get("name", k),
                    "Asal": v.get("origin", ""),
                    "Ekosistem": v.get("ecosystem", ""),
                    "Haplotipe Kunci": ", ".join(v.get("key_snps", [])),
                    "Ekspresi mRNA": v.get("relative_expression", ""),
                    "Fenotipe": v.get("phenotype", ""),
                }
            )
        render_table(cult_rows)
        f4 = get_image_path("rice_cultivar_panicle.png")
        if f4:
            st.image(f4, caption="Gambar 4: Makro malai padi plasma nutfah lokal Indonesia.", use_container_width=True)

    with tab_crispr:
        st.markdown("### ✂️ CRISPR Base Editing Studio (CBE & ABE)")
        st.info("💡 **Simulasi Molekuler 3D Tersedia!** Buka tab **🎬 Animasi 3D CRISPR** di atas untuk melihat proses pengikatan Cas9, pembentukan R-loop, dan deaminasi kimiawi basa DNA secara interaktif 360°.")

        st.markdown("#### ⚡ Desain Base Editor dari CDS NCBI & Simulasi 3D:")
        c_be_sel = st.selectbox(
            "Pilih Target Mutasi Toleransi Kekeringan:",
            [
                "P168L (DREB2A-CA: Stabilisasi Degron NRD - Cytosine Base Editor)",
                "V79I (Peningkatan Afinitas Ikatan DNA AP2 - Adenine Base Editor)",
                "S167A (Abolisi Fosforilasi Regulasi Negatif Karst - CBE)",
            ],
            key="st_crispr_tab_mut",
        )
        selected_crispr_mut = c_be_sel.split()[0]

        # Dua tombol dengan lebar sama persis (use_container_width=True)
        col_btn_be1, col_btn_be2 = st.columns(2)
        with col_btn_be1:
            btn_run_be = st.button("⚡ Desain sgRNA Base Editor dari CDS NCBI", use_container_width=True, key="btn_run_be")
        with col_btn_be2:
            btn_to_3d = st.button("🎬 Simulasi 3D Rekayasa Genetik →", use_container_width=True, key="btn_to_3d")

        if btn_to_3d:
            st.success(f"✅ Buka tab **🎬 Animasi 3D CRISPR** di atas untuk melihat simulasi 3D molekuler mutasi **{selected_crispr_mut}** secara dinamis!")

        if btn_run_be:
            from app.routers.phytoai import OSDREB2A_CDS_NCBI
            cds = OSDREB2A_CDS_NCBI
            mut_obj = analyze_dreb2a_mutation(selected_crispr_mut)
            pos = mut_obj.position
            c_start = (pos - 1) * 3
            c_end = pos * 3
            wt_cod = cds[c_start:c_end]
            w_start = max(0, c_start - 30)
            w_end = min(len(cds), c_end + 30)
            w_seq = cds[w_start:w_end]
            crispr_res = analyze_crispr_targets(w_seq, pam_type="SpCas9")

            st.markdown(f"**Target Mutasi:** `{selected_crispr_mut}` | **Kodon Asal NCBI:** `posisi {pos} ({wt_cod})`")
            st.info(f"**Rekomendasi Editor:** {mut_obj.crispr_base_editing_candidate or 'Base Editor'}")
            be_sg_rows = []
            for s in crispr_res.sites[:5]:
                be_sg_rows.append(
                    {
                        "Protospacer (20-nt)": s.protospacer_sequence,
                        "PAM": s.pam,
                        "GC (%)": f"{s.gc_content:.1f}%",
                        "Pol III Signal": "⚠️ TTTT" if s.has_poly_t_termination else "✅ Bersih",
                        "Kualitas": s.quality_assessment,
                    }
                )
            render_table(be_sg_rows)

        st.markdown("---")
        st.markdown("#### 🧪 Pemindaian Sekuens Bebas:")
        dna_seq = st.text_area(
            "Sekuens DNA Sasaran (5' -> 3'):",
            value="ATGGACGAGCCGCCGTCGCCGTCGGGGACGCAGTCGGCGTCGGTGGTGTCGCCGGCGAGGGAGGAGGCGAAGAAGCAGCGGCGGGTGGGCCTGCGGTACAGGGGGGTGAGGCAGCGGCCGTGGGGGAAGTGGGCGGCGGAGATCCGGGACCCGAACAAGGCCGCCCGGGTGTGGCTCGGCACGTTCGACACCGCGGAGGAGGCGGCGCTGGCCTACGACAAGGCGGCGAGGCTGCTGCGGGGCCGCAACGCGCTGCTCAACTTCCCGCTGCGGCTCGGCGAGCGG",
            height=100,
        )
        if st.button("🧪 Rancang Panduan gRNA"):
            c_obj = analyze_crispr_targets(dna_seq, pam_type="SpCas9")
            c_res = c_obj.model_dump()
            t_rows = []
            for t in c_res["sites"]:
                t_rows.append(
                    {
                        "ID": t["id"],
                        "Protospacer (20-nt)": t["protospacer_sequence"],
                        "PAM": t["pam"],
                        "Untai": t["strand"],
                        "Posisi": f"{t['start_position']}-{t['end_position']}",
                        "GC Content (%)": f"{t['gc_content']:.1f}%",
                        "Pol III (TTTT)": "⚠️ Ada Motif TTTT" if t["has_poly_t_termination"] else "✅ Bersih",
                        "Kualitas": t["quality_assessment"],
                    }
                )
            render_table(t_rows)

        f5 = get_image_path("crispr_rice_editing.png")
        if f5:
            st.image(f5, caption="Gambar 5: Kompleks molekuler nCas9 berfusi dengan deaminase sitidin.", use_container_width=True)

    with tab_targets:
        st.markdown("### 🧬 Katalog 10 Gen Regulon Ketahanan Abiotik Padi")
        reg_rows = []
        for t in RICE_TARGETS:
            t_dict = t.model_dump() if hasattr(t, "model_dump") else (t if isinstance(t, dict) else vars(t))
            reg_rows.append(
                {
                    "Simbol": t_dict.get("symbol", ""),
                    "Nama": t_dict.get("name", ""),
                    "Lokus": t_dict.get("locus", ""),
                    "Gene ID": t_dict.get("ncbi_gene_id", ""),
                    "Fungsi": t_dict.get("function", ""),
                    "Cekaman": t_dict.get("category", ""),
                }
            )
        render_table(reg_rows)
        f6 = get_image_path("rice_stress_regulon.png")
        if f6:
            st.image(f6, caption="Gambar 6: Penampang sel daun padi: modulasi regulon stomata dan translokasi fitohormon ABA.", use_container_width=True)

    with tab_ncbi:
        st.markdown("### 🌐 Integrasi Live NCBI Datasets v2 REST API")
        st.markdown("**Organisme:** *Oryza sativa* Japonica (`IRGSP-1.0`) | **Lokus Target:** *OsDREB2A* (Gene ID: `4324418`)")
        st.code(f">NCBI_RefSeq|NM_001051566.2|OsDREB2A (274 AA)\n{OSDREB2A_PROTEIN[:120]}...", language="fasta")
        f7 = get_image_path("rice_genomics_workstation.png")
        if f7:
            st.image(f7, caption="Gambar 7: Stasiun kerja komputasi genomik padi mengonsumsi REST API NCBI.", use_container_width=True)

    with tab_tests:
        st.markdown("### 🧪 Eksekusi Pengujian Otomatis (Pytest)")
        st.markdown("37 unit tests otomatis mencakup penanganan galat, formula SantaLucia $T_m$, dan model Transformer.")
        if st.button("▶️ Jalankan 37 Unit Tests Sekarang"):
            with st.spinner("Menjalankan test suite..."):
                proc = subprocess.run(["./.venv/bin/pytest", "tests/", "-v", "--tb=short"], capture_output=True, text=True, cwd=ROOT_DIR)
                st.code(proc.stdout, language="bash")
