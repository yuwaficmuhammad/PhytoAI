#!/usr/bin/env python3
"""
scripts/fetch_dreb2a_fasta.py
Mengunduh sekuens nukleotida gen DREB2A dari NCBI GenBank berdasarkan data/accessions.csv.
Sesuai Proposal Butir 1: Urutan nukleotida DREB2A dari minimal 5 landrace padi lokal + genom referensi.
"""

import os
import sys
import csv
import argparse
import logging
from typing import List, Dict, Any, Tuple
import httpx

# Tambahkan direktori root proyek ke sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.services.db_service import insert_landrace_sequence

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fetch_dreb2a")

NCBI_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def read_accessions_csv(csv_path: str) -> List[Dict[str, str]]:
    """Membaca daftar aksesi dari CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Berkas accessions.csv tidak ditemukan: {csv_path}")

    records = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({k.strip(): v.strip() for k, v in row.items()})
    return records


def validate_accessions(records: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Memisahkan aksesi valid vs placeholder.
    Memberi peringatan ilmiah jika landrace valid < 5.
    """
    valid = []
    pending = []

    for r in records:
        acc = r.get("accession", "")
        if not acc or acc.startswith("[") or "BELUM TERSEDIA" in acc:
            pending.append(r)
        else:
            valid.append(r)

    # Landrace lokal (di luar referensi Nipponbare)
    local_landraces = [r for r in valid if "nipponbare" not in r["landrace_name"].lower()]

    if len(local_landraces) < 5:
        logger.warning(
            f"PERINGATAN CAKUPAN RISET (Proposal Butir 1): "
            f"Hanya {len(local_landraces)} landrace lokal dengan aksesi valid (< 5). "
            f"{len(pending)} landrace masih berstatus [DATA BELUM TERSEDIA] dan harus diisi manual di {records}."
        )

    return valid, pending


def download_fasta_from_ncbi(accession: str, api_key: str = None) -> str:
    """Mengunduh sekuens nukleotida format FASTA dari NCBI E-utilities."""
    params = {
        "db": "nuccore",
        "id": accession,
        "rettype": "fasta",
        "retmode": "text"
    }
    if api_key:
        params["api_key"] = api_key

    headers = {"User-Agent": "PhytoAI-Genetics/2.0 (Academic Research; Salafiyah Kajen Pati)"}

    with httpx.Client(timeout=30.0) as client:
        response = client.get(NCBI_EFETCH_URL, params=params, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(
                f"Gagal mengunduh FASTA untuk aksesi {accession} (HTTP {response.status_code}): {response.text[:200]}"
            )
        fasta_text = response.text.strip()
        if not fasta_text or not fasta_text.startswith(">"):
            raise ValueError(f"Hasil unduhan NCBI untuk {accession} bukan format FASTA yang valid: {fasta_text[:100]}")
        return fasta_text


def parse_fasta(fasta_text: str) -> Tuple[str, str]:
    """Memisahkan header FASTA dan isi sekuens nukleotida."""
    lines = fasta_text.strip().splitlines()
    header = lines[0] if lines else ""
    sequence = "".join(line.strip().upper() for line in lines[1:] if line.strip())
    return header, sequence


def calculate_gc(sequence: str) -> float:
    """Menghitung persentase GC dari sekuens nukleotida."""
    if not sequence:
        return 0.0
    gc_count = sequence.count("G") + sequence.count("C")
    return round((gc_count / len(sequence)) * 100, 2)


def main():
    parser = argparse.ArgumentParser(description="Fetch DREB2A FASTA from NCBI GenBank.")
    parser.add_argument("--csv-path", default="data/accessions.csv", help="Jalur berkas accessions.csv")
    parser.add_argument("--output-dir", default="data/raw", help="Direktori penyimpanan FASTA mentah")
    parser.add_argument("--skip-download-if-exists", action="store_true", help="Lewati unduhan jika berkas lokal ada")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    records = read_accessions_csv(args.csv_path)
    valid_records, pending_records = validate_accessions(records)

    logger.info(f"Ditemukan {len(valid_records)} entri valid dan {len(pending_records)} entri placeholder.")

    api_key = settings.NCBI_API_KEY

    for r in valid_records:
        landrace_name = r["landrace_name"]
        accession = r["accession"]
        source_note = r.get("source_note", "")

        safe_name = f"{landrace_name}_{accession}".replace(" ", "_").replace("/", "_")
        out_file = os.path.join(args.output_dir, f"{safe_name}.fasta")

        if args.skip_download_if_exists and os.path.exists(out_file):
            logger.info(f"Memuat sekuens lokal untuk {landrace_name} ({accession}) dari {out_file}")
            with open(out_file, "r", encoding="utf-8") as f:
                fasta_text = f.read()
        else:
            logger.info(f"Mengunduh FASTA NCBI untuk {landrace_name} (Aksesi: {accession})...")
            try:
                fasta_text = download_fasta_from_ncbi(accession, api_key=api_key)
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(fasta_text + "\n")
            except Exception as e:
                logger.error(f"Gagal mengunduh {accession}: {e}")
                continue

        header, seq = parse_fasta(fasta_text)
        gc = calculate_gc(seq)
        rec_id = insert_landrace_sequence(
            landrace_name=landrace_name,
            accession=accession,
            sequence=seq,
            length=len(seq),
            gc_content=gc,
            source_note=f"{source_note} | Header: {header}"
        )
        logger.info(f"Berhasil menyimpan {landrace_name} (Panjang: {len(seq)} bp, GC: {gc}%) ke database [ID: {rec_id}].")

    logger.info("Selesai.")


if __name__ == "__main__":
    main()
