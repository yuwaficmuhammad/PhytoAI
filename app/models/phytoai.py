"""
app/models/phytoai.py
Skema data Pydantic untuk mutagenesis saturasi in silico DNABERT-2
dan prediksi varian gen DREB2A pada padi lokal (Oryza sativa).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NucleotideVariant(BaseModel):
    landrace: str = Field(..., description="Nama landrace padi lokal")
    position_nt: int = Field(..., description="Posisi nukleotida pada sekuens acuan (1-based)")
    ref: str = Field(..., description="Nukleotida referensi (WT)")
    alt: str = Field(..., description="Nukleotida mutan (substitusi)")
    delta_pll: Optional[float] = Field(None, description="Pergeseran pseudo-log-likelihood: PLL(mut) - PLL(wt)")
    pseudo_perplexity: Optional[float] = Field(None, description="Pseudo-perplexity sekuens varian")
    mutation_type: Optional[str] = Field(None, description="Konsekuensi translasi: synonymous, missense, atau nonsense (stop)")
    wt_codon: Optional[str] = None
    mut_codon: Optional[str] = None
    wt_aa: Optional[str] = None
    mut_aa: Optional[str] = None
    model_name: str = "zhihan1996/DNABERT-2-117M"


class VariantPredictionResult(BaseModel):
    variant: NucleotideVariant
    predicted_class: str = Field(
        ...,
        description="Kelas varian: Benign, Deleterious, atau 'kandidat zero-shot (bukan Beneficial terverifikasi)'"
    )
    class_probabilities: Optional[Dict[str, float]] = None
    predicted_lri: Optional[float] = Field(
        None,
        description="Prediksi Leaf Rolling Index (0.0-1.0). Null pada mode zero-shot sebelum model dilatih data riil."
    )
    is_zero_shot: bool = True
    method_note: str


class VariantListResponse(BaseModel):
    total: int
    landrace: Optional[str] = None
    variants: List[NucleotideVariant]
    method_note: str


class MethodDescriptionResponse(BaseModel):
    title: str
    target_gene: str = "DREB2A (Oryza sativa)"
    model_name: str = "zhihan1996/DNABERT-2-117M"
    embedding_dimension: int = 768
    task_scope: List[str]
    limitations: List[str]
    method_note: str
