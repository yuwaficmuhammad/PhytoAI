import pytest
from app.data.rice_targets import RICE_TARGETS, get_target_by_identifier


def test_rice_targets_loaded():
    assert len(RICE_TARGETS) >= 10


def test_get_target_by_symbol():
    target = get_target_by_identifier("OsDREB2A")
    assert target is not None
    assert target.ncbi_gene_id == 4324418
    assert "Kekeringan" in target.category

    target_dreb1a = get_target_by_identifier("osdreb1a")
    assert target_dreb1a is not None
    assert target_dreb1a.gene_symbol == "OsDREB1A"


def test_get_target_by_id():
    target = get_target_by_identifier("os-dreb2a")
    assert target is not None
    assert "Kekeringan" in target.category
    assert target.chromosome == "1"


def test_get_target_by_gene_id():
    target = get_target_by_identifier("4324418")
    assert target is not None
    assert target.gene_symbol == "OsDREB2A"

    target_dst = get_target_by_identifier("4334341")
    assert target_dst is not None
    assert target_dst.gene_symbol == "OsDST"
