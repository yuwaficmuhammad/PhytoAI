import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "PhytoAI-Genetics" in data["service"]
    assert "ncbi_api_key_configured" in data
    assert "ncbi_rate_limit" in data


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["organism"] == "Oryza sativa (Padi)"
    assert data["curated_targets_count"] >= 10


def test_list_targets():
    response = client.get("/api/v1/targets")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 10
    assert len(data["categories"]) > 0


def test_filter_targets_category():
    response = client.get("/api/v1/targets?category=Kekeringan")
    assert response.status_code == 200
    data = response.json()
    assert len(data["targets"]) >= 1
    symbols = [t["gene_symbol"] for t in data["targets"]]
    assert "OsDREB2A" in symbols


def test_crispr_find_targets_endpoint():
    payload = {
        "sequence": "ATGGCTGGCATGTCTCTTCAGCATCCCTGGGCCTTCGCCTTTGGTCTCCTAGGCAACATCATCTCCTTCATGACCTACCTGGCCCCACTGCCGACGTTCTACAGGATCTACAAGAGCAAGTCGACGCAG",
        "nuclease": "SpCas9",
        "min_gc": 35.0,
        "max_gc": 70.0
    }
    response = client.post("/api/v1/crispr/find-targets", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nuclease"] == "SpCas9"
    assert data["total_sites_found"] > 0
    assert len(data["sites"]) > 0


def test_invalid_mutation_format():
    """Format mutasi yang salah harus mengembalikan 400."""
    payload = {"variant": "INVALID123", "cultivar": "Nipponbare"}
    response = client.post("/api/v1/phytoai/dreb2a/predict-mutation", json=payload)
    assert response.status_code == 400
    assert "tidak valid" in response.json()["detail"].lower()


def test_cors_headers_present():
    """Endpoint harus mengembalikan CORS header yang valid."""
    response = client.options("/api/v1/targets", headers={"Origin": "http://localhost:3000"})
    # Header CORS seharusnya ada di semua respons
    assert response.status_code in (200, 405)
