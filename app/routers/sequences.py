from typing import Optional
from fastapi import APIRouter, Path, HTTPException
from app.models.gene import GeneSequencesResponse, SequenceData
from app.services.ncbi_client import ncbi_client

router = APIRouter(prefix="/sequences", tags=["Ekstraksi Sekuens NCBI"])


@router.get("/gene/{gene_id}", response_model=GeneSequencesResponse, summary="Ekstrak Sekuens Genomik, CDS, dan Protein Padi dari NCBI")
async def get_gene_sequences(
    gene_id: int = Path(..., description="NCBI Gene ID (mis. 4324418 untuk OsDREB2A)")
):
    """Mengunduh dan mengekstrak sekuens CDS dan Protein dari paket resmi NCBI Datasets v2."""
    sequences = await ncbi_client.extract_gene_sequences(gene_id=gene_id)
    if not sequences:
        raise HTTPException(
            status_code=404,
            detail=f"Sekuens untuk gen ID {gene_id} tidak ditemukan di NCBI Datasets."
        )
    return sequences


@router.get("/gene/{gene_id}/cds", response_model=SequenceData, summary="Ambil Sekuens Pengkode (CDS) Saja")
async def get_gene_cds(
    gene_id: int = Path(..., description="NCBI Gene ID (mis. 4324418 untuk OsDREB2A)")
):
    """Mengambil sekuens Coding DNA Sequence (CDS) spesifik dari gen padi untuk analisis mutagenesis."""
    sequences = await ncbi_client.extract_gene_sequences(gene_id=gene_id)
    if not sequences or not sequences.cds_sequence:
        raise HTTPException(
            status_code=404,
            detail=f"Sekuens CDS untuk gen ID {gene_id} tidak ditemukan pada data NCBI."
        )
    return sequences.cds_sequence
