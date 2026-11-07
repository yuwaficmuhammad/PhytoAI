"""
Unit tests for FASTA preprocessing and nucleotide sequence validation
(tests/test_preprocessing.py)
"""

import os
import tempfile
import pytest
from scripts.preprocess import (
    validate_nucleotide_sequence,
    clean_sequence,
    translate_cds,
    parse_fasta_file,
    process_fasta,
)


def test_validate_nucleotide_sequence():
    valid, err = validate_nucleotide_sequence("ATGCGATCGATCG")
    assert valid is True
    assert err is None

    valid_n, err = validate_nucleotide_sequence("ATGCNNAT")
    assert valid_n is True

    invalid, err = validate_nucleotide_sequence("ATGCRZ")
    assert invalid is False
    assert "tidak sah" in err

    empty, err = validate_nucleotide_sequence("")
    assert empty is False
    assert "kosong" in err


def test_clean_sequence():
    cleaned = clean_sequence("  atg\n 123 cgat ")
    assert cleaned == "ATGCGAT"


def test_translate_cds():
    # ATG (M), GCT (A), AAG (K), TAA (*)
    cds = "ATGGCTAAGTAA"
    protein = translate_cds(cds)
    assert protein == "MAK*"


def test_parse_fasta_file_and_process():
    fasta_content = ">OsDREB2A_test [organism=Oryza sativa]\nATGGCTAAGTAA\n"
    with tempfile.NamedTemporaryFile("w+", suffix=".fasta", delete=False) as tf:
        tf.write(fasta_content)
        tf_path = tf.name

    try:
        header, seq = parse_fasta_file(tf_path)
        assert header.startswith(">OsDREB2A_test")
        assert seq == "ATGGCTAAGTAA"

        with tempfile.TemporaryDirectory() as out_dir:
            summary = process_fasta(tf_path, out_dir, ap2_start_nt=1, ap2_end_nt=6)
            assert summary["nt_length"] == 12
            assert summary["has_valid_start_atg"] is True
            assert summary["has_valid_stop"] is True
            assert summary["protein_length"] == 4
    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)
