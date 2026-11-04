import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx

from app.core.config import settings
from app.routers import genomes, genes, targets, sequences, crispr, phytoai, database
from app.services.ncbi_client import ncbi_client
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manajemen siklus hidup aplikasi: inisialisasi HTTPX connection pool saat startup."""
    # Startup: buat satu AsyncClient berbagi (connection pooling)
    shared_client = httpx.AsyncClient(
        timeout=settings.HTTP_TIMEOUT_SECONDS,
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
    )
    ncbi_client.set_shared_client(shared_client)
    yield
    # Shutdown: tutup koneksi dengan bersih
    await shared_client.aclose()
    ncbi_client.clear_shared_client()


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "PhytoAI-Genetics: Pemodelan Transformer DREB2A & Kekeringan Padi",
            "description": "Pemodelan Transformer protein language model (pLM) untuk prediksi mutasi DREB2A, Deep Mutational Scanning (DMS), profil varietas padi lokal, dan CRISPR base editing toleransi kekeringan."
        },
        {
            "name": "Katalog Target Rekayasa Genetika Padi (CRISPR Targets)",
            "description": "Koleksi target gen unggulan padi untuk rekayasa genetika (ketahanan hawar daun bakteri SWEET, hasil gabah DEP1/GS3, aroma Badh2, keamanan pangan OsNramp5, toleransi kekeringan OsDREB2A)."
        },
        {
            "name": "Perancangan CRISPR & Bioinformatika (CRISPR Tools)",
            "description": "Pindai gRNA SpCas9 / Cas12a, eliminasi motif terminasi transkripsi Pol III TTTT, dan otomatisasi desain langsung dari sekuens CDS gen NCBI."
        },
        {
            "name": "Gen Padi (Rice Genes)",
            "description": "Pencarian dan penelusuran informasi gen padi (Oryza sativa) langsung ke NCBI Datasets v2 API."
        },
        {
            "name": "Ekstraksi Sekuens DNA/Protein (Sequences)",
            "description": "Ekstraksi otomatis sekuens genomik, CDS, dan protein dalam format FASTA serta unduhan paket arsip ZIP resmi NCBI."
        },
        {
            "name": "Database Lokal SQLite: Penyimpanan Data Real NCBI & InaRISK",
            "description": "Penyimpanan persisten lokal data gen NCBI (CDS, Protein, Locus) dan layer spasial BNPB InaRISK berlatensi <0.1ms untuk performa tinggi tanpa downtime jaringan."
        },
        {
            "name": "Genom Perakitan Padi (Genomes & Assemblies)",
            "description": "Laporan perakitan genom referensi padi Nipponbare (IRGSP-1.0, AGIS1.0) dan varietas Indica."
        }
    ]
)

# CORS — allow_credentials=False diperlukan saat allow_origins=["*"]
# (Spesifikasi W3C CORS melarang kombinasi wildcard + credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate Limiting — sliding window in-memory per IP
# Urutan penting: middleware diterapkan dari bawah ke atas di FastAPI/Starlette
app.add_middleware(RateLimitMiddleware)

# Include Routers under /api/v1
api_prefix = "/api/v1"
app.include_router(phytoai.router, prefix=api_prefix)
app.include_router(database.router, prefix=api_prefix)
app.include_router(targets.router, prefix=api_prefix)
app.include_router(crispr.router, prefix=api_prefix)
app.include_router(genes.router, prefix=api_prefix)
app.include_router(sequences.router, prefix=api_prefix)
app.include_router(genomes.router, prefix=api_prefix)

# Static files & Web UI Studio
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root_studio():
    """Tampilan web interaktif studio rekayasa genetika padi."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>Rice Genetic Engineering API Studio</h1><p>Visit <a href='/docs'>/docs</a></p>")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Mengembalikan berkas favicon ikon studio."""
    icon_svg = os.path.join(static_dir, "favicon.svg")
    if os.path.exists(icon_svg):
        return FileResponse(icon_svg, media_type="image/svg+xml")
    icon_png = os.path.join(static_dir, "favicon.png")
    if os.path.exists(icon_png):
        return FileResponse(icon_png, media_type="image/png")
    return HTMLResponse(status_code=404)


@app.get("/download-tutorial-pdf", include_in_schema=False)
@app.get("/Panduan_Lengkap_PhytoAI_Genetics_A4.pdf", include_in_schema=False)
async def download_tutorial_pdf():
    """Mengunduh berkas PDF tutorial panduan alur penggunaan aplikasi resmi (ukuran A4)."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(root_dir, "Panduan_Lengkap_PhytoAI_Genetics_A4.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Panduan_Lengkap_PhytoAI_Genetics_A4.pdf"}
        )
    return HTMLResponse("Berkas PDF belum ditemukan.", status_code=404)


@app.get("/download-step-by-step-pdf", include_in_schema=False)
@app.get("/Panduan_Alur_Penelitian_Step_by_Step_A4.pdf", include_in_schema=False)
async def download_step_by_step_pdf():
    """Mengunduh berkas PDF alur proses penelitian step-by-step bahasa mudah dipahami (ukuran A4)."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(root_dir, "Panduan_Alur_Penelitian_Step_by_Step_A4.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Panduan_Alur_Penelitian_Step_by_Step_A4.pdf"}
        )
    return HTMLResponse("Berkas PDF belum ditemukan.", status_code=404)


@app.get("/health", tags=["Sistem"])
async def health_check():
    """Pemeriksaan status operasional API."""
    has_api_key = bool(settings.NCBI_API_KEY)
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ncbi_base_url": settings.NCBI_BASE_URL,
        "default_taxon": settings.DEFAULT_RICE_TAXON,
        "ncbi_api_key_configured": has_api_key,
        "ncbi_rate_limit": "10 requests/second (Authenticated)" if has_api_key else "5 requests/second (Unauthenticated)"
    }


@app.get("/info", tags=["Sistem"])
async def system_info():
    """Informasi metadata taksonomi dan acuan genom padi."""
    return {
        "organism": "Oryza sativa (Padi)",
        "taxa": {
            "default_japonica": settings.DEFAULT_RICE_TAXON,
            "indica_group": settings.INDICA_TAXON,
            "general_species": settings.ORYZA_SATIVA_TAXON,
            "genus_oryza": settings.ORYZA_GENUS_TAXON
        },
        "assemblies": {
            "standard_reference": settings.DEFAULT_REFERENCE_ASSEMBLY,
            "latest_reference": settings.LATEST_REFERENCE_ASSEMBLY
        },
        "curated_targets_count": len(targets.RICE_TARGETS)
    }

