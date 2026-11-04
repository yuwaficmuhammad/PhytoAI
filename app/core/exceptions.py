from fastapi import HTTPException, status


class NCBIAPIException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_502_BAD_GATEWAY):
        super().__init__(status_code=status_code, detail=f"NCBI Datasets API Error: {detail}")


class GeneNotFoundException(HTTPException):
    def __init__(self, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gen padi dengan pengenal '{identifier}' tidak ditemukan di NCBI Datasets."
        )


class AssemblyNotFoundException(HTTPException):
    def __init__(self, accession: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Genom perakitan (assembly) dengan aksesi '{accession}' tidak ditemukan di NCBI Datasets."
        )

