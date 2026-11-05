from typing import List, Optional
from pydantic import BaseModel, Field


class GeneticEngineeringTarget(BaseModel):
    id: str = Field(..., description="ID unik target (mis. os-dreb2a)")
    gene_symbol: str = Field(..., description="Simbol gen di literatur (mis. OsDREB2A)")
    ncbi_gene_id: int = Field(..., description="NCBI Gene ID untuk Oryza sativa Japonica")
    ncbi_locus_tag: Optional[str] = Field(None, description="Locus tag RAP-DB atau MSU (mis. LOC4324418)")
    category: str = Field(
        ...,
        description="Kategori agronomi ketahanan abiotik kekeringan (Toleransi Kekeringan, Proteksi Osmotik, Regulasi Stomata, Arsitektur Perakaran)"
    )
    trait_description: str = Field(..., description="Deskripsi fenotip dan manfaat rekayasa genetika")
    target_strategy: str = Field(..., description="Strategi (mis. CRISPR Promoter KO, Base Editing, Gene Knockout)")
    pathway: Optional[str] = Field(None, description="Jalur metabolik / mekanisme molekuler")
    chromosome: str = Field(..., description="Kromosom padi (1-12)")
    key_publications: List[str] = Field(default_factory=list, description="Sitasi literatur kunci (DOI / PubMed)")


class TargetCatalogResponse(BaseModel):
    total: int
    categories: List[str]
    targets: List[GeneticEngineeringTarget]

