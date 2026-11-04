import pytest
from app.services.crispr_service import (
    reverse_complement,
    calculate_gc,
    analyze_crispr_targets
)


def test_reverse_complement():
    assert reverse_complement("ATGC") == "GCAT"
    assert reverse_complement("AATTGGCC") == "GGCCAATT"
    assert reverse_complement("atgc") == "GCAT"


def test_calculate_gc():
    assert calculate_gc("GCGC") == 100.0
    assert calculate_gc("ATAT") == 0.0
    assert calculate_gc("ATGC") == 50.0
    assert calculate_gc("GGCCAT") == 66.67


def test_analyze_crispr_targets_spcas9():
    # Construct a sequence with an NGG motif
    # 20 nt protospacer + CGG
    seq = "ATGGCTGGCATGTCTCTTCA" + "CGG" + "ATCGATCGATCGATCGATC"
    res = analyze_crispr_targets(sequence=seq, nuclease="SpCas9")
    
    assert res.nuclease == "SpCas9"
    assert res.total_sites_found >= 1
    
    # Check first forward site
    forward_sites = [s for s in res.sites if s.strand == "+"]
    assert len(forward_sites) >= 1
    first = forward_sites[0]
    assert first.protospacer_sequence == "ATGGCTGGCATGTCTCTTCA"
    assert first.pam == "CGG"
    assert first.has_poly_t_termination is False


def test_analyze_crispr_targets_poly_t_warning():
    # Sequence containing TTTT inside the 20 nt protospacer
    seq = "ATGGCTTTTTCTCTCTTCAT" + "AGG" + "ATCGATCGATCGATCGATC"
    res = analyze_crispr_targets(sequence=seq, nuclease="SpCas9")
    
    forward_sites = [s for s in res.sites if s.strand == "+"]
    assert len(forward_sites) >= 1
    site = forward_sites[0]
    assert site.has_poly_t_termination is True
    assert "TTTT" in site.quality_assessment


def test_analyze_crispr_targets_cas12a():
    # Cas12a PAM: TTTV (e.g. TTTA) at 5' followed by 23 nt protospacer
    seq = "TTTA" + "GGCATGTCTCTTCAGCATCCCTG" + "AAAAAAA"
    res = analyze_crispr_targets(sequence=seq, nuclease="Cas12a")
    
    assert res.nuclease == "Cas12a"
    assert res.total_sites_found >= 1
    
    site = res.sites[0]
    assert site.pam == "TTTA"
    assert len(site.protospacer_sequence) == 23



def test_crispr_sequence_too_long():
    """Sekuens > 100.000 nt harus ditolak oleh schema validation Pydantic (422) atau guard service (413)."""
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    long_seq = "ATGC" * 30000  # 120.000 nt — melebihi batas 100k
    payload = {"sequence": long_seq, "nuclease": "SpCas9"}
    resp = client.post("/api/v1/crispr/find-targets", json=payload)
    assert resp.status_code in (413, 422)


def test_crispr_sequence_too_short():
    """Sekuens < 23 nt harus ditolak Pydantic dengan 422."""
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    payload = {"sequence": "ATGCATGC", "nuclease": "SpCas9"}
    resp = client.post("/api/v1/crispr/find-targets", json=payload)
    assert resp.status_code == 422
