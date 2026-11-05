from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GenomicLocation(BaseModel):
    genomic_accession_version: Optional[str] = Field(None, description="Aksesi kromosom/kontig (mis. NC_089045.1)")
    sequence_name: Optional[str] = Field(None, description="Nomor kromosom (mis. 1, 11)")
    begin: Optional[int] = Field(None, description="Posisi awal genomik (1-based)")
    end: Optional[int] = Field(None, description="Posisi akhir genomik")
    orientation: Optional[str] = Field(None, description="Arah untai (plus/minus)")


class GeneAnnotation(BaseModel):
    assembly_accession: Optional[str] = None
    assembly_name: Optional[str] = None
    annotation_name: Optional[str] = None
    genomic_locations: List[GenomicLocation] = []


class RiceGeneSummary(BaseModel):
    gene_id: int = Field(..., description="NCBI Gene ID numerik")
    symbol: str = Field(..., description="Simbol gen (mis. LOC4324418, OsDREB2A)")
    common_symbol: Optional[str] = Field(None, description="Simbol gen populer dalam literatur (mis. OsDREB2A)")
    description: Optional[str] = Field(None, description="Nama lengkap dan deskripsi fungsi gen")
    tax_id: int = Field(..., description="NCBI Taxon ID")
    taxname: Optional[str] = Field(None, description="Nama takson (mis. Oryza sativa Japonica Group)")
    type: Optional[str] = Field(None, description="Tipe gen (protein-coding, tRNA, etc.)")
    chromosomes: List[str] = []
    synonyms: List[str] = []
    locus_tag: Optional[str] = None
    transcript_count: Optional[int] = 0
    protein_count: Optional[int] = 0
    primary_location: Optional[GenomicLocation] = None
    trait_category: Optional[str] = Field(None, description="Kategori agronomi / rekayasa genetika jika terdaftar")


class GeneDetailResponse(BaseModel):
    gene: RiceGeneSummary
    raw_report: Optional[Dict[str, Any]] = Field(None, description="Data mentah langsung dari NCBI Datasets")


class GeneSearchResponse(BaseModel):
    total_found: int
    genes: List[RiceGeneSummary]

