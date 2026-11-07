"""
app/routers/database.py
REST API endpoint untuk inspeksi data lokal sekuens landrace dan skor mutasi DNABERT-2.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from app.services.db_service import (
    get_db_stats,
    get_all_landraces,
    get_landrace_sequence,
    get_saturation_scores
)

router = APIRouter(prefix="/db", tags=["Database Lokal SQLite"])


@router.get("/status", summary="Status & Metrik Database Lokal SQLite")
async def database_status():
    """Mengembalikan ringkasan status tabel database lokal SQLite."""
    return get_db_stats()


@router.get("/landraces", summary="Daftar Sekuens Landrace Padi Lokal Tersimpan")
async def list_database_landraces():
    """Mengambil seluruh data sekuens landrace padi lokal yang tersimpan di DB."""
    return get_all_landraces()


@router.get("/landraces/{identifier}", summary="Detail Sekuens Landrace Berdasarkan Nama atau Aksesi")
async def get_single_landrace(identifier: str = Path(..., description="Nama landrace atau nomor aksesi NCBI")):
    """Mengambil informasi dan sekuens FASTA untuk satu landrace tertentu."""
    record = get_landrace_sequence(identifier)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Landrace '{identifier}' tidak ditemukan di database lokal."
        )
    return record


@router.get("/scores", summary="Daftar Skor Mutagenesis Saturasi In Silico")
async def list_database_scores(
    landrace: Optional[str] = Query(None, description="Filter nama landrace"),
    min_delta_pll: Optional[float] = Query(None, description="Ambang batas minimum delta PLL"),
    limit: int = Query(100, ge=1, le=1000, description="Batas maksimal jumlah baris")
):
    """Mengambil daftar varian dan skor pergeseran PLL dari tabel saturation_scores."""
    return get_saturation_scores(landrace=landrace, min_delta_pll=min_delta_pll, limit=limit)
