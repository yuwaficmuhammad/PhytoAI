"""
app/routers/phytoai.py
Router API minimal PhytoAI-Genetics untuk pembacaan varian hasil saturasi DNABERT-2
dan dokumentasi metodologi in silico sesuai proposal.
"""

from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from app.core.config import settings
from app.models.phytoai import (
    NucleotideVariant,
    VariantListResponse,
    MethodDescriptionResponse
)
from app.services.db_service import get_saturation_scores

router = APIRouter(prefix="/phytoai", tags=["PhytoAI-Genetics: Varian DREB2A"])


@router.get(
    "/variants",
    response_model=VariantListResponse,
    summary="Daftar Varian Mutagenesis Saturasi In Silico (DNABERT-2)"
)
async def list_variants(
    landrace: Optional[str] = Query(None, description="Filter nama landrace padi lokal"),
    min_delta_pll: Optional[float] = Query(None, description="Ambang batas minimum pergeseran pseudo-log-likelihood"),
    limit: int = Query(100, ge=1, le=1000, description="Jumlah maksimal varian yang dikembalikan")
):
    """
    Membaca hasil komputasi mutagenesis saturasi in silico pada koordinat domain AP2/ERF
    dari database lokal. Tidak melakukan inferensi berat saat runtime server.
    """
    raw_scores = get_saturation_scores(landrace=landrace, min_delta_pll=min_delta_pll, limit=limit)
    variants = [
        NucleotideVariant(
            landrace=row["landrace"],
            position_nt=row["position_nt"],
            ref=row["ref"],
            alt=row["alt"],
            delta_pll=row["delta_pll"],
            pseudo_perplexity=row["pseudo_perplexity"],
            mutation_type=row.get("mutation_type"),
            wt_codon=row.get("wt_codon"),
            mut_codon=row.get("mut_codon"),
            wt_aa=row.get("wt_aa"),
            mut_aa=row.get("mut_aa"),
            model_name=row.get("model_name", "zhihan1996/DNABERT-2-117M")
        )
        for row in raw_scores
    ]

    return VariantListResponse(
        total=len(variants),
        landrace=landrace,
        variants=variants,
        method_note=settings.METHOD_NOTE
    )


@router.get(
    "/methods",
    response_model=MethodDescriptionResponse,
    summary="Deskripsi Metode Bioinformatika & Keterbatasan Saintifik"
)
async def get_methods():
    """
    Mengembalikan penjelasan eksplisit mengenai model DNABERT-2, cara perhitungan skor PLL,
    lingkungan kerja Google Colab, serta batas validitas ilmiah hasil komputasi in silico.
    """
    return MethodDescriptionResponse(
        title=settings.PROJECT_NAME,
        target_gene="DREB2A (Oryza sativa)",
        model_name="zhihan1996/DNABERT-2-117M",
        embedding_dimension=768,
        task_scope=[
            "1. Unduh sekuens nukleotida DREB2A landrace padi lokal Indonesia dari NCBI GenBank (format FASTA).",
            "2. Pra-pemrosesan sekuens dan tokenisasi via BPE AutoTokenizer bawaan DNABERT-2.",
            "3. Ekstraksi representasi 768-dimensi dari hidden state terakhir encoder DNABERT-2.",
            "4. Mutagenesis saturasi in silico pada koordinat domain AP2/ERF pengikat DNA.",
            "5. Perhitungan pergeseran pseudo-log-likelihood (delta PLL) dan pseudo-perplexity varian.",
            "6. Arsitektur dual-prediction head (MLP) untuk klasifikasi varian dan regresi LRI di Google Colab.",
            "7. Penyusunan koordinat varian kandidat sebagai cetak biru untuk rekayasa genom di masa depan."
        ],
        limitations=[
            "Skor zero-shot adalah ukuran kewajaran urutan menurut model bahasa genomik, bukan bukti fenotipe toleransi kekeringan.",
            "Model dual-prediction head (LRI dan klasifikasi Beneficial) memerlukan data fenotipe basah terukur untuk pelatihan; tanpa data tersebut kepala prediksi tidak dilatih.",
            "CRISPR-Cas9 dan uji basah laboratorium bukan bagian dari lingkup proyek saat ini melainkan pekerjaan masa depan."
        ],
        method_note=settings.METHOD_NOTE
    )
