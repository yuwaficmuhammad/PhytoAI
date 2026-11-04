"""
Unit Tests untuk Layanan Database Lokal SQLite & Endpoint REST API
(tests/test_database.py)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.db_service import (
    get_db_stats,
    get_all_db_genes,
    get_db_gene,
    get_all_db_inarisk,
    get_all_db_cultivars,
    get_all_db_dms,
    get_db_crispr_guides,
)

client = TestClient(app)


def test_db_stats_service():
    stats = get_db_stats()
    assert stats["status"] == "online"
    assert "SQLite3" in stats["database_type"]
    assert stats["tables"]["ncbi_genes"] == 10
    assert stats["tables"]["inarisk_clusters"] == 6
    assert stats["tables"]["rice_cultivars"] == 8
    assert stats["tables"]["dms_mutations"] >= 5
    assert stats["tables"]["crispr_guides"] >= 3
    assert stats["file_size_kb"] > 0


def test_db_genes_retrieval():
    genes = get_all_db_genes()
    assert len(genes) == 10
    symbols = [g["gene_symbol"] for g in genes]
    assert "OsDREB2A" in symbols
    assert "OsLEA3-1" in symbols
    assert "OsDREB1A" in symbols

    # Check specific gene by symbol
    dreb2a = get_db_gene("OsDREB2A")
    assert dreb2a is not None
    assert dreb2a["gene_id"] == 4324418
    assert dreb2a["chromosome"] == "1"
    assert dreb2a["cds_length"] == 825
    assert dreb2a["protein_length"] == 274
    assert len(dreb2a["cds_sequence"]) == 825
    assert len(dreb2a["protein_sequence"]) == 274

    # Check specific gene by ID
    lea3 = get_db_gene(4337666)
    assert lea3 is not None
    assert lea3["gene_symbol"] == "OsLEA3-1"
    assert lea3["chromosome"] == "5"


def test_db_inarisk_and_cultivars():
    clusters = get_all_db_inarisk()
    assert len(clusters) == 6
    demak = next((c for c in clusters if c["id"] == "demak-pati"), None)
    assert demak is not None
    assert demak["inarisk_risk_index"] == 0.82

    cultivars = get_all_db_cultivars()
    assert len(cultivars) == 8
    inpari = next((c for c in cultivars if c["id"] == "inpari-32"), None)
    assert inpari is not None
    assert "P168L" in inpari["recommended_edit"]


def test_db_dms_and_crispr_guides():
    dms = get_all_db_dms()
    assert len(dms) >= 5
    p168l = next((d for d in dms if d["variant"] == "P168L"), None)
    assert p168l is not None
    assert p168l["delta_llr"] == 1.84

    guides = get_db_crispr_guides("P168L")
    assert len(guides) >= 1
    assert guides[0]["target_mutation"] == "P168L"
    assert "oligo_fwd" in guides[0]
    assert "oligo_rev" in guides[0]


def test_api_db_endpoints():
    # 1. Status endpoint
    resp = client.get("/api/v1/db/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert data["tables"]["ncbi_genes"] == 10

    # 2. Genes list endpoint
    resp = client.get("/api/v1/db/genes")
    assert resp.status_code == 200
    genes = resp.json()
    assert len(genes) == 10

    # 3. Gene detail by symbol & ID
    resp = client.get("/api/v1/db/genes/OsDREB2A")
    assert resp.status_code == 200
    assert resp.json()["gene_symbol"] == "OsDREB2A"

    resp = client.get("/api/v1/db/genes/4324418")
    assert resp.status_code == 200
    assert resp.json()["gene_id"] == 4324418

    # 4. Gene not found (404)
    resp = client.get("/api/v1/db/genes/NON_EXISTENT_GENE_1234")
    assert resp.status_code == 404

    # 5. InaRISK endpoint
    resp = client.get("/api/v1/db/inarisk")
    assert resp.status_code == 200
    assert len(resp.json()) == 6

    # 6. Cultivars endpoint
    resp = client.get("/api/v1/db/cultivars")
    assert resp.status_code == 200
    assert len(resp.json()) == 8

    # 7. DMS endpoint
    resp = client.get("/api/v1/db/dms")
    assert resp.status_code == 200
    assert len(resp.json()) >= 5

    # 8. CRISPR guides endpoint
    resp = client.get("/api/v1/db/crispr-guides?target_mutation=P168L")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
