import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PhytoAI-Genetics: Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (Oryza sativa)"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = (
        "Pipeline bioinformatika dan pemodelan Transformer DNABERT-2 untuk analisis in silico "
        "mutagenesis saturasi lokus DREB2A pada landrace padi lokal Indonesia (Oryza sativa)."
    )

    # NCBI Datasets v2 API Base URL
    NCBI_BASE_URL: str = "https://api.ncbi.nlm.nih.gov/datasets/v2"

    # NCBI API Key (Opsional, meningkatkan rate limit)
    NCBI_API_KEY: Optional[str] = None

    # Hugging Face Access Token (Opsional, untuk otentikasi Hub & bypass rate limit)
    HF_TOKEN: Optional[str] = None

    # HTTP Client Configuration
    HTTP_TIMEOUT_SECONDS: float = 30.0

    # Taksonomi Padi Acuan (Oryza sativa)
    DEFAULT_RICE_TAXON: str = "39947"  # Oryza sativa Japonica Group (Standard Reference Nipponbare)

    # Catatan Metodologi Wajib (Disertakan di setiap respon skor model)
    METHOD_NOTE: str = (
        "Skor adalah pergeseran pseudo-log-likelihood DNABERT-2 (zero-shot), "
        "ukuran kewajaran urutan menurut model. Bukan bukti fenotipe toleransi kekeringan."
    )

    # Koordinat Domain AP2/ERF Pengikat DNA pada gen OsDREB2A (Acuan Nipponbare LOC_Os01g07120)
    # [PERLU VERIFIKASI ke UniProt/NCBI]
    # Residu asam amino 68-130 -> Rentang nukleotida CDS: bp 202 - 390
    AP2_DOMAIN_AA_START: int = 68
    AP2_DOMAIN_AA_END: int = 130
    AP2_DOMAIN_NT_START: int = (68 - 1) * 3 + 1  # 202
    AP2_DOMAIN_NT_END: int = 130 * 3             # 390

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
