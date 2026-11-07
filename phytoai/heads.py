"""
phytoai/heads.py
Arsitektur Dual-Prediction Head (MLP) untuk klasifikasi varian dan regresi Leaf Rolling Index (LRI).
Sesuai Proposal Butir 5 dan Deviasi Ilmiah D3.

Arsitektur:
- Input: Representasi vektor embedding 768-dimensi dari encoder DNABERT-2.
- Lapisan tersembunyi (shared MLP) dengan normalisasi dan Dropout.
- Cabang 1: Klasifikasi varian 3-kelas (0: Benign, 1: Deleterious, 2: Beneficial) -> Logits [batch_size, 3]
- Cabang 2: Regresi Leaf Rolling Index (LRI) -> Skala kontinu [0.0, 1.0] via aktivasi Sigmoid.
"""

from typing import Dict, Any, Tuple, Optional
import os

CLASS_NAMES = ["Benign", "Deleterious", "Beneficial"]


def get_dual_head_model(input_dim: int = 768, hidden_dim: int = 256, dropout: float = 0.2):
    """
    Mengembalikan instance DualPredictionHead PyTorch.
    Memerlukan pustaka torch.
    """
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        raise ImportError(
            "PyTorch belum terpasang. Pasang dengan: pip install -r requirements-ml.txt "
            "atau jalankan di Google Colab."
        )

    class DualPredictionHead(nn.Module):
        def __init__(self, in_features: int = input_dim, hidden: int = hidden_dim, drop: float = dropout):
            super().__init__()
            # Lapisan tersembunyi bersama (shared representations)
            self.shared_fc = nn.Sequential(
                nn.Linear(in_features, hidden),
                nn.LayerNorm(hidden),
                nn.ReLU(),
                nn.Dropout(drop),
                nn.Linear(hidden, hidden // 2),
                nn.LayerNorm(hidden // 2),
                nn.ReLU(),
                nn.Dropout(drop)
            )

            # Cabang 1: Klasifikasi Varian (3 kelas)
            self.classifier = nn.Linear(hidden // 2, 3)

            # Cabang 2: Regresi Leaf Rolling Index (LRI 0.0 - 1.0)
            # Aktivasi Sigmoid menjamin luaran berada ketat dalam rentang [0.0, 1.0]
            self.regressor = nn.Sequential(
                nn.Linear(hidden // 2, 1),
                nn.Sigmoid()
            )

        def forward(self, embeddings: "torch.Tensor") -> Tuple["torch.Tensor", "torch.Tensor"]:
            """
            Forward pass.
            Input: embeddings tensor shape [batch_size, 768]
            Output:
            - logits: [batch_size, 3]
            - lri: [batch_size, 1]
            """
            shared = self.shared_fc(embeddings)
            logits = self.classifier(shared)
            lri = self.regressor(shared)
            return logits, lri

    return DualPredictionHead(input_dim, hidden_dim, dropout)


def format_prediction_output(
    delta_pll: Optional[float],
    is_trained: bool = False,
    logits: Optional[Any] = None,
    predicted_lri: Optional[float] = None
) -> Dict[str, Any]:
    """
    Format hasil evaluasi prediksi dengan gating integritas ilmiah.
    Jika model belum dilatih (is_trained=False):
    - Tidak mengarang skor LRI (dikembalikan None / [DATA BELUM TERSEDIA]).
    - Klasifikasi hanya berupa dugaan zero-shot berdasar likelihood sekuens.
    """
    if not is_trained:
        # Zero-shot heuristic fallback:
        # Menegaskan bahwa ini HANYA urutan likelihood model, BUKAN bukti fenotipe basah
        if delta_pll is not None and delta_pll > 0.5:
            pred_class = "kandidat zero-shot (bukan Beneficial terverifikasi)"
        elif delta_pll is not None and delta_pll < -1.0:
            pred_class = "kandidat disrupted (zero-shot)"
        else:
            pred_class = "unclassified (zero-shot)"

        return {
            "predicted_class": pred_class,
            "class_probabilities": None,
            "predicted_lri": None,
            "is_zero_shot": True,
            "method_note": (
                "Perhatian: Dual-head MLP belum dilatih karena ketiadaan data fenotipe riil (Deviasi D3). "
                "LRI tidak diestimasi untuk mencegah halusinasi data ilmiah."
            )
        }

    return {
        "predicted_class": "Trained_Evaluation",
        "predicted_lri": predicted_lri,
        "is_zero_shot": False,
        "method_note": "Evaluasi dari bobot MLP terlatih pada data fenotipe terverifikasi."
    }
