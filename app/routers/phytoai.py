from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Body
from app.models.phytoai import (
    ProteinDomain,
    MutationAnalysisRequest,
    MutationPredictionResult,
    DMSScanResponse,
    LocalRiceCultivarProfile,
    IndonesianDroughtRegion,
    CoordinateAssessmentRequest,
    CoordinateAssessmentResponse
)
from app.services.phytoai_service import (
    OSDREB2A_DOMAINS,
    LOCAL_CULTIVARS,
    INDONESIAN_DROUGHT_REGIONS,
    REGIONS_BY_ID,
    analyze_dreb2a_mutation,
    generate_dms_scan,
    OSDREB2A_PROTEIN,
    OSDREB2A_CDS_NCBI,
    assess_custom_coordinates,
    get_drought_regions
)
from app.services.crispr_service import analyze_crispr_targets
from app.services.ncbi_client import ncbi_client
from app.services.db_service import get_db_gene

router = APIRouter(prefix="/phytoai", tags=["PhytoAI-Genetics: Pemodelan Transformer DREB2A & Kekeringan Padi"])


@router.get("/dreb2a/domains", response_model=List[ProteinDomain], summary="Domain Struktural & Fungsional Protein OsDREB2A")
async def get_dreb2a_domains():
    """
    Mengambil anotasi domain fungsional protein OsDREB2A (274 AA):
    - **NLS (Nuclear Localization Signal)** (AA 13-22)
    - **AP2/ERF DNA-Binding Domain** (AA 68-130): Pengikat motif DRE/CRT `5'-GCCGAC-3'`
    - **NRD (Negative Regulatory Domain / Degron PEST)** (AA 136-192): Target ubiquitinasi & proteasom 26S
    - **TAD (Transactivation Domain)** (AA 200-274): Perekrut kompleks transkripsi
    """
    return OSDREB2A_DOMAINS


@router.post("/dreb2a/predict-mutation", response_model=MutationPredictionResult, summary="Prediksi Dampak Mutasi DREB2A Menggunakan Model Transformer")
async def predict_dreb2a_mutation(
    request: MutationAnalysisRequest = Body(
        ...,
        openapi_examples={
            "demak_pati_case": {
                "summary": "Kasus 1: Sawah Tadah Hujan Vertisol Demak & Pati (P168L pada Inpari 32)",
                "value": {
                    "variant": "P168L",
                    "cultivar": "Inpari 32 HDB",
                    "target_region": "demak-pati"
                }
            },
            "ntt_semiarid_case": {
                "summary": "Kasus 2: Semi-Arid Ekstrem NTT (Kombinasi P168L pada Padi Gogo Merah NTT)",
                "value": {
                    "variant": "P168L",
                    "cultivar": "Padi Gogo Merah NTT",
                    "target_region": "ntt-semiarid"
                }
            },
            "gunungkidul_karst_case": {
                "summary": "Kasus 3: Lahan Karst Cepat Kering Gunungkidul (S167A pada Segreng Handayani)",
                "value": {
                    "variant": "S167A",
                    "cultivar": "Segreng Handayani",
                    "target_region": "gunungkidul-karst"
                }
            },
            "ap2_dna_contact": {
                "summary": "Kasus 4: Peningkatan Afinitas Ikatan DNA AP2 (V79I)",
                "value": {
                    "variant": "V79I",
                    "cultivar": "Salumpikit",
                    "target_region": "sulawesi-lahan-kering"
                }
            }
        }
    )
):
    """
    **PhytoAI Transformer Engine**:
    Memprediksi dampak fungsional mutasi titik pada protein OsDREB2A terhadap fenotipe toleransi kekeringan padi
    sekaligus mengaitkannya dengan agroekosistem kekeringan spesifik di Indonesia (Demak, Pati, NTT, NTB, Gunungkidul, dll.).
    """
    try:
        return analyze_dreb2a_mutation(request.variant, request.cultivar, request.target_region)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/drought-regions", response_model=List[IndonesianDroughtRegion], summary="Basis Data Wilayah & Klaster Rawan Kekeringan di Seluruh Indonesia")
