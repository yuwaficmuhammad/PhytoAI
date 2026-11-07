import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.core.config import settings
from app.routers import sequences, phytoai, database
from app.services.ncbi_client import ncbi_client
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manajemen siklus hidup aplikasi: connection pooling HTTPX untuk client NCBI."""
    shared_client = httpx.AsyncClient(
        timeout=settings.HTTP_TIMEOUT_SECONDS,
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
    )
    ncbi_client.set_shared_client(shared_client)
    yield
    await shared_client.aclose()
    ncbi_client.clear_shared_client()


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow_credentials=False diperlukan saat allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate Limiting — sliding window in-memory per IP
app.add_middleware(RateLimitMiddleware)

# Include Routers under /api/v1
api_prefix = "/api/v1"
app.include_router(phytoai.router, prefix=api_prefix)
app.include_router(database.router, prefix=api_prefix)
app.include_router(sequences.router, prefix=api_prefix)


@app.get("/health", tags=["Sistem"])
async def health_check():
    """Pemeriksaan status operasional API."""
    has_api_key = bool(settings.NCBI_API_KEY)
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_target": "zhihan1996/DNABERT-2-117M",
        "ncbi_base_url": settings.NCBI_BASE_URL,
        "ncbi_api_key_configured": has_api_key,
        "method_note": settings.METHOD_NOTE
    }


@app.get("/info", tags=["Sistem"])
async def system_info():
    """Informasi metadata taksonomi acuan dan domain penelitian."""
    return {
        "organism": "Oryza sativa (Padi)",
        "target_gene": "OsDREB2A (LOC_Os01g07120)",
        "default_taxon": settings.DEFAULT_RICE_TAXON,
        "ap2_domain_coordinates": {
            "aa_range": f"{settings.AP2_DOMAIN_AA_START}-{settings.AP2_DOMAIN_AA_END}",
            "nt_cds_range": f"{settings.AP2_DOMAIN_NT_START}-{settings.AP2_DOMAIN_NT_END}",
            "verification_status": "[PERLU VERIFIKASI ke UniProt/NCBI]"
        },
        "method_note": settings.METHOD_NOTE
    }
