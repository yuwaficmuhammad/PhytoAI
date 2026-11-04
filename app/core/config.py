from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "PhytoAI-Genetics: Transformer Modeling of DREB2A Mutations and Drought Tolerance in Local Rice (Oryza sativa)"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "Platform bioinformatika dan AI berbasis model Transformer (pLM) untuk memodelkan mutasi OsDREB2A, "
        "pemetaan domain AP2/NRD, desain CRISPR Base Editing, dan integrasi risiko kekeringan spasial BNPB InaRISK "
        "di seluruh agroekosistem padi Indonesia yang mengonsumsi NCBI Datasets v2 API."
    )
    
    # NCBI Datasets v2 API Base URL
    NCBI_BASE_URL: str = "https://api.ncbi.nlm.nih.gov/datasets/v2"
    
    # NCBI API Key (Opsional, meningkatkan limit dari 5 rps ke 10 rps)
    NCBI_API_KEY: Optional[str] = None
    
    # HTTP Client Configuration
    HTTP_TIMEOUT_SECONDS: float = 30.0
    
    # Taksonomi Padi (Oryza)
    DEFAULT_RICE_TAXON: str = "39947"  # Oryza sativa Japonica Group (Standard Reference Nipponbare)
    ORYZA_SATIVA_TAXON: str = "4530"   # Oryza sativa (General species)
    INDICA_TAXON: str = "39946"        # Oryza sativa Indica Group
    ORYZA_GENUS_TAXON: str = "4527"    # Genus Oryza
    
    # Reference Assembly
    DEFAULT_REFERENCE_ASSEMBLY: str = "GCF_001433935.1"  # IRGSP-1.0
    LATEST_REFERENCE_ASSEMBLY: str = "GCF_034140825.1"   # AGIS1.0

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
