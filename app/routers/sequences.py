from typing import Optional
from fastapi import APIRouter, Path, Query, Response, HTTPException
from fastapi.responses import StreamingResponse
import io

from app.models.crispr import GeneSequencesResponse, SequenceData
from app.services.ncbi_client import ncbi_client
from app.data.rice_targets import TARGETS_BY_GENE_ID

router = APIRouter(prefix="/sequences", tags=["Ekstraksi Sekuens DNA/Protein (Sequences)"])


@router.get("/gene/{gene_id}", response_model=GeneSequencesResponse, summary="Ekstrak Sekuens Genomik, CDS, dan Protein Padi")
async def get_gene_sequences(
    gene_id: int = Path(..., description="NCBI Gene ID (mis. 4350572 untuk OsSWEET14, 4347178 untuk DEP1)")
):
    """
    Mengunduh dan mengekstrak sekuens DNA Genomik (fna), Coding Sequence (CDS),
    dan Asam Amino Protein (faa) dari paket resmi NCBI Datasets v2.
    Data ini esensial untuk mendesain gRNA CRISPR, primer PCR, dan analisis mutasi titik.
    """
    target = TARGETS_BY_GENE_ID.get(gene_id)
    symbol = target.gene_symbol if target else None

    sequences = await ncbi_client.extract_gene_sequences(gene_id=gene_id, symbol=symbol)
    return sequences


@router.get("/gene/{gene_id}/cds", response_model=SequenceData, summary="Ambil Sekuens Pengkode (CDS) Saja")
async def get_gene_cds(
    gene_id: int = Path(..., description="NCBI Gene ID (mis. 4350572 untuk OsSWEET14)")
):
    """
    Mengambil bagian Coding DNA Sequence (CDS) spesifik dari gen padi.
    Sekuens CDS digunakan langsung untuk mencari situs target Cas9/Cas12a
    yang menyebabkan mutasi pergeseran rangka baca (frameshift knockout).
    """
    target = TARGETS_BY_GENE_ID.get(gene_id)
    symbol = target.gene_symbol if target else None

    sequences = await ncbi_client.extract_gene_sequences(gene_id=gene_id, symbol=symbol)
    if not sequences.cds_sequence:
        raise HTTPException(
            status_code=404,
            detail=f"Sekuens CDS untuk gen ID {gene_id} tidak ditemukan pada paket data NCBI."
        )
    return sequences.cds_sequence


@router.get("/gene/{gene_id}/download-package", summary="Unduh File Arsip ZIP Resmi NCBI Datasets (FASTA, GFF3, JSON)")
async def download_ncbi_package(
    gene_id: int = Path(..., description="NCBI Gene ID")
):
    """
    Mengunduh arsip ZIP lengkap yang dihasilkan oleh NCBI Datasets v2
    berisi berkas FASTA genom, transkrip, protein, serta laporan katalog anotasi.
    """
    content = await ncbi_client.download_gene_package([gene_id])
    if not content:
        raise HTTPException(status_code=503, detail="Layanan NCBI Datasets tidak tersedia atau gagal mengunduh arsip paket gen.")

    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=rice_gene_{gene_id}_ncbi_dataset.zip"}
    )

