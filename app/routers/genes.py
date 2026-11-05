from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Path
from app.models.gene import RiceGeneSummary, GeneSearchResponse, GeneDetailResponse, GenomicLocation
from app.services.ncbi_client import ncbi_client
from app.core.config import settings
from app.data.rice_targets import TARGETS_BY_GENE_ID, TARGETS_BY_SYMBOL

router = APIRouter(prefix="/genes", tags=["Gen Padi (Rice Genes)"])


def format_gene_report(raw_report: dict) -> RiceGeneSummary:
    gene_data = raw_report.get("gene", {})
    gene_id = int(gene_data.get("gene_id", 0))
    symbol = gene_data.get("symbol", "")
    
    # Check if this gene is in our curated genetic engineering catalog
    target_info = TARGETS_BY_GENE_ID.get(gene_id) or TARGETS_BY_SYMBOL.get(symbol.lower())
    common_symbol = target_info.gene_symbol if target_info else symbol
    trait_category = target_info.category if target_info else None

    # Parse primary location
    primary_loc = None
    annotations = gene_data.get("annotations", [])
    if annotations:
        locs = annotations[0].get("genomic_locations", [])
        if locs:
            first_loc = locs[0]
            rng = first_loc.get("genomic_range", {})
            primary_loc = GenomicLocation(
                genomic_accession_version=first_loc.get("genomic_accession_version"),
                sequence_name=first_loc.get("sequence_name"),
                begin=int(rng.get("begin")) if rng.get("begin") else None,
                end=int(rng.get("end")) if rng.get("end") else None,
                orientation=rng.get("orientation")
            )

    return RiceGeneSummary(
        gene_id=gene_id,
        symbol=symbol,
        common_symbol=common_symbol,
        description=gene_data.get("description"),
        tax_id=int(gene_data.get("tax_id", 0)),
        taxname=gene_data.get("taxname"),
        type=gene_data.get("type"),
        chromosomes=gene_data.get("chromosomes", []),
        synonyms=gene_data.get("synonyms", []),
        locus_tag=gene_data.get("locus_tag"),
        transcript_count=gene_data.get("transcript_count", 0),
        protein_count=gene_data.get("protein_count", 0),
        primary_location=primary_loc,
        trait_category=trait_category
    )


@router.get("/search", response_model=GeneSearchResponse, summary="Cari Gen Padi berdasarkan Simbol atau Kata Kunci")
async def search_rice_genes(
    query: str = Query(..., description="Simbol gen regulon kekeringan (mis. OsDREB2A, OsLEA3, OsERD1, OsRAB16A, OsNAC6) atau kata kunci"),
    taxon: Optional[str] = Query(
        None,
        description="NCBI Taxon ID. Kosongkan untuk pencarian otomatis (Japonica 39947 / Oryza sativa 4530 / Indica 39946)."
    )
):
    """
    Mencari gen padi di NCBI Datasets v2.
    Otomatis memeriksa takson Japonica (Nipponbare) dan fallback ke taxa terkait lainnya
    sehingga simbol gen regulon kekeringan (seperti OsDREB2A atau OsLEA3) langsung ditemukan.
    """
    raw_reports = await ncbi_client.get_genes_by_symbol(symbol=query, taxon=taxon)
    results = [format_gene_report(r) for r in raw_reports if "gene" in r]
    return GeneSearchResponse(total_found=len(results), genes=results)


@router.get("/symbol/{symbol}", response_model=GeneDetailResponse, summary="Detail Gen berdasarkan Simbol (mis. OsDREB2A, OsLEA3)")
async def get_gene_by_symbol(
    symbol: str = Path(..., description="Simbol gen (mis. OsDREB2A, OsLEA3, OsERD1, OsRAB16A, OsNAC6)"),
    taxon: Optional[str] = Query(None, description="Takson spesifik (opsional)")
):
    """
    Mengambil data gen spesifik berdasarkan simbol gen resminya.
    """
    raw_reports = await ncbi_client.get_genes_by_symbol(symbol=symbol, taxon=taxon)
    if not raw_reports:
        raise HTTPException(
            status_code=404,
            detail=f"Gen padi dengan simbol '{symbol}' tidak ditemukan pada basis data NCBI."
        )
    rep = raw_reports[0]
    return GeneDetailResponse(
        gene=format_gene_report(rep),
        raw_report=rep
    )


@router.get("/id/{gene_id}", response_model=GeneDetailResponse, summary="Detail Gen Lengkap berdasarkan NCBI Gene ID")
async def get_gene_by_id(
    gene_id: int = Path(..., description="ID Gen numerik NCBI (mis. 4324418 untuk OsDREB2A, 4337666 untuk OsLEA3-1)")
):
    """
    Mengambil laporan komprehensif gen padi dari NCBI Datasets v2 berdasarkan NCBI Gene ID,
    termasuk koordinat genomik, ekson/intron, nomor kromosom, dan varian transkrip.
    """
    raw_rep = await ncbi_client.get_gene_by_id(gene_id=gene_id)
    return GeneDetailResponse(
        gene=format_gene_report(raw_rep),
        raw_report=raw_rep
    )


@router.get("", response_model=GeneSearchResponse, summary="Daftar Gen Padi (Paginasi)")
async def list_rice_genes(
    taxon: Optional[str] = Query(settings.DEFAULT_RICE_TAXON, description="Taxon ID (default 39947 Japonica)"),
    page_size: int = Query(20, ge=1, le=100, description="Jumlah data"),
    page_token: Optional[str] = Query(None, description="Token halaman berikutnya")
):
    """
    Menelusuri daftar gen padi teranotasi dari NCBI Datasets.
    """
    raw_data = await ncbi_client.get_genes_by_taxon(taxon=taxon, page_size=page_size, page_token=page_token)
    reports = raw_data.get("reports", [])
    results = [format_gene_report(r) for r in reports if "gene" in r]
    return GeneSearchResponse(total_found=len(results), genes=results)

