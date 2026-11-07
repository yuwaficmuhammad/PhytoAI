"""
Unit tests for Dual-Prediction Head and Scientific Data Gating
(tests/test_heads.py)
"""

import os
import tempfile
import csv
import pytest
from phytoai.heads import format_prediction_output
from scripts.train_heads import check_training_data_prerequisites


def test_data_gating_missing_files():
    is_valid, reason = check_training_data_prerequisites(
        "nonexistent_class.csv", "nonexistent_lri.csv"
    )
    assert is_valid is False
    assert "tidak ditemukan" in reason
    assert "Deviasi Ilmiah D3" in reason


def test_data_gating_insufficient_samples():
    with tempfile.TemporaryDirectory() as tmpdir:
        class_csv = os.path.join(tmpdir, "class.csv")
        lri_csv = os.path.join(tmpdir, "lri.csv")

        # Write only 5 samples (< min_samples 30)
        with open(class_csv, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["variant_id", "label"])
            for i in range(5):
                writer.writerow([f"var_{i}", "Benign"])

        with open(lri_csv, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["variant_id", "lri"])
            for i in range(5):
                writer.writerow([f"var_{i}", 0.5])

        is_valid, reason = check_training_data_prerequisites(
            class_csv, lri_csv, min_samples=30
        )
        assert is_valid is False
        assert "tidak mencukupi" in reason


def test_data_gating_sufficient_samples():
    with tempfile.TemporaryDirectory() as tmpdir:
        class_csv = os.path.join(tmpdir, "class.csv")
        lri_csv = os.path.join(tmpdir, "lri.csv")

        with open(class_csv, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["variant_id", "label"])
            for i in range(35):
                writer.writerow([f"var_{i}", "Benign"])

        with open(lri_csv, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["variant_id", "lri"])
            for i in range(35):
                writer.writerow([f"var_{i}", 0.45])

        is_valid, reason = check_training_data_prerequisites(
            class_csv, lri_csv, min_samples=30
        )
        assert is_valid is True
        assert "terverifikasi" in reason


def test_format_prediction_output_zero_shot():
    res_pos = format_prediction_output(delta_pll=0.85, is_trained=False)
    assert res_pos["is_zero_shot"] is True
    assert res_pos["predicted_lri"] is None
    assert "kandidat zero-shot (bukan Beneficial terverifikasi)" in res_pos["predicted_class"]

    res_neg = format_prediction_output(delta_pll=-2.10, is_trained=False)
    assert res_neg["is_zero_shot"] is True
    assert res_neg["predicted_lri"] is None
    assert "kandidat disrupted (zero-shot)" in res_neg["predicted_class"]


def test_dual_head_architecture_torch_if_available():
    try:
        import torch
        from phytoai.heads import get_dual_head_model
    except ImportError:
        pytest.skip("PyTorch tidak terpasang di environment lokal (dirancang untuk Google Colab)")

    model = get_dual_head_model(input_dim=768, hidden_dim=64)
    # SYNTHETIC_TEST_ONLY dummy tensor
    mock_input = torch.randn(4, 768)
    logits, lri = model(mock_input)

    assert logits.shape == (4, 3)
    assert lri.shape == (4, 1)

    # Sigmoid constraint: lri must be in [0.0, 1.0]
    assert (lri >= 0.0).all() and (lri <= 1.0).all()
