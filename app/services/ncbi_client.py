import io
import zipfile
import re
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import NCBIAPIException, GeneNotFoundException, AssemblyNotFoundException
from app.models.gene import SequenceData, GeneSequencesResponse


def calculate_gc(sequence: str) -> float:
    """Menghitung persentase kandungan Guanin-Sitosin (GC%) dari sekuens nukleotida."""
    seq = sequence.upper()
    total = len(seq)
    if total == 0:
        return 0.0
    gc = seq.count("G") + seq.count("C")
    return round((gc / total) * 100, 2)


class NCBIDatasetsClient:
    def __init__(self):
        self.base_url = settings.NCBI_BASE_URL.rstrip("/")
        self.api_key = settings.NCBI_API_KEY
        self.timeout = settings.HTTP_TIMEOUT_SECONDS
        self._shared_client: Optional[httpx.AsyncClient] = None

    def set_shared_client(self, client: httpx.AsyncClient) -> None:
        """Menetapkan shared AsyncClient dari lifespan aplikasi (connection pooling)."""
        self._shared_client = client

    def clear_shared_client(self) -> None:
        """Menghapus referensi shared client saat shutdown."""
        self._shared_client = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": f"RiceGenomicsAPI/{settings.VERSION} (Genetic Research Proposal Suite)"
        }
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        expect_binary: bool = False
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = self._get_headers()
        if expect_binary:
            headers["Accept"] = "application/zip, application/octet-stream"

        async def _do_request(client: httpx.AsyncClient) -> Any:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers
                )
            except httpx.RequestError as exc:
                raise NCBIAPIException(f"Koneksi ke NCBI Datasets gagal: {str(exc)}")

            if response.status_code == 404:
                return None
            if response.status_code >= 400:
                raise NCBIAPIException(
                    f"NCBI Datasets mengembalikan status {response.status_code}: {response.text[:300]}",
                    status_code=response.status_code if response.status_code < 500 else 502
                )

            if expect_binary:
                return response.content
            return response.json()

        if self._shared_client is not None:
            return await _do_request(self._shared_client)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await _do_request(client)

    # --- GENE ENDPOINTS ---

    async def get_gene_by_id(self, gene_id: int) -> Dict[str, Any]:
        data = await self._request("GET", f"/gene/id/{gene_id}/dataset_report")
        if not data or not data.get("reports"):
            raise GeneNotFoundException(str(gene_id))
        return data["reports"][0]

    # --- DOWNLOAD & SEQUENCE EXTRACTION ---

    async def download_gene_package(
        self,
        gene_ids: List[int],
        annotation_types: Optional[List[str]] = None
    ) -> bytes:
        types = annotation_types or ["FASTA_GENE", "FASTA_CDS", "FASTA_PROTEIN"]
        payload = {
            "gene_ids": gene_ids,
            "include_annotation_type": types
        }
        content = await self._request("POST", "/gene/download", json_data=payload, expect_binary=True)
        return content

    async def extract_gene_sequences(self, gene_id: int, symbol: Optional[str] = None) -> GeneSequencesResponse:
        content = await self.download_gene_package([gene_id])
        if not content:
            raise NCBIAPIException(f"Gagal mengunduh paket sekuens untuk Gene ID {gene_id}")

        res = GeneSequencesResponse(gene_id=gene_id, symbol=symbol)

        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                for filename in zf.namelist():
                    if filename.endswith("gene.fna"):
                        header, seq = self._parse_first_fasta(zf.read(filename).decode("utf-8", errors="ignore"))
                        if seq:
                            res.genomic_sequence = SequenceData(
                                gene_id=gene_id,
                                symbol=symbol,
                                header=header,
                                sequence=seq,
                                length=len(seq),
                                type="genomic",
                                gc_percent=calculate_gc(seq)
                            )
                    elif filename.endswith("cds.fna"):
                        header, seq = self._parse_first_fasta(zf.read(filename).decode("utf-8", errors="ignore"))
                        if seq:
                            res.cds_sequence = SequenceData(
                                gene_id=gene_id,
                                symbol=symbol,
                                header=header,
                                sequence=seq,
                                length=len(seq),
                                type="cds",
                                gc_percent=calculate_gc(seq)
                            )
                    elif filename.endswith("protein.faa"):
                        header, seq = self._parse_first_fasta(zf.read(filename).decode("utf-8", errors="ignore"))
                        if seq:
                            res.protein_sequence = SequenceData(
                                gene_id=gene_id,
                                symbol=symbol,
                                header=header,
                                sequence=seq,
                                length=len(seq),
                                type="protein"
                            )
        except zipfile.BadZipFile:
            raise NCBIAPIException("Format arsip ZIP paket sekuens dari NCBI rusak.")

        return res

    def _parse_first_fasta(self, fasta_str: str) -> (str, str):
        lines = fasta_str.strip().splitlines()
        header = ""
        seq_parts = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header:
                    break
                header = line[1:]
            else:
                seq_parts.append(line)
        return header, "".join(seq_parts)


ncbi_client = NCBIDatasetsClient()
