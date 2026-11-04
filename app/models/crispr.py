from typing import List, Optional
from pydantic import BaseModel, Field


class CRISPRTargetSite(BaseModel):
    id: int
    protospacer_sequence: str = Field(..., description="Sekuens gRNA 20 nt (5' ke 3')")
    pam: str = Field(..., description="Motif PAM (mis. NGG untuk SpCas9, TTTV untuk Cas12a)")
    strand: str = Field(..., description="Untai DNA (+ atau -)")
    start_position: int = Field(..., description="Posisi awal 1-based pada sekuens input")
    end_position: int = Field(..., description="Posisi akhir 1-based pada sekuens input")
    gc_content: float = Field(..., description="Persentase GC protospacer (%)")
    has_poly_t_termination: bool = Field(
        ...,
        description="True jika mengandung motif TTTT (berisiko terminasi dini transkripsi promotor U6/U3 padi)"
    )
    full_target_with_pam: str = Field(..., description="Sekuens gabungan protospacer + PAM")
    quality_assessment: str = Field(..., description="Penilaian kesesuaian: Optimal, Diterima, atau Waspada")


class CRISPRAnalysisRequest(BaseModel):
    sequence: str = Field(..., min_length=23, max_length=100_000, description="Sekuens DNA cetakan (minimal 23 nt, maksimal 100.000 nt)")
    nuclease: str = Field("SpCas9", description="Pilihan nuklease: 'SpCas9' (PAM: NGG) atau 'Cas12a' (PAM: TTTV)")
    min_gc: float = Field(35.0, description="Kandungan GC minimum (%)")
    max_gc: float = Field(70.0, description="Kandungan GC maksimum (%)")


class CRISPRAnalysisResponse(BaseModel):
    nuclease: str
    pam_motif: str
    total_sites_found: int
    optimal_sites_count: int
    sites: List[CRISPRTargetSite]
    sequence_length: int
    overall_gc_percent: float


class SequenceData(BaseModel):
    gene_id: int
    symbol: Optional[str] = None
    header: str
    sequence: str
    length: int
    type: str = Field(..., description="genomic, cds, atau protein")
    gc_percent: Optional[float] = None


class GeneSequencesResponse(BaseModel):
    gene_id: int
    symbol: Optional[str] = None
    genomic_sequence: Optional[SequenceData] = None
    cds_sequence: Optional[SequenceData] = None
    protein_sequence: Optional[SequenceData] = None

