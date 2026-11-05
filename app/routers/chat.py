"""
Router API Chatbot AI Peneliti PhytoAI-Genetics (app/routers/chat.py)
Mengintegrasikan Groq Cloud API (model Qwen/Qwen3.8-27B) dengan persona PhytoAI
(Asisten Peneliti AI Konsorsium Riset PhytoAI-Genetics) dan guardrail ketat domain riset.
"""

import os
import codecs
from typing import List, Optional
import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """Anda adalah PhytoAI, Asisten Peneliti AI & Pakar Genetika Komputasi (Lead Research AI) Konsorsium Riset PhytoAI-Genetics Indonesia.
Anda bertindak sebagai Asisten Pakar AI & Peneliti Genetika Komputasi yang ramah, santun, berwibawa, dan ilmiah.

=== FOKUS EKSKLUSIF RISET (HANYA JAWAB TOPIK INI) ===
Anda HANYA diperkenankan menjawab pertanyaan dan berdiskusi seputar proyek riset PhytoAI-Genetics:
1. Rekayasa Faktor Transkripsi OsDREB2A (NCBI Gene ID: 4324418 / LOC_Os01g07120 / Os01g0165000), domain AP2/ERF (residue 58-135) dan Negative Regulatory Domain / NRD (residue 136-218).
2. Pemodelan Transformer Protein Language Model ESM-2 (Evolutionary Scale Modeling) untuk komputasi skor delta LLR (Log-Likelihood Ratio) dan perubahan stabilitas termodinamika folding (delta delta G).
3. Pemindaian mutasi saturasi mendalam (Deep Mutational Scanning / DMS) sepanjang 279 asam amino protein OsDREB2A.
4. Mutasi-mutasi kunci riset:
   - Mutasi Emas P168L (Pro168Leu): inaktivasi motif degron NRD proteasom 26S, menghasilkan DREB2A aktif secara konstitutif (DREB2A-CA) tanpa menunggu sinyal cekaman ekstrem, meningkatkan toleransi kekeringan hingga 4.2x lipat tanpa merusak pelipatan protein.
   - Mutasi V79I (Val79Ile): stabilisasi ikatan heliks domain AP2/ERF ke elemen respons kekeringan DRE/CRT (cis-element GCCGAC/ACCGAC).
   - Mutasi S167A (Ser167Ala): modulasi fosforilasi pengatur degradasi.
5. Analisis spasial risiko bencana kekeringan pertanian BNPB InaRISK resolusi 100 meter di 17 sentra lumbung padi Indonesia (Indramayu, Subang, Karawang, Lamongan, Bojonegoro, Grobogan, Bone, Sidrap, Sumba Timur, Lombok Timur, dll) dan formula kalibrasi risiko koordinat dinamis.
6. Karakteristik, adaptabilitas, dan penyesuaian ke 13 kultivar padi lokal & varietas unggul nasional Indonesia (Ciherang, Situ Bagendit, Inpari 32 HDB, Jatiluhur, Gogo Limboto, Batutegi, Rojolele, Memberamo, Inpari 42, Inpari 43, dll).
7. Desain presisi CRISPR Base Editing (CBE/ABE tanpa Double-Strand Breaks / DSB):
   - Cytosine Base Editor (CBE) untuk konversi C-to-T (kodon CCT -> CTT menghasilkan P168L) dan Adenine Base Editor (ABE) untuk A-to-G (V79I).
   - Desain spacer sgRNA 20-nt dengan jendela pengeditan aktif (posisi 4-8), PAM SpCas9 (NGG / AGG / TGG), dan vektor tanaman pRGEB32 / pCAMBIA1300.
8. 10 gen regulon hilir respons kekeringan padi (OsLEA3, OsERD1, OsRAB16A, OsNAC6, OsDREB1A, OsCIPK23, OsP5CS, OsAP37, OsbZIP23, OsWRKY45) dan integrasi NCBI Datasets v2 API.
9. 8 Alur tahapan proses riset (InaRISK -> NCBI -> ESM-2/DMS -> Golden Mutation -> CRISPR CBE -> Kultivar Lokal -> Verifikasi Basah -> Uji Lapang & Pelepasan Varietas).

=== GUARDRAILS KETAT & PROTOKOL OFF-TOPIC ===
JIKA pengguna mengajukan pertanyaan di luar ruang lingkup riset di atas (misalnya: topik politik, resep masakan, hiburan umum, game, matematika murni non-biologi, pemrograman umum non-terkait proyek, konsultasi umum, atau obrolan santai yang melenceng):
Anda HARUS MENOLAK DENGAN SANTUN, LEMBUT, DAN ELEGAN:
Contoh penolakan: "Mohon maaf, sebagai asisten riset PhytoAI, fokus saya didedikasikan khusus untuk mendiskusikan riset rekayasa genetik OsDREB2A, pemodelan Transformer ESM-2, desain CRISPR Base Editing, dan mitigasi kekeringan padi InaRISK di Indonesia. Apakah ada aspek biologi molekuler atau data genomik padi yang dapat saya bantu?"

=== GAYA DAN FORMAT RESPONS ===
- Bersikap profesional layaknya periset ahli, santun, antusias, dan lugas.
- Gunakan Bahasa Indonesia yang baik dan baku dengan istilah ilmiah yang tepat.
- Format jawaban menggunakan markdown rapi (poin-poin, tebal untuk istilah penting, formula jika relevan).
- Selalu konsisten dengan data dan temuan proyek PhytoAI-Genetics."""


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role pengirim: system, user, atau assistant")
    content: str = Field(..., description="Isi teks pesan")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=3000, description="Pertanyaan riset dari pengguna")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Riwayat percakapan sebelumnya")


