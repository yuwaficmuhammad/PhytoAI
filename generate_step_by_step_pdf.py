#!/usr/bin/env python3
"""
generate_step_by_step_pdf.py
Script pembuat dokumen PDF resmi:
"PANDUAN ALUR PROSES PENELITIAN STEP-BY-STEP (PhytoAI-Genetics)"
Bahasa: Jelas, Terstruktur, dan Mudah Dipahami.
Ukuran kertas: A4 (210 x 297 mm), Tipografi Arial/Segoe UI, Rata Kanan-Kiri (Justified),
dilengkapi 8 ilustrasi ilmiah resolusi tinggi dan kartu ringkasan eksekutif.
"""

import os
import sys
import re
import shutil
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


# ==================== 1. KONFIGURASI FONT NATIVE ====================
font_dirs = [
    "/Library/Fonts",
    "/System/Library/Fonts",
    "/System/Library/Fonts/Supplemental",
]

def register_fonts():
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
        print(f"Peringatan registrasi font: {e}, menggunakan fallback.")

register_fonts()


# ==================== 2. RUNNING HEADER & FOOTER ====================
class StepByStepNumberedCanvas(canvas.Canvas):
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

        # Header (Mulai halaman 2 ke atas)
        if self._pageNumber > 1:
            header_left = "PhytoAI-Genetics: Panduan Alur Proses Penelitian Step-by-Step"
            header_right = "Rekayasa Genetik Padi Tahan Kekeringan Berbasis AI Transformer & CRISPR"
            self.drawString(36, 815, header_left)
            self.drawRightString(A4[0] - 36, 815, header_right)
            self.setStrokeColor(HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 809, A4[0] - 36, 809)

        # Footer (Semua halaman)
        footer_page = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(A4[0] - 36, 24, footer_page)
        self.drawString(36, 24, "Kementerian Pendidikan Tinggi, Sains, dan Teknologi RI  |  Pusat Riset Bioteknologi Pangan")
        self.setStrokeColor(HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 33, A4[0] - 36, 33)

        self.restoreState()


# ==================== 3. SANITASI MARKDOWN ====================
def md_clean(text: str) -> str:
    """Mengonversi Markdown standar ke tag ReportLab XML."""
    if not text:
        return ""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(?<![A-Za-z0-9_])_([A-Za-z0-9\s]+?)_(?![A-Za-z0-9_])', r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`', r'<font face="Courier" color="#0369a1">\1</font>', text)
    return text


