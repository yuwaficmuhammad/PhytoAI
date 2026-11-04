import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.phytoai_service import (
    OSDREB2A_DOMAINS,
    LOCAL_CULTIVARS,
    analyze_dreb2a_mutation,
    generate_dms_scan
)

client = TestClient(app)


def test_dreb2a_domains_loaded():
    assert len(OSDREB2A_DOMAINS) == 4
    domain_names = [d.name for d in OSDREB2A_DOMAINS]
    assert any("AP2" in n for n in domain_names)
    assert any("NRD" in n for n in domain_names)
    assert any("NLS" in n for n in domain_names)
    assert any("TAD" in n for n in domain_names)


def test_analyze_mutation_nrd_activation():
    # P168L is inside NRD domain (136-192), wildtype at 168 is P
    res = analyze_dreb2a_mutation("P168L", cultivar="Rojolele")
    assert res.variant == "P168L"
    assert res.position == 168
    assert res.wildtype_aa == "P"
    assert res.mutant_aa == "L"
    assert "NRD" in res.affected_domain
    assert res.transformer_score > +1.5
    assert "Constitutive" in res.predicted_functional_effect or "DREB2A-CA" in res.predicted_functional_effect
    assert res.crispr_base_editing_candidate is not None


def test_analyze_mutation_ap2_gain_of_function():
    # V79I is in AP2 domain, position 79
    res = analyze_dreb2a_mutation("V79I", cultivar="Gogo Jatiluhur")
    assert res.variant == "V79I"
    assert res.position == 79
    assert "AP2" in res.affected_domain
    assert res.transformer_score > 0
    assert "ABE" in res.crispr_base_editing_candidate


def test_analyze_mutation_ap2_disruptive():
    # V79A is a critical DNA contact residue in AP2 (YRGVR core)
    res = analyze_dreb2a_mutation("V79A", cultivar="IR64")
    assert res.transformer_score < -2.0
    assert "Loss-of-Function" in res.predicted_functional_effect
    assert "Rentan" in res.drought_tolerance_index


def test_dms_scan():
    dms = generate_dms_scan(start_pos=75, end_pos=80)
    assert len(dms.positions) == 6
    assert dms.positions[0].position == 75
    assert "Y" in dms.positions[0].scores


def test_local_cultivars():
    assert len(LOCAL_CULTIVARS) >= 5
    names = [c.cultivar_name for c in LOCAL_CULTIVARS]
    assert "Gogo Jatiluhur" in names
    assert "Salumpikit" in names
    assert "Rojolele" in names


def test_api_phytoai_domains():
    resp = client.get("/api/v1/phytoai/dreb2a/domains")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4


def test_api_phytoai_predict():
    payload = {"variant": "P168L", "cultivar": "Rojolele"}
    resp = client.post("/api/v1/phytoai/dreb2a/predict-mutation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["variant"] == "P168L"
    assert data["transformer_score"] > 1.0


def test_api_phytoai_local_cultivars():
    resp = client.get("/api/v1/phytoai/dreb2a/local-cultivars")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5


def test_drought_regions_api():
    resp = client.get("/api/v1/phytoai/drought-regions")
    assert resp.status_code == 200
    regions = resp.json()
    assert len(regions) >= 5
    r_ids = [r["region_id"] for r in regions]
    assert "demak-pati" in r_ids
    assert "ntt-semiarid" in r_ids
    assert "gunungkidul-karst" in r_ids


def test_demak_pati_regional_case():
    resp = client.get("/api/v1/phytoai/drought-regions/demak-pati")
    assert resp.status_code == 200
    reg = resp.json()
    assert "Demak" in reg["region_name"]
    assert "Pati" in reg["region_name"]
    assert "Vertisol" in reg["agroecosystem_type"] or "Lempung" in reg["agroecosystem_type"]
    assert "P168L" in reg["recommended_mutations"]


def test_ntt_semiarid_regional_case():
    resp = client.get("/api/v1/phytoai/drought-regions/ntt-semiarid")
    assert resp.status_code == 200
    reg = resp.json()
    assert "Nusa Tenggara Timur" in reg["region_name"]
    assert "Semi-Arid" in reg["agroecosystem_type"]
    assert "V79I" in reg["recommended_mutations"]


def test_mutation_prediction_regional_notes():
    # Test Demak-Pati regional analysis on Inpari 32
    payload = {
        "variant": "P168L",
        "cultivar": "Inpari 32 HDB",
        "target_region": "demak-pati"
    }
    resp = client.post("/api/v1/phytoai/dreb2a/predict-mutation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["regional_adaptation_notes"] is not None
    assert "Demak" in data["regional_adaptation_notes"]
    assert "Pati" in data["regional_adaptation_notes"]


def test_inarisk_metadata_api():
    resp = client.get("/api/v1/phytoai/inarisk/metadata")
    assert resp.status_code == 200
    data = resp.json()
    assert "inarisk" in data["service_name"]
    assert "gis.bnpb.go.id" in data["service_url"]
    assert "100m" in data["pixel_resolution"]


def test_inarisk_risk_assessment_api():
    resp = client.get("/api/v1/phytoai/inarisk/risk-assessment")
    assert resp.status_code == 200
    data = resp.json()
    assert "demak-pati" in data
    assert "ntt-semiarid" in data
    assert data["demak-pati"]["inarisk_hazard_level"] == "TINGGI (High Hazard)"
    assert data["ntt-semiarid"]["inarisk_hazard_level"] == "SANGAT TINGGI (Extreme Hazard)"


def test_inarisk_single_region():
    resp = client.get("/api/v1/phytoai/inarisk/risk-assessment/demak-pati")
    assert resp.status_code == 200
    data = resp.json()
    assert "Demak" in data["region_name"]
    assert "Pati" in data["region_name"]
    assert data["inarisk_risk_index"] > 0.8


def test_assess_coordinates_api():
    # Test point in Demak/Pati (-6.8944, 110.8)
    resp = client.get("/api/v1/phytoai/assess-coordinates?lat=-6.8944&lon=110.8")
    assert resp.status_code == 200
    data = resp.json()
    assert "demak-pati" in data["nearest_region_id"]
    assert data["inarisk_hazard_score"] >= 0.70
    assert data["primary_mutation"] in ["P168L", "V79I"]
    assert "Jawa" in data["island_group"]


def test_assess_coordinates_post_api():
    payload = {"latitude": -10.1772, "longitude": 123.6070}
    resp = client.post("/api/v1/phytoai/assess-coordinates", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "ntt" in data["nearest_region_id"]
    assert data["inarisk_hazard_score"] >= 0.80
    assert "P168L" in data["recommended_mutations"]


def test_drought_regions_filter_api():
    resp = client.get("/api/v1/phytoai/drought-regions?province=Jawa")
    assert resp.status_code == 200
    regions = resp.json()
    assert len(regions) >= 4
    for r in regions:
        assert any("Jawa" in p for p in r["provinces"])

    # Search filter test
    resp_search = client.get("/api/v1/phytoai/drought-regions?search=Madura")
    assert resp_search.status_code == 200
    madura_regions = resp_search.json()
    assert len(madura_regions) >= 1
    assert "Madura" in madura_regions[0]["region_name"]