async def list_drought_regions(
    province: Optional[str] = Query(None, description="Filter berdasarkan nama provinsi (mis. 'Jawa Tengah', 'Jawa Timur', 'Nusa Tenggara Timur', 'Sulawesi Selatan')"),
    min_hazard: Optional[float] = Query(None, description="Filter minimum skor indeks bahaya InaRISK (0.0 - 1.0)"),
    search: Optional[str] = Query(None, description="Cari nama kabupaten, kultivar lokal, atau strategi mutasi")
):
    """
    Menyajikan pemetaan komprehensif klaster sentra padi terdampak kekeringan di seluruh Indonesia
    (Jawa, Madura, Bali, NTB, NTT, Sulawesi, Sumatera, Kalimantan) yang diambil dinamis dari endpoint API.
    """
    return get_drought_regions(province=province, min_hazard=min_hazard, search=search)


@router.get("/assess-coordinates", response_model=CoordinateAssessmentResponse, summary="Penilaian Risiko Kekeringan & Rekomendasi DREB2A Berdasarkan Titik Koordinat Bebas (Seluruh Indonesia)")
async def assess_coordinates_get(
    lat: float = Query(..., description="Garis lintang (Latitude), contoh: -6.8944"),
    lon: float = Query(..., description="Garis bujur (Longitude), contoh: 110.6386")
):
    """
    **Deteksi Spasial Titik Koordinat Dinamis**:
    Menerima titik koordinat sembarang (klik peta Leaflet) di seluruh wilayah kepulauan Indonesia,
    menghubungkan ke raster indeks risiko kekeringan BNPB InaRISK, mendeteksi zona agroekosistem,
    dan menghasilkan rekomendasi mutasi OsDREB2A serta varietas padi lokal yang paling adaptif.
    """
    return assess_custom_coordinates(lat, lon)


@router.post("/assess-coordinates", response_model=CoordinateAssessmentResponse, summary="Penilaian Risiko Kekeringan & Rekomendasi DREB2A (POST)")
async def assess_coordinates_post(
    request: CoordinateAssessmentRequest = Body(
        ...,
        openapi_examples={
            "demak_point": {
                "summary": "Titik Demak (Jawa Tengah)",
                "value": {"latitude": -6.8944, "longitude": 110.6386}
            },
            "timor_point": {
                "summary": "Titik Timor Barat (NTT)",
                "value": {"latitude": -10.1772, "longitude": 123.6070}
            },
            "madura_point": {
                "summary": "Titik Sampang (Madura)",
                "value": {"latitude": -7.0500, "longitude": 113.3000}
            }
        }
    )
):
    """Versi POST dari endpoint penilaian koordinat bebas untuk integrasi payload JSON."""
    return assess_custom_coordinates(request.latitude, request.longitude)


