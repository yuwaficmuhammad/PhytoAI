#!/usr/bin/env python3
"""
scripts/train_heads.py
Pelatihan arsitektur Dual-Prediction Head (MLP) pada representasi embedding DNABERT-2.
Sesuai Proposal Butir 5 dan Deviasi Ilmiah D3:
- Pintu pengaman integritas ilmiah (Data Gating): Menolak melatih tanpa data fenotipe riil terukur.
- Mencegah fabrikasi data training sintetis.
"""

import os
import sys
import csv
import argparse
import logging
from typing import Optional, Tuple, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phytoai.heads import get_dual_head_model, CLASS_NAMES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_heads")


def check_training_data_prerequisites(
    class_labels_path: str,
    lri_phenotype_path: str,
    min_samples: int = 30
) -> Tuple[bool, str]:
    """
    Memeriksa keberadaan dan kecukupan data fenotipe riil untuk melatih model.
    Menegakkan integritas ilmiah: zero tolerance terhadap pelatihan pada data fiktif/kosong.
    """
    if not os.path.exists(class_labels_path):
        return False, (
            f"Berkas label klasifikasi varian ({class_labels_path}) tidak ditemukan.\n"
            f"Sesuai Deviasi Ilmiah D3: Proposal tidak menyediakan dataset label biologis "
            f"(Benign/Deleterious/Beneficial). Kepala prediksi tidak boleh dilatih dengan data karangan."
        )

    if not os.path.exists(lri_phenotype_path):
        return False, (
            f"Berkas fenotipe Leaf Rolling Index ({lri_phenotype_path}) tidak ditemukan.\n"
            f"Sesuai Deviasi Ilmiah D3: Pelatihan regresi LRI di bawah cekaman osmotik "
            f"memerlukan data fenotipe basah terukur dari uji laboratorium/lapangan nyata."
        )

    # Validasi jumlah baris data
    try:
        with open(class_labels_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            class_rows = list(reader)
        with open(lri_phenotype_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            lri_rows = list(reader)
    except Exception as e:
        return False, f"Gagal membaca berkas CSV data pelatihan: {e}"

    if len(class_rows) < min_samples or len(lri_rows) < min_samples:
        return False, (
            f"Jumlah sampel berlabel tidak mencukupi untuk pelatihan ilmiah yang valid "
            f"(ditemukan {len(class_rows)} klasifikasi, {len(lri_rows)} LRI; batas minimum: {min_samples})."
        )

    return True, "Data fenotipe riil terverifikasi."


def run_training_loop(
    embeddings_tensor: Any,
    labels_class_tensor: Any,
    labels_lri_tensor: Any,
    epochs: int = 5,
    lr: float = 1e-3,
    lri_weight: float = 1.0
):
    """
    Menjalankan loop pelatihan PyTorch dengan optimasi AdamW dan loss multi-task.
    Hanya dijalankan jika data riil telah divalidasi atau dalam pengetesan sintetis terisolasi.
    """
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
    except ImportError:
        raise ImportError("PyTorch belum terpasang. Pasang dengan: pip install -r requirements-ml.txt")

    model = get_dual_head_model(input_dim=embeddings_tensor.shape[1])
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    criterion_class = nn.CrossEntropyLoss()
    criterion_lri = nn.MSELoss()

    model.train()
    history = []

    for epoch in range(epochs):
        optimizer.zero_grad()
        logits, lri_pred = model(embeddings_tensor)

        loss_c = criterion_class(logits, labels_class_tensor)
        loss_r = criterion_lri(lri_pred.squeeze(-1), labels_lri_tensor)
        total_loss = loss_c + (lri_weight * loss_r)

        total_loss.backward()
        optimizer.step()

        history.append({
            "epoch": epoch + 1,
            "total_loss": round(total_loss.item(), 4),
            "class_loss": round(loss_c.item(), 4),
            "lri_loss": round(loss_r.item(), 4)
        })

    return model, history


def main():
    parser = argparse.ArgumentParser(description="Train Dual-Prediction Head (Classification & LRI Regression).")
    parser.add_argument("--class-labels", default="data/labels_variant_class.csv", help="Jalur CSV label varian riil")
    parser.add_argument("--lri-phenotype", default="data/phenotype_lri.csv", help="Jalur CSV fenotipe LRI riil")
    parser.add_argument("--min-samples", type=int, default=30, help="Jumlah minimal sampel untuk mengizinkan pelatihan")
    parser.add_argument("--synthetic-test-only", action="store_true", help="Gunakan hanya dalam unit testing terisolasi")
    parser.add_argument("--output-weights", default="data/dual_head_weights.pt", help="Jalur penyimpanan bobot model")
    args = parser.parse_args()

    if args.synthetic_test_only:
        logger.warning(
            "MODUS SYNTHETIC_TEST_ONLY DIAKTIFKAN: Menguji arsitektur komputasi dalam isolasi pengujian. "
            "Bobot yang dihasilkan TIDAK VALID untuk interpretasi ilmiah biologis."
        )
        try:
            import torch
            mock_emb = torch.randn(10, 768)
            mock_class = torch.randint(0, 3, (10,))
            mock_lri = torch.rand(10)
            model, hist = run_training_loop(mock_emb, mock_class, mock_lri, epochs=2)
            logger.info(f"Uji coba loop pelatihan sintetis berhasil: {hist}")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Gagal dalam uji coba sintetis: {e}")
            sys.exit(1)

    # Validasi Pintu Pengaman (Data Gating)
    is_valid, reason = check_training_data_prerequisites(
        args.class_labels, args.lri_phenotype, min_samples=args.min_samples
    )

    if not is_valid:
        logger.error("\n" + "=" * 70 + "\nPELATIHAN DITOLAK (PINTU PENGAMAN INTEGRITAS ILMIAH):\n" + reason + "\n" + "=" * 70)
        sys.exit(1)

    logger.info("Data fenotipe riil terdeteksi. Melanjutkan proses pelatihan...")


if __name__ == "__main__":
    main()
