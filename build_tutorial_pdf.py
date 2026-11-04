"""
Skrip Pembuat Dokumen PDF Tutorial & Panduan Riset PhytoAI-Genetics
Ukuran Kertas: A4 (210 x 297 mm)
Format Teks: Justify (Rata Kiri-Kanan) dengan Tipografi Segoe UI / TrueType
Gambar: 100% Rasio Aspek Proporsional Asli (1.7917 : 1)
Struktur: 13 Bab, 10 Halaman Lengkap, Rapi, Bersih Tanpa Tag Asteris Mentah.
Fitur Unggulan: Komponen Bullet & Numbered List Berbasis Tabel Presisi Tinggi (True Hanging Indent).
"""

import os
import sys
import re
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ==================== 1. KONFIGURASI FONT SEGOE UI ====================
font_dirs = [
    "/Library/Fonts",
    "/System/Library/Fonts",
    "/System/Library/Fonts/Supplemental",
]

def register_segoe_fonts():
    segoe_regular = None
    segoe_bold = None
    segoe_italic = None
    segoe_bolditalic = None

    for fdir in font_dirs:
        if not os.path.isdir(fdir):
            continue
        try:
            fnames = os.listdir(fdir)
        except Exception:
            continue
        for fname in fnames:
            fl = fname.lower()
            fpath = os.path.join(fdir, fname)
            if "segoeui" in fl or "segoe_ui" in fl or fl == "segoe ui.ttf":
                if "bolditalic" in fl or "z.ttf" in fl:
                    segoe_bolditalic = fpath
                elif "bold" in fl or "b.ttf" in fl:
                    segoe_bold = fpath
                elif "italic" in fl or "i.ttf" in fl:
                    segoe_italic = fpath
                elif "regular" in fl or fl in ["segoeui.ttf", "segoe ui.ttf"]:
                    segoe_regular = fpath

    # Fallback ke Arial jika Segoe UI tidak tersedia langsung di macOS
    if not segoe_regular:
        for fdir in font_dirs:
            if not os.path.isdir(fdir):
                continue
            ar = os.path.join(fdir, "Arial.ttf")
            arb = os.path.join(fdir, "Arial Bold.ttf")
            ari = os.path.join(fdir, "Arial Italic.ttf")
            arbi = os.path.join(fdir, "Arial Bold Italic.ttf")
            if os.path.exists(ar):
                segoe_regular = ar
                segoe_bold = arb if os.path.exists(arb) else ar
                segoe_italic = ari if os.path.exists(ari) else ar
                segoe_bolditalic = arbi if os.path.exists(arbi) else ar
                break

    try:
        pdfmetrics.registerFont(TTFont('SegoeUI', segoe_regular))
        pdfmetrics.registerFont(TTFont('SegoeUI-Bold', segoe_bold))
        pdfmetrics.registerFont(TTFont('SegoeUI-Italic', segoe_italic))
        pdfmetrics.registerFont(TTFont('SegoeUI-BoldItalic', segoe_bolditalic))
        print("Font Segoe UI / Arial berhasil didaftarkan secara native.")
    except Exception as e:
        print(f"Peringatan registrasi font: {e}, menggunakan font Helvetica fallback.")

register_segoe_fonts()


# ==================== 2. NUMBERED CANVAS UNTUK RUNNING HEADER & FOOTER ====================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("SegoeUI", 7.2)
        self.setFillColor(HexColor("#64748b"))

        # Halaman Sampul (Cover Page) tidak menampilkan header & footer
        if self._pageNumber > 1:
            # Header
            header_text = "PhytoAI-Genetics: Panduan Alur Pengoperasian, Rekayasa Molekuler & Persiapan Riset"
            self.drawString(36, 815, header_text)
            self.drawRightString(A4[0] - 36, 815, "Platform Pemodelan Transformer OsDREB2A, CRISPR Base Editing & InaRISK BNPB")
            self.setStrokeColor(HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 809, A4[0] - 36, 809)

            # Footer
            footer_page = f"Halaman {self._pageNumber} dari {page_count}"
            self.drawRightString(A4[0] - 36, 24, footer_page)
            self.drawString(36, 24, "Kementerian Pendidikan Tinggi, Sains, dan Teknologi RI  |  Pusat Riset Bioteknologi Pangan")
            self.setStrokeColor(HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 33, A4[0] - 36, 33)

        self.restoreState()


