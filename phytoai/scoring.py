"""
phytoai/scoring.py
Mutagenesis saturasi in silico, evaluasi konsekuensi translasi,
dan perhitungan pergeseran pseudo-log-likelihood (PLL) serta pseudo-perplexity via DNABERT-2.
Sesuai Proposal Butir 4 dan Deviasi Ilmiah D2.
"""

import math
from typing import Dict, Any, Tuple, Optional, List
from scripts.preprocess import CODON_TABLE, clean_sequence


def evaluate_mutation_consequence(
    cds_sequence: str,
    position_nt_1based: int,
    alt_nt: str
) -> Dict[str, Any]:
    """
    Mengevaluasi efek biologis substitusi nukleotida pada CDS terhadap translasi protein.

    Parameter:
    - cds_sequence: Urutan CDS wildtype lengkap (panjang kelipatan 3)
    - position_nt_1based: Posisi nukleotida 1-based (1, 2, ..., len(cds))
    - alt_nt: Basa nukleotida pengganti (A, C, G, atau T)

    Return:
    - Dict berisi: ref_nt, alt_nt, position_nt, codon_index, wt_codon, mut_codon,
      wt_aa, mut_aa, mutation_type ('synonymous', 'missense', atau 'nonsense').
    """
    cds = clean_sequence(cds_sequence)
    seq_len = len(cds)

    if position_nt_1based < 1 or position_nt_1based > seq_len:
        raise ValueError(
            f"Posisi nukleotida {position_nt_1based} di luar rentang CDS (1 - {seq_len})."
        )

    idx = position_nt_1based - 1
    ref_nt = cds[idx]
    alt_nt = alt_nt.upper().strip()

    if alt_nt not in ("A", "C", "G", "T"):
        raise ValueError(f"Basa nukleotida pengganti tidak sah: {alt_nt}")

    codon_idx = idx // 3
    nt_offset = idx % 3
    codon_start = codon_idx * 3
    codon_end = codon_start + 3

    wt_codon = cds[codon_start:codon_end]
    if len(wt_codon) < 3:
        raise ValueError(f"Kodon wildtype pada indeks {codon_idx} tidak lengkap: {wt_codon}")

    mut_codon_list = list(wt_codon)
    mut_codon_list[nt_offset] = alt_nt
    mut_codon = "".join(mut_codon_list)

    wt_aa = CODON_TABLE.get(wt_codon, "X")
    mut_aa = CODON_TABLE.get(mut_codon, "X")

    if wt_aa == mut_aa:
        mutation_type = "synonymous"
    elif mut_aa == "*":
        mutation_type = "nonsense"
    else:
        mutation_type = "missense"

    return {
        "position_nt": position_nt_1based,
        "ref_nt": ref_nt,
        "alt_nt": alt_nt,
        "codon_index_1based": codon_idx + 1,
        "nt_offset_in_codon": nt_offset + 1,
        "wt_codon": wt_codon,
        "mut_codon": mut_codon,
        "wt_aa": wt_aa,
        "mut_aa": mut_aa,
        "mutation_type": mutation_type,
    }


def compute_pseudo_log_likelihood(
    sequence: str,
    target_pos_0based: int,
    model: Any,
    tokenizer: Any,
    device: Optional[Any] = None,
    window_nt: int = 30
) -> Tuple[float, float]:
    """
    Menghitung Pseudo-Log-Likelihood (PLL) dan Pseudo-Perplexity pada jendela token di sekitar target_pos.
    
    Catatan Ilmiah Deviasi D2:
    DNABERT-2 adalah model bahasa bertopeng (Masked Language Model / MLM).
    Perplexity kausal autoregresif standar secara matematis tidak valid pada MLM dua-arah.
    Pendekatan saintifik baku (Salazar et al., ACL 2020) adalah masking token lokal dan
    menghitung log-probabilitas token target yang ditutupi:
    PLL = log P(token_target | context)
    Pseudo-Perplexity = exp(-PLL)
    """
    try:
        import torch
        import torch.nn.functional as F
    except ImportError:
        raise ImportError(
            "PyTorch belum terpasang. Pasang dengan: pip install -r requirements-ml.txt"
        )

    if device is None:
        device = next(model.parameters()).device

    # Ekstraksi subsekuens lokal di sekitar mutasi untuk efisiensi
    start_nt = max(0, target_pos_0based - window_nt)
    end_nt = min(len(sequence), target_pos_0based + window_nt + 1)
    subseq = sequence[start_nt:end_nt]
    rel_pos = target_pos_0based - start_nt

    # Tokenisasi
    encoding = tokenizer(subseq, return_tensors="pt", return_offsets_mapping=True)
    input_ids = encoding["input_ids"].to(device)
    offsets = encoding["offset_mapping"][0]

    # Cari token yang mencakup rel_pos
    mask_token_idx = None
    for idx_tok, (start, end) in enumerate(offsets):
        if start <= rel_pos < end:
            mask_token_idx = idx_tok
            break

    if mask_token_idx is None:
        # Fallback jika offset mapping tidak cocok: gunakan token tengah
        mask_token_idx = input_ids.shape[1] // 2

    original_token_id = input_ids[0, mask_token_idx].item()

    # Buat masked input
    masked_input_ids = input_ids.clone()
    masked_input_ids[0, mask_token_idx] = tokenizer.mask_token_id

    with torch.no_grad():
        outputs = model(masked_input_ids)
        logits = outputs.logits if hasattr(outputs, "logits") else outputs[0]
        # Logits pada posisi mask: [vocab_size]
        mask_logits = logits[0, mask_token_idx]
        log_probs = F.log_softmax(mask_logits, dim=-1)

        token_log_prob = log_probs[original_token_id].item()

    # Pseudo-perplexity untuk token ini: exp(-log_prob)
    pseudo_ppl = math.exp(-token_log_prob) if token_log_prob < 50 else float("inf")

    return token_log_prob, pseudo_ppl


def compute_delta_pll(
    wt_sequence: str,
    position_nt_1based: int,
    alt_nt: str,
    model: Any,
    tokenizer: Any,
    device: Optional[Any] = None,
    window_nt: int = 30
) -> Dict[str, Any]:
    """
    Menghitung delta PLL antara varian mutan dan wildtype:
    delta_pll = PLL(mutant) - PLL(wildtype)
    """
    pos_0based = position_nt_1based - 1
    ref_nt = wt_sequence[pos_0based]

    mut_seq_list = list(wt_sequence)
    mut_seq_list[pos_0based] = alt_nt
    mut_sequence = "".join(mut_seq_list)

    wt_pll, wt_ppl = compute_pseudo_log_likelihood(
        wt_sequence, pos_0based, model, tokenizer, device, window_nt
    )
    mut_pll, mut_ppl = compute_pseudo_log_likelihood(
        mut_sequence, pos_0based, model, tokenizer, device, window_nt
    )

    delta_pll = mut_pll - wt_pll

    return {
        "wt_pll": round(wt_pll, 4),
        "mut_pll": round(mut_pll, 4),
        "delta_pll": round(delta_pll, 4),
        "wt_pseudo_perplexity": round(wt_ppl, 2),
        "mut_pseudo_perplexity": round(mut_ppl, 2),
    }
