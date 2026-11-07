"""
Unit tests for mutation consequence evaluation and scoring
(tests/test_scoring.py)
"""

import pytest
from phytoai.scoring import evaluate_mutation_consequence


def test_evaluate_mutation_synonymous():
    # Kodon 1: ATG (M)
    # Kodon 68: GGT (G) -> nt 202, 203, 204
    # nt 204: T -> A menghasilkan GGA (G) => synonymous
    cds = "ATG" * 67 + "GGT" + "TAA"
    res = evaluate_mutation_consequence(cds, position_nt_1based=204, alt_nt="A")
    assert res["mutation_type"] == "synonymous"
    assert res["ref_nt"] == "T"
    assert res["alt_nt"] == "A"
    assert res["wt_aa"] == "G"
    assert res["mut_aa"] == "G"


def test_evaluate_mutation_missense():
    # nt 202: G -> A menghasilkan AGT (S) => missense
    cds = "ATG" * 67 + "GGT" + "TAA"
    res = evaluate_mutation_consequence(cds, position_nt_1based=202, alt_nt="A")
    assert res["mutation_type"] == "missense"
    assert res["ref_nt"] == "G"
    assert res["alt_nt"] == "A"
    assert res["wt_aa"] == "G"
    assert res["mut_aa"] == "S"


def test_evaluate_mutation_nonsense():
    # GAA (E) -> TAA (*) => nonsense
    cds = "ATG" + "GAA" + "TAA"
    res = evaluate_mutation_consequence(cds, position_nt_1based=4, alt_nt="T")
    assert res["mutation_type"] == "nonsense"
    assert res["ref_nt"] == "G"
    assert res["alt_nt"] == "T"
    assert res["wt_aa"] == "E"
    assert res["mut_aa"] == "*"


def test_evaluate_mutation_out_of_bounds():
    cds = "ATGGCTAAGTAA"
    with pytest.raises(ValueError) as exc:
        evaluate_mutation_consequence(cds, position_nt_1based=0, alt_nt="A")
    assert "di luar rentang" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        evaluate_mutation_consequence(cds, position_nt_1based=13, alt_nt="A")
    assert "di luar rentang" in str(exc.value)


def test_evaluate_mutation_invalid_nucleotide():
    cds = "ATGGCTAAGTAA"
    with pytest.raises(ValueError) as exc:
        evaluate_mutation_consequence(cds, position_nt_1based=2, alt_nt="Z")
    assert "tidak sah" in str(exc.value)