@router.get("/inarisk/sample-point", response_model=CoordinateAssessmentResponse, summary="Alias Endpoint Sampling Titik Peta InaRISK")
async def sample_inarisk_point(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """Endpoint utilitas untuk penanganan klik event peta Leaflet."""
    return assess_custom_coordinates(lat, lon)


@router.get("/drought-regions/{region_id}", response_model=IndonesianDroughtRegion, summary="Detail Agroekosistem & Strategi DREB2A untuk Wilayah Tertentu")
async def get_drought_region_detail(region_id: str):
    """
    Mengambil karakteristik lengkap kekeringan, varietas lokal dominan,
    dan rekomendasi mutasi DREB2A spesifik untuk wilayah target (mis. 'demak-pati' atau 'ntt-semiarid').
    """
    reg = REGIONS_BY_ID.get(region_id.lower())
    if not reg:
        raise HTTPException(
            status_code=404,
            detail=f"Wilayah kekeringan '{region_id}' tidak ditemukan. Pilihan: {list(REGIONS_BY_ID.keys())}"
        )
    return reg


@router.get("/dreb2a/deep-mutational-scan", response_model=DMSScanResponse, summary="In Silico Deep Mutational Scanning (DMS) OsDREB2A")
async def run_dms_scan(
    start_pos: int = Query(68, ge=1, le=274, description="Posisi asam amino awal (default 68 = awal AP2)"),
    end_pos: int = Query(128, ge=1, le=274, description="Posisi asam amino akhir (default 128 = akhir AP2)")
):
    """
    Melakukan pemindaian mutasional mendalam (*Deep Mutational Scanning*) secara *in silico*
    pada seluruh 20 asam amino untuk setiap posisi pada domain pilihan.
    Menghasilkan peta lanskap kebugaran (*fitness landscape*) untuk memandu rekayasa presisi toleransi kekeringan.
    """
    if start_pos > end_pos:
        raise HTTPException(status_code=400, detail="start_pos tidak boleh lebih besar dari end_pos")
    return generate_dms_scan(start_pos, end_pos)


@router.get("/dreb2a/local-cultivars", response_model=List[LocalRiceCultivarProfile], summary="Database Haplotype & Varian Alami OsDREB2A Padi Lokal")
async def list_local_cultivars():
    """
    Menyajikan profil alel dan mutasi alami *OsDREB2A* pada berbagai varietas padi lokal Indonesia & Asia:
    - **Gogo Jatiluhur** (Padi Gogo Jawa Barat - Toleran Kekeringan Ekstrem Lahan Kering Masam)
    - **Salumpikit** (Padi Gogo Tradisional Sulawesi)
    - **Nagina 22 / N22** (Acu Global Toleransi Panas & Kering)
    - **Rojolele** (Padi Landrace Jawa Tengah)
    - **Mentik Wangi** (Padi Aromatik Lokal Yogyakarta)
    - **IR64** (Varietas Sawah Irigasi Nasional)
    """
    return LOCAL_CULTIVARS


@router.post("/dreb2a/design-base-editing", summary="Desain gRNA CRISPR Base Editor untuk Mengintroduksi Mutasi Toleran Kekeringan")
async def design_base_editing_for_dreb2a(
    variant: Optional[str] = Query(None, description="Notasi mutasi yang diprediksi unggul (mis. 'V85I' atau 'P140L')"),
    target_mutation: Optional[str] = Query(None, description="Alias untuk parameter variant")
):
    """
    Mengambil sekuens CDS *OsDREB2A* dari NCBI Datasets dan merancang calon sgRNA
    CRISPR Base Editor (Adenine / Cytosine Base Editor) untuk mengintroduksi
    mutasi toleran kekeringan ke dalam genom padi lokal tanpa memotong untai ganda DNA (*double-strand break*).
    """
    mut_str = variant or target_mutation
    if not mut_str:
        raise HTTPException(status_code=400, detail="Parameter 'variant' atau 'target_mutation' wajib diisi (mis. 'V79I', 'P168L').")

    try:
        mut_result = analyze_dreb2a_mutation(mut_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch live CDS for OsDREB2A (Gene ID: 4324418) via SQLite local cache or NCBI API fallback
    cds = None
    try:
        db_gene = get_db_gene(4324418)
        if db_gene and db_gene.get("cds_sequence"):
            cds = db_gene["cds_sequence"]
    except Exception:
        pass

    if not cds:
        try:
            seqs = await ncbi_client.extract_gene_sequences(4324418, "OsDREB2A")
            if seqs and seqs.cds_sequence and seqs.cds_sequence.sequence:
                cds = seqs.cds_sequence.sequence
        except Exception:
            pass

    if not cds:
        cds = OSDREB2A_CDS_NCBI

    # Target codon position in CDS (1-based codon is pos, nucleotide is (pos-1)*3 to pos*3)
    codon_start = (mut_result.position - 1) * 3
    codon_end = mut_result.position * 3
    wt_codon = cds[codon_start:codon_end]

    # Get local window of 60 bp around the target codon for base editing guide design
    window_start = max(0, codon_start - 30)
    window_end = min(len(cds), codon_end + 30)
    window_seq = cds[window_start:window_end]

    crispr_analysis = analyze_crispr_targets(sequence=window_seq, nuclease="SpCas9")

    # Ambil cetak biru presisi nomor basa DNA jika tersedia
    bp = None
    try:
        from app.services.variety_designer_service import get_nucleotide_edit_blueprint
        bp = get_nucleotide_edit_blueprint(mut_str)
    except Exception:
        pass

    return {
        "target_mutation": mut_str,
        "mutation_profile": mut_result,
        "target_codon_index": mut_result.position,
        "wt_codon_ncbi": wt_codon,
        "mutant_codon": bp.mutant_codon if bp else None,
        "exact_base_number_edited": bp.exact_base_number_edited if bp else None,
        "exact_base_change": bp.exact_base_change if bp else None,
        "cas9_cut_site_bp": bp.cas9_cut_site_bp if bp else None,
        "editing_technology": bp.editing_technology if bp else mut_result.crispr_base_editing_candidate,
        "flanking_window_60bp": window_seq,
        "candidate_sgRNAs": crispr_analysis.sites[:5],
        "base_editor_recommendation": mut_result.crispr_base_editing_candidate or (bp.editing_technology if bp else "Membutuhkan Prime Editing atau Homology-Directed Repair (HDR)"),
        "protocol_summary": (
            f"Gunakan sgRNA di atas pada vektor pRGEB32/pCAMBIA yang mengekspresikan "
            f"Cas9 nickase (nCas9-D10A) terfusi dengan deaminase (ABE8e atau evoCDA1) "
            f"di bawah kendali promotor OsU3/OsU6 padi untuk mengonversi kodon {wt_codon} -> target varian toleran kekeringan."
        )
    }


# --- INTEGRASI SPASIAL BNPB INARISK ---
from app.services.inarisk_service import (
    INARISK_IMAGE_SERVER_URL,
    INARISK_REGIONAL_ASSESSMENT,
    fetch_inarisk_service_metadata
)


@router.get("/inarisk/metadata", summary="Status & Metadata Resmi ArcGIS ImageServer BNPB InaRISK (Layer Risiko Kekeringan)")
async def get_inarisk_metadata():
    """
    Menghubungkan langsung ke layanan spasial resmi BNPB Indonesia:
    `https://gis.bnpb.go.id/server/rest/services/inarisk/layer_risiko_kekeringan/ImageServer`
    Menyediakan resolusi piksel 100m, sistem koordinat, dan petunjuk integrasi QGIS/Leaflet.
    """
    return await fetch_inarisk_service_metadata()


@router.get("/inarisk/risk-assessment", summary="Data Tingkat Bahaya & Risiko Kekeringan BNPB untuk Daerah Studi Kasus")
async def get_all_inarisk_assessments():
    """
    Mengambil data indeks risiko kekeringan BNPB InaRISK resmi untuk seluruh klaster wilayah padi di Indonesia
    (Demak & Pati, NTT, NTB, Gunungkidul, Pantura Jabar, dan Sulawesi).
    """
    return INARISK_REGIONAL_ASSESSMENT


@router.get("/inarisk/risk-assessment/{region_id}", summary="Indeks Risiko BNPB InaRISK untuk Satu Wilayah Tertentu (mis. demak-pati atau ntt-semiarid)")
async def get_single_inarisk_assessment(region_id: str):
    """
    Mengambil skor risiko kekeringan resmi BNPB InaRISK dan rekomendasi rekayasa genetika DREB2A untuk satu wilayah tertentu.
    """
    reg = INARISK_REGIONAL_ASSESSMENT.get(region_id.lower())
    if not reg:
        raise HTTPException(
            status_code=404,
            detail=f"Wilayah '{region_id}' tidak ditemukan di katalog InaRISK. Pilihan: {list(INARISK_REGIONAL_ASSESSMENT.keys())}"
        )
    return reg


# --- PERANCANG VARIETAS BARU & PRESISI BASA DNA ---
from app.services.variety_designer_service import (
    NucleotideEditBlueprint,
    SynthesizedVarietyProfile,
    PLANT_GENOMICS_CATALOG,
    get_nucleotide_edit_blueprint,
    synthesize_new_variety,
    get_research_varieties,
    get_graphical_analysis_data
)
from pydantic import BaseModel, Field


class SynthesizeVarietyRequest(BaseModel):
    parent_cultivar: str = Field("Ciherang", description="Kultivar padi induk lokal (donor/resipien)")
    selected_traits: List[str] = Field(default_factory=lambda: ["drought_dreb2a", "deep_root_dro1"], description="Daftar ID sifat unggul yang di-stack")
    target_environment: str = Field("Lahan Vertisol Kering (Indramayu / Grobogan)", description="Kondisi tanah dan lingkungan target")
    custom_name: Optional[str] = Field(None, description="Nama kustom untuk varietas unggul baru yang dirancang")


@router.get("/variety-designer/blueprint/{mutation_code}", response_model=NucleotideEditBlueprint, summary="Cetak Biru Presisi Nomor Basa DNA yang Diubah/Dipotong")
async def get_blueprint_for_mutation(mutation_code: str):
    """
    Menampilkan nomor basa nukleotida CDS yang tepat diubah/dipotong (misal P168L di basa nomor 503 C->T),
    kodon asal vs kodon baru, urutan spacer sgRNA 20-nt, posisi PAM, dan rekomendasi enzim base editor.
    """
    try:
        return get_nucleotide_edit_blueprint(mutation_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/variety-designer/plant-catalog", summary="Katalog Genomik Multi-Tanaman NCBI (Padi, Jagung, Kedelai, Sorgum, Gandum)")
async def get_plant_genomics_catalog():
    """
    Menyediakan katalog gen ketahanan cekaman iklim/tanah dari berbagai tanaman pangan dunia di NCBI.
    Membuktikan arsitektur PhytoAI dapat digeneralisasi untuk semua jenis organisme dan cekaman.
    """
    return PLANT_GENOMICS_CATALOG


@router.post("/variety-designer/synthesize", response_model=SynthesizedVarietyProfile, summary="Rancang & Sintesis Varietas Unggul Baru (Multi-Trait Gene Pyramiding)")
async def api_synthesize_new_variety(payload: SynthesizeVarietyRequest):
    """
    Menggabungkan sifat unggul pilihan (tahan kekeringan, perakaran dalam, tahan banjir, kebal hawar daun, kebal blas)
    ke dalam genom kultivar induk lokal untuk melahirkan profil Varietas Baru karya Periset MA Salafiyah Kajen Pati.
    """
    try:
        return synthesize_new_variety(
            parent_cultivar=payload.parent_cultivar,
            selected_traits=payload.selected_traits,
            target_environment=payload.target_environment,
            custom_name=payload.custom_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal merancang varietas baru: {str(e)}")


@router.get("/variety-designer/research-varieties", summary="Katalog 4 Varietas Unggul Baru Hasil Penelitian MA Salafiyah Kajen Pati")
async def api_get_research_varieties():
    """
    Menyajikan daftar resmi 4 varietas unggul baru hasil penelitian PhytoAI-Genetics karya Periset MA Salafiyah Kajen Pati:
    Salafiyah Agritama-1 (DREB Super), Salafiyah Amfibi-2 (SubDREB), Salafiyah Salina-3 (Coastal), dan Salafiyah Savana-4 (Arid Gora).
    """
    return get_research_varieties()


@router.get("/variety-designer/graphical-analysis", summary="Data Analisis Grafik Komparatif Fenotipe, Produktivitas & Biofisika")
async def api_get_graphical_analysis():
    """
    Menyajikan dataset lengkap untuk visualisasi grafik komparatif: perbandingan hasil panen normal vs cekaman,
    kinetika Relative Water Content (RWC %) daun selama 25 hari tanpa air, skor stabilitas delta LLR ESM-2, dan radar multi-sifat.
    """
    return get_graphical_analysis_data()

