from typing import List, Optional
from pydantic import BaseModel, Field


class AssemblyStats(BaseModel):
    total_sequence_length: Optional[int] = Field(None, description="Total panjang basa pasangan (bp)")
    number_of_chromosomes: Optional[int] = Field(None, description="Jumlah kromosom")
    contig_n50: Optional[int] = Field(None, description="Contig N50")
    scaffold_n50: Optional[int] = Field(None, description="Scaffold N50")
    total_number_of_chromosomes: Optional[int] = None
    gc_percent: Optional[float] = Field(None, description="Persentase kandungan GC (%)")


class AssemblyOrganism(BaseModel):
    tax_id: Optional[int] = Field(None, description="NCBI Taxonomy ID")
    organism_name: Optional[str] = Field(None, description="Nama taksonomik organisme")
    infraspecific_names: Optional[dict] = Field(None, description="Nama varietas / kultivar / subspesies")


class AssemblyInfo(BaseModel):
    assembly_accession: str = Field(..., description="Nomor aksesi genom perakitan (mis. GCF_001433935.1)")
    assembly_name: Optional[str] = Field(None, description="Nama perakitan (mis. IRGSP-1.0)")
    assembly_level: Optional[str] = Field(None, description="Tingkat perakitan (Chromosome, Complete Genome)")
    assembly_type: Optional[str] = None
    release_date: Optional[str] = None
    submitter: Optional[str] = None


class RiceGenomeSummary(BaseModel):
    accession: str
    assembly_name: Optional[str]
    assembly_level: Optional[str]
    organism_name: Optional[str]
    tax_id: Optional[int]
    total_length: Optional[int]
    contig_n50: Optional[int]
    chromosomes_count: Optional[int]
    is_reference: bool = False


class RiceGenomeListResponse(BaseModel):
    total_count: int
    reports: List[RiceGenomeSummary]
    next_page_token: Optional[str] = None

