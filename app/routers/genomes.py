from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.models.genome import RiceGenomeListResponse, RiceGenomeSummary
from app.services.ncbi_client import ncbi_client
from app.core.config import settings

router = APIRouter(prefix="/genomes", tags=["Genom Perakitan Padi (Genomes & Assemblies)"])


@router.get("", response_model=RiceGenomeListResponse, summary="Daftar Genom Perakitan Padi (Oryza sativa)")
async def list_rice_genomes(
    taxon: Optional[str] = Query(
        settings.DEFAULT_RICE_TAXON,
        description="NCBI Taxon ID. Default 39947 (Japonica). Gunakan 39946 untuk Indica atau 4530 untuk Oryza sativa umum."
    ),
    reference_only: bool = Query(
        False,
        description="Jika true, hanya tampilkan perakitan referensi resmi NCBI (Reference/Representative Genome)."
    ),
    page_size: int = Query(20, ge=1, le=100, description="Jumlah perakitan per halaman"),
    page_token: Optional[str] = Query(None, description="Token paginasi NCBI berikutnya")
):
    """
    Mengambil daftar perakitan genom padi dari NCBI Datasets v2 API.
    Memungkinkan peneliti menelusuri genom referensi Nipponbare (IRGSP-1.0 / AGIS1.0)
    maupun kultivar Indica untuk pemetaan variasi genetik dan desain primer/gRNA.
    """
    raw_data = await ncbi_client.get_genome_reports_by_taxon(
        taxon=taxon,
        reference_only=reference_only,
        page_size=page_size,
        page_token=page_token
    )

    reports = raw_data.get("reports", [])
    summaries = []
    for r in reports:
        ass_info = r.get("assembly_info", {})
        org = r.get("organism", {})
        stats = r.get("assembly_stats", {})
        
        acc = r.get("accession") or ass_info.get("assembly_accession")
        summaries.append(RiceGenomeSummary(
            accession=acc,
            assembly_name=ass_info.get("assembly_name"),
            assembly_level=ass_info.get("assembly_level"),
            organism_name=org.get("organism_name"),
            tax_id=org.get("tax_id"),
            total_length=stats.get("total_sequence_length"),
            contig_n50=stats.get("contig_n50"),
            chromosomes_count=stats.get("number_of_chromosomes"),
            is_reference=ass_info.get("refseq_category") in ["reference genome", "representative genome"]
        ))

    return RiceGenomeListResponse(
        total_count=len(summaries),
        reports=summaries,
        next_page_token=raw_data.get("next_page_token")
    )


@router.get("/reference/irgsp10", summary="Ambil Data Genom Emas IRGSP-1.0 (Nipponbare)")
async def get_irgsp10_reference():
    """
    Shortcut langsung ke genom acuan standar internasional padi: IRGSP-1.0 (GCF_001433935.1),
    yang paling luas digunakan dalam anotasi gen RAP-DB/MSU dan rekayasa genetika CRISPR.
    """
    return await ncbi_client.get_genome_by_accession(settings.DEFAULT_REFERENCE_ASSEMBLY)


@router.get("/{accession}", summary="Detail Perakitan Genom berdasarkan Nomor Aksesi (mis. GCF_001433935.1)")
async def get_genome_detail(accession: str):
    """
    Mengambil laporan lengkap perakitan genom tertentu dari NCBI Datasets v2,
    termasuk statistik sekuens, informasi submitter, dan tingkat perakitan kromosom.
    """
    return await ncbi_client.get_genome_by_accession(accession)

