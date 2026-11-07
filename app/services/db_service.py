"""
app/services/db_service.py
Layanan database SQLite lokal untuk penyimpanan sekuens landrace padi,
skor mutagenesis saturasi in silico (DNABERT-2), dan prediksi varian.
"""

import os
import sqlite3
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(APP_DIR, "data", "phytoai_local.db")


@contextmanager
def get_db_connection():
    """Mengembalikan koneksi database SQLite lokal dengan row_factory Row."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_db_stats() -> Dict[str, Any]:
    """Mengembalikan statistik jumlah rekaman tabel dalam database lokal."""
    stats = {
        "status": "online",
        "database_type": "SQLite3",
        "database_path": DB_PATH,
        "file_size_kb": round(os.path.getsize(DB_PATH) / 1024, 2) if os.path.exists(DB_PATH) else 0,
        "tables": {}
    }
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for table in ["landrace_sequences", "saturation_scores", "variant_predictions"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats["tables"][table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats["tables"][table] = 0
    return stats


def insert_landrace_sequence(
    landrace_name: str,
    accession: str,
    sequence: str,
    length: int,
    gc_content: Optional[float] = None,
    source_note: Optional[str] = None
) -> str:
    """Menyimpan atau memperbarui sekuens FASTA landrace padi lokal."""
    record_id = f"{landrace_name}_{accession}".replace(" ", "_")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO landrace_sequences (id, landrace_name, accession, sequence, length, gc_content, source_note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                sequence=excluded.sequence,
                length=excluded.length,
                gc_content=excluded.gc_content,
                source_note=excluded.source_note
            """,
            (record_id, landrace_name, accession, sequence.upper().strip(), length, gc_content, source_note)
        )
        conn.commit()
    return record_id


def get_all_landraces() -> List[Dict[str, Any]]:
    """Mengambil seluruh data sekuens landrace yang tersimpan di DB."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM landrace_sequences ORDER BY landrace_name")
        return [dict(row) for row in cursor.fetchall()]


def get_landrace_sequence(identifier: str) -> Optional[Dict[str, Any]]:
    """Mengambil data sekuens satu landrace berdasarkan nama atau nomor aksesi."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM landrace_sequences
            WHERE LOWER(landrace_name) = LOWER(?) OR LOWER(accession) = LOWER(?) OR id = ?
            LIMIT 1
            """,
            (identifier, identifier, identifier)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def insert_saturation_score(
    landrace: str,
    position_nt: int,
    ref: str,
    alt: str,
    delta_pll: Optional[float],
    pseudo_perplexity: Optional[float],
    mutation_type: Optional[str],
    wt_codon: Optional[str],
    mut_codon: Optional[str],
    wt_aa: Optional[str],
    mut_aa: Optional[str],
    model_name: str,
    window: Optional[int] = None
) -> None:
    """Menyimpan satu skor mutagenesis saturasi in silico (idempoten)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO saturation_scores (
                landrace, position_nt, ref, alt, delta_pll, pseudo_perplexity,
                mutation_type, wt_codon, mut_codon, wt_aa, mut_aa, model_name, window
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(landrace, position_nt, ref, alt, model_name) DO UPDATE SET
                delta_pll=excluded.delta_pll,
                pseudo_perplexity=excluded.pseudo_perplexity,
                mutation_type=excluded.mutation_type,
                wt_codon=excluded.wt_codon,
                mut_codon=excluded.mut_codon,
                wt_aa=excluded.wt_aa,
                mut_aa=excluded.mut_aa,
                window=excluded.window,
                computed_at=CURRENT_TIMESTAMP
            """,
            (
                landrace, position_nt, ref.upper(), alt.upper(), delta_pll, pseudo_perplexity,
                mutation_type, wt_codon, mut_codon, wt_aa, mut_aa, model_name, window
            )
        )
        conn.commit()


def get_saturation_scores(
    landrace: Optional[str] = None,
    min_delta_pll: Optional[float] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Mengambil daftar varian dan skor mutagenesis saturasi dari database."""
    query = "SELECT * FROM saturation_scores WHERE 1=1"
    params = []

    if landrace:
        query += " AND LOWER(landrace) = LOWER(?)"
        params.append(landrace)
    if min_delta_pll is not None:
        query += " AND delta_pll >= ?"
        params.append(min_delta_pll)

    query += " ORDER BY delta_pll DESC LIMIT ?"
    params.append(limit)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]


def insert_variant_prediction(
    landrace: str,
    position_nt: int,
    ref: str,
    alt: str,
    predicted_class: Optional[str],
    class_probabilities: Optional[str] = None,
    predicted_lri: Optional[float] = None,
    is_zero_shot: int = 1,
    method_note: Optional[str] = None
) -> int:
    """Menyimpan hasil prediksi kelas varian dan regresi LRI."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO variant_predictions (
                landrace, position_nt, ref, alt, predicted_class,
                class_probabilities, predicted_lri, is_zero_shot, method_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                landrace, position_nt, ref.upper(), alt.upper(), predicted_class,
                class_probabilities, predicted_lri, is_zero_shot, method_note
            )
        )
        conn.commit()
        return cursor.lastrowid


def get_variant_predictions(
    landrace: Optional[str] = None,
    predicted_class: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Mengambil daftar prediksi varian dari database."""
    query = "SELECT * FROM variant_predictions WHERE 1=1"
    params = []
    if landrace:
        query += " AND LOWER(landrace) = LOWER(?)"
        params.append(landrace)
    if predicted_class:
        query += " AND predicted_class = ?"
        params.append(predicted_class)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

