"""
phytoai/embedding.py
Ekstraksi representasi vektor 768-dimensi dari hidden state terakhir encoder
model DNABERT-2 (zhihan1996/DNABERT-2-117M) dengan mean pooling.
Sesuai Proposal Butir 3.
"""

from typing import Optional, Tuple, Any
import logging

logger = logging.getLogger("phytoai.embedding")


def get_torch_device():
    """
    Menentukan akselerator komputasi terbaik:
    CUDA (GPU NVIDIA / Colab) > MPS (Apple Silicon Mac) > CPU.
    """
    try:
        import torch
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    except ImportError:
        raise ImportError(
            "PyTorch belum terpasang di environment ini. "
            "Pasang dependensi ML dengan: pip install -r requirements-ml.txt "
            "atau jalankan di Google Colab (Proposal Butir 7)."
        )


def load_dnabert2_model_and_tokenizer(
    model_name: str = "zhihan1996/DNABERT-2-117M",
    device: Optional[Any] = None
) -> Tuple[Any, Any]:
    """
    Memuat AutoTokenizer dan AutoModel untuk DNABERT-2.
    Wajib menggunakan trust_remote_code=True sesuai model card resmi Hugging Face.
    """
    try:
        import torch
        from transformers import AutoTokenizer, AutoModel
    except ImportError:
        raise ImportError(
            "PyTorch atau Transformers belum terpasang. "
            "Pasang dengan: pip install -r requirements-ml.txt"
        )

    if device is None:
        device = get_torch_device()

    logger.info(f"Memuat model {model_name} pada peranti: {device}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
    model.to(device)
    model.eval()

    return model, tokenizer


def extract_embeddings(
    sequence: str,
    model: Any,
    tokenizer: Any,
    device: Optional[Any] = None,
    max_length: int = 512
) -> Any:
    """
    Mengekstraksi representasi 768-dimensi dari sekuens nukleotida.
    
    Langkah:
    1. Tokenisasi sekuens via AutoTokenizer BPE bawaan DNABERT-2.
    2. Forward pass ke encoder DNABERT-2.
    3. Mengambil hidden state terakhir (last_hidden_state), bentuk: (batch_size, seq_len, 768).
    4. Mean pooling bertopeng (masking) token padding untuk menghasilkan vektor tunggal 768-dimensi.
    
    Return:
    - Tensor PyTorch 1-D berukuran [768] (atau numpy array jika dikonversi).
    """
    try:
        import torch
    except ImportError:
        raise ImportError("PyTorch belum terpasang.")

    if device is None:
        device = next(model.parameters()).device

    # Tokenisasi
    inputs = tokenizer(
        sequence,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_length
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        # last_hidden_state: [batch_size, seq_len, 768]
        if hasattr(outputs, "last_hidden_state"):
            hidden_states = outputs.last_hidden_state
        else:
            hidden_states = outputs[0]

        # Mean pooling dengan attention mask
        attention_mask = inputs["attention_mask"].unsqueeze(-1)  # [batch_size, seq_len, 1]
        masked_hidden = hidden_states * attention_mask
        sum_hidden = masked_hidden.sum(dim=1)  # [batch_size, 768]
        sum_mask = attention_mask.sum(dim=1).clamp(min=1e-9)
        embedding = (sum_hidden / sum_mask).squeeze(0)  # [768]

    return embedding
