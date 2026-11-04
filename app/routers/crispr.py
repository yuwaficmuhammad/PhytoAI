from typing import Optional
from fastapi import APIRouter, Path, Query, HTTPException, Body
from app.models.crispr import (
    CRISPRAnalysisRequest,
    CRISPRAnalysisResponse,
    CRISPRTargetSite
)
from app.services.crispr_service import analyze_crispr_targets
from app.services.ncbi_client import ncbi_client
from app.data.rice_targets import TARGETS_BY_GENE_ID

router = APIRouter(prefix="/crispr", tags=["Perancangan CRISPR & Bioinformatika (CRISPR Tools)"])


@router.post("/find-targets", response_model=CRISPRAnalysisResponse, summary="Pindai Situs Target gRNA CRISPR dari Sekuens DNA")
async def find_crispr_targets(
    request: CRISPRAnalysisRequest = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Sekuens Ekson OsSWEET14 Padi",
                "value": {
                    "sequence": "ATGGCTGGCATGTCTCTTCAGCATCCCTGGGCCTTCGCCTTTGGTCTCCTAGGCAACATCATCTCCTTCATGACCTACCTGGCCCCACTGCCGACGTTCTACAGGATCTACAAGAGCAAGTCGACGCAG",
                    "nuclease": "SpCas9",
                    "min_gc": 35.0,
                    "max_gc": 70.0
                }
            }
        }
    )
):
    """
    Memindai sekuens DNA untuk menemukan situs target gRNA CRISPR.
    Fitur evaluasi bioinformatika untuk rekayasa genetika tanaman padi:
    - **Deteksi PAM**: NGG (SpCas9, 3') atau TTTV (Cas12a/Cpf1, 5').
    - **Pemeriksaan Strand**: Mendeteksi situs pada untai sensus (+) dan antisense (-).
    - **Evaluasi GC Content**: Rekomendasi 40-60% untuk efisiensi pemotongan optimal.
    - **Deteksi Sinyal Terminasi Pol III (TTTT)**: Memperingatkan jika guide RNA mengandung
      rentetan 4+ Timin (TTTT) yang memicu penghentian transkripsi dini pada promotor U6/U3 padi.
    """
    try:
        return analyze_crispr_targets(
            sequence=request.sequence,
            nuclease=request.nuclease,
            min_gc=request.min_gc,
            max_gc=request.max_gc
        )
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))


@router.post("/design-for-gene/{gene_id}", response_model=CRISPRAnalysisResponse, summary="Otomasi Desain gRNA CRISPR Langsung dari NCBI Gene ID")
async def design_crispr_for_gene(
    gene_id: int = Path(..., description="NCBI Gene ID padi (mis. 4350572 untuk OsSWEET14, 4347178 untuk DEP1, 4345606 untuk Badh2)"),
    nuclease: str = Query("SpCas9", description="Pilihan sistem enzim: 'SpCas9' atau 'Cas12a'"),
    target_region: str = Query("cds", description="Daerah target: 'cds' (ekson pengkode protein) atau 'genomic' (promotor/intron)")
):
    """
    **Alur Kerja Rekayasa Genetika Otomatis Satu Klik (One-Click CRISPR Pipeline)**:
    1. Mengambil sekuens gen resmi langsung dari NCBI Datasets v2 API.
    2. Mengekstrak sekuens CDS atau daerah genomik gen padi pilihan.
    3. Memindai seluruh situs target gRNA secara otomatis.
    4. Mengeliminasi calon gRNA berisiko tinggi (mis. memiliki sinyal terminasi TTTT).
    5. Menghasilkan daftar gRNA optimal siap pakai untuk sintesis oligo dan kloning vektor (mis. pCAMBIA, pRGEB32).
    """
    target = TARGETS_BY_GENE_ID.get(gene_id)
    symbol = target.gene_symbol if target else None

    sequences = await ncbi_client.extract_gene_sequences(gene_id=gene_id, symbol=symbol)

    selected_seq = ""
    if target_region.lower() == "cds":
        if not sequences.cds_sequence:
            raise HTTPException(
                status_code=404,
                detail=f"Sekuens CDS untuk Gene ID {gene_id} tidak ditemukan di NCBI."
            )
        selected_seq = sequences.cds_sequence.sequence
    else:
        if not sequences.genomic_sequence:
            raise HTTPException(
                status_code=404,
                detail=f"Sekuens genomik untuk Gene ID {gene_id} tidak ditemukan di NCBI."
            )
        selected_seq = sequences.genomic_sequence.sequence

    return analyze_crispr_targets(
        sequence=selected_seq,
        nuclease=nuclease
    )