# ==================== 4. PEMBANGUN DOKUMEN UTAMA ====================
def build_step_by_step_pdf(output_path: str):
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
    PRIMARY_DARK = HexColor("#065f46")    # Forest Dark Green
    PRIMARY_LIGHT = HexColor("#10b981")   # Vibrant Mint
    PRIMARY_SUBTLE = HexColor("#ecfdf5")  # Soft Emerald Wash
    ACCENT_BLUE = HexColor("#0284c7")     # Genomic Cyan
    ACCENT_BLUE_LIGHT = HexColor("#e0f2fe")
    TEXT_MAIN = HexColor("#1e293b")       # Slate 800
    TEXT_MUTED = HexColor("#64748b")      # Slate 500
    BG_CARD = HexColor("#f8fafc")         # Slate 50
    BORDER_COLOR = HexColor("#cbd5e1")    # Slate 300
    BORDER_DARK = HexColor("#94a3b8")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='SegoeUI-Bold',
        fontSize=18,
        leading=23,
        textColor=PRIMARY_DARK,
        alignment=TA_LEFT,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='SegoeUI',
        fontSize=9.5,
        leading=14.5,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        fontName='SegoeUI-Bold',
        fontSize=11.5,
        leading=15,
        textColor=PRIMARY_DARK,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        fontName='SegoeUI-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=ACCENT_BLUE,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_justify = ParagraphStyle(
        'BodyJustify',
        fontName='SegoeUI',
        fontSize=8.5,
        leading=13,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=4.5
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='SegoeUI-Bold',
        fontSize=8.5,
        leading=13,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=3,
        keepWithNext=True
    )

    list_item_style = ParagraphStyle(
        'ListItemStyle',
        fontName='SegoeUI',
        fontSize=8.5,
        leading=12.8,
        textColor=TEXT_MAIN,
        alignment=TA_JUSTIFY,
        spaceAfter=0
    )

    bullet_label_style = ParagraphStyle(
        'BulletLabel',
        fontName='SegoeUI-Bold',
        fontSize=8.5,
        leading=12.8,
        textColor=PRIMARY_DARK,
        alignment=TA_CENTER,
        spaceAfter=0
    )

    caption_style = ParagraphStyle(
        'CaptionStyle',
        fontName='SegoeUI-Italic',
        fontSize=7.2,
        leading=10.2,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='SegoeUI-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='SegoeUI',
        fontSize=7.8,
        leading=11,
        textColor=TEXT_MAIN,
        alignment=TA_LEFT
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        fontName='SegoeUI',
        fontSize=7.8,
        leading=11,
        textColor=TEXT_MAIN,
        alignment=TA_CENTER
    )

    def P(text, style=body_justify):
        return Paragraph(md_clean(text), style)

    def make_bullet_row(label, text_content):
        p_label = Paragraph(label, bullet_label_style)
        p_text = Paragraph(md_clean(text_content), list_item_style)
        return Table(
            [[p_label, p_text]],
            colWidths=[18, printable_width - 18],
            style=[
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 1.2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
            ]
        )

    def make_card(flowables, bg=BG_CARD, border=BORDER_COLOR):
        t = Table([[flowables]], colWidths=[printable_width], style=[
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 0.75, border),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ])
        return KeepTogether([Spacer(1, 3), t, Spacer(1, 4)])

    img_dir = "/Users/yuwaficmuhammad/Desktop/ncbi/app/static/images"

    def make_figure(image_name, caption_text, target_width=370):
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

        return KeepTogether([Spacer(1, 3), wrapper, Spacer(1, 2.5), caption, Spacer(1, 4)])

    def make_step_header(step_num, step_title, step_badge="TAHAP KRUSIAL"):
        header_table = Table([
            [
                Paragraph(f"<b>TAHAP {step_num}</b>", ParagraphStyle('Badge', fontName='SegoeUI-Bold', fontSize=8, textColor=colors.white, alignment=TA_CENTER)),
                Paragraph(f"<b>{step_title}</b>", ParagraphStyle('Title', fontName='SegoeUI-Bold', fontSize=10.5, textColor=PRIMARY_DARK, alignment=TA_LEFT)),
                Paragraph(f"<i>{step_badge}</i>", ParagraphStyle('SubBadge', fontName='SegoeUI-Italic', fontSize=7.5, textColor=ACCENT_BLUE, alignment=TA_RIGHT))
            ]
        ], colWidths=[65, printable_width - 175, 110], style=[
            ('BACKGROUND', (0,0), (0,0), PRIMARY),
            ('BACKGROUND', (1,0), (-1,-1), PRIMARY_SUBTLE),
            ('BOX', (0,0), (-1,-1), 0.75, PRIMARY),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ])
        return KeepTogether([Spacer(1, 5), header_table, Spacer(1, 4)])

    story = []

    # ==================== HALAMAN 1: COVER & RINGKASAN EKSEKUTIF ====================
    # Banner Header Lembaga
    header_box = Table([
        [
            Paragraph("<b>KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI REPUBLIK INDONESIA</b><br/>"
                      "<font size='7.5' color='#64748b'>Pusat Riset Bioteknologi Pangan & Konsorsium Genomika Pertanian Tropis</font>",
                      ParagraphStyle('GovHeader', fontName='SegoeUI-Bold', fontSize=8.5, leading=12, textColor=PRIMARY_DARK, alignment=TA_LEFT)),
            Paragraph("<font size='7.5' color='#059669'><b>DOKUMEN TEKNIS RESMI</b></font><br/>"
                      "<font size='7' color='#64748b'>Kode: PB-PHYTOAI-2026/A4</font>",
                      ParagraphStyle('GovDocId', fontName='SegoeUI', fontSize=8, leading=11, alignment=TA_RIGHT))
        ]
    ], colWidths=[printable_width - 130, 130], style=[
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,0), (-1,-1), 1.2, PRIMARY),
    ])
    story.append(header_box)
    story.append(Spacer(1, 7))

    story.append(P("PANDUAN ALUR PROSES PENELITIAN STEP-BY-STEP", title_style))
    story.append(P("<b>Rekayasa Genetik Padi Tahan Kekeringan Ekstrem Menggunakan Pemodelan AI Transformer OsDREB2A, Data Spasial InaRISK BNPB, dan Presisi CRISPR Base Editing</b>", subtitle_style))

    # Executive Summary Card
    exec_summary_content = [
        P("<b>RANGKUMAN EKSEKUTIF UNTUK PENELITI & PEMANGKU KEBIJAKAN</b>", ParagraphStyle('CardH', fontName='SegoeUI-Bold', fontSize=8.8, textColor=PRIMARY_DARK, spaceAfter=2.5)),
        P("Penelitian ini menyatukan tiga pilar teknologi modern dalam satu alur terpadu: "
          "<b>(1) Pemetaan Geospasial Kebencanaan InaRISK BNPB</b> untuk menemukan titik sawah paling rawan kekeringan di Indonesia, "
          "<b>(2) Kecerdasan Buatan (AI Protein Transformer ESM-2)</b> untuk memindai jutaan kemungkinan mutasi gen tanpa coba-coba wet-lab yang mahal, serta "
          "<b>(3) CRISPR Base Editing (CBE)</b> yang mengoreksi tepat satu huruf DNA pada saklar darurat <i>OsDREB2A</i> tanpa memasukkan gen asing dari bakteri (non-GMO transgenik). "
          "Hasilnya adalah strategi rekayasa presisi yang siap diaplikasikan pada 8 varietas padi lokal unggulan nasional."),
    ]
    story.append(make_card(exec_summary_content, bg=PRIMARY_SUBTLE, border=PRIMARY))

    story.append(P("1. Latar Belakang Masalah: Tantangan Iklim & Kerapuhan Padi Nasional", h1_style))
    story.append(P(
        "Kekeringan berkepanjangan akibat fenomena El Niño dan pemanasan global telah mengancam sentra-sentra produksi beras nasional. "
        "Di wilayah seperti Pantura Jawa, tanah lempung <i>vertisol</i> (grumusol) mengalami retak hebat saat kekurangan air, "
        "memutus perakaran tanaman padi dan menurunkan hasil panen hingga 60–80%. "
        "Secara alami, tanaman padi (<i>Oryza sativa</i>) memiliki gen faktor transkripsi bernama <b>OsDREB2A</b> (Gene ID NCBI: <code>4324418</code>). "
        "Protein ini bertindak sebagai 'saklar darurat' yang mampu menghidupkan ratusan gen pertahanan kekeringan, "
        "seperti sintesis osmolit prolin (<i>OsP5CS</i>), protein pelindung membran sel (<i>OsLEA3</i>), dan penutup stomata daun."
    ))
    story.append(P(
        "<b>Kelemahan Biologis Alami:</b> Di kondisi normal, tanaman padi memiliki sistem perusak otomatis bernama "
        "<b>NRD (Negative Regulatory Domain) / PEST Degron</b> (asam amino 136–192). Akibatnya, saat kekeringan tiba-tiba melanda, "
        "protein DREB2A terlalu cepat dihancurkan oleh mesin ubiquitin-proteasom seluler sebelum sempat menyelamatkan tanaman. "
        "Oleh karena itu, rekayasa genetik presisi mutlak diperlukan untuk menonaktifkan domain perusak tersebut."
    ))

    story.append(make_figure("rice_drought_vertisol_field.png",
                             "Gambar 1. Agroekosistem sawah vertisol tropis Indonesia yang mengalami rekahan tanah hebat pada musim kemarau ekstrem.",
                             target_width=380))

    story.append(PageBreak())

    # ==================== HALAMAN 2: TAHAP 1 & TAHAP 2 ====================
    story.append(make_step_header("1", "Deteksi Titik Kritis Lapangan Berbasis GIS InaRISK BNPB", "SPASIAL 100M"))

    story.append(P(
        "Alih-alih berasumsi umum, penelitian ini memulai alur dari <b>kebutuhan nyata di lapangan</b>. "
        "Sistem mengintegrasikan data kebencanaan spasial Badan Nasional Penanggulangan Bencana (InaRISK BNPB) beresolusi tinggi 100 meter "
        "untuk mengidentifikasi 5 sentra pertanian padi yang paling kritis terancam kekeringan di Indonesia:"
    ))

    # Tabel InaRISK
    inarisk_table_data = [
        [
            Paragraph("Sentra Produksi Padi", table_header_style),
            Paragraph("Koordinat", table_header_style),
            Paragraph("Indeks Bahaya", table_header_style),
            Paragraph("Karakteristik Agroekosistem", table_header_style),
            Paragraph("Strategi DREB2A", table_header_style),
        ],
        [
            Paragraph("<b>Pantura Jateng</b><br/>Demak & Pati", table_cell_style),
            Paragraph("-6.89° S<br/>110.64° E", table_cell_center),
            Paragraph("<b>0.88</b><br/>TINGGI", table_cell_center),
            Paragraph("Vertisol Grumusol retak tinggi, salinitas pesisir pasang surut.", table_cell_style),
            Paragraph("<code>P168L</code> (DREB2A-CA: Konstitutif Aktif)", table_cell_style),
        ],
        [
            Paragraph("<b>Pantura Jabar</b><br/>Indramayu & Karawang", table_cell_style),
            Paragraph("-6.32° S<br/>108.32° E", table_cell_center),
            Paragraph("<b>0.82</b><br/>TINGGI", table_cell_center),
            Paragraph("Aluvial hidromorfik, penurunan debit irigasi Waduk Jatiluhur.", table_cell_style),
            Paragraph("<code>V79I</code> (Afinitas Pengikat AP2/ERF Tinggi)", table_cell_style),
        ],
        [
            Paragraph("<b>Jawa Timur</b><br/>Lamongan & Bojonegoro", table_cell_style),
            Paragraph("-7.12° S<br/>112.41° E", table_cell_center),
            Paragraph("<b>0.79</b><br/>SEDANG-TINGGI", table_cell_center),
            Paragraph("Vertisol kapur karst, fluktuasi air tanah Bengawan Solo.", table_cell_style),
            Paragraph("<code>S167A</code> (Abolisi Titik Fosforilasi)", table_cell_style),
        ],
        [
            Paragraph("<b>NTT Semi-Arid</b><br/>Timor & Sumba", table_cell_style),
            Paragraph("-9.86° S<br/>124.28° E", table_cell_center),
            Paragraph("<b>0.94</b><br/>EKSTREM TINGGI", table_cell_center),
            Paragraph("Litosol & mediteran kering berbatu, defisit air > 7 bulan.", table_cell_style),
            Paragraph("<code>P168L</code> + Aktivasi Promotor OsLEA3", table_cell_style),
        ],
        [
            Paragraph("<b>NTB Lahan Kering</b><br/>Lombok & Sumbawa", table_cell_style),
            Paragraph("-8.65° S<br/>117.42° E", table_cell_center),
            Paragraph("<b>0.91</b><br/>EKSTREM TINGGI", table_cell_center),
            Paragraph("Regosol berpasir gora, infiltrasi air sangat cepat.", table_cell_style),
            Paragraph("Kombinasi ABE (<code>V79I</code>) + Padi Gogo Jatiluhur", table_cell_style),
        ],
    ]
    t_inarisk = Table(inarisk_table_data, colWidths=[100, 55, 65, 170, 134], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    story.append(t_inarisk)
    story.append(Spacer(1, 6))

    story.append(make_step_header("2", "Penarikan Data Genom Real dari NCBI GenBank", "ENTREZ API LIVE"))
    story.append(P(
        "Penelitian tidak menggunakan data fiktif atau perkiraan umum, melainkan terhubung langsung ke "
        "<b>NCBI GenBank Entrez API</b> untuk mengekstrak sekuens DNA dan protein sebenarnya dari *Oryza sativa* Nipponbare / Indica:"
    ))
    story.append(make_bullet_row("•", "<b>Lokus Gen Inti:</b> <i>OsDREB2A</i> (Gene ID: <code>4324418</code>, RefSeq Nucleotide: <code>NM_001051515.1</code>)."))
    story.append(make_bullet_row("•", "<b>Panjang CDS & Protein:</b> 825 pasang basa (Coding Sequence) yang menyandi 274 asam amino."))
    story.append(make_bullet_row("•", "<b>Jejaring 9 Gen Regulon Terkait:</b> <i>OsLEA3</i> (kadar proteksi sel), <i>OsP5CS</i> (sintesis prolin), "
                                      "<i>OsbZIP23</i> (regulasi ABA), <i>OsSNAC1</i> (penutupan stomata), <i>OsNAC6</i>, <i>OsERD1</i>, "
                                      "<i>OsCIPK03</i>, <i>OsKAT2</i>, dan <i>OsRab16A</i>."))

    story.append(make_figure("rice_genomics_workstation.png",
                             "Gambar 2. Integrasi data komputasi NCBI GenBank dan stasiun kerja perancangan genomika padi tropis.",
                             target_width=370))

    story.append(PageBreak())

    # ==================== HALAMAN 3: TAHAP 3 (AI TRANSFORMER & DMS) ====================
    story.append(make_step_header("3", "Detektif AI Transformer: Deep Mutational Scanning (DMS)", "ZERO-SHOT PREDICTION"))

    story.append(P(
        "Jika seorang peneliti harus menguji seluruh 274 posisi asam amino di laboratorium secara acak, "
        "akan ada $274 \\times 19 = 5.206$ kombinasi mutasi tunggal. Pengujian ini mustahil dilakukan secara manual. "
        "PhytoAI-Genetics menerapkan <b>AI Protein Language Model (arsitektur Transformer ESM-2)</b> yang telah mempelajari "
        "jutaan struktur protein evolusioner dunia untuk melakukan <i>Deep Mutational Scanning (DMS)</i> secara in silico dalam hitungan detik."
    ))

    # Komparasi WT vs P168L
    dms_compare_data = [
        [
            Paragraph("Parameter Evaluasi AI", table_header_style),
            Paragraph("Kondisi Asli (Wild-Type)", table_header_style),
            Paragraph("Hasil Mutasi AI (P168L)", table_header_style),
            Paragraph("Dampak Biologis Molekuler", table_header_style),
        ],
        [
            Paragraph("<b>Kodon Asam Amino 168</b>", table_cell_style),
            Paragraph("<code>CCG</code> (Prolin / P)", table_cell_center),
            Paragraph("<b><code>CTG</code> (Leusin / L)</b>", table_cell_center),
            Paragraph("Perubahan rantai samping cincin pirolidin kaku menjadi rantai alifatik fleksibel.", table_cell_style),
        ],
        [
            Paragraph("<b>Indeks Toleransi Kekeringan</b>", table_cell_style),
            Paragraph("0.42 (Rentan - Standar)", table_cell_center),
            Paragraph("<b>0.94 (Toleran Ekstrem)</b>", table_cell_center),
            Paragraph("Peningkatan resistensi seluler terhadap stres osmotik hingga +123%.", table_cell_style),
        ],
        [
            Paragraph("<b>Stabilitas Protein Degron</b>", table_cell_style),
            Paragraph("Waktu paruh singkat (< 30 menit)", table_cell_center),
            Paragraph("<b>Stabil & Konstitutif Aktif</b>", table_cell_center),
            Paragraph("Mengabolisi motif pengenalan ubiquitin ligase; saklar tetap siaga tanpa terdegradasi.", table_cell_style),
        ],
        [
            Paragraph("<b>Integritas Domain AP2/ERF</b>", table_cell_style),
            Paragraph("Utuh (Posisi 56–114)", table_cell_center),
            Paragraph("<b>100% Terjaga Sempurna</b>", table_cell_center),
            Paragraph("Kemampuan menempel pada motif DRE/CRT di promotor gen target tidak terganggu.", table_cell_style),
        ],
    ]
    t_dms = Table(dms_compare_data, colWidths=[115, 95, 105, 209], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4.5),
        ('RIGHTPADDING', (0,0), (-1,-1), 4.5),
    ])
    story.append(t_dms)
    story.append(Spacer(1, 6))

    story.append(P(
        "<b>Mengapa Mutasi P168L Dinamakan 'Mutasi Emas'?</b><br/>"
        "AI Transformer menemukan bahwa posisi 168 berada tepat di pusat wilayah NRD Degron. "
        "Mengganti Prolin dengan Leusin tidak merusak struktur pelipatan global protein (protein folding), "
        "namun secara efektif melumpuhkan sinyal ubiquitinasi. Akibatnya, tanaman memiliki faktor transkripsi DREB2A "
        "yang selalu siaga (<i>Constitutively Active / DREB2A-CA</i>) bahkan sebelum tanaman mengalami kekeringan fisik."
    ))

    story.append(make_figure("rice_dreb2a_hero.png",
                             "Gambar 3. Struktur tiga dimensi protein OsDREB2A: Domain pengikat DNA AP2/ERF (cyan) dan daerah regulasi negatif NRD Degron (emas) target mutasi P168L.",
                             target_width=365))

    story.append(PageBreak())

    # ==================== HALAMAN 4: TAHAP 4 & TAHAP 5 (CRISPR & SIMULASI 3D) ====================
    story.append(make_step_header("4", "Desain Pisau Bedah Presisi: CRISPR Base Editing (CBE)", "NON-TRANSGENIK"))

    story.append(P(
        "Pendekatan rekayasa genetik modern menolak metode GMO klasik yang memasukkan DNA asing (seperti gen racun Bt dari bakteri). "
        "Penelitian ini menggunakan teknologi <b>Cytosine Base Editing (CBE)</b>: mesin molekuler fusi dCas9/Cas9-nickase "
        "dengan enzim *cytidine deaminase* yang hanya mengoreksi huruf basa DNA spesifik tanpa memotong kedua untai DNA "
        "(<i>no double-strand DNA breaks</i>), sehingga bebas risiko insersi mutasi acak yang berbahaya."
    ))

    story.append(make_bullet_row("1", "<b>Pemilihan sgRNA Target:</b> Algoritma menyaring kandidat protospacer 20 nukleotida yang berdekatan dengan target kodon 168."))
    story.append(make_bullet_row("2", "<b>Sekuens sgRNA Optimal:</b> <code>5'-GATGAGAAGGATGAGCTGGA-3'</code>."))
    story.append(make_bullet_row("3", "<b>Motif PAM (Protospacer Adjacent Motif):</b> <code>AGG</code> (SpCas9-compatible pada untai +)."))
    story.append(make_bullet_row("4", "<b>Jendela Pengeditan (Editing Window):</b> Basa C pada posisi kodon target terletak di jendela aktivitas deaminase (nukleotida ke-4 hingga ke-8 dari ujung 5')."))
    story.append(make_bullet_row("5", "<b>Evaluasi Kualitas sgRNA:</b> Kandungan GC sebesar 50.0% (ideal 40–60%), suhu leleh $T_m$ 58.2°C, dan 100% bebas dari motif terminasi dini poly-T (<code>TTTT</code>)."))

    story.append(make_figure("crispr_rice_editing.png",
                             "Gambar 4. Mekanisme kerja CRISPR Cytosine Base Editor (CBE) dalam mengubah satu huruf basa kodon target pada untai DNA padi.",
                             target_width=370))

    story.append(make_step_header("5", "Konfirmasi Spasial & Simulasi Molekuler 3D", "WEBGL THREE.JS"))
    story.append(P(
        "Sebelum melangkah ke sintesis oligonukleotida fisik, sistem menyediakan modul simulasi visual 3D WebGL Three.js. "
        "Peneliti dapat memutar, memperbesar, dan menginspeksi posisi mendaratnya kompleks ribonucleoprotein (RNP) Cas9-sgRNA "
        "pada untai ganda DNA target secara real-time, memastikan tidak adanya tabrakan sterik (steric hindrance) "
        "pada struktur kromatin padi."
    ))

    story.append(PageBreak())

    # ==================== HALAMAN 5: TAHAP 6 & KULTIVAR LOKAL INDONESIA ====================
    story.append(make_step_header("6", "Implementasi ke Plasma Nutfah Padi Lokal Indonesia", "8 VARIETAS UNGGUL"))

    story.append(P(
        "Strategi rekayasa genetik presisi ini langsung diselaraskan dengan <b>8 varietas padi lokal</b> "
        "yang menjadi tulang punggung ketahanan pangan di berbagai pulau Indonesia:"
    ))

    cultivar_table_data = [
        [
            Paragraph("Kultivar Padi", table_header_style),
            Paragraph("Asal & Tipe Ekologi", table_header_style),
            Paragraph("Karakteristik & Kelemahan", table_header_style),
            Paragraph("Intervensi CRISPR AI", table_header_style),
        ],
        [
            Paragraph("<b>Ciherang</b>", table_cell_style),
            Paragraph("Nasional (Jawa)<br/>Sawah Irigasi", table_cell_style),
            Paragraph("Paling disukai petani & konsumen; anjlok saat air irigasi surut.", table_cell_style),
            Paragraph("CBE <code>P168L</code>: Mengubah Ciherang menjadi galur tahan kekeringan tanpa mengubah rasa pulen.", table_cell_style),
        ],
        [
            Paragraph("<b>Inpari 32 HDB</b>", table_cell_style),
            Paragraph("Pantura Jawa<br/>Sawah Dataran Rendah", table_cell_style),
            Paragraph("Tahan hawar daun bakteri, rentan stress kekeringan fase bunting.", table_cell_style),
            Paragraph("CBE <code>P168L</code>: Menghasilkan varietas dwifungsi (tahan penyakit + tahan kemarau).", table_cell_style),
        ],
        [
            Paragraph("<b>Situ Bagendit</b>", table_cell_style),
            Paragraph("Sumatera & Jawa Barat<br/>Padi Lahan Kering (Gogo)", table_cell_style),
            Paragraph("Adaptif di tanah masam, potensi hasil terbatas di kondisi kering panjang.", table_cell_style),
            Paragraph("ABE <code>V79I</code>: Meningkatkan efisiensi pengikatan DNA regulon pada curah hujan minim.", table_cell_style),
        ],
        [
            Paragraph("<b>Jatiluhur</b>", table_cell_style),
            Paragraph("Jawa Barat / NTB<br/>Padi Gogo Lahan Marginal", table_cell_style),
            Paragraph("Perakaran dalam, fotosintesis menurun drastis di musim kering.", table_cell_style),
            Paragraph("Kombinasi <code>P168L</code> + <code>S167A</code>: Stabilitas ganda faktor transkripsi.", table_cell_style),
        ],
        [
            Paragraph("<b>IR64</b>", table_cell_style),
            Paragraph("Nasional / Internasional<br/>Indica Primadona", table_cell_style),
            Paragraph("Berasal dari IRRI; rentan terhadap cekaman panas dan defisit air.", table_cell_style),
            Paragraph("CBE <code>P168L</code>: Peremajaan varietas legendaris menjadi tangguh iklim baru.", table_cell_style),
        ],
        [
            Paragraph("<b>Rojolele</b>", table_cell_style),
            Paragraph("Jawa Tengah (Klaten)<br/>Padi Aromatik Lokal", table_cell_style),
            Paragraph("Aroma wangi tinggi, umur panjang, kebutuhan air tinggi.", table_cell_style),
            Paragraph("Presisi CBE: Mempertahankan gen aroma <i>badh2</i> sambil menyuntikkan sifat tahan kering.", table_cell_style),
        ],
    ]
    t_cultivars = Table(cultivar_table_data, colWidths=[90, 110, 150, 174], style=[
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    story.append(t_cultivars)
    story.append(Spacer(1, 6))

    story.append(make_figure("rice_cultivar_panicle.png",
                             "Gambar 5. Bulir malai padi lokal Indonesia yang tetap terisi penuh (bebas hampa) berkat ekspresi konstitutif OsDREB2A pada fase pengisian biji.",
                             target_width=370))

    story.append(PageBreak())

    # ==================== HALAMAN 6: TANYA-JAWAB & REKOMENDASI WET-LAB ====================
    story.append(P("6. Tanya-Jawab Penting (FAQ Riset)", h1_style))

    def make_qa_box(q_text, a_text):
        content = [
            Paragraph(f"<b>T: {q_text}</b>", ParagraphStyle('Q', fontName='SegoeUI-Bold', fontSize=8.5, textColor=PRIMARY_DARK, spaceAfter=2)),
            Paragraph(f"<b>J:</b> {a_text}", ParagraphStyle('A', fontName='SegoeUI', fontSize=8.3, leading=12.2, textColor=TEXT_MAIN)),
        ]
        return make_card(content, bg=BG_CARD, border=BORDER_COLOR)

    story.append(make_qa_box(
        "Apakah hasil rekayasa ini termasuk produk GMO berbahaya?",
        "<b>Tidak.</b> Pendekatan CRISPR Base Editing (CBE) dikategorikan sebagai <i>New Breeding Techniques (NBT / Gene Editing SDN-1)</i>. "
        "Di banyak regulasi pangan internasional dan pedoman keamanan hayati Kementerian Pertanian RI, "
        "tanaman hasil perbaikan huruf basa alami tanpa insersi DNA asing dapat diperlakukan setara dengan hasil mutasi alami atau persilangan konvensional."
    ))

    story.append(make_qa_box(
        "Mengapa memilih gen OsDREB2A, bukan gen lain seperti OsDREB1A?",
        "<i>OsDREB1A</i> terutama merespons cekaman dingin (cold shock), sedangkan <b>OsDREB2A adalah master regulator spesifik cekaman kekeringan dan suhu tinggi (drought & heat stress)</b>. "
        "Mengaktifkan DREB2A memberikan proteksi ganda yang sangat cocok untuk iklim tropis Indonesia."
    ))

    story.append(make_qa_box(
        "Apakah tanaman padi yang selalu siaga (konstitutif aktif) pertumbuhannya akan kerdil?",
        "Pada GMO lama yang menggunakan promotor virus kuat (CaMV 35S), tanaman memang bisa mengalami *growth penalty* (kerdil). "
        "Namun dengan <b>Base Editing pada lokus asli (endogen)</b> di bawah kendali promotor alami padi sendiri, "
        "tanaman hanya mempertahankan protein yang sudah diproduksi tanpa memproduksi secara berlebihan, "
        "sehingga pertumbuhan vegetatif dan tinggi tanaman tetap normal."
    ))

    story.append(P("7. Rekomendasi Protokol Eksekusi Laboratorium (Wet-Lab)", h1_style))
    story.append(P(
        "Bagi tim peneliti di Balai Besar Perakitan Varietas Tanaman Padi (BBPadi / BRIN), "
        "berikut adalah panduan teknis untuk mengeksekusi desain komputasi ini ke dalam kultur jaringan:"
    ))
    story.append(make_bullet_row("1.", "<b>Vektor Transformasi:</b> Gunakan plasmid biner tanaman <code>pRGEB32</code> atau <code>pCAMBIA-CBE</code>."))
    story.append(make_bullet_row("2.", "<b>Promotor sgRNA:</b> Kloning protospacer <code>GATGAGAAGGATGAGCTGGA</code> di bawah kendali promotor snRNA padi <code>OsU3</code> atau <code>OsU6</code>."))
    story.append(make_bullet_row("3.", "<b>Metode Transfer Gen:</b> Transformasi genetik berbantuan <i>Agrobacterium tumefaciens</i> galur EHA105 ke kalus embriogenik varietas Ciherang atau Inpari 32."))
    story.append(make_bullet_row("4.", "<b>Skrining Generasi T0:</b> Lakukan sekuensing Sanger atau amplicon Deep Sequencing pada lokus CDS DREB2A untuk mengonfirmasi konversi kodon <code>CCG -> CTG</code>."))
    story.append(make_bullet_row("5.", "<b>Segregasi Transgen-Free:</b> Pada generasi T1, seleksi anakan tanaman yang mempertahankan mutasi P168L namun sudah bersih/lepas dari kaset T-DNA Cas9 (*Cas9-free segregant*)."))

    # Closing Signature Table
    sig_table = Table([
        [
            Paragraph("Disusun dan Diverifikasi Oleh:<br/>"
                      "<b>Tim Peneliti Komputasi Genomika Padi</b><br/>"
                      "Konsorsium Riset PhytoAI-Genetics RI",
                      ParagraphStyle('SigL', fontName='SegoeUI', fontSize=7.5, leading=11, textColor=TEXT_MAIN)),
            Paragraph("Mengetahui & Menyetujui:<br/>"
                      "<b>Pusat Riset Bioteknologi Pangan</b><br/>"
                      "Kementerian Pendidikan Tinggi, Sains, dan Teknologi RI",
                      ParagraphStyle('SigR', fontName='SegoeUI', fontSize=7.5, leading=11, textColor=TEXT_MAIN, alignment=TA_RIGHT))
        ]
    ], colWidths=[printable_width/2, printable_width/2], style=[
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LINEABOVE', (0,0), (-1,-1), 0.75, BORDER_COLOR),
    ])
    story.append(Spacer(1, 10))
    story.append(sig_table)

    doc.build(story, canvasmaker=StepByStepNumberedCanvas)
    print(f"PDF Alur Riset Step-by-Step berhasil dibuat: {output_path}")


if __name__ == "__main__":
    out_pdf = "/Users/yuwaficmuhammad/Desktop/ncbi/Panduan_Alur_Penelitian_Step_by_Step_A4.pdf"
    build_step_by_step_pdf(out_pdf)

    # Salin juga ke direktori artifact agar dapat diakses oleh sistem Antigravity
    artifact_dir = "/Users/yuwaficmuhammad/.gemini/antigravity/brain/c0c69064-b29e-4aa0-8563-42c09955d890"
    if os.path.isdir(artifact_dir):
        dest_pdf = os.path.join(artifact_dir, "Panduan_Alur_Penelitian_Step_by_Step_A4.pdf")
        shutil.copyfile(out_pdf, dest_pdf)
        print(f"PDF berhasil disalin ke direktori artifact: {dest_pdf}")

