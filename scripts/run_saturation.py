#!/usr/bin/env python3
"""
scripts/run_saturation.py
Eksekusi mutagenesis saturasi in silico pada domain AP2/ERF gen DREB2A.
Sesuai Proposal Butir 4:
- Substitusi sistematis nukleotida pada domain AP2/ERF pengikat DNA.
- Menghitung pergeseran pseudo-log-likelihood (delta PLL) dan pseudo-perplexity via DNABERT-2.
- Menyimpan hasil secara idempoten ke database SQLite dan CSV.
"""

import os
import sys
import csv
import argparse
import logging
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.services.db_service import insert_saturation_score, get_landrace_sequence
from phytoai.scoring import evaluate_mutation_consequence, compute_delta_pll
from scripts.preprocess import parse_fasta_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_saturation")

NUCLEOTIDES = ["A", "C", "G", "T"]


def run_saturation_mutagenesis(
    landrace_name: str,
    sequence: str,
    start_nt: int = 202,
    end_nt: int = 390,
    model_name: str = "zhihan1996/DNABERT-2-117M",
    dry_run: bool = False,
    window_nt: int = 30
) -> List[Dict[str, Any]]:
    """
    Menjalankan mutagenesis saturasi in silico pada rentang nukleotida domain AP2/ERF.
    """
    seq_len = len(sequence)
    if end_nt > seq_len:
        raise ValueError(f"Batas akhir koordinat ({end_nt}) melebihi panjang sekuens ({seq_len} bp).")

    model = None
    tokenizer = None
    device = None

    if not dry_run:
        try:
            from transformers import AutoTokenizer, AutoModelForMaskedLM
            import torch
            from phytoai.embedding import get_torch_device

            device = get_torch_device()
            hf_token = settings.HF_TOKEN or os.getenv("HF_TOKEN")
            logger.info(f"Memuat DNABERT-2 MaskedLM ({model_name}) pada peranti {device}...")
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=hf_token)
            model = AutoModelForMaskedLM.from_pretrained(model_name, trust_remote_code=True, token=hf_token)
            model.to(device)
            model.eval()
        except Exception as e:
            logger.error(
                f"Tidak dapat memuat model DNABERT-2 ({e}).\n"
                f"Sesuai Proposal Butir 7, inferensi neural penuh dirancang berjalan di Google Colab dengan GPU.\n"
                f"Gunakan flag --dry-run untuk memetakan koordinat dan konsekuensi kodon tanpa evaluasi skor model."
            )
            raise RuntimeError(f"Gagal memuat model DNABERT-2: {e}")

    results = []
    total_positions = end_nt - start_nt + 1
    total_mutations = total_positions * 3

    logger.info(
        f"Memulai mutagenesis saturasi in silico untuk {landrace_name} pada rentang nt {start_nt}-{end_nt} "
        f"({total_positions} posisi x 3 alternatif = {total_mutations} total varian)..."
    )

    for pos in range(start_nt, end_nt + 1):
        ref_nt = sequence[pos - 1]
        alts = [nt for nt in NUCLEOTIDES if nt != ref_nt]

        for alt in alts:
            bio_effect = evaluate_mutation_consequence(sequence, pos, alt)

            delta_pll = None
            pseudo_ppl = None

            if model is not None and tokenizer is not None:
                try:
                    score_res = compute_delta_pll(
                        wt_sequence=sequence,
                        position_nt_1based=pos,
                        alt_nt=alt,
                        model=model,
                        tokenizer=tokenizer,
                        device=device,
                        window_nt=window_nt
                    )
                    delta_pll = score_res["delta_pll"]
                    pseudo_ppl = score_res["mut_pseudo_perplexity"]
                except Exception as ex:
                    logger.warning(f"Gagal menghitung skor pada posisi {pos} {ref_nt}>{alt}: {ex}")

            record = {
                "landrace": landrace_name,
                "position_nt": pos,
                "ref": ref_nt,
                "alt": alt,
                "mutation_type": bio_effect["mutation_type"],
                "wt_codon": bio_effect["wt_codon"],
                "mut_codon": bio_effect["mut_codon"],
                "wt_aa": bio_effect["wt_aa"],
                "mut_aa": bio_effect["mut_aa"],
                "delta_pll": delta_pll,
                "pseudo_perplexity": pseudo_ppl,
                "model_name": model_name if not dry_run else "None (dry-run)",
                "window": window_nt,
            }
            results.append(record)

            # Simpan idempoten ke SQLite database
            insert_saturation_score(
                landrace=landrace_name,
                position_nt=pos,
                ref=ref_nt,
                alt=alt,
                delta_pll=delta_pll,
                pseudo_perplexity=pseudo_ppl,
                mutation_type=bio_effect["mutation_type"],
                wt_codon=bio_effect["wt_codon"],
                mut_codon=bio_effect["mut_codon"],
                wt_aa=bio_effect["wt_aa"],
                mut_aa=bio_effect["mut_aa"],
                model_name=record["model_name"],
                window=window_nt
            )

    logger.info(f"Selesai! {len(results)} varian berhasil dievaluasi dan disimpan.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Run saturation mutagenesis on AP2/ERF domain.")
    parser.add_argument("--landrace", default="Nipponbare", help="Nama landrace target")
    parser.add_argument("--fasta-file", default="data/processed/Nipponbare_NM_001051515.2_cleaned.fasta", help="Jalur berkas FASTA")
    parser.add_argument("--start-nt", type=int, default=settings.AP2_DOMAIN_NT_START, help="Koordinat awal nt domain AP2")
    parser.add_argument("--end-nt", type=int, default=settings.AP2_DOMAIN_NT_END, help="Koordinat akhir nt domain AP2")
    parser.add_argument("--dry-run", action="store_true", help="Petakan kodon dan asam amino tanpa model neural")
    parser.add_argument("--output-csv", default="data/processed/saturation_mutagenesis_results.csv", help="Jalur luaran CSV")
    args = parser.parse_args()

    # Muat sekuens
    if os.path.exists(args.fasta_file):
        _, sequence = parse_fasta_file(args.fasta_file)
    else:
        db_rec = get_landrace_sequence(args.landrace)
        if not db_rec:
            logger.error(f"Sekuens untuk {args.landrace} tidak ditemukan di {args.fasta_file} maupun di database.")
            sys.exit(1)
        sequence = db_rec["sequence"]

    results = run_saturation_mutagenesis(
        landrace_name=args.landrace,
        sequence=sequence,
        start_nt=args.start_nt,
        end_nt=args.end_nt,
        dry_run=args.dry_run
    )

    if results and args.output_csv:
        os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
        fieldnames = list(results[0].keys())
        with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"Hasil mutagenesis saturasi disimpan ke CSV: {args.output_csv}")


if __name__ == "__main__":
    main()
