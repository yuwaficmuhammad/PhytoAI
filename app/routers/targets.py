from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path
from app.models.target import GeneticEngineeringTarget, TargetCatalogResponse
from app.data.rice_targets import RICE_TARGETS, get_target_by_identifier
from app.services.ncbi_client import ncbi_client

router = APIRouter(prefix="/targets", tags=["Katalog Target Rekayasa Genetika Padi (CRISPR Targets)"])


@router.get("", response_model=TargetCatalogResponse, summary="Katalog Gen Target Rekayasa Genetika & CRISPR Padi")
async def list_targets(
    category: Optional[str] = Query(
        None,
        description="Filter berdasarkan kategori agronomi (mis. 'Toleransi Kekeringan', 'Proteksi Membran', 'Regulasi Stomata')"
    )
):
    """
    Menyajikan daftar gen target rekayasa genetika padi yang paling sering diteliti secara global
    beserta strategi pengeditan gen (CRISPR/Cas9, Base Editing, Prime Editing) dan lokus genomnya.
    """
    targets = RICE_TARGETS
    if category:
        cat_lower = category.lower()
        targets = [t for t in targets if cat_lower in t.category.lower()]

    all_categories = sorted(list({t.category for t in RICE_TARGETS}))
    return TargetCatalogResponse(
        total=len(targets),
        categories=all_categories,
        targets=targets
    )


@router.get("/categories", response_model=List[str], summary="Daftar Kategori Sifat Agronomi Target")
async def list_categories():
    """
    Mengambil semua kategori agronomi yang tersedia dalam basis data target padi.
    """
    return sorted(list({t.category for t in RICE_TARGETS}))


@router.get("/{identifier}", summary="Detail Target Rekayasa Genetika + Integrasi Anotasi Live NCBI")
async def get_target_detail(
    identifier: str = Path(..., description="ID target (mis. os-dreb2a, os-lea3-1, snac1) atau simbol (OsDREB2A, OsLEA3-1) atau Gene ID (4324418)")
):
    """
    Mengambil informasi target rekayasa genetika dan secara langsung menghubungkannya
    dengan data sekuens dan anotasi kromosom terbaru dari NCBI Datasets v2 API.
    """
    target = get_target_by_identifier(identifier)
    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"Target rekayasa genetika padi '{identifier}' tidak terdaftar di katalog."
        )

    ncbi_report = None
    try:
        ncbi_report = await ncbi_client.get_gene_by_id(target.ncbi_gene_id)
    except Exception:
        # Fallback if NCBI network fails
        pass

    return {
        "target_info": target,
        "ncbi_live_annotation": ncbi_report
    }

