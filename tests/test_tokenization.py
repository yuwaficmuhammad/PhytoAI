"""
Unit tests for k-mer tokenization
(tests/test_tokenization.py)
"""

import pytest
from phytoai.tokenization import kmerize, kmer_frequencies


def test_kmerize_basic():
    seq = "ATGCATGC"
    kmers = kmerize(seq, k=6, stride=1)
    # len = 8, k = 6, stride = 1 -> (8 - 6)/1 + 1 = 3 kmers
    assert len(kmers) == 3
    assert kmers == ["ATGCAT", "TGCATG", "GCATGC"]


def test_kmerize_stride_2():
    seq = "ATGCATGC"
    kmers = kmerize(seq, k=6, stride=2)
    # (8 - 6)/2 + 1 = 2 kmers
    assert len(kmers) == 2
    assert kmers == ["ATGCAT", "GCATGC"]


def test_kmerize_short_sequence():
    seq = "ATGC"
    kmers = kmerize(seq, k=6, stride=1)
    assert kmers == []


def test_kmerize_empty_sequence():
    kmers = kmerize("", k=6, stride=1)
    assert kmers == []


def test_kmerize_whitespace_and_lowercase():
    seq = "  atg\ncat  gc "
    kmers = kmerize(seq, k=6, stride=1)
    assert kmers == ["ATGCAT", "TGCATG", "GCATGC"]


def test_kmerize_invalid_k_or_stride():
    with pytest.raises(ValueError):
        kmerize("ATGCATGC", k=0)
    with pytest.raises(ValueError):
        kmerize("ATGCATGC", k=6, stride=0)


def test_kmer_frequencies():
    kmers = ["AAAAAA", "CCCCCC", "AAAAAA"]
    freq = kmer_frequencies(kmers)
    assert freq["AAAAAA"] == 2
    assert freq["CCCCCC"] == 1
