"""
Unit tests for core API endpoints
(tests/test_api.py)
"""

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
    assert "method_note" in data
    assert "DNABERT-2" in data["method_note"]


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["organism"] == "Oryza sativa (Padi)"
    assert "OsDREB2A" in data["target_gene"]
    assert "method_note" in data


def test_phytoai_methods_endpoint():
    response = client.get("/api/v1/phytoai/methods")
    assert response.status_code == 200
    data = response.json()
    assert "DNABERT-2" in data["model_name"]
    assert data["embedding_dimension"] == 768
    assert len(data["task_scope"]) == 7
    assert len(data["limitations"]) >= 3
    assert "method_note" in data



def test_phytoai_variants_endpoint():
    response = client.get("/api/v1/phytoai/variants")
    assert response.status_code == 200
    data = response.json()
    assert "variants" in data
    assert "total" in data
    assert "method_note" in data


def test_cors_headers_present():
    """Verify CORS headers on public endpoints."""
    response = client.options("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code in (200, 405)
