"""
PhytoAI-Genetics: Router Database Lokal SQLite (app/routers/database.py)
Menyediakan REST API endpoint untuk inspeksi, penarikan, dan pemanfaatan data tersimpan
dari NCBI Datasets v2 dan BNPB InaRISK GIS.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from app.services.db_service import (
    get_db_stats,
    get_all_db_genes,
    get_db_gene,
    get_all_db_inarisk,
    get_all_db_cultivars,
    get_all_db_dms,
    get_db_crispr_guides
)

router = APIRouter(prefix="/db", tags=["Database Lokal SQLite: Penyimpanan Data Real NCBI & InaRISK"])


@router.get("/status", summary="Status & Metrik Database Lokal SQLite")
async def database_status():
    """
    Mengembalikan ringkasan status operasional database SQLite lokal (`phytoai_local.db`),
    meliputi total baris pada 5 tabel utama, ukuran berkas di disk, dan tipe engine.
    """
    return get_db_stats()


@router.get("/genes", summary="Daftar 10 Gen Regulon Ketahanan Padi dari Database Lokal")
async def list_database_genes():
    """
    Mengambil data sekuens lengkap (CDS, Protein, GC%, Locus Tag) dari 10 gen respon dehidrasi padi
    yang tersimpan di database lokal. Menjamin latensi <0.1ms tanpa ketergantungan jaringan eksternal.
    """
    return get_all_db_genes()


@router.get("/genes/{identifier}", summary="Detail Sekuens & Anotasi Gen Berdasarkan Simbol atau NCBI Gene ID")
async def get_database_gene(
    identifier: str = Path(..., description="Simbol gen (mis. OsDREB2A, OsLEA3-1) atau NCBI Gene ID (mis. 4324418, 4337666)")
):
    """
    Mengambil informasi rinci dan sekuens FASTA CDS/Protein untuk satu gen tertentu dari database lokal.
    """
    gene = get_db_gene(identifier)
    if not gene:
        raise HTTPException(
            status_code=404,
            detail=f"Gen '{identifier}' tidak ditemukan di database lokal. Silakan gunakan simbol gen seperti 'OsDREB2A' atau ID numerik."
        )
    return gene


@router.get("/inarisk", summary="Data Klaster Risiko Kekeringan BNPB InaRISK Tersimpan")
async def list_database_inarisk():
    """
    Mengambil data spasial dan indeks bahaya kekeringan BNPB InaRISK untuk seluruh sentra padi Indonesia.
    """
    return get_all_db_inarisk()


@router.get("/cultivars", summary="Daftar Profil 8 Kultivar Padi Lokal Tersimpan")
async def list_database_cultivars():
    """
    Mengambil katalog 8 plasma nutfah kultivar padi lokal Indonesia beserta profil alel DREB2A dan rekomendasi pengeditan gen.
    """
    return get_all_db_cultivars()


@router.get("/dms", summary="Matriks Fitness Landscape Deep Mutational Scanning (DMS)")
async def list_database_dms():
    """
    Mengambil hasil pemodelan Transformer skor $\Delta$LLR dan indeks toleransi mutasi asam amino DREB2A.
    """
    return get_all_db_dms()


@router.get("/crispr-guides", summary="Koleksi sgRNA & Pasangan Oligo Kloning Terverifikasi")
async def list_database_crispr_guides(
    target_mutation: Optional[str] = Query(None, description="Filter mutasi target (mis. 'P168L', 'V79I', 'S167A')")
):
    """
    Mengambil calon sgRNA 20-nt protospacer, skor efisiensi, dan primer oligo forward/reverse untuk kloning ke vektor pRGEB32/pCAMBIA.
    """
    return get_db_crispr_guides(target_mutation)
