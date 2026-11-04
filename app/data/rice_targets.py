from typing import Dict, List, Optional
from app.models.target import GeneticEngineeringTarget

# Katalog Gen Target Terkurasi Khusus Riset Toleransi Kekeringan Padi (Oryza sativa)
# PhytoAI-Genetics: Transformer Modeling of DREB2A Mutations and Drought Tolerance
RICE_TARGETS: List[GeneticEngineeringTarget] = [
    GeneticEngineeringTarget(
        id="os-dreb2a",
        gene_symbol="OsDREB2A",
        ncbi_gene_id=4324418,
        ncbi_locus_tag="LOC4324418",
        category="Toleransi Kekeringan & Suhu Ekstrem (Master Regulator)",
        trait_description=(
            "Dehydration-Responsive Element-Binding Protein 2A (Faktor Transkripsi AP2/ERF). "
            "Regulator sentral respons kekeringan, salinitas, dan suhu tinggi pada padi lokal. "
            "Modifikasi degron NRD (Negative Regulatory Domain) menghasilkan mutan konstitutif aktif (DREB2A-CA) "
            "yang meningkatkan kelangsungan hidup padi saat kekeringan ekstrem tanpa menghambat pertumbuhan vegetatif normal."
        ),
        target_strategy="Transformer-guided Base Editing (CBE/ABE) / Delesi Degron PEST NRD / Mutasi P168L & V79I",
        pathway="Jalur Cekaman Abiotik ABA-Independent / Pengikatan cis-element DRE/CRT 5'-GCCGAC-3'",
        chromosome="1",
        key_publications=[
            "Dubouzet et al., The Plant Journal (2003) 33:751–763 (OsDREB genes in rice)",
            "Sakuma et al., PNAS (2006) 103:1887–1892 (Constitutively active DREB2A confers drought tolerance)",
            "Cui et al., Frontiers in Plant Science (2018) 9:1113"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-dreb1a",
        gene_symbol="OsDREB1A",
        ncbi_gene_id=4341490,
        ncbi_locus_tag="LOC4341490",
        category="Toleransi Kekeringan & Suhu Dingin",
        trait_description=(
            "DRE-binding protein 1A / CBF3. Berperan penting dalam regulasi transkripsi cepat saat tanaman "
            "mengalami penurunan potensial osmotik drastis akibat kemarau atau suhu ekstrem."
        ),
        target_strategy="Overekspresi Terinduksi Promotor Cekaman / CRISPR Activation (CRISPRa)",
        pathway="DREB1/CBF Regulon Pathway",
        chromosome="6",
        key_publications=[
            "Ito et al., Plant & Cell Physiology (2006) 47:141–153",
            "Qin et al., Plant Molecular Biology (2007)"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-dreb2b",
        gene_symbol="OsDREB2B",
        ncbi_gene_id=4338981,
        ncbi_locus_tag="LOC4338981",
        category="Regulasi Cekaman Kekeringan Berbasis Splicing",
        trait_description=(
            "Paralog OsDREB2A yang diekspresikan melalui proses alternative splicing terinduksi kekeringan. "
            "Transkrip fungsional hanya terbentuk saat sel mengalami dehidrasi berat."
        ),
        target_strategy="Splice-Site Engineering / Perbaikan Akumulasi Transkrip Fungsional Bebas Cekaman",
        pathway="Alternative Splicing Abiotic Stress Control",
        chromosome="5",
        key_publications=[
            "Matsukura et al., Journal of Plant Research (2010) 123:559–570"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-lea3-1",
        gene_symbol="OsLEA3-1",
        ncbi_gene_id=4337666,
        ncbi_locus_tag="LOC4337666",
        category="Proteksi Membran Sel & Osmoproteksi",
        trait_description=(
            "Late Embryogenesis Abundant protein kelompok 3. Target efektor hilir utama yang diaktivasi oleh OsDREB2A. "
            "Berfungsi melindungi integritas membran plasma sel dan enzim dari denaturasi akibat hilangnya air jaringan."
        ),
        target_strategy="Promoter Up-regulation / CRISPR-Cas Transcription Activator",
        pathway="Chaperone-like Membrane Stabilization",
        chromosome="5",
        key_publications=[
            "Xiao et al., Theoretical and Applied Genetics (2007) 115:35–46"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-areb1",
        gene_symbol="OsAREB1",
        ncbi_gene_id=4340578,
        ncbi_locus_tag="LOC4340578",
        category="Jalur ABA-Dependent Toleransi Kekeringan",
        trait_description=(
            "ABA-Responsive Element-Binding Protein 1 (OsbZIP46). Mengatur respons kekeringan fase reproduktif padi. "
            "Bekerja sinergis dan komplementer bersama OsDREB2A untuk menutup kehilangan air malai."
        ),
        target_strategy="Mutasi Konstitutif Aktif Domain Regulasi (Delesi MOD) / Base Editing",
        pathway="Abscisic Acid (ABA) Signaling Cascade",
        chromosome="6",
        key_publications=[
            "Tang et al., Plant Physiology (2012) 158:1755–1768"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-p5cs1",
        gene_symbol="OsP5CS1",
        ncbi_gene_id=4338302,
        ncbi_locus_tag="LOC4338302",
        category="Biosintesis Osmolit Prolin",
        trait_description=(
            "Delta-1-pyrroline-5-carboxylate synthetase 1. Enzim penentu laju biosintesis asam amino prolin. "
            "Akumulasi prolin tinggi mencegah plasmolisis sel daun padi saat kelembapan tanah anjlok."
        ),
        target_strategy="Promoter Editing / Deregulasi Umpan Balik Inhibisi Alosterik",
        pathway="Proline Biosynthetic Pathway / Osmotic Adjustment",
        chromosome="5",
        key_publications=[
            "Hur et al., Molecules and Cells (2004) 18:210–218"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-skipa",
        gene_symbol="OsSKIPa",
        ncbi_gene_id=4331776,
        ncbi_locus_tag="LOC4331776",
        category="Viabilitas Sel & Ketahanan Reaktif Oksigen (ROS)",
        trait_description=(
            "SNW/SKI-Interacting Protein a. Faktor regulasi transkripsi yang meningkatkan toleransi terhadap kekeringan "
            "dan menekan stres oksidatif pada sel perakaran padi."
        ),
        target_strategy="CRISPRa Promoter Upregulation",
        pathway="Transcriptional Stress Machinery / ROS Scavenging",
        chromosome="2",
        key_publications=[
            "Hou et al., The Plant Cell (2009) 21:2150–2165"
        ]
    ),
    GeneticEngineeringTarget(
        id="snac1",
        gene_symbol="SNAC1",
        ncbi_gene_id=4334002,
        ncbi_locus_tag="LOC4334002",
        category="Regulasi Penutupan Stomata & Efisiensi Air",
        trait_description=(
            "Stress-Responsive NAC 1 (OsNAC9). Faktor transkripsi yang memicu penutupan stomata secara cepat "
            "saat defisit air di udara/tanah tanpa menurunkan laju fotosintesis netto."
        ),
        target_strategy="Targeted Base Editing / Rekayasa Promotor Spesifik Sel Penjaga (Guard Cell)",
        pathway="Stomatal Closure Regulation / Drought Resistance",
        chromosome="3",
        key_publications=[
            "Hu et al., PNAS (2006) 103:12987–12992"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-dst",
        gene_symbol="OsDST",
        ncbi_gene_id=4334341,
        ncbi_locus_tag="LOC4334341",
        category="Regulasi Kerapatan Stomata (Target Knockout)",
        trait_description=(
            "Drought and Salt Tolerance Zinc Finger TF. Regulator negatif penutupan stomata dan pengatur kerapatan stomata. "
            "Loss-of-function mutasi atau knockout OsDST memperlebar bukaan daun toleran kekeringan dan menurunkan transpirasi air hingga 30%."
        ),
        target_strategy="CRISPR/Cas9 Frameshift Knockout pada ekson 1 / Stop Codon Insertion",
        pathway="Negative Regulator of Stomatal Closure / H2O2 Accumulation",
        chromosome="3",
        key_publications=[
            "Huang et al., Genes & Development (2009) 23:1805–1817",
            "Santosh Kumar et al., Biotechnology Advances (2017)"
        ]
    ),
    GeneticEngineeringTarget(
        id="os-erf71",
        gene_symbol="OsERF71",
        ncbi_gene_id=4330107,
        ncbi_locus_tag="LOC4330107",
        category="Arsitektur Perakaran Lahan Kering",
        trait_description=(
            "AP2/ERF Transcription Factor yang merombak struktur perakaran padi menjadi lebih tebal dan dalam, "
            "memungkinkan penyerapan air dari lapisan akuifer tanah yang lebih dalam saat lapisan atas mengering."
        ),
        target_strategy="Promoter Modification / Root-Specific Overexpression",
        pathway="Root Morphology Remodeling / Drought Escape",
        chromosome="2",
        key_publications=[
            "Lee et al., Plant Physiology (2016) 172:575–588"
        ]
    )
]

TARGETS_BY_ID: Dict[str, GeneticEngineeringTarget] = {t.id: t for t in RICE_TARGETS}
TARGETS_BY_GENE_ID: Dict[int, GeneticEngineeringTarget] = {t.ncbi_gene_id: t for t in RICE_TARGETS}
TARGETS_BY_SYMBOL: Dict[str, GeneticEngineeringTarget] = {t.gene_symbol.lower(): t for t in RICE_TARGETS}


def get_target_by_identifier(query: str) -> Optional[GeneticEngineeringTarget]:
    q = query.strip().lower()
    if q in TARGETS_BY_ID:
        return TARGETS_BY_ID[q]
    if q in TARGETS_BY_SYMBOL:
        return TARGETS_BY_SYMBOL[q]
    try:
        gid = int(query)
        if gid in TARGETS_BY_GENE_ID:
            return TARGETS_BY_GENE_ID[gid]
    except ValueError:
        pass
    return None
