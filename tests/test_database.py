"""
Unit tests for streamlined database service and endpoints
(tests/test_database.py)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.db_service import (
    get_db_stats,
    get_all_landraces,
    get_landrace_sequence,
    insert_landrace_sequence,
    get_saturation_scores,
    insert_saturation_score,
    get_variant_predictions,
    insert_variant_prediction,
)

client = TestClient(app)


def test_db_stats_service():
    stats = get_db_stats()
    assert stats["status"] == "online"
    assert "SQLite3" in stats["database_type"]
    assert "landrace_sequences" in stats["tables"]
    assert "saturation_scores" in stats["tables"]
    assert "variant_predictions" in stats["tables"]
    assert stats["file_size_kb"] > 0


def test_landrace_crud():
    rec_id = insert_landrace_sequence(
        landrace_name="Test_Landrace",
        accession="TEST_ACC_001",
        sequence="ATGCATGC",
        length=8,
        gc_content=50.0,
        source_note="TEST_SOURCE"
    )
    assert rec_id is not None
    res = get_landrace_sequence("TEST_ACC_001")
    assert res is not None
    assert res["landrace_name"] == "Test_Landrace"

    all_landraces = get_all_landraces()
    assert any(l["accession"] == "TEST_ACC_001" for l in all_landraces)


def test_saturation_score_idempotency():
    # Insert score
    insert_saturation_score(
        landrace="Test_Landrace",
        position_nt=205,
        ref="A",
        alt="T",
        delta_pll=-3.45,
        pseudo_perplexity=14.2,
        mutation_type="nonsense",
        wt_codon="AAG",
        mut_codon="TAG",
        wt_aa="K",
        mut_aa="*",
        model_name="zhihan1996/DNABERT-2-117M",
        window=20,
    )
    # Insert again (idempotent ON CONFLICT DO UPDATE)
    insert_saturation_score(
        landrace="Test_Landrace",
        position_nt=205,
        ref="A",
        alt="T",
        delta_pll=-3.45,
        pseudo_perplexity=14.2,
        mutation_type="nonsense",
        wt_codon="AAG",
        mut_codon="TAG",
        wt_aa="K",
        mut_aa="*",
        model_name="zhihan1996/DNABERT-2-117M",
        window=20,
    )
    scores = get_saturation_scores(landrace="Test_Landrace", limit=10)
    matching = [s for s in scores if s["position_nt"] == 205 and s["alt"] == "T"]
    assert len(matching) == 1
    assert matching[0]["delta_pll"] == -3.45


def test_variant_prediction_crud():
    row_id = insert_variant_prediction(
        landrace="Test_Landrace",
        position_nt=205,
        ref="A",
        alt="T",
        predicted_class="Deleterious",
        class_probabilities='{"Benign": 0.05, "Deleterious": 0.90, "Beneficial": 0.05}',
        predicted_lri=0.85,
        is_zero_shot=0,
        method_note="Trained MLP evaluation",
    )
    assert row_id > 0
    preds = get_variant_predictions(landrace="Test_Landrace")
    matching = [p for p in preds if p["position_nt"] == 205 and p["alt"] == "T"]
    assert len(matching) >= 1
    assert matching[0]["predicted_class"] == "Deleterious"
    assert matching[0]["predicted_lri"] == 0.85


def test_api_db_endpoints():
    resp = client.get("/api/v1/db/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert "landrace_sequences" in data["tables"]

    resp = client.get("/api/v1/db/landraces")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    resp = client.get("/api/v1/db/scores")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