# ==================== 3. SANITASI TAG MARKDOWN ====================
def md_clean(text: str) -> str:
    """Mengonversi sintaks Markdown (*kata*, **kata**) ke tag ReportLab (<i>kata</i>, <b>kata</b>)."""
    if not text:
        return ""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Hindari mengubah underscore pada nama file atau kode snake_case (seperti test_live_integration.py)
    text = re.sub(r'(?<![A-Za-z0-9_])_([A-Za-z0-9\s]+?)_(?![A-Za-z0-9_])', r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


# ==================== 4. PEMBANGUN DOKUMEN UTAMA ====================
def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=42
    )

    printable_width = A4[0] - 72

    # Palet Warna Bertema Alam Ilmiah & Laboratorium Presisi
    PRIMARY = HexColor("#059669")         # Emerald Green
    PRIMARY_DARK = HexColor("#065f46")    # Deep Forest Green
    PRIMARY_LIGHT = HexColor("#10b981")   # Vibrant Mint
    PRIMARY_SUBTLE = HexColor("#ecfdf5")  # Soft Emerald Wash
    ACCENT_BLUE = HexColor("#0284c7")     # Genomic Indigo/Cyan
    ACCENT_BLUE_LIGHT = HexColor("#e0f2fe")
    TEXT_MAIN = HexColor("#1e293b")       # Slate 800
    TEXT_MUTED = HexColor("#64748b")      # Slate 500
    BG_CARD = HexColor("#f8fafc")         # Slate 50
    BORDER_COLOR = HexColor("#cbd5e1")    # Slate 300

    styles = getSampleStyleSheet()

    # Tipografi Khusus Rata Kiri-Kanan (Justified)
    title_cover = ParagraphStyle(
        'CoverTitle',
        fontName='SegoeUI-Bold',
        fontSize=20,
        leading=25,
        textColor=PRIMARY_DARK,
        alignment=TA_LEFT,
        spaceAfter=5
    )

    subtitle_cover = ParagraphStyle(
        'CoverSubtitle',
        fontName='SegoeUI',
        fontSize=9.5,
        leading=14.5,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    h1 = ParagraphStyle(
        'SectionH1',
        fontName='SegoeUI-Bold',
        fontSize=11.5,
        leading=15,
        textColor=PRIMARY_DARK,
        spaceBefore=8,
        spaceAfter=3.5,
        keepWithNext=True
    )

    h2 = ParagraphStyle(
        'SectionH2',
        fontName='SegoeUI-Bold',
        fontSize=9.4,
        leading=13,
        textColor=ACCENT_BLUE,
        spaceBefore=6,
        spaceAfter=2.5,
        keepWithNext=True
    )

    body_justify = ParagraphStyle(
        'BodyJustify',
        fontName='SegoeUI',
        fontSize=8.4,
        leading=12.6,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=4
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='SegoeUI-Bold',
        fontSize=8.4,
        leading=12.6,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=3,
        keepWithNext=True
    )

    list_item_style = ParagraphStyle(
        'ListItemStyle',
        fontName='SegoeUI',
        fontSize=8.4,
        leading=12.6,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=0
    )

    bullet_label_style = ParagraphStyle(
        'BulletLabel',
        fontName='SegoeUI-Bold',
        fontSize=9,
        leading=12.6,
        textColor=PRIMARY,
        alignment=TA_CENTER
    )

    num_label_style = ParagraphStyle(
        'NumLabel',
        fontName='SegoeUI-Bold',
        fontSize=8.4,
        leading=12.6,
        textColor=ACCENT_BLUE,
        alignment=TA_RIGHT
    )

    callout_text = ParagraphStyle(
        'CalloutText',
        fontName='SegoeUI',
        fontSize=8,
        leading=11.8,
        textColor=PRIMARY_DARK,
        alignment=TA_JUSTIFY
    )

    caption_style = ParagraphStyle(
        'CaptionStyle',
        fontName='SegoeUI-Italic',
        fontSize=7.5,
        leading=10.2,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    table_header = ParagraphStyle(
        'TableHeader',
        fontName='SegoeUI-Bold',
        fontSize=7.4,
        leading=9.5,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_cell = ParagraphStyle(
        'TableCell',
        fontName='SegoeUI',
        fontSize=7.2,
        leading=9.5,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        fontName='SegoeUI',
        fontSize=7.2,
        leading=9.5,
        textColor=TEXT_MAIN,
        alignment=TA_CENTER
    )

    def P(raw_text: str, style=body_justify) -> Paragraph:
        return Paragraph(md_clean(raw_text), style)

    # ==================== KOMPONEN LIST BULLET & NUMBERING RAPI ====================
    def make_bullet_list(items, bullet_char='•', bullet_color=PRIMARY, text_style=None):
        """Menghasilkan bullet list dengan hanging indent presisi tinggi via 2-column Table."""
        if text_style is None:
            text_style = list_item_style
        bullet_width = 14
        text_width = printable_width - bullet_width
        rows = []
        for it in items:
            b_p = Paragraph(f"<font color='{bullet_color}'><b>{bullet_char}</b></font>", bullet_label_style)
            t_p = Paragraph(md_clean(it), text_style)
            rows.append([b_p, t_p])
        t = Table(rows, colWidths=[bullet_width, text_width])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (0,-1), 3),
            ('RIGHTPADDING', (1,0), (1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 1.2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ]))
        return t

    def make_numbered_list(items, start_num=1, num_color=ACCENT_BLUE, text_style=None):
        """Menghasilkan numbered list dengan nomor rata-kanan (sejajar pada tanda titik) dan hanging indent mutlak."""
        if text_style is None:
            text_style = list_item_style
        num_width = 18
        text_width = printable_width - num_width
        rows = []
        for idx, it in enumerate(items, start=start_num):
            n_p = Paragraph(f"<font color='{num_color}'><b>{idx}.</b></font>", num_label_style)
            t_p = Paragraph(md_clean(it), text_style)
            rows.append([n_p, t_p])
        t = Table(rows, colWidths=[num_width, text_width])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (0,-1), 4),
            ('RIGHTPADDING', (1,0), (1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 1.2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.4),
        ]))
        return t

    def make_callout(title, content, bg=PRIMARY_SUBTLE, border=PRIMARY):
        """Membuat kotak callout informatif. Konten dapat berupa string tunggal atau list bullet rapi."""
        header_p = P(f"<b>💡 {title}</b>", ParagraphStyle('CalloutH', fontName='SegoeUI-Bold', fontSize=8.4, leading=11, textColor=border))
        flowables = [header_p, Spacer(1, 2)]

        callout_inner_w = printable_width - 16

        if isinstance(content, list):
            b_width = 12
            t_width = callout_inner_w - b_width
            rows = []
            for it in content:
                b_p = Paragraph(f"<font color='{border}'><b>•</b></font>", ParagraphStyle('CBullet', fontName='SegoeUI-Bold', fontSize=8.4, leading=11.6, alignment=TA_CENTER))
                t_p = Paragraph(md_clean(it), ParagraphStyle('CText', fontName='SegoeUI', fontSize=8, leading=11.6, textColor=PRIMARY_DARK, alignment=TA_JUSTIFY))
                rows.append([b_p, t_p])
            t_inner = Table(rows, colWidths=[b_width, t_width])
            t_inner.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (0,-1), 3),
                ('RIGHTPADDING', (1,0), (1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
            ]))
            flowables.append(t_inner)
        else:
            flowables.append(P(content, callout_text))

        t = Table([[flowables]], colWidths=[printable_width], style=[
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 0.75, border),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ])
        return KeepTogether([Spacer(1, 2.5), t, Spacer(1, 3.5)])

    story = []
    img_dir = "/Users/yuwaficmuhammad/Desktop/ncbi/app/static/images"

    def make_figure(image_name, caption_text, target_width=350):
        img_path = os.path.join(img_dir, image_name)
        if not os.path.exists(img_path):
            return Spacer(1, 2)
        
        with PILImage.open(img_path) as pil_img:
            orig_w, orig_h = pil_img.size
            aspect = orig_h / orig_w
            
        final_w = target_width
        final_h = round(target_width * aspect, 2)
        
        img = Image(img_path, width=final_w, height=final_h)
        caption = P(caption_text, caption_style)
        
        img_table = Table([[img]], colWidths=[final_w], style=[
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 0.75, BORDER_COLOR),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ])
        
        wrapper = Table([[img_table]], colWidths=[printable_width], style=[
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ])
        
        return KeepTogether([Spacer(1, 3), wrapper, Spacer(1, 2), caption, Spacer(1, 3.5)])

    def make_qa_item(q_num, question, answer):
        """Membuat baris Tanya-Jawab terstruktur dengan badge nomor rapi dan pemisah visual halus."""
        badge_p = Paragraph(f"<font color='{ACCENT_BLUE}'><b>T&amp;J&nbsp;{q_num}</b></font>", ParagraphStyle('QABadge', fontName='SegoeUI-Bold', fontSize=8, leading=11, alignment=TA_CENTER))
        q_p = Paragraph(f"<b>\"{question}\"</b>", ParagraphStyle('QAQuestion', fontName='SegoeUI-Bold', fontSize=8.4, leading=12, textColor=PRIMARY_DARK, alignment=TA_JUSTIFY))
        a_p = Paragraph(f"<font color='{PRIMARY}'><b>Model Jawaban Saintifik:</b></font> \"{answer}\"", ParagraphStyle('QAAnswer', fontName='SegoeUI', fontSize=8.2, leading=12.2, textColor=TEXT_MAIN, alignment=TA_JUSTIFY))
        content = [q_p, Spacer(1, 2), a_p]
        t = Table([[badge_p, content]], colWidths=[38, printable_width - 38])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (0,-1), 6),
            ('RIGHTPADDING', (1,0), (1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 2.2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.2),
            ('LINEBELOW', (0,0), (-1,-1), 0.4, colors.HexColor("#e2e8f0")),
        ]))
        return t

    # ==================== HALAMAN 1: SAMPUL RESMI / COVER ====================
    badge_data = [
        [P("<font color='#059669'><b>BUKU PANDUAN PENGGUNA RESMI & PROTOKOL RISET</b></font> &nbsp;|&nbsp; Versi 1.0.0 &nbsp;|&nbsp; <i>Oryza sativa</i> Japonica & Indica", ParagraphStyle('Badge', fontName='SegoeUI', fontSize=7.8, leading=10, textColor=TEXT_MUTED))]
    ]
    badge_table = Table(badge_data, colWidths=[printable_width], style=[
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.6, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6.5),
    ])
    story.append(badge_table)
    story.append(Spacer(1, 6))

    story.append(P("PANDUAN LENGKAP & ALUR PENGGUNAAN<br/>PLATFORM PhytoAI-Genetics", title_cover))
    story.append(P(
        "Buku Panduan Komprehensif: Pemodelan Transformer <i>OsDREB2A</i>, Desain CRISPR Base Editing Presisi, "
        "Mekanisme Molekuler & Kultur Jaringan Tanaman, Spesifikasi 4 Model AI & Biofisika, Arsitektur Tech Stack, "
        "Matriks Pengujian Sistem & Validasi Eksperimental, serta 10 Simulasi Tanya Jawab Kritis Sidang Akademik.",
        subtitle_cover
    ))
    story.append(HRFlowable(width="100%", thickness=1.2, color=PRIMARY, spaceBefore=0, spaceAfter=5))

    # Hero Banner Proporsional (target_width=410 -> height=228.84, native aspect 1.7917)
    story.append(make_figure(
        "rice_dreb2a_hero.png",
        "<b>Visualisasi Riset Utama:</b> Arsitektur faktor transkripsi OsDREB2A berikatan dengan heliks DNA motif DRE/CRT untuk toleransi kekeringan ekstrem.",
        target_width=410
    ))

    # Metadata Cover Box
    cover_box = [
        [
            P("<b>Target Pengguna:</b>", ParagraphStyle('CB1', fontName='SegoeUI-Bold', fontSize=7.4, textColor=TEXT_MAIN)),
            P("Peneliti Bioteknologi Tanaman, Dosen Penguji, Mahasiswa Pascasarjana Pemuliaan Tanaman, Agronom.", ParagraphStyle('CB2', fontName='SegoeUI', fontSize=7.4, textColor=TEXT_MAIN))
        ],
        [
            P("<b>Spesifikasi Sistem:</b>", ParagraphStyle('CB1', fontName='SegoeUI-Bold', fontSize=7.4, textColor=TEXT_MAIN)),
            P("FastAPI 0.115, Protein Language Model (Transformer pLM), Leaflet GIS InaRISK BNPB 100m, NCBI Datasets v2 REST API.", ParagraphStyle('CB2', fontName='SegoeUI', fontSize=7.4, textColor=TEXT_MAIN))
        ],
        [
            P("<b>Akses Aplikasi:</b>", ParagraphStyle('CB1', fontName='SegoeUI-Bold', fontSize=7.4, textColor=TEXT_MAIN)),
            P("Antarmuka Studio Web: <code>http://localhost:8000</code> &nbsp;|&nbsp; Dokumentasi Interaktif API: <code>/docs</code>", ParagraphStyle('CB2', fontName='SegoeUI', fontSize=7.4, textColor=TEXT_MAIN))
        ]
    ]
    cover_table = Table(cover_box, colWidths=[95, printable_width - 95], style=[
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY_SUBTLE),
        ('BOX', (0,0), (-1,-1), 0.75, PRIMARY_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor("#a7f3d0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ])
    story.append(cover_table)

    # Pindah Halaman Bersih ke Halaman 2
    story.append(PageBreak())

    # ==================== HALAMAN 2: BAB 1 & BAB 2 ====================
    story.append(P("1. Mengenal Platform PhytoAI-Genetics: Filosofi & Urgensi Riset", h1))
    story.append(P(
        "Kekeringan ekstrem yang diperparah oleh fenomena iklim El Nino merupakan ancaman eksistensial paling nyata terhadap kedaulatan pangan nasional Indonesia. Di sentra-sentra produksi padi lahan sawah tadah hujan berlempung vertisol (seperti di Pantura Jawa Tengah: Demak, Pati, Grobogan, serta Bojonegoro) dan lahan kering semi-arid (Nusa Tenggara Timur dan Nusa Tenggara Barat), defisit air berkepanjangan secara berkala menyebabkan puso massal dan gagal panen total.",
        body_justify
    ))
    story.append(P(
        "Secara biologis, tanaman padi (<i>Oryza sativa</i>) sebenarnya memiliki 'saklar genetik' alami pengendali ketahanan kekeringan, yaitu faktor transkripsi <b>OsDREB2A</b> (NCBI Gene ID: <code>4324418</code>). Namun, pada padi budidaya konvensional (seperti IR64 atau Ciherang), saklar ini dibatasi oleh mekanisme bawaan seluler: protein DREB2A sengaja dihancurkan oleh enzim ubiquitin ligase E3 melalui domain degron <b>NRD (Negative Regulatory Domain)</b> ketika tanah masih berair. Tanaman baru mulai memproduksi dan mempertahankan DREB2A setelah mengalami dehidrasi parah—kondisi di mana kerusakan jaringan tanaman sering kali sudah terlambat untuk diselamatkan.",
        body_justify
    ))
    story.append(P(
        "<b>PhytoAI-Genetics</b> hadir sebagai terobosan terintegrasi pertama di Indonesia yang menggabungkan tiga pilar teknologi mutakhir dalam satu alur kerja yang kohesif:",
        body_justify
    ))

    # Tiga Pilar dengan Bullet List Rapi
    pilar_items = [
        "<b>Pemodelan AI Transformer (Protein Language Model / pLM):</b> Memprediksi secara akurat dampak mutasi titik asam amino terhadap energi bebas pengikatan molekuler (&Delta;&Delta;G) dan skor fitness evolusioner (&Delta;LLR) tanpa memerlukan waktu bertahun-tahun uji coba laboratorium basah acak.",
        "<b>Perancangan CRISPR Base Editing (CBE & ABE) Presisi:</b> Mengonversi hasil prediksi AI menjadi panduan oligonukleotida pemotongan tanpa patahan untai ganda (Double-Stranded Breaks / DSB), menghasilkan produk tanaman non-transgenik (bebas sisipan gen asing) yang aman bagi lingkungan dan regulasi.",
        "<b>Integrasi Data Spasial Risiko Kekeringan BNPB InaRISK:</b> Mengaitkan koordinat geografis nyata sawah petani (resolusi 100 meter) langsung dengan varietas padi lokal yang paling adaptif dan strategi rekayasa genetik spesifik lokasi."
    ]
    story.append(make_bullet_list(pilar_items))
    story.append(Spacer(1, 2))

    story.append(make_callout(
        "Nilai Plus untuk Presentasi Riset",
        "Saat mempresentasikan proyek ini, tekankan bahwa pendekatan ini <b>bukan produk transgenik (GMO) klasik</b>. Kita tidak menyisipkan DNA bakteri atau gen dari spesies lain ke dalam genom padi. Kita melakukan <i>precision base editing</i> (meniru mutasi alel alami varietas unggul tradisional) sehingga tanaman yang dihasilkan secara hukum dan biosekuriti dikategorikan sebagai produk pemuliaan mutasi terarah non-transgenik."
    ))

    story.append(P("2. Memulai Aplikasi & Anatomi Antarmuka Studio Web", h1))
    story.append(P(
        "Aplikasi PhytoAI-Genetics dirancang dengan filosofi antarmuka satu layar penuh (<i>Single Page Application</i>) yang responsif, menggunakan palet visual bertema alam ilmiah (Google Sans Flex, warna hijau zamrud <code>#059669</code>, dan aksen biru sitogenetika). Studio ini menyajikan 8 tab navigasi utama yang dapat diakses seketika:",
        body_justify
    ))

    nav_table_data = [
        [P("<b>Tab Navigasi</b>", table_header), P("<b>Fungsi Utama</b>", table_header), P("<b>Target Output Riset</b>", table_header)],
        [
            P("<b>1. Peta Geospasial & InaRISK</b>", table_cell),
            P("Peta interaktif GIS InaRISK BNPB (100m) dan alat input koordinat GPS bebas.", table_cell),
            P("Skor bahaya kekeringan lokasi, jarak ke sentra padi, rekomendasi kultivar adaptif.", table_cell)
        ],
        [
            P("<b>2. PhytoAI: Prediksi Mutasi</b>", table_cell),
            P("Simulasi mutasi titik tunggal (mis. V79I, P168L) via model Transformer pLM.", table_cell),
            P("Skor log-likelihood &Delta;LLR, estimasi &Delta;&Delta;G, efek fungsional (Gain-of-Function/DREB2A-CA).", table_cell)
        ],
        [
            P("<b>3. In Silico DMS Matrix</b>", table_cell),
            P("Pemindaian komparatif 20 asam amino pada domain AP2/ERF dan NRD degron.", table_cell),
            P("Matriks heatmap skor toleransi per residu, identifikasi mutasi terbaik (<i>Best Mutation</i>).", table_cell)
        ],
        [
            P("<b>4. Profil Kultivar Padi Lokal</b>", table_cell),
            P("Eksplorasi haplotipe DREB2A plasma nutfah (Gogo Jatiluhur, Salumpikit, Rojolele).", table_cell),
            P("Pemetaan SNP alami, perbandingan ekspresi mRNA saat kekeringan dibanding IR64.", table_cell)
        ],
        [
            P("<b>5. CRISPR Base Editing Studio</b>", table_cell),
            P("Generator otomatis protokol pengeditan basa DNA (CBE/ABE) tanpa memotong untai ganda.", table_cell),
            P("Sekuens 20-nt protospacer, deamination window (basa 4–8), filter terminator TTTT.", table_cell)
        ],
        [
            P("<b>6. Gen Regulon Kekeringan</b>", table_cell),
            P("Katalog terkurasi 10 gen target rekayasa padi (OsDREB2A, SWEET14, DEP1, Badh2, dst).", table_cell),
            P("Lokus kromosom, nomor Gene ID resmi, strategi perakitan ganda (<i>multiplexing</i>).", table_cell)
        ],
        [
            P("<b>7. Live NCBI Datasets v2</b>", table_cell),
            P("Koneksi langsung ke server National Center for Biotechnology Information (AS).", table_cell),
            P("Ekstraksi live sekuens CDS (825 bp) dan Protein (274 AA), tombol unduh arsip ZIP.", table_cell)
        ],
        [
            P("<b>8. Dokumentasi & Formula</b>", table_cell),
            P("Modul landasan teori, rumus matematika biofisika, contoh soal hitungan, dan deployment.", table_cell),
            P("Referensi metodologi saintifik terstandardisasi untuk publikasi jurnal dan tesis.", table_cell)
        ]
    ]

    t_nav = Table(nav_table_data, colWidths=[115, 195, 205], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    story.append(t_nav)

    # Pindah Halaman Bersih ke Halaman 3
    story.append(PageBreak())

    # ==================== HALAMAN 3: BAB 3 (ALUR KERJA SPASIAL) ====================
    story.append(P("3. Alur Kerja 1: Eksplorasi Geospasial InaRISK & Penilaian Titik Koordinat Sawah", h1))
    story.append(P(
        "Alur kerja penelitian dimulai dari lapangan. Sebelum merekayasa susunan molekuler tanaman, seorang pemulia tanaman atau bioteknolog perlu mengetahui profil cekaman agroklimat spesifik di lokasi tanam yang ditargetkan.",
        body_justify
    ))

    story.append(P("Langkah Pengoperasian Fitur Peta Spasial:", h2))
    peta_steps = [
        "<b>Buka Tab 1 ('Peta Risiko Kekeringan & Agroekosistem'):</b> Di layar utama akan tampil peta interaktif wilayah kedaulatan Indonesia yang ditenagai oleh Leaflet GIS Engine dan terhubung dengan layer ArcGIS ImageServer BNPB InaRISK beresolusi 100 meter.",
        "<b>Pilih Wilayah Sentra Padi:</b> Klik salah satu tombol cepat yang tersedia di atas peta, seperti <i>'Demak & Pati'</i>, <i>'NTT Semi-Arid'</i>, <i>'NTB Gora'</i>, atau <i>'Gunungkidul Karst'</i>. Peta akan otomatis melakukan animasi terbang (<i>flyTo</i>) ke sentra sawah tersebut dan menampilkan lingkaran radius risiko berwarna merah pekat.",
        "<b>Uji Coba Titik Koordinat Bebas:</b> Pada panel kanan, masukkan nilai garis lintang (Latitude) dan garis bujur (Longitude) lahan sawah mana pun di Indonesia, lalu klik <b>'Analisis Koordinat Bebas'</b>.",
        "<b>Membaca Hasil Analisis:</b> Sistem secara otomatis menjalankan kalkulasi geodesik Haversine untuk mencari klaster iklim terdekat, menghitung jarak riil (km), mengidentifikasi skor indeks bahaya InaRISK (skala 0.0 – 1.0), tipe agroekosistem lahan, serta memunculkan rekomendasi varietas padi lokal dan strategi mutasi DREB2A yang paling mendesak."
    ]
    story.append(make_numbered_list(peta_steps))
    story.append(Spacer(1, 1))

    # Gallery Dua Gambar Lapangan (100% Proporsional target_width=350 -> height=195.35)
    story.append(make_figure(
        "indonesia_rice_agroecosystem.png",
        "<b>Gambar 1:</b> Lanskap pengujian agroekosistem sawah rawan kekeringan dengan sensor mikroklimat IoT (InaRISK &ge; 0.75).",
        target_width=350
    ))

    story.append(make_figure(
        "rice_drought_vertisol_field.png",
        "<b>Gambar 2:</b> Kondisi tanah lempung vertisol retak sedalam 30–50 cm di Pantura Jawa vs ketahanan malai padi teredit OsDREB2A.",
        target_width=350
    ))

    story.append(P(
        "<b>Interpretasi Kasus Lapangan Riil:</b> Ketika koordinat <b>-6.8944, 110.6386</b> (Kabupaten Demak) dianalisis, sistem mendeteksi agroekosistem <i>Sawah Tadah Hujan Vertisol Berlempung Berat</i> dengan indeks bahaya <b>0.82 (Tinggi)</b>. Tanah vertisol mengalami rekahan lebar saat kadar air merosot di bawah -50 kPa yang memutus perakaran padi biasa. Rekomendasi sistem adalah introduksi mutasi <b>P168L</b> pada varietas <b>Inpari 32 HDB</b> agar tanaman mengaktifkan proteksi turgor sebelum fase bunting terganggu.",
        body_justify
    ))

    # Pindah Halaman Bersih ke Halaman 4
    story.append(PageBreak())

    # ==================== HALAMAN 4: BAB 4 & BAB 5 ====================
    story.append(P("4. Alur Kerja 2: Prediksi Mutasi OsDREB2A dengan Transformer pLM", h1))
    story.append(P(
        "Setelah menentukan wilayah dan target mutasi di Tab 1, langkah berikutnya adalah memvalidasi kelayakan biofisika mutasi tersebut di <b>Tab 2 ('PhytoAI: Prediksi Mutasi OsDREB2A')</b> menggunakan model representasi bahasa protein (<i>Protein Language Model / pLM</i>).",
        body_justify
    ))

    story.append(P("Panduan Langkah Input & Prediksi:", h2))
    pred_steps = [
        "Masukkan notasi mutasi pada kolom <b>Notasi Mutasi</b> menggunakan format standar biologis (Asam Amino Asli &rarr; Nomor Posisi &rarr; Asam Amino Mutan). Contoh: <code>P168L</code>, <code>V79I</code>, <code>S167A</code>, atau <code>E166K</code>.",
        "Pilih varietas padi acuan pada menu drop-down Select2, misalnya <b>Inpari 32 HDB</b>, <b>Rojolele</b>, atau <b>Gogo Jatiluhur</b>.",
        "Pilih wilayah target kekeringan (mis. <i>Pantura Jawa Tengah / Demak-Pati</i>).",
        "Klik tombol hijau <b>'Jalankan Prediksi Transformer pLM'</b>. Sistem langsung mengevaluasi sekuens acuan protein OsDREB2A (274 AA) dan menyajikan kartu hasil komprehensif."
    ]
    story.append(make_numbered_list(pred_steps))
    story.append(Spacer(1, 1))

    # Callout Parameter Output Transformer dengan List Rapi
    output_bullets = [
        "<b>Skor Transformer (&Delta;LLR):</b> Nilai selisih probabilitas log-likelihood log[P(mutan)/P(wildtype)]. Jika bernilai <b>positif (&gt; 0)</b>, mutasi disukai secara evolusi dan meningkatkan stabilitas protein. Jika <b>negatif (&lt; 0)</b>, mutasi bersifat merusak (destruktif).",
        "<b>Perubahan Energi Bebas (&Delta;&Delta;G):</b> Dihitung via kalibrasi biokimia. &Delta;&Delta;G &gt; 0 menandakan peningkatan afinitas ikatan ke DNA promotor.",
        "<b>Efek Fungsional:</b> Mengkategorikan apakah mutasi memicu <i>Constitutive Activation (DREB2A-CA)</i>, <i>Gain-of-Function</i>, atau <i>Loss-of-Function</i>.",
        "<b>Kelayakan Base Editor:</b> Menampilkan enzim pengedit basa yang cocok (CBE vs ABE) dan perubahan kodon asam amino spesifik."
    ]
    story.append(make_callout(
        "Cara Menafsirkan Parameter Output Transformer:",
        output_bullets
    ))

    # BAB 5: DEEP MUTATIONAL SCANNING
    story.append(P("5. Alur Kerja 3: In Silico Deep Mutational Scanning (DMS)", h1))
    story.append(P(
        "Deep Mutational Scanning (DMS) mengeksplorasi seluruh ruang kemungkinan mutasi pada satu domain fungsional secara paralel. Daripada menguji mutasi satu per satu, fitur di <b>Tab 3 ('In Silico Deep Mutational Scanning')</b> memindai semua 20 jenis asam amino standar di setiap posisi residu secara simultan.",
        body_justify
    ))

    story.append(P("Langkah Pengoperasian DMS:", h2))
    dms_steps = [
        "<b>Pindai Domain AP2/ERF:</b> Klik tombol <i>'Pindai Domain AP2/ERF (70-90)'</i> untuk mengevaluasi 21 posisi asam amino yang berinteraksi langsung dengan lekukan heliks DNA motif DRE/CRT (5'-GCCGAC-3').",
        "<b>Pindai Domain NRD Degron:</b> Klik tombol <i>'Pindai Domain NRD Degron (160-180)'</i> untuk mengevaluasi daerah penentu stabilitas protein terhadap degradasi enzim proteasom."
    ]
    story.append(make_bullet_list(dms_steps))
    story.append(Spacer(1, 1))

    story.append(make_figure(
        "rice_dms_landscape.png",
        "<b>Gambar 3:</b> Visualisasi molekuler 3D konformasi domain AP2/ERF dan pendaran awan data skor fitness Deep Mutational Scanning.",
        target_width=350
    ))

    story.append(P(
        "Setelah pemindaian selesai, tabel interaktif menampilkan skor &Delta;LLR untuk masing-masing dari 20 asam amino substitusi dengan gradasi hijau cerah (skor positif) hingga merah (skor negatif). Kolom <b>Mutasi Terbaik (<i>Best Mutation</i>)</b> merangkum varian paling unggul di posisi tersebut (contoh: di posisi 79, varian terbaik adalah <code>V79I</code> dengan skor +1.74; sedangkan <code>V79A</code> merusak pengikatan DNA dengan skor -2.85).",
        body_justify
    ))

    # Pindah Halaman Bersih ke Halaman 5
    story.append(PageBreak())

    # ==================== HALAMAN 5: BAB 6 & BAB 7 ====================
    story.append(P("6. Alur Kerja 4: Analisis Haplotipe Plasma Nutfah Padi Lokal", h1))
    story.append(P(
        "Indonesia kaya akan plasma nutfah padi lokal yang telah beradaptasi ratusan tahun terhadap cekaman abiotik. Di <b>Tab 4 ('Kultivar Padi Lokal Indonesia')</b>, peneliti dapat mempelajari keragaman haplotipe alami gen <i>OsDREB2A</i> dari berbagai varietas tradisional kepulauan nusantara dibandingkan dengan varietas acuan global.",
        body_justify
    ))

    cultivar_table_data = [
        [P("<b>Varietas / Asal</b>", table_header), P("<b>Tipe & Fenotipe</b>", table_header), P("<b>Haplotipe Mutasi DREB2A Kunci</b>", table_header), P("<b>Ekspresi Relatif mRNA</b>", table_header)],
        [
            P("<b>Gogo Jatiluhur</b><br/>(Jawa Barat)", table_cell),
            P("Padi Gogo Lahan Kering Masam; Sangat Toleran Kekeringan", table_cell),
            P("• Duplikasi promotor (+45 bp DRE)<br/>• SNP A412C (Thr138Pro pada NRD)<br/>• SNP G580A (Val194Met)", table_cell),
            P("<b>4.8&times;</b> lipat vs IR64 pada 14 hari tanpa air", table_cell_center)
        ],
        [
            P("<b>Salumpikit</b><br/>(Sulawesi)", table_cell),
            P("Padi Gogo Tradisional; Toleran Cekaman Osmotik Tinggi", table_cell),
            P("• SNP C248T (Ala83Val pada domain AP2)<br/>• Silent SNP C522T", table_cell),
            P("<b>5.2&times;</b> lipat pada defisit air tanah (-50 kPa)", table_cell_center)
        ],
        [
            P("<b>Rojolele</b><br/>(Jawa Tengah)", table_cell),
            P("Padi Sawah Landrace Bulu; Kualitas Beras Premium, Peka Kering", table_cell),
            P("• Haplotipe liar sekuens Nipponbare standar tanpa SNP protektif", table_cell),
            P("<b>1.1&times;</b> (Rentan puso jika saluran irigasi kering)", table_cell_center)
        ],
        [
            P("<b>Nagina 22 (N22)</b><br/>(India / Aus Group)", table_cell),
            P("Acuan Internasional Heat & Drought Tolerant (>42°C)", table_cell),
            P("• Delesi alami 12 AA pada domain NRD (DREB2A-CA alami)<br/>• SNP T255G (Ile85Met)", table_cell),
            P("Stabil terus-menerus tanpa didegradasi cepat oleh proteasom", table_cell_center)
        ]
    ]

    t_cultivar = Table(cultivar_table_data, colWidths=[95, 135, 185, 100], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    story.append(t_cultivar)

    story.append(make_figure(
        "rice_cultivar_panicle.png",
        "<b>Gambar 4:</b> Makro malai dan bulir padi plasma nutfah lokal Indonesia yang memperlihatkan keragaman fenotipe gabah.",
        target_width=280
    ))

    # BAB 7: CRISPR BASE EDITING
    story.append(P("7. Alur Kerja 5: Desain CRISPR Base Editing (CBE & ABE) Presisi", h1))
    story.append(P(
        "Setelah mutasi ideal terbukti secara bioinformatika, <b>Tab 5 ('CRISPR Base Editing Studio')</b> mengubah desain tersebut menjadi rancangan laboratorium biologi molekuler yang konkret dan siap sintesis oligo.",
        body_justify
    ))

    story.append(make_figure(
        "crispr_rice_editing.png",
        "<b>Gambar 5:</b> Kompleks molekuler nCas9 berfusi dengan enzim deaminase sitidin (CBE) yang melakukan pertukaran basa C ke T.",
        target_width=280
    ))

    story.append(P("Parameter Kritis Perancangan Guide RNA Padi:", h2))
    crispr_params = [
        "<b>Pemilihan Sistem Enzim:</b> Pilih <b>Cytidine Base Editor (CBE)</b> untuk mutasi transisi C&bull;G &rarr; T&bull;A (misalnya membuat kodon leusin dari prolin pada P168L). Pilih <b>Adenine Base Editor (ABE)</b> untuk mutasi A&bull;T &rarr; G&bull;C (misalnya membuat kodon isoleusin dari valin pada V79I).",
        "<b>Jendela Deaminasi (<i>Editing Window</i>):</b> Basa target harus berada di antara posisi <b>ke-4 hingga ke-8</b> dihitung dari ujung 5' protospacer (dengan posisi 1 adalah nukleotida terdepan dan basa 21–23 adalah motif PAM SpCas9 <code>NGG</code>).",
        "<b>Eliminasi Motif Bahaya Terminator Pol III (<code>TTTT</code>):</b> Pada kloning vektor tanaman padi (seperti plasmid <code>pRGEB32</code> atau <code>pCAMBIA1300</code>), ekspresi gRNA digerakkan oleh promotor RNA Polimerase III (promotor snRNA padi U3 atau U6). Jika sekuens protospacer mengandung deretan 4 timin (<code>TTTT</code>), enzim Pol III menghentikan transkripsi dini, menyebabkan gRNA terpotong dan gagal total di lab basah. Algoritma kami secara otomatis menyaring dan mengeliminasi kandidat gRNA bermotif <code>TTTT</code>."
    ]
    story.append(make_numbered_list(crispr_params))

    # Pindah Halaman Bersih ke Halaman 6
    story.append(PageBreak())

    # ==================== HALAMAN 6: BAB 8 & BAB 9 ====================
    story.append(P("8. Alur Kerja 6: Katalog 10 Gen Regulon Ketahanan Abiotik Padi", h1))
    story.append(P(
        "Kekeringan di sawah sering kali diiringi oleh salinitas tanah pesisir atau serangan bakteri hawar daun saat musim hujan terlambat. Di <b>Tab 6 ('Regulon Toleransi Kekeringan & Gen Target Padi')</b>, platform menyajikan 10 gen target rekayasa genetika padi paling strategis acuan genom Nipponbare IRGSP-1.0:",
        body_justify
    ))

    story.append(make_figure(
        "rice_stress_regulon.png",
        "<b>Gambar 6:</b> Penampang sel daun padi: modulasi regulon stomata dan translokasi sinyal fitohormon ABA penahan kekeringan.",
        target_width=350
    ))

    story.append(P(
        "Peneliti dapat menggabungkan rekayasa genetik multipel (<i>multiplex genome editing</i>), misalnya mengombinasikan mutasi aktivasi <b>OsDREB2A</b> (toleransi kekeringan) dengan inaktivasi promotor <b>OsSWEET14</b> (tahan hawar daun bakteri) dan penonaktifan transporter <b>OsNramp5</b> (mencegah penyerapan racun kadmium ke beras) dalam satu kali transformasi tanaman via <i>Agrobacterium tumefaciens</i>.",
        body_justify
    ))

    # BAB 9: LIVE NCBI DATASETS V2
    story.append(P("9. Alur Kerja 7: Integrasi Live NCBI Datasets v2 REST API", h1))
    story.append(P(
        "Di <b>Tab 7 ('Integrasi Live NCBI Datasets')</b>, pengguna dapat berinteraksi langsung dengan pangkalan data genomik resmi dunia. Klik tombol biru <b>'Ekstrak Sekuens Live'</b> untuk memicu pemanggilan API asinkronus ke server NCBI Datasets v2. Sistem akan mengekstrak sekuens DNA pengkode CDS (825 bp) dan sekuens asam amino protein (274 AA) secara utuh, lengkap dengan tombol instan untuk mengunduh arsip paket ZIP resmi berisi berkas FASTA genomik, GFF3, dan metadata anotasi.",
        body_justify
    ))

    story.append(make_figure(
        "rice_genomics_workstation.png",
        "<b>Gambar 7:</b> Stasiun kerja komputasi genomik padi berkecepatan tinggi yang mengonsumsi REST API resmi NCBI Datasets v2.",
        target_width=350
    ))

    story.append(P(
        "Fitur live sync ini memastikan seluruh analisis genomik padi yang dilakukan selalu mengacu pada rilis anotasi NCBI RefSeq dan Ensembl Plants paling mutakhir, menghindari ketidaksesuaian nomor koordinat genomik saat mempersiapkan manuskrip publikasi internasional.",
        body_justify
    ))

    # Pindah Halaman Bersih ke Halaman 7
    story.append(PageBreak())

    # ==================== HALAMAN 7: BAB 10 (MEKANISME REKAYASA GENETIKA) ====================
    story.append(P("10. Mekanisme Molekuler & Protokol Rekayasa Genetika (In Silico &rarr; In Vitro &rarr; In Planta)", h1))
    story.append(P(
        "Rekayasa genetika pada platform ini dirancang dengan standar biologi molekuler presisi tinggi untuk menghasilkan varietas padi toleran kekeringan yang <b>bebas dari sisipan gen asing (non-transgenik / transgene-free)</b>. Alur hilirisasi laboratorium basah terbagi ke dalam tiga fase sekuensial yang terdefinisi secara ketat:",
        body_justify
    ))

    # FASE 1: IN SILICO
    story.append(P("A. Fase 1: In Silico (Bioinformatika Komputasi & Desain gRNA)", h2))
    story.append(P(
        "Platform PhytoAI-Genetics memindai sekuens DNA gen <i>OsDREB2A</i> (NCBI Gene ID: <code>4324418</code>). Sistem mengidentifikasi kodon Prolin ke-168 (<code>CCG</code>) pada domain NRD degron dan Valin ke-79 (<code>GTT</code>) pada domain AP2/ERF. Enzim Cytidine Base Editor (CBE) atau Adenine Base Editor (ABE) dipilih secara otomatis, dilanjutkan dengan perancangan protospacer 20-nt yang memiliki jendela deaminasi ideal pada nukleotida ke-4 hingga ke-8 dari motif PAM SpCas9 (<code>5'-NGG-3'</code>), seraya membuang seluruh calon oligonukleotida yang memuat motif terminator Pol III (<code>TTTT</code>).",
        body_justify
    ))

    # FASE 2: IN VITRO DENGAN NUMBERED LIST RAPI
    story.append(P("B. Fase 2: In Vitro (Konstruksi Vektor Biner & Transformasi Agrobacterium)", h2))
    in_vitro_items = [
        "<b>Sintesis & Aniling Oligo:</b> Sepasang oligonukleotida DNA sintetik untai tunggal (sensus dan antisense) disintesis dengan ujung kohesif (overhang) 4-bp restriksi enzim <i>BsaI</i>.",
        "<b>Ligasi Plasmid Vektor Tanaman:</b> Oligo diligasikan ke dalam plasmid biner tanaman padi standar, yaitu <b>pRGEB32</b> atau <b>pH-nCas9-CBE</b>. Pada vektor ini, kaset sgRNA digerakkan oleh promotor spesifik padi <i>OsU3</i>, sedangkan fusi nCas9(D10A)-deaminase digerakkan oleh promotor <i>Ubiquitin-1</i> padi.",
        "<b>Elektroporasi ke Agrobacterium:</b> Plasmid rekombinan diintroduksikan ke dalam sel kompeten <i>Agrobacterium tumefaciens</i> galur virulen super <b>EHA105</b> atau <b>LBA4404</b>."
    ]
    story.append(make_numbered_list(in_vitro_items))
    story.append(Spacer(1, 1))

    # FASE 3: IN PLANTA DENGAN NUMBERED LIST RAPI
    story.append(P("C. Fase 3: In Planta (Kokultivasi Kalus Padi, Regenerasi, & Segregasi Non-GMO)", h2))
    in_planta_items = [
        "<b>Induksi Kalus Embriogenik:</b> Biji matang padi varietas lokal (Inpari 32 HDB, Rojolele, atau Gogo Jatiluhur) disterilisasi permukaan dan ditumbuhkan pada media induksi kalus NB (mengandung 2 mg/L 2,4-D) selama 21 hari hingga terbentuk kalus embriogenik kompak berwarna kuning cerah.",
        "<b>Inokulasi & Kokultivasi:</b> Kalus diinokulasi suspensi <i>Agrobacterium</i> (kepadatan OD600 = 0.3) dengan penambahan 100 &mu;M asetosiringon selama 3 hari dalam kondisi gelap.",
        "<b>Seleksi Higromisin & Regenerasi Planlet:</b> Kalus dipindahkan ke media seleksi higromisin (50 mg/L) + sefotaksim (250 mg/L) selama 3 putaran seleksi. Kalus resisten dipindahkan ke media regenerasi tunas dan perakaran.",
        "<b>Validasi Genotipe Generasi T0:</b> DNA diekstraksi dari daun planlet hijau; amplifikasi PCR dan sekuensing Sanger membuktikan konversi kodon <code>CCG</code> &rarr; <code>CTG</code> (mutasi P168L).",
        "<b>Segregasi Bebas Transgen Generasi T1:</b> Pada keturunan generasi T1, tanaman diselfing; hukum segregasi Mendel akan memisahkan kaset T-DNA plasmid. Sekitar 25% galur T1 akan membawa mutasi stabil <i>OsDREB2A</i> namun <b>bersih total dari materi gen asing plasmid (100% Transgene-Free / Non-GMO)</b>."
    ]
    story.append(make_numbered_list(in_planta_items))
    story.append(Spacer(1, 2))

    story.append(make_callout(
        "Alur Hilirisasi Non-Transgenik",
        "Dengan memilih teknologi CRISPR Base Editing dan memanfaatkan segregasi Mendel pada generasi T1, benih padi yang didistribusikan ke petani tidak memuat DNA asing sama sekali. Hal ini memangkas waktu pengujian regulasi biosafety hingga bertahun-tahun serta membebaskan petani dari royalti teknologi transgenik multinasional."
    ))

    # Pindah Halaman Bersih ke Halaman 8
    story.append(PageBreak())

    # ==================== HALAMAN 8: BAB 11 & BAB 12 ====================
    story.append(P("11. Spesifikasi 4 Model Komputasi, Biofisika & Kecerdasan Buatan (AI) yang Digunakan", h1))
    story.append(P(
        "Platform PhytoAI-Genetics mengintegrasikan empat model matematis multidisipliner yang saling melengkapi:",
        body_justify
    ))

    story.append(P("Model 1: Protein Language Model (pLM Transformer)", h2))
    story.append(P(
        "Model representasi Transformer encoder yang dilatih menggunakan objektif <i>Masked Language Modeling (MLM)</i> pada jutaan sekuens protein tanaman UniRef50/100. Model mengevaluasi probabilitas kondisional residu asam amino terhadap konteks spasial sekuens protein sekelilingnya:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Formula Log-Likelihood Ratio:</b> &Delta;LLR(x<sub>i</sub> &rarr; m) = log P(x<sub>i</sub> = m | x<sub>-i</sub>) - log P(x<sub>i</sub> = w | x<sub>-i</sub>)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Kalibrasi Energi Bebas Lipatan:</b> &Delta;&Delta;G &approx; -&alpha; &middot; &Delta;LLR + &beta; (dalam satuan kcal/mol).<br/>"
        "Nilai &Delta;LLR positif menandakan mutasi disukai secara evolusioner (stabil / toleran), sedangkan skor negatif menandakan mutasi destruktif.",
        body_justify
    ))

    story.append(P("Model 2: Termodinamika Dupleks Asam Nukleat (SantaLucia Nearest-Neighbor)", h2))
    story.append(P(
        "Menghitung temperatur leleh (Melting Temperature / T<sub>m</sub>) hibridisasi antara sgRNA 20-nt dengan DNA genomik padi berdasarkan model termodinamika pasangan basa tetangga terdekat:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Formula SantaLucia:</b> T<sub>m</sub> = [&Delta;H&deg; / (&Delta;S&deg; + R &middot; ln(C<sub>t</sub> / 4))] - 273.15 + 16.6 &middot; log<sub>10</sub>[Na<sup>+</sup>]<br/>"
        "Di mana &Delta;H&deg; dan &Delta;S&deg; adalah entalpi dan entropi kumulatif doublet, R = 1.987&times;10<sup>-3</sup> kcal/(mol&middot;K), C<sub>t</sub> = 0.25 &mu;M, dan [Na<sup>+</sup>] = 0.05 M buffer. Kriteria lolos: T<sub>m</sub> berada pada rentang 55°C – 68°C dengan GC content 40% – 60%.",
        body_justify
    ))

    story.append(P("Model 3: Geodesik Spasial Haversine & Kalibrasi Risiko InaRISK BNPB", h2))
    story.append(P(
        "Menghitung jarak lengkung lingkaran besar pada elipsoid bumi WGS-84 antara koordinat GPS pengguna (&phi;<sub>1</sub>, &lambda;<sub>1</sub>) dengan klaster sentra padi terdampak (&phi;<sub>2</sub>, &lambda;<sub>2</sub>):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Formula Haversine:</b> a = sin<sup>2</sup>(&Delta;&phi;/2) + cos(&phi;<sub>1</sub>)&middot;cos(&phi;<sub>2</sub>)&middot;sin<sup>2</sup>(&Delta;&lambda;/2); &nbsp; d = 2 &middot; R &middot; arcsin(&radic;a) (R = 6.371 km).<br/>"
        "Data dikalibrasi ke layer ArcGIS ImageServer BNPB InaRISK resolusi 100m untuk mengklasifikasikan kelas bahaya: Ekstrem (&ge;0.85), Tinggi (0.70–0.85), Sedang (0.50–0.70), atau Rendah (&lt;0.50).",
        body_justify
    ))

    story.append(P("Model 4: Probabilitas Jendela Deaminasi Base Editor & Filter Terminasi Pol III", h2))
    story.append(P(
        "Memodelkan probabilitas efisiensi konversi kimiawi deaminase (CBE/ABE) yang terkonsentrasi pada nukleotida ke-4 hingga ke-8 dari ujung 5' protospacer (di mana basa 21–23 adalah motif PAM <code>NGG</code>):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Probabilitas Deaminasi:</b> P<sub>edit</sub>(i) = 0.85 – 0.95 untuk i &isin; [4, 8]; P<sub>edit</sub>(i) &lt; 0.05 di luar jendela tersebut.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Filter Pol III:</b> Jika sekuens protospacer memuat motif <code>TTTT</code>, status dinyatakan <i>Waspada / Gugur</i> karena memicu terminasi prematur transkripsi RNA Polimerase III pada promotor U3/U6 padi.",
        body_justify
    ))

    # BAB 12: ARSITEKTUR & TECH STACK
    story.append(P("12. Arsitektur Perangkat Lunak & Spesifikasi Lengkap Tech Stack", h1))
    story.append(P(
        "Sistem dibangun secara modular dengan standar rekayasa perangkat lunak modern untuk menjamin konkurensi tinggi, keamanan data, dan kemudahan deployment di server riset:",
        body_justify
    ))

    tech_table_data = [
        [P("<b>Lapisan Sistem</b>", table_header), P("<b>Teknologi / Pustaka</b>", table_header), P("<b>Peran & Fungsionalitas Kunci</b>", table_header)],
        [
            P("<b>Backend Core</b>", table_cell),
            P("Python 3.11, FastAPI 0.115, Uvicorn (multi-worker)", table_cell),
            P("REST API asinkronus berkecepatan tinggi, dependency injection, auto-generated Swagger UI di <code>/docs</code>.", table_cell)
        ],
        [
            P("<b>Klien HTTP & I/O</b>", table_cell),
            P("HTTPX 0.27 (AsyncClient + Lifespan Connection Pool)", table_cell),
            P("Connection pooling (max 20 koneksi TCP), konsumsi API resmi NCBI Datasets v2 dan ArcGIS ImageServer BNPB.", table_cell)
        ],
        [
            P("<b>Skema & Validasi Data</b>", table_cell),
            P("Pydantic v2.6, Pydantic-Settings 2.2", table_cell),
            P("Enforcement tipe data ketat DTO, validasi batas panjang sekuens DNA (maks 100.000 nt), isolasi environment <code>.env</code>.", table_cell)
        ],
        [
            P("<b>Keamanan & Rate Limit</b>", table_cell),
            P("In-Memory Sliding Window Middleware, W3C CORS Strict", table_cell),
            P("Perlindungan DoS endpoint komputasi berat (30 req/min), CORS credentials isolation, proteksi SSL/TLS.", table_cell)
        ],
        [
            P("<b>Frontend UI/UX</b>", table_cell),
            P("Single Page Application, Google Sans Flex, JetBrains Mono", table_cell),
            P("Antarmuka terang responsif, tipografi saintifik modern, integrasi komponen visual molekuler beresolusi tinggi.", table_cell)
        ],
        [
            P("<b>Geospasial GIS</b>", table_cell),
            P("Leaflet 1.9.4, Esri-Leaflet 3.0.12", table_cell),
            P("Rendering peta batas wilayah Indonesia, overlay layer bahaya kekeringan InaRISK 100m, reverse geocoding koordinat.", table_cell)
        ],
        [
            P("<b>Komponen Interaktif</b>", table_cell),
            P("Select2 4.1, SweetAlert2 11, jQuery 3.7.1", table_cell),
            P("Pencarian cerdas dropdown kultivar dan wilayah padi, modal notifikasi analitik biofisika interaktif.", table_cell)
        ],
        [
            P("<b>Testing & DevOps</b>", table_cell),
            P("Pytest 8.4, Docker (python:3.11-slim), Docker Compose", table_cell),
            P("37 automated test suite (100% lulus), container aman dengan user non-root <code>appuser</code>, healthcheck berkala.", table_cell)
        ]
    ]

    t_tech = Table(tech_table_data, colWidths=[95, 145, 275], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    story.append(t_tech)

    # Pindah Halaman Bersih ke Halaman 9
    story.append(PageBreak())

    # ==================== HALAMAN 9: BAB 13 (PENGUJIAN & VALIDASI SISTEM) ====================
    story.append(P("13. Metodologi Pengujian, Verifikasi Komputasi & Validasi Biologis Molekuler", h1))
    story.append(P(
        "Untuk menjamin integritas saintifik dan keandalan rekayasa, platform PhytoAI-Genetics menerapkan metodologi "
        "Verifikasi &amp; Validasi (V&amp;V) dua lapis yang terpadu: pengujian komputasi otomatis (<i>automated software testing</i>) "
        "pada lapisan perangkat lunak dan protokol validasi bertingkat pada lapisan laboratorium basah (<i>wet-lab pipeline</i>):",
        body_justify
    ))

    story.append(P("A. Pengujian Otomatis Perangkat Lunak (Automated Software Testing & Pytest Suite)", h2))
    story.append(P(
        "Pengujian komputasi mencakup 40 skenario pengujian unit dan integrasi otomatis menggunakan kerangka kerja <code>pytest</code> "
        "(dengan 37 unit test passed 100% dan 3 live NCBI test). Eksekusi pengujian dijalankan via terminal riset:",
        body_justify
    ))

    # Terminal Command Box
    cmd_box = [
        [P("<code>$ ./.venv/bin/pytest tests/ -v &nbsp;&nbsp;# Eksekusi 37 Unit Tests Otomatis (100% Lulus dalam 0.57s)</code>", ParagraphStyle('Cmd', fontName='SegoeUI', fontSize=7.4, leading=10, textColor=PRIMARY_DARK))]
    ]
    t_cmd = Table(cmd_box, colWidths=[printable_width], style=[
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ])
    story.append(t_cmd)
    story.append(Spacer(1, 3))

    test_matrix_data = [
        [P("<b>Modul Pengujian</b>", table_header), P("<b>Kasus Uji</b>", table_header), P("<b>Parameter Kritis & Aspek yang Divalidasi</b>", table_header), P("<b>Status & Benchmark</b>", table_header)],
        [
            P("<code>tests/test_phytoai.py</code>", table_cell),
            P("<b>19 Tests</b>", table_cell_center),
            P("Prediksi Transformer (&Delta;LLR) mutasi P168L (+1.85), V79I (+1.74), dan V79A (-2.85); matriks saturasi DMS 20 asam amino; geodesik Haversine InaRISK klaster Demak (0.82) dan NTT; haplotipe 4 varietas lokal.", table_cell),
            P("<font color='#059669'><b>100% Lulus</b></font><br/>(0.28s)", table_cell_center)
        ],
        [
            P("<code>tests/test_crispr.py</code>", table_cell),
            P("<b>7 Tests</b>", table_cell_center),
            P("Deteksi protospacer SpCas9 (NGG) & Cas12a (TTTV); eliminasi wajib terminator Pol III (motif TTTT); termodinamika SantaLucia Tm (55°C–68°C, GC 40–60%); penolakan batas panjang sekuens (&lt;20 nt & &gt;100.000 nt).", table_cell),
            P("<font color='#059669'><b>100% Lulus</b></font><br/>(0.12s)", table_cell_center)
        ],
        [
            P("<code>tests/test_targets.py</code>", table_cell),
            P("<b>4 Tests</b>", table_cell_center),
            P("Integritas katalog 10 gen regulon padi IRGSP-1.0; pemetaan lokus kromosom, query simbolik gen, dan validasi keabsahan nomor NCBI Gene ID resmi (misal Gene ID 4324418 untuk OsDREB2A).", table_cell),
            P("<font color='#059669'><b>100% Lulus</b></font><br/>(0.05s)", table_cell_center)
        ],
        [
            P("<code>tests/test_api.py</code>", table_cell),
            P("<b>7 Tests</b>", table_cell_center),
            P("Kesiapan server (/api/health, /api/info); isolasi header keamanan W3C CORS; proteksi in-memory sliding window rate limiting (30 req/min); penanganan exception penolakan notasi mutasi abnormal (HTTP 400).", table_cell),
            P("<font color='#059669'><b>100% Lulus</b></font><br/>(0.08s)", table_cell_center)
        ],
        [
            P("<code>tests/test_live_integration.py</code>", table_cell),
            P("<b>3 Tests</b>", table_cell_center),
            P("Koneksi HTTP asinkronus ke server REST API resmi NCBI Datasets v2; parsing laporan genomik, ekstraksi sekuens CDS pengkode (825 bp), dan sekuens asam amino protein lengkap (274 AA).", table_cell),
            P("<font color='#0284c7'><b>Terverifikasi</b></font><br/>(Live Integration)", table_cell_center)
        ]
    ]

    t_test = Table(test_matrix_data, colWidths=[105, 50, 282, 78], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3.5),
        ('RIGHTPADDING', (0,0), (-1,-1), 3.5),
    ])
    story.append(t_test)
    story.append(Spacer(1, 3))

    story.append(P("B. Protokol Pengujian & Validasi Eksperimental Laboratorium Basah (Wet-Lab Pipeline)", h2))
    wetlab_test_items = [
        "<b>Tahap 1: Validasi In Silico (Cross-Validation Transformer & AlphaFold):</b> Menguji korelasi skor fitness &Delta;LLR terhadap energi bebas konformasi &Delta;&Delta;G dan kestabilan ikatan kompleks protein DREB2A pada motif heliks DRE/CRT (5'-GCCGAC-3').",
        "<b>Tahap 2: Validasi In Vitro (Kontrol Kualitas Plasmid & Koloni PCR):</b> Verifikasi ligasi oligo gRNA ke vektor tanaman padi <code>pRGEB32</code> via digesti restriksi <i>BsaI</i> dan amplifikasi PCR koloni sel <i>Agrobacterium tumefaciens</i> EHA105.",
        "<b>Tahap 3: Pengujian Fisiologis & Cekaman In Planta:</b> Pengujian kalus embriogenik pada media perlakuan polietilena glikol (PEG 6000 20%) untuk mensimulasikan cekaman potensial air -50 kPa tanah vertisol, diikuti sekuensing Sanger generasi T0 untuk mengonfirmasi konversi basa C&rarr;T pada lokus target.",
        "<b>Tahap 4: Pengujian Genetik Segregasi Bebas Transgen (T1 Null-Segregant Screening):</b> Penapisan PCR negatif terhadap kaset <i>Cas9</i> dan marka higromisin pada tanaman generasi T1 untuk menyortir galur murni mutan yang 100% bersih dari DNA plasmid (Non-Transgenik)."
    ]
    story.append(make_numbered_list(wetlab_test_items))
    story.append(Spacer(1, 2))

    story.append(make_callout(
        "Jaminan Kualitas Riset (Research Quality Assurance)",
        "Kombinasi 37 uji komputasi otomatis berkecepatan 0.57 detik dengan protokol validasi bertingkat in vitro dan in planta memberikan jaminan bahwa seluruh rekomendasi molekuler yang dihasilkan oleh PhytoAI-Genetics memiliki landasan verifikasi ilmiah yang kokoh dan siap direproduksi oleh tim peneliti bioteknologi tanaman."
    ))

    story.append(PageBreak())

    # ==================== HALAMAN 10: BAB 14 (PRESENTASI RISET & Q&A 1-5) ====================
    story.append(P("14. Panduan Khusus: Persiapan Presentasi Riset & 10 Tanya Jawab Kritis Sidang", h1))
    story.append(P(
        "Bagian ini memuat struktur presentasi riset 10–15 menit yang efektif dan 10 simulasi pertanyaan tajam dewan penguji beserta model jawaban berbasis bukti saintifik:",
        body_justify
    ))

    pres_steps_data = [
        [P("<b>Waktu</b>", table_header), P("<b>Tahapan Presentasi</b>", table_header), P("<b>Poin Kunci yang Harus Disampaikan (<i>Speaking Points</i>)</b>", table_header)],
        [
            P("Menit 01–03", table_cell_center),
            P("<b>Latar Belakang & Masalah Riil</b>", table_cell),
            P("Buka dengan data faktual puso sawah di Pantura & NTT akibat El Nino. Jelaskan bahwa pemuliaan konvensional memakan waktu 8–10 tahun, sedangkan kekeringan terjadi sekarang. Perlu terobosan komputasi presisi.", table_cell)
        ],
        [
            P("Menit 04–06", table_cell_center),
            P("<b>Arsitektur Solusi PhytoAI-Genetics</b>", table_cell),
            P("Tunjukkan integrasi 3 pilar: Peta BNPB InaRISK (lokasi) &rarr; Model Transformer (prediksi biokimia) &rarr; CRISPR Base Editor (alat potong presisi non-transgenik).", table_cell)
        ],
        [
            P("Menit 07–10", table_cell_center),
            P("<b>Live Demo Antarmuka Aplikasi</b>", table_cell),
            P("Buka <code>http://localhost:8000</code>. Tunjukkan demo kasus Demak-Pati: masukkan mutasi <code>P168L</code> pada varietas Inpari 32 HDB. Tunjukkan skor &Delta;LLR positif dan bagaimana CRISPR studio menyusun panduan gRNA tanpa terminator TTTT.", table_cell)
        ],
        [
            P("Menit 11–13", table_cell_center),
            P("<b>Keunggulan & Validasi Saintifik</b>", table_cell),
            P("Paparkan hasil Deep Mutational Scanning (DMS) dan 37 unit test otomatis yang lulus tanpa cela. Tekankan efisiensi biaya: mendesain oligo secara presisi sebelum masuk ke lab basah menghemat puluhan juta rupiah.", table_cell)
        ],
        [
            P("Menit 14–15", table_cell_center),
            P("<b>Kesimpulan & Dampak Nasional</b>", table_cell),
            P("Tutup dengan visi hilirisasi: varietas padi lokal yang tahan kekeringan ekstrem tanpa gen asing, memperkuat cadangan beras nasional di era perubahan iklim.", table_cell)
        ]
    ]

    t_pres = Table(pres_steps_data, colWidths=[65, 135, 315], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    story.append(t_pres)
    story.append(Spacer(1, 4))

    story.append(P("Simulasi 10 Tanya Jawab Kritis Dewan Penguji (Master Defense Q&A):", h2))

    # TANYA JAWAB 1 HINGGA 5 DI HALAMAN 9
    qa_p1 = [
        (
            1,
            "Apakah padi hasil rekayasa ini termasuk produk transgenik (GMO) dan bagaimana status regulasinya?",
            "Bukan, Prof/Bapak/Ibu Penguji. Pendekatan yang kami rancang menggunakan teknologi <b>CRISPR Base Editing (CBE/ABE)</b>. Kita hanya menukar satu pasang basa nukleotida endogen tanaman padi (misalnya sitosin menjadi timin pada kodon Pro168Leusin) untuk meniru variasi alel unggul alami. Tidak ada fragmen DNA asing dari bakteri atau virus yang terintegrasi secara permanen ke dalam genom tanaman. Menurut regulasi biosafety internasional dan pedoman Komisi Keamanan Hayati Produk Rekayasa Genetik (KKH PRG), tanaman hasil pengeditan genom tipe SDN-1 dan SDN-2 tanpa gen asing diklasifikasikan sebagai produk non-transgenik konvensional."
        ),
        (
            2,
            "Bagaimana model AI Transformer pLM memvalidasi bahwa mutasi P168L tidak merusak konformasi protein?",
            "Model Protein Language Model (pLM) mengevaluasi seluruh ruang urutan evolusi protein tumbuhan. Residu Pro168 berada pada domain NRD (regulator negatif). Pada tanaman normal, NRD dikenali oleh ubiquitin ligase untuk merusak DREB2A. Mutasi P168L menghasilkan nilai &Delta;LLR positif (+1.85), yang membuktikan bahwa substitusi ke Leusin disukai secara termodinamika, mencegah pengikatan ubiquitin, dan menstabilkan faktor transkripsi tanpa merusak lipatan domain pengikat DNA AP2/ERF."
        ),
        (
            3,
            "Bukankah aktivasi DREB2A secara terus-menerus memicu efek kerdil (stunting) pada tanaman padi?",
            "Pertanyaan yang sangat tajam dan mendalam. Fenomena kerdil (<i>stunting</i>) atau <i>growth penalty</i> memang terjadi pada tanaman transgenik model lama yang menggunakan promotor konstitutif kuat (seperti CaMV 35S) yang memproduksi protein secara berlebihan tanpa henti. Namun, pada pendekatan PhytoAI-Genetics, gen <i>OsDREB2A</i> tetap berada di bawah kendali promotor aslinya (<i>native promoter</i>). Transkripsi mRNA hanya dipicu ketika tanaman mulai merasakan penurunan potensial air tanah, namun protein yang terbentuk memiliki waktu paruh (<i>half-life</i>) yang jauh lebih panjang karena degron NRD telah termodifikasi. Dengan demikian, tanaman tumbuh dengan tinggi dan jumlah anakan normal saat air cukup, namun langsung mengaktifkan proteksi osmotik saat kemarau tiba."
        ),
        (
            4,
            "Mengapa riset ini memprioritaskan gen OsDREB2A daripada gen toleransi abiotik lainnya?",
            "Gen <i>OsDREB2A</i> merupakan regulator tingkat puncak (<i>master switch</i>). Satu molekul OsDREB2A yang stabil mampu mengikat elemen cis DRE/CRT pada promotor puluhan gen hilir sekaligus, seperti gen biosintesis osmolit prolin (<i>OsP5CS</i>), protein pelindung membran LEA (<i>Late Embryogenesis Abundant</i>), dan enzim antioksidan SOD/CAT penangkal radikal bebas (ROS). Mengedit satu gen hulu memberikan dampak pertahanan seluler yang menyeluruh dibandingkan merekayasa satu per satu gen hilir."
        ),
        (
            5,
            "Bagaimana cara memitigasi risiko mutasi di luar sasaran (off-target mutations) pada genom padi?",
            "Kami menerapkan empat lapis kontrol keamanan: (1) Menggunakan enzim <i>nCas9 nickase</i> (D10A) yang tidak memotong untai ganda DNA sehingga meniadakan translokasi kromosom acak; (2) Algoritma studio kami memindai seluruh genom padi IRGSP-1.0 untuk memastikan protospacer 20-nt memiliki ketidakcocokan (<i>mismatch</i>) minimal 3 basa terhadap lokus non-target; (3) Membatasi jendela deaminasi hanya pada basa ke-4 hingga ke-8; dan (4) Mengeliminasi motif terminator Pol III (TTTT) untuk mencegah transkrip gRNA abnormal."
        )
    ]

    for q_num, q_text, a_text in qa_p1:
        story.append(make_qa_item(q_num, q_text, a_text))

    # Pindah Halaman Bersih ke Halaman 10
    story.append(PageBreak())

    # ==================== HALAMAN 10: Q&A 6-10 & PENUTUP ====================
    qa_p2 = [
        (
            6,
            "Mengapa eliminasi motif TTTT pada gRNA menjadi parameter kritis dalam aplikasi ini?",
            "Ini adalah pertimbangan teknis biologi molekuler yang sangat krusial. Pada vektor transformasi tanaman padi (seperti plasmid pRGEB32), ekspresi gRNA digerakkan oleh promotor RNA Polimerase III (U3 atau U6 padi). Enzim Pol III mengenali rentetan empat atau lebih timin (<code>TTTT</code>) sebagai sinyal terminasi transkripsi alami. Jika gRNA mengandung TTTT, sintesis gRNA akan berhenti di tengah jalan dan tidak akan pernah mengenali target di genom. Algoritma kami secara otomatis menyaring dan membuang kandidat gRNA yang mengandung motif tersebut."
        ),
        (
            7,
            "Setelah mendapatkan desain gRNA dari aplikasi ini, bagaimana tahapan konkret di laboratorium basah (wet-lab)?",
            "Tahapannya mengikuti protokol baku bioteknologi tanaman: (1) Sintesis sepasang oligonukleotida sintetik sesuai sekuens protospacer dari studio kami; (2) Aniling dan kloning ke situs restriksi BsaI plasmid biner tanaman (misal pRGEB32); (3) Transformasi vektor ke kalus embriogenik padi lokal (misal Inpari 32) menggunakan bakteri <i>Agrobacterium tumefaciens</i> galur EHA105; (4) Seleksi kalus resisten higromisin dan regenerasi planlet menjadi tanaman hijau utuh; (5) Ekstraksi DNA genomik dan verifikasi Sanger sequencing pada lokus target generasi T0 untuk mengonfirmasi ketepatan konversi basa C&rarr;T."
        ),
        (
            8,
            "Bagaimana data spasial BNPB InaRISK memengaruhi keputusan strategi pemuliaan di lapangan?",
            "Cekaman kekeringan di Indonesia bersifat spesifik lokasi (<i>site-specific</i>). Di sentra Demak-Pati, tanah lempung vertisol mengalami retakan mekanik berat yang memutus akar saat kemarau; strateginya adalah introduksi alel P168L pada varietas Inpari 32 HDB untuk mempertahankan turgor saat pengisian bulir. Sebaliknya, di NTT semi-arid dengan kemarau 8–9 bulan, cekamannya adalah ketiadaan lengas tanah sejak fase bibit; rekomendasinya adalah kombinasi alel ganda P168L dan V79I pada plasma nutfah Padi Gogo Merah NTT. Integrasi InaRISK memastikan bahwa rekayasa genetik yang didesain benar-benar menjawab kebutuhan agroklimat di sawah petani."
        ),
        (
            9,
            "Bagaimana arsitektur perangkat lunak menjamin keandalan saat diakses simultan oleh banyak peneliti?",
            "Sistem dibangun dengan arsitektur mikro-layanan asinkronus menggunakan FastAPI dan Uvicorn multi-worker. Pemanggilan ke NCBI Datasets dan ArcGIS BNPB menggunakan connection pool HTTPX non-blocking untuk meminimalkan beban koneksi TCP/TLS. Selain itu, kami menyematkan middleware in-memory sliding window rate-limiting yang memproteksi endpoint komputasi berat (DMS dan CRISPR) dari risiko lonjakan beban tak terduga (DoS), dengan proteksi kontainerisasi Docker dan penanganan exception terpusat."
        ),
        (
            10,
            "Bagaimana alur segregasi genetik memastikan tanaman generasi lanjut benar-benar bersih dari plasmid T-DNA?",
            "Pada generasi primer (T0), tanaman hasil regenerasi kalus membawa integrasi T-DNA hemizigot. Ketika tanaman T0 mengalami penyerbukan sendiri (self-pollination) menghasilkan benih T1, kaset T-DNA yang menyandi nCas9 dan marka higromisin akan bersegregasi secara independen dari lokus mutasi target OsDREB2A sesuai rasio Mendel 1:2:1. Melalui seleksi PCR negatif terhadap kaset Cas9 dan resistensi higromisin, kita mengisolasi galur T1 homozigot mutan yang null-segregant (bersih 100% dari DNA vektor). Dengan metode ini, sertifikasi non-transgenik dapat dipenuhi secara absolut."
        )
    ]

    for q_num, q_text, a_text in qa_p2:
        story.append(make_qa_item(q_num, q_text, a_text))

    story.append(Spacer(1, 4))
    story.append(make_callout(
        "Pesan Penutup untuk Presenter",
        "Tunjukkan keyakinan dan antusiasme Anda. Platform PhytoAI-Genetics mendemonstrasikan bahwa kecerdasan buatan (AI) bukan sekadar alat bantu analitik abstrak, melainkan instrumen rekayasa presisi yang dapat secara langsung memecahkan krisis pangan nyata di tanah air kita. Semoga sukses dalam presentasi dan sidang riset Anda!"
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF berhasil dibuat: {output_path}")


if __name__ == "__main__":
    out_pdf = "/Users/yuwaficmuhammad/Desktop/ncbi/Panduan_Lengkap_PhytoAI_Genetics_A4.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
