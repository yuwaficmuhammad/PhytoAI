import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.variety_designer_service import (
    get_nucleotide_edit_blueprint,
    synthesize_new_variety,
    PLANT_GENOMICS_CATALOG,
    get_research_varieties,
    get_graphical_analysis_data
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


def test_research_varieties_catalog():
    varieties = get_research_varieties()
    assert len(varieties) == 4
    v_names = [v["name"] for v in varieties]
    assert any("Agritama-1" in name for name in v_names)
    assert any("Amfibi-2" in name for name in v_names)
    assert any("Salina-3" in name for name in v_names)
    assert any("Savana-4" in name for name in v_names)


def test_graphical_analysis_dataset():
    data = get_graphical_analysis_data()
    assert "yield_comparison" in data
    assert "rwc_kinetics" in data
    assert "thermodynamic_stability" in data
    assert "radar_traits" in data
    assert len(data["yield_comparison"]["categories"]) >= 7


def test_api_research_varieties_endpoint():
    resp = client.get("/api/v1/phytoai/variety-designer/research-varieties")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4
    assert data[0]["institution"] == "Periset MA Salafiyah Kajen Pati"


def test_api_graphical_analysis_endpoint():
    resp = client.get("/api/v1/phytoai/variety-designer/graphical-analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert "yield_normal" in data["yield_comparison"]
    assert "Hari 25" in data["rwc_kinetics"]["days"]


def test_nucleotide_blueprint_e166k():
    bp = get_nucleotide_edit_blueprint("E166K")
    assert bp.gene_symbol == "OsDREB2A"
    assert bp.amino_acid_position == 166
    assert bp.exact_base_number_edited == 496
    assert bp.wildtype_codon == "GAG"
    assert bp.mutant_codon == "AAG"


def test_api_design_base_editing_with_nucleotide_details():
    resp = client.post("/api/v1/phytoai/dreb2a/design-base-editing?variant=P168L")
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_mutation"] == "P168L"
    assert data["exact_base_number_edited"] == 503
    assert "Basa #503" in data["exact_base_change"]
    assert data["cas9_cut_site_bp"] == 512
    assert data["mutant_codon"] == "CTT"