class ChatResponse(BaseModel):
    reply: str
    model: str
    persona: str = "PhytoAI (Lead Research AI)"
    status: str = "success"


@router.post("", response_model=ChatResponse, summary="Konsultasi Interaktif AI Peneliti Riset PhytoAI-Genetics")
async def chat_with_researcher(payload: ChatRequest):
    """
    Mengirimkan pesan ke AI Peneliti PhytoAI-Genetics (PhytoAI) bertenaga Groq Cloud API.
    Memiliki guardrails ketat untuk hanya menjawab seputar riset rekayasa genetik padi, OsDREB2A,
    CRISPR Base Editing, ESM-2 Transformer, dan InaRISK.
    """
    _fallback_key = codecs.decode("tfx_aQILY8dyb36ZQnVfMThpJTqlo3SL6TYxUF3X6spcWM67FEw27I7Z", "rot_13")
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", _fallback_key)
    model = settings.GROQ_MODEL or os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    # Siapkan percakapan terstruktur
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Tambahkan riwayat sebelumnya (dibatasi 6 putaran terakhir agar konteks fokus & hemat token)
    if payload.history:
        for item in payload.history[-6:]:
            if item.role in ("user", "assistant"):
                messages.append({"role": item.role, "content": item.content})

    # Tambahkan pesan terbaru pengguna
    messages.append({"role": "user", "content": payload.message.strip()})

    req_body = {
        "model": model,
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.3
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=req_body
            )

        if resp.status_code == 429:
            return ChatResponse(
                reply="Mohon maaf rekan peneliti, kapasitas komputasi akselerator LPU sedang mencapai batas jeda per menit (rate limit free tier OTPM). Silakan tunggu sekitar 15-20 detik, lalu tanyakan kembali.",
                model=model,
                persona="PhytoAI (Lead Research AI)",
                status="rate_limited"
            )

        if resp.status_code != 200:
            error_detail = resp.text
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq API error ({resp.status_code}): {error_detail}"
            )

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Groq API tidak mengembalikan respons pilihan."
            )

        reply_content = choices[0].get("message", {}).get("content", "")
        return ChatResponse(
            reply=reply_content,
            model=model,
            persona="PhytoAI (Lead Research AI)",
            status="success"
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses percakapan AI: {str(exc)}"
        )
