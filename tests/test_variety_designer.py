import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.variety_designer_service import (
    get_nucleotide_edit_blueprint,
    synthesize_new_variety,
    PLANT_GENOMICS_CATALOG
)

client = TestClient(app)


def test_nucleotide_blueprint_p168l():
    bp = get_nucleotide_edit_blueprint("P168L")
    assert bp.gene_symbol == "OsDREB2A"
    assert bp.amino_acid_position == 168
    assert bp.exact_base_number_edited == 503
    assert "C" in bp.wildtype_codon
    assert "T" in bp.mutant_codon
    assert "503" in bp.exact_base_change
    assert "CBE" in bp.editing_technology or "Cytosine" in bp.editing_technology


def test_nucleotide_blueprint_v79i():
    bp = get_nucleotide_edit_blueprint("V79I")
    assert bp.gene_symbol == "OsDREB2A"
    assert bp.amino_acid_position == 79
    assert bp.exact_base_number_edited == 235
    assert "G" in bp.wildtype_codon
    assert "A" in bp.mutant_codon
    assert "ABE" in bp.editing_technology or "Adenine" in bp.editing_technology


def test_synthesize_variety_logic():
    res = synthesize_new_variety(
        parent_cultivar="Ciherang",
        selected_traits=["drought_dreb2a", "deep_root_dro1"],
        custom_name="Salafiyah Padi Super"
    )
    assert res.variety_name == "Salafiyah Padi Super"
    assert "Periset MA Salafiyah Kajen Pati" in res.institution
    assert len(res.molecular_blueprints) == 2
    assert "OsDREB2A" in res.stacked_genes[0]


def test_api_variety_designer_blueprint():
    resp = client.get("/api/v1/phytoai/variety-designer/blueprint/P168L")
    assert resp.status_code == 200
    data = resp.json()
    assert data["exact_base_number_edited"] == 503
    assert data["wildtype_codon"] == "CCT"
    assert data["mutant_codon"] == "CTT"


def test_api_variety_designer_plant_catalog():
    resp = client.get("/api/v1/phytoai/variety-designer/plant-catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert "Oryza sativa (Padi)" in data
    assert "Zea mays (Jagung)" in data
    assert "Glycine max (Kedelai)" in data


def test_api_variety_designer_synthesize():
    payload = {
        "parent_cultivar": "Situ Bagendit",
        "selected_traits": ["drought_dreb2a", "submergence_sub1a"],
        "target_environment": "Pantura Jawa Rawan Banjir & Kering",
        "custom_name": "Salafiyah BioPadi-Amfibi"
    }
    resp = client.post("/api/v1/phytoai/variety-designer/synthesize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["variety_name"] == "Salafiyah BioPadi-Amfibi"
    assert len(data["molecular_blueprints"]) == 2
    assert "Induk" in data["scientific_summary"] or "Situ Bagendit" in data["scientific_summary"]
