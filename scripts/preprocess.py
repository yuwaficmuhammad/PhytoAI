#!/usr/bin/env python3
"""
scripts/preprocess.py
Pra-pemrosesan sekuens FASTA gen DREB2A:
1. Parsing header FASTA
2. Validasi alfabet nukleotida (A, C, G, T, N) dan pembersihan
3. Translasi CDS ke asam amino
4. Validasi start codon (ATG) & stop codon (TAA, TAG, TGA)
5. Ekstraksi koordinat domain AP2/ERF (default: bp 202 - 390 pada CDS 825 bp acuan)
"""

import os
import sys
import glob
import json
import argparse
import logging
from typing import Dict, Any, Tuple, Optional

# Standard genetic code table (NCBI Translation Table 1)
CODON_TABLE: Dict[str, str] = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G"
}

VALID_NUCLEOTIDES = set("ACGTN")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("preprocess")


def validate_nucleotide_sequence(sequence: str) -> Tuple[bool, Optional[str]]:
    """Memeriksa apakah sekuens hanya mengandung basa DNA yang sah (A, C, G, T, N)."""
    clean_seq = sequence.upper().strip()
    if not clean_seq:
        return False, "Sekuens kosong"
    invalid_chars = set(clean_seq) - VALID_NUCLEOTIDES
    if invalid_chars:
        return False, f"Karakter nukleotida tidak sah: {invalid_chars}"
    return True, None


def clean_sequence(raw_sequence: str) -> str:
    """Membersihkan whitespace, angka, spasi, dan mengubah ke huruf besar."""
    cleaned = "".join(c for c in raw_sequence if c.isalpha()).upper()
    is_valid, err = validate_nucleotide_sequence(cleaned)
    if not is_valid:
        raise ValueError(f"Sekuens tidak valid setelah pembersihan: {err}")
    return cleaned


def translate_cds(cds_seq: str) -> str:
    """
    Menerjemahkan urutan CDS nukleotida menjadi rantai asam amino (simbol 1 huruf).
    Stop codon diterjemahkan sebagai '*'.
    """
    clean_cds = clean_sequence(cds_seq)
    protein = []
    for i in range(0, len(clean_cds) - 2, 3):
        codon = clean_cds[i:i + 3]
        if len(codon) == 3:
            aa = CODON_TABLE.get(codon, "X")
            protein.append(aa)
    return "".join(protein)


def parse_fasta_file(filepath: str) -> Tuple[str, str]:
    """Membaca berkas FASTA dan mengembalikan header dan sekuens yang dibersihkan."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Berkas FASTA tidak ditemukan: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header = ""
    seq_lines = []
    for line in lines:
        line_str = line.strip()
        if line_str.startswith(">"):
            header = line_str
        elif line_str:
            seq_lines.append(line_str)

    sequence = clean_sequence("".join(seq_lines))
    return header, sequence


def process_fasta(
    input_path: str,
    output_dir: str,
    ap2_start_nt: int = 202,
    ap2_end_nt: int = 390
) -> Dict[str, Any]:
    """
    Memproses satu berkas FASTA dan menyimpan hasil pembersihan serta metadata.
    """
    header, sequence = parse_fasta_file(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    protein = translate_cds(sequence)
    has_valid_start = sequence.startswith("ATG")
    has_valid_stop = sequence[-3:] in ("TAA", "TAG", "TGA")

    gc_count = sequence.count("G") + sequence.count("C")
    gc_percent = round((gc_count / len(sequence)) * 100, 2) if sequence else 0.0

    # Ekstraksi domain AP2/ERF (1-based index)
    ap2_seq = sequence[ap2_start_nt - 1:ap2_end_nt] if len(sequence) >= ap2_end_nt else ""

    summary = {
        "file": os.path.basename(input_path),
        "header": header,
        "nt_length": len(sequence),
        "gc_percent": gc_percent,
        "has_valid_start_atg": has_valid_start,
        "has_valid_stop": has_valid_stop,
        "protein_length": len(protein),
        "ap2_domain_nt_length": len(ap2_seq),
        "ap2_domain_aa": translate_cds(ap2_seq) if ap2_seq else ""
    }

    os.makedirs(output_dir, exist_ok=True)
    out_fasta = os.path.join(output_dir, f"{base_name}_cleaned.fasta")
    with open(out_fasta, "w", encoding="utf-8") as f:
        f.write(f"{header} [cleaned; length={len(sequence)}nt; gc={gc_percent}%]\n")
        # Format 60 nt per baris standar FASTA
        for i in range(0, len(sequence), 60):
            f.write(sequence[i:i + 60] + "\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Preprocess FASTA files for PhytoAI-Genetics.")
    parser.add_argument("--input-dir", default="data/raw", help="Direktori FASTA mentah")
    parser.add_argument("--output-dir", default="data/processed", help="Direktori FASTA hasil pra-pemrosesan")
    args = parser.parse_args()

    files = glob.glob(os.path.join(args.input_dir, "*.fasta"))
    if not files:
        logger.warning(f"Tidak ada berkas .fasta ditemukan di {args.input_dir}.")
        return

    summaries = []
    for fp in files:
        try:
            summary = process_fasta(fp, args.output_dir)
            summaries.append(summary)
            logger.info(
                f"Selesai pra-pemrosesan {summary['file']}: {summary['nt_length']} bp, "
                f"GC {summary['gc_percent']}%, {summary['protein_length']} aa."
            )
        except Exception as e:
            logger.error(f"Gagal memproses {fp}: {e}")

    summary_file = os.path.join(args.output_dir, "preprocessing_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)
    logger.info(f"Ringkasan pra-pemrosesan disimpan ke {summary_file}")


if __name__ == "__main__":
    main()
