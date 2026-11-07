"""
phytoai/tokenization.py
Modul tokenisasi k-mer dan integrasi BPE AutoTokenizer untuk DNABERT-2.

Catatan Deviasi Ilmiah (D1):
Proposal menyebutkan tokenisasi k-mer (k=6, stride=1). Namun model DNABERT-2 (Zhou et al., 2023;
zhihan1996/DNABERT-2-117M) secara arsitektural menggunakan Byte-Pair Encoding (BPE)
dengan PreTrainedTokenizerFast (kosakata ~4096 token), bukan k-mer overlap seperti DNABERT-1.
Oleh karena itu:
1. Fungsi kmerize() disediakan untuk analisis frekuensi k-mer deskriptif (Rumusan Masalah 1).
2. Tokenisasi untuk model inferensi/embedding menggunakan AutoTokenizer bawaan DNABERT-2.
"""

from typing import List, Dict, Optional
import collections


def kmerize(sequence: str, k: int = 6, stride: int = 1) -> List[str]:
    """
    Membagi sekuens nukleotida menjadi token-token k-mer dengan stride tertentu.

    Parameter:
    - sequence: Urutan basa nukleotida (string)
    - k: Panjang k-mer (default: 6 sesuai proposal)
    - stride: Jarak pergeseran jendela (default: 1 untuk overlapping)

    Return:
    - List of k-mer strings. Jika panjang sekuens < k atau sequence kosong, mengembalikan list kosong.

    Rumus jumlah token:
    N_kmers = max(0, (len(seq) - k) // stride + 1)
    """
    if k <= 0:
        raise ValueError(f"Nilai k harus bernilai positif (> 0), diberikan: {k}")
    if stride <= 0:
        raise ValueError(f"Nilai stride harus bernilai positif (> 0), diberikan: {stride}")

    clean_seq = "".join(sequence.split()).upper()
    seq_len = len(clean_seq)

    if seq_len < k:
        return []

    kmers = []
    for i in range(0, seq_len - k + 1, stride):
        kmers.append(clean_seq[i:i + k])

    return kmers


def kmer_frequencies(kmers: List[str]) -> Dict[str, int]:
    """Menghitung frekuensi kemunculan setiap k-mer."""
    return dict(collections.Counter(kmers))


def get_dnabert2_tokenizer(model_name: str = "zhihan1996/DNABERT-2-117M"):
    """
    Memuat tokenizer bawaan DNABERT-2 (BPE PreTrainedTokenizerFast).
    Memerlukan dependensi transformers dan opsi trust_remote_code=True.
    """
    try:
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    except Exception as e:
        raise RuntimeError(
            f"Gagal memuat AutoTokenizer untuk {model_name}. Pastikan pustaka transformers terpasang "
            f"dan trust_remote_code=True diizinkan: {e}"
        )
