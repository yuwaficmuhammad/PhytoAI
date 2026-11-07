import pytest
import httpx
from app.services.ncbi_client import ncbi_client
from app.core.exceptions import NCBIAPIException


@pytest.mark.asyncio
async def test_live_ncbi_gene_dreb2a():
    try:
        rep = await ncbi_client.get_gene_by_id(4324418)
    except NCBIAPIException as e:
        if "nodename nor servname" in str(e) or "Koneksi ke NCBI" in str(e):
            pytest.skip(f"Akses jaringan NCBI tidak tersedia (offline/sandbox): {e}")
        raise
    assert rep is not None
    assert "gene" in rep
    g = rep["gene"]
    assert g.get("gene_id") == "4324418" or g.get("gene_id") == 4324418
    assert "dreb2a" in g.get("description", "").lower() or "dehydration" in g.get("description", "").lower()


@pytest.mark.asyncio
async def test_live_ncbi_dreb2a_sequence_extraction():
    try:
        seqs = await ncbi_client.extract_gene_sequences(gene_id=4324418, symbol="OsDREB2A")
    except NCBIAPIException as e:
        if "nodename nor servname" in str(e) or "Koneksi ke NCBI" in str(e):
            pytest.skip(f"Akses jaringan NCBI tidak tersedia (offline/sandbox): {e}")
        raise
    assert seqs.gene_id == 4324418
    assert seqs.cds_sequence is not None
    assert len(seqs.cds_sequence.sequence) == 825
    assert seqs.protein_sequence is not None
    assert len(seqs.protein_sequence.sequence) == 274
