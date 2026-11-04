import re
from typing import List, Tuple, Optional
from app.models.crispr import CRISPRTargetSite, CRISPRAnalysisResponse


COMPLEMENT_MAP = str.maketrans("ACGTacgtNn", "TGCAtgcaNn")

# Batas maksimum panjang sekuens untuk mencegah CPU exhaustion (DoS)
MAX_SEQUENCE_LENGTH = 100_000  # 100 kb


def reverse_complement(seq: str) -> str:
    return seq.translate(COMPLEMENT_MAP)[::-1].upper()


def calculate_gc(seq: str) -> float:
    seq_upper = seq.upper()
    g_count = seq_upper.count("G")
    c_count = seq_upper.count("C")
    total = len(seq_upper)
    return round(((g_count + c_count) / total) * 100, 2) if total > 0 else 0.0


def _assess_guide_quality(gc: float, has_poly_t: bool, min_gc: float, max_gc: float) -> str:
    """Menilai kualitas guide RNA berdasarkan kandungan GC dan motif terminasi Pol III.
    
    Fungsi helper DRY untuk menghindari duplikasi logika di 4 blok pencarian situs gRNA.
    """
    if has_poly_t:
        return "Waspada (Mengandung motif terminator Pol III: TTTT)"
    if gc < min_gc or gc > max_gc:
        return f"Waspada (GC {gc}% di luar rentang {min_gc}-{max_gc}%)"
    if 40.0 <= gc <= 60.0:
        return "Optimal"
    return "Diterima"


def analyze_crispr_targets(
    sequence: str,
    nuclease: str = "SpCas9",
    min_gc: float = 35.0,
    max_gc: float = 70.0,
    pam_type: Optional[str] = None
) -> CRISPRAnalysisResponse:
    effective_nuclease = pam_type if pam_type is not None else nuclease
    clean_seq = re.sub(r"\s+", "", sequence).upper()
    seq_len = len(clean_seq)

    # Guard: tolak sekuens terlalu panjang untuk mencegah CPU exhaustion
    if seq_len > MAX_SEQUENCE_LENGTH:
        raise ValueError(
            f"Sekuens terlalu panjang ({seq_len:,} nt). Batas maksimum adalah {MAX_SEQUENCE_LENGTH:,} nt."
        )

    overall_gc = calculate_gc(clean_seq)
    
    sites: List[CRISPRTargetSite] = []
    site_id = 1
    
    nuclease_lower = effective_nuclease.lower()
    
    if "cas12" in nuclease_lower or "cpf1" in nuclease_lower:
        # Cas12a (Cpf1): PAM is 5'-TTTV-3' (V = A, C, G) followed by 20-24 nt protospacer (default 23 nt)
        pam_motif = "TTTV (5')"
        protospacer_len = 23
        
        # Forward strand search
        for i in range(len(clean_seq) - 4 - protospacer_len + 1):
            pam = clean_seq[i:i+4]
            if pam[:3] == "TTT" and pam[3] in "ACG":
                proto = clean_seq[i+4:i+4+protospacer_len]
                gc = calculate_gc(proto)
                has_poly_t = "TTTT" in proto
                quality = _assess_guide_quality(gc, has_poly_t, min_gc, max_gc)
                    
                sites.append(CRISPRTargetSite(
                    id=site_id,
                    protospacer_sequence=proto,
                    pam=pam,
                    strand="+",
                    start_position=i + 1,
                    end_position=i + 4 + protospacer_len,
                    gc_content=gc,
                    has_poly_t_termination=has_poly_t,
                    full_target_with_pam=f"{pam}{proto}",
                    quality_assessment=quality
                ))
                site_id += 1
                
        # Reverse complement strand
        rc_seq = reverse_complement(clean_seq)
        for i in range(len(rc_seq) - 4 - protospacer_len + 1):
            pam = rc_seq[i:i+4]
            if pam[:3] == "TTT" and pam[3] in "ACG":
                proto = rc_seq[i+4:i+4+protospacer_len]
                gc = calculate_gc(proto)
                has_poly_t = "TTTT" in proto
                
                orig_start = seq_len - (i + 4 + protospacer_len) + 1
                orig_end = seq_len - i
                quality = _assess_guide_quality(gc, has_poly_t, min_gc, max_gc)
                    
                sites.append(CRISPRTargetSite(
                    id=site_id,
                    protospacer_sequence=proto,
                    pam=pam,
                    strand="-",
                    start_position=orig_start,
                    end_position=orig_end,
                    gc_content=gc,
                    has_poly_t_termination=has_poly_t,
                    full_target_with_pam=f"{pam}{proto}",
                    quality_assessment=quality
                ))
                site_id += 1
    else:
        # SpCas9: 20 nt protospacer followed by 3' PAM: NGG
        pam_motif = "NGG (3')"
        protospacer_len = 20
        
        # Forward strand: [20 nt][N][G][G]
        for i in range(len(clean_seq) - protospacer_len - 3 + 1):
            pam = clean_seq[i+protospacer_len : i+protospacer_len+3]
            if pam[1:] == "GG":
                proto = clean_seq[i:i+protospacer_len]
                gc = calculate_gc(proto)
                has_poly_t = "TTTT" in proto
                quality = _assess_guide_quality(gc, has_poly_t, min_gc, max_gc)
                    
                sites.append(CRISPRTargetSite(
                    id=site_id,
                    protospacer_sequence=proto,
                    pam=pam,
                    strand="+",
                    start_position=i + 1,
                    end_position=i + protospacer_len + 3,
                    gc_content=gc,
                    has_poly_t_termination=has_poly_t,
                    full_target_with_pam=f"{proto}{pam}",
                    quality_assessment=quality
                ))
                site_id += 1
                
        # Reverse complement strand
        rc_seq = reverse_complement(clean_seq)
        for i in range(len(rc_seq) - protospacer_len - 3 + 1):
            pam = rc_seq[i+protospacer_len : i+protospacer_len+3]
            if pam[1:] == "GG":
                proto = rc_seq[i:i+protospacer_len]
                gc = calculate_gc(proto)
                has_poly_t = "TTTT" in proto
                
                orig_start = seq_len - (i + protospacer_len + 3) + 1
                orig_end = seq_len - i
                quality = _assess_guide_quality(gc, has_poly_t, min_gc, max_gc)
                    
                sites.append(CRISPRTargetSite(
                    id=site_id,
                    protospacer_sequence=proto,
                    pam=pam,
                    strand="-",
                    start_position=orig_start,
                    end_position=orig_end,
                    gc_content=gc,
                    has_poly_t_termination=has_poly_t,
                    full_target_with_pam=f"{proto}{pam}",
                    quality_assessment=quality
                ))
                site_id += 1

    optimal_count = sum(1 for s in sites if s.quality_assessment == "Optimal")
    
    return CRISPRAnalysisResponse(
        nuclease="SpCas9" if "cas9" in nuclease_lower else "Cas12a",
        pam_motif=pam_motif,
        total_sites_found=len(sites),
        optimal_sites_count=optimal_count,
        sites=sites,
        sequence_length=seq_len,
        overall_gc_percent=overall_gc
    )
