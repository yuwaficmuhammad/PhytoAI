from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProteinDomain(BaseModel):
    name: str = Field(..., description="Nama domain struktural/fungsional")
    start: int = Field(..., description="Posisi asam amino awal (1-based)")
    end: int = Field(..., description="Posisi asam amino akhir")
    description: str = Field(..., description="Peran biologis domain")
    key_motifs: List[str] = Field(default_factory=list, description="Motif asam amino khas")
    sequence_slice: Optional[str] = None


class MutationAnalysisRequest(BaseModel):
    variant: str = Field(..., description="Notasi mutasi (mis. 'P168L', 'V79I', 'V79A', 'E166K')")
    cultivar: str = Field("Nipponbare", description="Varietas/kultivar acuan (mis. Rojolele, Gogo Jatiluhur, Inpari 32, Padi Gogo NTT)")
    target_region: Optional[str] = Field(
        None,
        description="Wilayah kekeringan spesifik di Indonesia (mis. 'demak-pati', 'ntt-semiarid', 'ntb-gora', 'gunungkidul-karst')"
    )


class MutationPredictionResult(BaseModel):
    variant: str
    position: int
    wildtype_aa: str
    mutant_aa: str
    affected_domain: str
    transformer_score: float = Field(..., description="Skor kecukupan evolusioner Transformer pLM (ΔLLR). Positif = stabil/toleran, Negatif = merusak")
    predicted_functional_effect: str = Field(..., description="Gain-of-Function, Loss-of-Function, Neutral, atau Constitutive-Activation")
    drought_tolerance_index: str = Field(..., description="Prediksi fenotipe toleransi kekeringan (Tinggi, Sangat Tinggi, Normal, Rentan)")
    biochemical_rationale: str
    crispr_base_editing_candidate: Optional[str] = None
    target_codon_edit: Optional[str] = None
    regional_adaptation_notes: Optional[str] = None


class DMSPositionScore(BaseModel):
    position: int
    wildtype_aa: str
    domain: str
    scores: Dict[str, float] = Field(..., description="Skor Transformer untuk setiap 20 asam amino substitusi")
    best_mutation: str
    best_score: float


class DMSScanResponse(BaseModel):
    gene_symbol: str = "OsDREB2A"
    ncbi_gene_id: int = 4324418
    region_scanned: str
    start_pos: int
    end_pos: int
    positions: List[DMSPositionScore]


class LocalRiceCultivarProfile(BaseModel):
    cultivar_name: str
    origin: str
    rice_type: str = Field(..., description="Padi Gogo (Lahan Kering), Padi Sawah (Lowland), atau Landrace")
    drought_phenotype: str
    dreb2a_haplotype_snps: List[str]
    relative_expression_under_drought: str
    notes: str


class IndonesianDroughtRegion(BaseModel):
    region_id: str = Field(..., description="ID unik wilayah (mis. demak-pati, ntt-semiarid)")
    region_name: str = Field(..., description="Nama wilayah / klaster kekeringan di Indonesia")
    provinces: List[str]
    latitude: Optional[float] = Field(None, description="Garis lintang koordinat pusat wilayah")
    longitude: Optional[float] = Field(None, description="Garis bujur koordinat pusat wilayah")
    inarisk_hazard_score: Optional[float] = Field(None, description="Skor indeks bahaya kekeringan InaRISK 0.0 - 1.0")
    agroecosystem_type: str = Field(..., description="Tipe agroekosistem lahan")
    annual_rainfall_mm: str
    dry_season_duration: str
    drought_characteristics: str = Field(..., description="Karakteristik cekaman kekeringan lokal")
    predominant_local_cultivars: List[str]
    dreb2a_target_strategy: str = Field(..., description="Strategi rekayasa genetika DREB2A yang disarankan")
    recommended_mutations: List[str]


class CoordinateAssessmentRequest(BaseModel):
    latitude: float = Field(..., description="Garis lintang (Latitude), contoh: -6.8944")
    longitude: float = Field(..., description="Garis bujur (Longitude), contoh: 110.6386")


class CoordinateAssessmentResponse(BaseModel):
    latitude: float
    longitude: float
    nearest_region_id: str
    nearest_region_name: str
    province: str
    island_group: str
    distance_km: float
    inarisk_hazard_level: str = Field(..., description="Klasifikasi bahaya kekeringan BNPB (Rendah, Sedang, Tinggi, Ekstrem)")
    inarisk_hazard_score: float = Field(..., description="Skor indeks bahaya kekeringan InaRISK 0.0 - 1.0")
    agroecosystem_type: str
    annual_rainfall_mm: str
    dry_season_duration: str
    drought_impact_profile: str
    recommended_cultivars: List[str]
    recommended_mutations: List[str]
    primary_mutation: str
    dreb2a_strategy: str
    inarisk_layer_url: str
