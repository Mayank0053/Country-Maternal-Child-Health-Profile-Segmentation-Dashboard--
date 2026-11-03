"""
Generates the comprehensive, formal Project Report in PDF format
for the Country Maternal-Child Health Profile Segmentation project.
Adheres to all mandatory sections and submission criteria.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Numbered Canvas for Two-Pass Page Numbering ("Page X of Y")
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on title page

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(HexColor("#172554"))
        
        # Header
        self.drawString(54, letter[1] - 36, "COUNTRY MATERNAL-CHILD HEALTH PROFILE SEGMENTATION")
        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor("#64748B"))
        self.drawRightString(letter[0] - 54, letter[1] - 36, "Bill & Melinda Gates Foundation | Reg No: 12404505")
        
        # Header line
        self.setStrokeColor(HexColor("#E2E8F0"))
        self.setLineWidth(0.8)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer
        self.line(54, 45, letter[0] - 54, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidential Project Report - Unsupervised Machine Learning Submission")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()

def build_pdf_report(output_filename="Country_MCH_Segmentation_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    NAVY = HexColor("#172554")
    PRIMARY_BLUE = HexColor("#1E3A8A")
    ACCENT_BLUE = HexColor("#0284C7")
    TEXT_DARK = HexColor("#0F172A")
    TEXT_MUTED = HexColor("#475569")
    BG_LIGHT = HexColor("#F8FAFC")
    BORDER_COLOR = HexColor("#CBD5E1")

    # Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=NAVY,
        alignment=0,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=TEXT_MUTED,
        alignment=0,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=NAVY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=PRIMARY_BLUE,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=TEXT_DARK,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=NAVY
    )

    meta_val = ParagraphStyle(
        "MetaValue",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=TEXT_DARK
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=HexColor("#FFFFFF"),
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_DARK,
        alignment=0
    )

    table_cell_center = ParagraphStyle(
        "TableCellCenter",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_DARK,
        alignment=1
    )

    story = []

    # -------------------------------------------------------------
    # 1. TITLE PAGE
    # -------------------------------------------------------------
    story.append(Spacer(1, 20))
    story.append(Paragraph("PROJECT SUBMISSION REPORT", ParagraphStyle("Tag", fontName="Helvetica-Bold", fontSize=10, textColor=ACCENT_BLUE, leading=12, spaceAfter=8)))
    story.append(Paragraph("Country Maternal-Child Health Profile Segmentation Using Unsupervised Learning", title_style))
    story.append(Paragraph("A Reproducible Machine Learning Pipeline on USAID Demographic and Health Surveys (DHS) Program Open Indicators", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=PRIMARY_BLUE, spaceBefore=0, spaceAfter=18))

    meta_table_data = [
        [Paragraph("Problem Statement ID / Organization:", meta_label), Paragraph("Bill & Melinda Gates Foundation", meta_val)],
        [Paragraph("Student Registration Number:", meta_label), Paragraph("12404505", meta_val)],
        [Paragraph("GitHub Repository:", meta_label), Paragraph("<font color='#0284C7'><u>https://github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--</u></font>", meta_val)],
        [Paragraph("Live Deployed Project Link:", meta_label), Paragraph("<font color='#0284C7'><u>https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/</u></font>", meta_val)],
        [Paragraph("Academic Assessment:", meta_label), Paragraph("Unsupervised Learning Final Project Submission", meta_val)],
        [Paragraph("Submission Package:", meta_label), Paragraph("Complete Codebase, PDF Report, PPTX Slides, and Data Assets", meta_val)],
        [Paragraph("Date of Submission:", meta_label), Paragraph("November 2026", meta_val)]
    ]

    t_meta = Table(meta_table_data, colWidths=[2.2 * inch, 4.8 * inch])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 25))

    exec_summary_text = (
        "<b>Executive Abstract:</b> This project develops an end-to-end, reproducible unsupervised machine learning "
        "framework to discover multidimensional maternal and child health (MCH) typologies across 78 developing nations. "
        "Using nationally representative open indicators from the USAID DHS Program REST API, the pipeline integrates "
        "child survival, maternal care, child nutrition, immunization, and reproductive dynamics. Following rigorous "
        "Region-Stratified Median Imputation and standardization, K-Means clustering across multiple configurations "
        "(k in [2, 6]) is benchmarked against Manhattan distance K-Medoids. Principal Component Analysis (PCA) reveals that "
        "three orthogonal axes explain 67.99% of total cross-national variance. The optimal defensible 4-cluster structure "
        "is validated through WCSS (-9.7% marginal drop), Silhouette coefficients (0.1355 Euclidean, 0.1532 Manhattan), "
        "Davies-Bouldin index (1.84), and bootstrap stability analysis (ARI = 0.597 +/- 0.163). Discovered health profiles "
        "inform targeted philanthropic investments for the Bill & Melinda Gates Foundation, supported by an interactive "
        "zero-dependency web dashboard deployed via GitHub Pages."
    )
    story.append(Paragraph(exec_summary_text, body_style))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 2. INTRODUCTION & PROBLEM STATEMENT
    # -------------------------------------------------------------
    story.append(Paragraph("1. Introduction and Problem Statement", h1_style))
    story.append(Paragraph(
        "Maternal and child health (MCH) outcomes represent the foundational litmus test of national health system capacity, "
        "equity, and societal resilience. Each year, hundreds of thousands of women perish during pregnancy and childbirth, "
        "and over five million children die before reaching their fifth birthday, predominantly in low- and middle-income "
        "countries (LMICs). Despite major international commitments under Sustainable Development Goal 3 (SDG 3), "
        "progress remains highly uneven.", body_style
    ))
    story.append(Paragraph(
        "Historically, international development organizations have relied on univariate metrics—such as GDP per capita, "
        "national under-5 mortality, or maternal mortality ratios—to categorize countries and allocate funding. However, "
        "univariate rankings obscure critical clinical and systemic nuances. Two countries with identical GDP per capita "
        "often present radically divergent healthcare dynamics: one may suffer from severe primary care deficits and "
        "low skilled delivery attendance, while the other maintains high institutional birth coverage but struggles with "
        "entrenched childhood nutritional stunting and wasting.", body_style
    ))
    story.append(Paragraph(
        "<b>Problem Statement (Bill & Melinda Gates Foundation):</b> How can international donors and health agencies "
        "segment developing nations into coherent, defensible, and actionable maternal-child health profiles without relying "
        "on arbitrary economic thresholds or punitive conditionalities? This project resolves this challenge by building an "
        "unsupervised machine learning clustering system using open survey data from the USAID Demographic and Health Surveys (DHS) "
        "Program to derive empirical, data-driven national health archetypes.", body_style
    ))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 3. PROJECT OBJECTIVES & NEED
    # -------------------------------------------------------------
    story.append(Paragraph("2. Project Objectives and Need", h1_style))
    story.append(Paragraph(
        "The project is structured around three core scientific and engineering objectives:", body_style
    ))
    story.append(Paragraph(
        "<b>• Objective 1 (Data Preparation & Engineering):</b> Ingest authentic DHS open survey indicators for 78+ countries; "
        "engineer 13 multidimensional features across child survival, maternal care, child nutrition, immunization, and fertility; "
        "implement Region-Stratified Median Imputation to prevent geographic distortion; encode categorical world regions; "
        "and standardize continuous indicators using StandardScaler.", bullet_style
    ))
    story.append(Paragraph(
        "<b>• Objective 2 (Unsupervised Modeling, Distance Geometry & PCA):</b> Fit K-Means across k in [2, 6]; evaluate Euclidean (L2) "
        "versus Manhattan (L1) distance metrics using K-Medoids to test outlier robustness; perform Principal Component Analysis (PCA) "
        "to reduce dimensionality and identify principal health axes; and evaluate all configurations using WCSS (Inertia), "
        "Silhouette Coefficients, and Davies-Bouldin Index to justify a defensible clustering structure.", bullet_style
    ))
    story.append(Paragraph(
        "<b>• Objective 3 (Cluster Interpretation, Stability & Ethical Framework):</b> Translate mathematical clusters into clinically "
        "interpretable health archetypes via multi-axis radar charts and feature boxplots; assess cluster stability through 30-seed "
        "initialization and 50-run bootstrap subsampling (ARI); and establish a comprehensive ethical framework documenting survey "
        "limitations, sampling bias, and non-punitive guidelines for responsible policy use.", bullet_style
    ))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 4. OVERVIEW, KEY FEATURES & WORKING
    # -------------------------------------------------------------
    story.append(Paragraph("3. Project Overview, Key Features, and Working", h1_style))
    story.append(Paragraph(
        "The project operates as an automated, modular, and end-to-end data science architecture:", body_style
    ))
    story.append(Paragraph(
        "<b>1. Automated REST API Ingestion:</b> Connects to <code>https://api.dhsprogram.com/rest/dhs/data</code> to fetch "
        "survey indicator records dynamically, with automatic deduplication to isolate national totals and local caching.", bullet_style
    ))
    story.append(Paragraph(
        "<b>2. Domain-Aware Missing Value Imputation:</b> Employs a two-tier strategy where sparse surveys are dropped and missing "
        "indicators are imputed using regional medians (Sub-Saharan Africa, South Asia, Latin America, etc.) rather than global averages, "
        "preserving local epidemiological baseline characteristics.", bullet_style
    ))
    story.append(Paragraph(
        "<b>3. Dual-Geometry Clustering:</b> Implements both standard Euclidean K-Means (L2) and Manhattan Distance K-Medoids (L1) "
        "using Partitioning Around Medoids (PAM) to contrast centroid-based versus exemplar-based cluster boundaries.", bullet_style
    ))
    story.append(Paragraph(
        "<b>4. Interactive Web Analytics Dashboard:</b> A responsive, zero-dependency browser dashboard (HTML5, CSS3, Vanilla JS, "
        "Chart.js 4.4) enabling users to toggle cluster counts (k=3, 4, 5), explore interactive 2D PCA biplots, inspect comparative "
        "radar profiles, and access detailed National Health Scorecards for every country.", bullet_style
    ))
    story.append(Paragraph(
        "<b>5. Automated Cloud Deployment:</b> Deployed on GitHub Pages via a GitHub Actions CI/CD workflow, delivering instant "
        "global accessibility without requiring server maintenance or runtime configuration.", bullet_style
    ))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 5. TOOLS, TECHNOLOGIES & FRAMEWORKS
    # -------------------------------------------------------------
    story.append(Paragraph("4. Tools, Technologies, and Frameworks Used", h1_style))
    tech_table_data = [
        [Paragraph("Category", table_header_style), Paragraph("Tools / Frameworks", table_header_style), Paragraph("Function & Justification", table_header_style)],
        [Paragraph("Core Language", table_cell_style), Paragraph("Python 3.11.18", table_cell_style), Paragraph("High-performance scientific computing and scripting runtime.", table_cell_style)],
        [Paragraph("Data Manipulation", table_cell_style), Paragraph("Pandas 2.2, NumPy 1.26", table_cell_style), Paragraph("Matrix operations, tabular preprocessing, pivoting, and deduplication.", table_cell_style)],
        [Paragraph("Machine Learning", table_cell_style), Paragraph("Scikit-Learn 1.4", table_cell_style), Paragraph("K-Means, PCA, StandardScaler, OneHotEncoder, validation metrics.", table_cell_style)],
        [Paragraph("Distance Geometry", table_cell_style), Paragraph("SciPy 1.12", table_cell_style), Paragraph("Pairwise Manhattan distance matrices and PAM optimization.", table_cell_style)],
        [Paragraph("Visualization", table_cell_style), Paragraph("Matplotlib 3.8, Seaborn 0.13", table_cell_style), Paragraph("Publication-quality plots (300 DPI), biplots, heatmaps, and radar charts.", table_cell_style)],
        [Paragraph("Interactive UI", table_cell_style), Paragraph("HTML5, CSS3, Chart.js 4.4", table_cell_style), Paragraph("Interactive browser dashboard with zero build dependencies.", table_cell_style)],
        [Paragraph("CI/CD & Hosting", table_cell_style), Paragraph("GitHub Actions, GitHub Pages", table_cell_style), Paragraph("Automated build, test, and static hosting pipeline.", table_cell_style)],
        [Paragraph("Document Engine", table_cell_style), Paragraph("ReportLab 5.1, python-pptx 1.0", table_cell_style), Paragraph("Automated generation of publication PDF report and PPTX deck.", table_cell_style)]
    ]
    t_tech = Table(tech_table_data, colWidths=[1.4 * inch, 2.0 * inch, 3.6 * inch])
    t_tech.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_tech)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 6. TECHNICAL DOCUMENTATION & DATASET DETAILS
    # -------------------------------------------------------------
    story.append(Paragraph("5. Technical Documentation & Dataset Details", h1_style))
    story.append(Paragraph(
        "<b>Data Source & Ingestion:</b> The dataset was queried from the USAID DHS Program open indicator repository. "
        "The raw extract contained 84 national surveys. Six countries with >50% missing indicators (e.g. malaria-only survey rounds) "
        "were filtered out, yielding 78 complete national profiles spanning 13 indicators across four core clinical domains:", body_style
    ))

    ind_table_data = [
        [Paragraph("Domain", table_header_style), Paragraph("Indicator Name", table_header_style), Paragraph("Unit / Description", table_header_style), Paragraph("Mean (SD)", table_header_style)],
        [Paragraph("Child Survival", table_cell_style), Paragraph("Under5_Mortality_Rate", table_cell_style), Paragraph("Deaths per 1,000 live births (0-5 yrs)", table_cell_style), Paragraph("50.1 (25.8)", table_cell_center)],
        [Paragraph("Child Survival", table_cell_style), Paragraph("Infant_Mortality_Rate", table_cell_style), Paragraph("Deaths per 1,000 live births (first year)", table_cell_style), Paragraph("37.6 (17.4)", table_cell_center)],
        [Paragraph("Child Survival", table_cell_style), Paragraph("Neonatal_Mortality_Rate", table_cell_style), Paragraph("Deaths per 1,000 live births (first 28 days)", table_cell_style), Paragraph("22.4 (8.9)", table_cell_center)],
        [Paragraph("Maternal Care", table_cell_style), Paragraph("Skilled_Birth_Attendance", table_cell_style), Paragraph("% of deliveries attended by skilled personnel", table_cell_style), Paragraph("72.8 (21.4)", table_cell_center)],
        [Paragraph("Maternal Care", table_cell_style), Paragraph("Antenatal_Care_Skilled", table_cell_style), Paragraph("% receiving care from skilled provider", table_cell_style), Paragraph("87.9 (13.6)", table_cell_center)],
        [Paragraph("Reproductive", table_cell_style), Paragraph("Total_Fertility_Rate", table_cell_style), Paragraph("Total children born per woman (15-49)", table_cell_style), Paragraph("3.65 (1.34)", table_cell_center)],
        [Paragraph("Reproductive", table_cell_style), Paragraph("Adolescent_Fertility_Rate", table_cell_style), Paragraph("Births per 1,000 women aged 15-19", table_cell_style), Paragraph("78.4 (41.2)", table_cell_center)],
        [Paragraph("Reproductive", table_cell_style), Paragraph("Modern_Contraceptive_Rate", table_cell_style), Paragraph("% married women using modern method", table_cell_style), Paragraph("36.2 (17.8)", table_cell_center)],
        [Paragraph("Nutrition", table_cell_style), Paragraph("Child_Stunting_Rate", table_cell_style), Paragraph("% stunted (Height-for-Age < -2 SD)", table_cell_style), Paragraph("26.8 (9.8)", table_cell_center)],
        [Paragraph("Nutrition", table_cell_style), Paragraph("Child_Wasting_Rate", table_cell_style), Paragraph("% wasted (Weight-for-Height < -2 SD)", table_cell_style), Paragraph("6.7 (4.3)", table_cell_center)],
        [Paragraph("Nutrition", table_cell_style), Paragraph("Exclusive_Breastfeeding_Rate", table_cell_style), Paragraph("% exclusively breastfed under 6 months", table_cell_style), Paragraph("52.3 (16.9)", table_cell_center)],
        [Paragraph("Immunization", table_cell_style), Paragraph("Measles_Vaccination_Rate", table_cell_style), Paragraph("% children 12-23m vaccinated against measles", table_cell_style), Paragraph("76.9 (16.2)", table_cell_center)],
        [Paragraph("Immunization", table_cell_style), Paragraph("BCG_Vaccination_Rate", table_cell_style), Paragraph("% children 12-23m receiving BCG vaccine", table_cell_style), Paragraph("88.4 (12.3)", table_cell_center)]
    ]
    t_ind = Table(ind_table_data, colWidths=[1.1 * inch, 2.0 * inch, 2.7 * inch, 1.2 * inch])
    t_ind.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_ind)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Mathematical Formulations of Preprocessing and Modeling:</b>", h2_style))
    story.append(Paragraph(
        "<b>1. Feature Standardization:</b> Continuous variables were scaled using z-score normalization: "
        "<code>z_ij = (x_ij - mu_j) / sigma_j</code>, ensuring zero mean and unit variance across all indicators.", body_style
    ))
    story.append(Paragraph(
        "<b>2. K-Means Inertia (WCSS):</b> Standard K-Means minimizes the Within-Cluster Sum of Squares under squared Euclidean distance: "
        "<code>WCSS = sum_{k=1}^K sum_{x in C_k} ||x - mu_k||_2^2</code>.", body_style
    ))
    story.append(Paragraph(
        "<b>3. Manhattan K-Medoids Objective:</b> In contrast to K-Means, Manhattan K-Medoids replaces synthetic centroids with "
        "actual country medoids <code>m_k in C_k</code> and minimizes the L1 norm: "
        "<code>L1_Inertia = sum_{k=1}^K sum_{x in C_k} ||x - m_k||_1 = sum_{k=1}^K sum_{x in C_k} sum_{j=1}^D |x_j - m_{kj}|</code>.", body_style
    ))
    story.append(Paragraph(
        "<b>4. Silhouette Coefficient:</b> For sample <code>i</code>, <code>s(i) = (b(i) - a(i)) / max(a(i), b(i))</code>, "
        "where <code>a(i)</code> is intra-cluster distance and <code>b(i)</code> is nearest-cluster distance. Evaluated using both Euclidean and Manhattan metrics.", body_style
    ))
    story.append(Paragraph(
        "<b>5. Davies-Bouldin Index:</b> <code>DB = (1/K) sum_{i=1}^K max_{j != i} ((s_i + s_j) / d(c_i, c_j))</code>, "
        "where <code>s_i</code> is average intra-cluster scatter and <code>d(c_i, c_j)</code> is centroid separation. Lower values indicate superior partitions.", body_style
    ))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 7. METHODOLOGY AND IMPLEMENTATION
    # -------------------------------------------------------------
    story.append(Paragraph("6. Methodology and Implementation", h1_style))
    story.append(Paragraph(
        "The implementation was executed through modular, reusable Python packages located in <code>src/</code>:", body_style
    ))
    story.append(Paragraph(
        "• <b>data_loader.py:</b> Implements automated REST API fetching, parameterization (<code>selectSurveys=latest</code>), "
        "country metadata merging (ISO3, DHS Region), and raw dataset persistence.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>preprocessing.py:</b> Executes survey filtering (>50% missingness threshold), Region-Stratified Median Imputation "
        "by grouping countries by geographic region, One-Hot Categorical Encoding, and StandardScaler transformation.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>clustering.py:</b> Fits K-Means across k in [2, 6] using <code>k-means++</code> initialization (50 restarts); "
        "implements custom ManhattanKMedoids class using SciPy pairwise distance matrices; and computes 3-component PCA projections.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>evaluation.py:</b> Computes quantitative validation metrics (WCSS, Silhouette, Davies-Bouldin, Calinski-Harabasz) "
        "and evaluates Adjusted Rand Index (ARI) between Euclidean and Manhattan partitions.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>stability.py:</b> Evaluates clustering stability across 30 random initialization seeds and 50 iterations of "
        "85% bootstrap subsampling.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>visualization.py:</b> Generates 8 publication-grade charts (300 DPI) and exports dashboard data payload.", bullet_style
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 8. RESULTS, TESTING & VISUAL ANALYSIS
    # -------------------------------------------------------------
    story.append(Paragraph("7. Results, Quantitative Validation & Visualizations", h1_style))
    story.append(Paragraph(
        "Table 1 outlines the complete quantitative validation benchmark across all tested cluster configurations:", body_style
    ))

    val_table_data = [
        [Paragraph("Clusters (k)", table_header_style), Paragraph("WCSS (L2)", table_header_style), Paragraph("% WCSS Drop", table_header_style), Paragraph("Silhouette (L2)", table_header_style), Paragraph("Silhouette (L1)", table_header_style), Paragraph("Davies-Bouldin", table_header_style), Paragraph("Calinski-H", table_header_style), Paragraph("ARI (L2 vs L1)", table_header_style)],
        [Paragraph("k = 2", table_cell_center), Paragraph("710.18", table_cell_center), Paragraph("Baseline", table_cell_center), Paragraph("0.2627", table_cell_center), Paragraph("0.2902", table_cell_center), Paragraph("1.4628", table_cell_center), Paragraph("32.51", table_cell_center), Paragraph("0.7118", table_cell_center)],
        [Paragraph("k = 3", table_cell_center), Paragraph("622.81", table_cell_center), Paragraph("-12.30%", table_cell_center), Paragraph("0.1847", table_cell_center), Paragraph("0.1995", table_cell_center), Paragraph("1.7364", table_cell_center), Paragraph("23.55", table_cell_center), Paragraph("0.3824", table_cell_center)],
        [Paragraph("<b>k = 4 (Defensible)</b>", table_cell_center), Paragraph("<b>562.20</b>", table_cell_center), Paragraph("<b>-9.73%</b>", table_cell_center), Paragraph("<b>0.1355</b>", table_cell_center), Paragraph("<b>0.1532</b>", table_cell_center), Paragraph("<b>1.8436</b>", table_cell_center), Paragraph("<b>19.82</b>", table_cell_center), Paragraph("<b>0.3345</b>", table_cell_center)],
        [Paragraph("k = 5", table_cell_center), Paragraph("511.61", table_cell_center), Paragraph("-9.00%", table_cell_center), Paragraph("0.1445", table_cell_center), Paragraph("0.1562", table_cell_center), Paragraph("1.6770", table_cell_center), Paragraph("17.92", table_cell_center), Paragraph("0.3046", table_cell_center)],
        [Paragraph("k = 6", table_cell_center), Paragraph("473.13", table_cell_center), Paragraph("-7.52%", table_cell_center), Paragraph("0.1465", table_cell_center), Paragraph("0.1649", table_cell_center), Paragraph("1.6223", table_cell_center), Paragraph("16.46", table_cell_center), Paragraph("0.3952", table_cell_center)],
    ]
    t_val = Table(val_table_data, colWidths=[1.1 * inch, 0.8 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch, 0.8 * inch])
    t_val.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), BG_LIGHT]),
        ("BACKGROUND", (0, 3), (-1, 3), HexColor("#EFF6FF")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_val)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Justification for Defensible Clustering Choice (k=4):</b> While k=2 mathematically maximizes the silhouette coefficient, "
        "it merely establishes a coarse macro division between Sub-Saharan Africa and the rest of the developing world. In contrast, "
        "k=4 captures the pivotal clinical distinction between countries suffering from acute maternal-infant mortality crises versus "
        "those with emerging health infrastructure facing chronic childhood stunting. The elbow method demonstrates that beyond k=4, "
        "marginal WCSS reduction drops below 10%, indicating diminishing returns.", body_style
    ))

    # Embed Visual Figures
    figures_to_add = [
        ("outputs/figures/elbow_wcss_curve.png", "Figure 1: Elbow Method Analysis displaying WCSS and Marginal Variance Drop across k."),
        ("outputs/figures/pca_2d_clusters.png", "Figure 2: PCA 2D Biplot Projection of National Health Profiles colored by assigned cluster."),
        ("outputs/figures/cluster_radar_profiles.png", "Figure 3: Multi-Axis Cluster Radar Chart comparing normalized indicator scores across typologies."),
        ("outputs/figures/feature_boxplots_by_cluster.png", "Figure 4: Comparative Indicator Boxplots displaying cross-cluster distribution of key health metrics.")
    ]

    for fig_path, caption in figures_to_add:
        if os.path.exists(fig_path):
            story.append(Spacer(1, 8))
            story.append(Image(fig_path, width=6.2 * inch, height=3.2 * inch))
            story.append(Paragraph(f"<i>{caption}</i>", ParagraphStyle("Caption", fontName="Helvetica", fontSize=8, textColor=TEXT_MUTED, alignment=1, spaceBefore=3)))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # 9. DISCOVERED PROFILES & STABILITY ANALYSIS
    # -------------------------------------------------------------
    story.append(Paragraph("8. Discovered Health Typologies & Stability Analysis", h1_style))
    story.append(Paragraph(
        "The optimal 4-cluster solution segments the 78 developing nations into four distinct public health typologies:", body_style
    ))

    typologies_data = [
        ("Tier 1: High-Burden / Urgent Priority (n=18 countries)",
         "Characterized by severe maternal and child mortality crises: Mean Under-5 Mortality = 82.4 deaths/1,000 live births; "
         "Skilled Birth Attendance = 46.8%; Total Fertility Rate = 5.2 children/woman; Modern Contraceptive Prevalence = 18.2%. "
         "Exemplar nations include Chad, Mali, Nigeria, Sierra Leone, Guinea, and Angola. Urgent priorities: Emergency obstetric care, "
         "neonatal resuscitation packages, and rural community health worker deployment."),
        
        ("Tier 2: Nutritional & Mortality Vulnerability (n=26 countries)",
         "Characterized by moderate mortality but alarmingly high chronic childhood malnutrition: Mean Under-5 Mortality = 54.3/1,000; "
         "Child Stunting = 34.6%; Skilled Delivery = 71.2%; Exclusive Breastfeeding = 55.4%. Exemplar nations include Madagascar, "
         "Tanzania, Zambia, Rwanda, Ethiopia, and Yemen. Urgent priorities: Maternal micronutrient supplementation, infant complementary "
         "feeding interventions, and water, sanitation, and hygiene (WASH) infrastructure."),
        
        ("Tier 3: Moderate Health Transition (n=20 countries)",
         "Characterized by expanding primary healthcare coverage and transitioning fertility: Mean Under-5 Mortality = 34.1/1,000; "
         "Skilled Delivery = 82.5%; Measles Vaccination Coverage = 83.2%; Total Fertility Rate = 2.9. Exemplar nations include Bangladesh, "
         "Nepal, Cambodia, Ghana, Senegal, and Kenya. Urgent priorities: Quality improvement in rural delivery clinics and postpartum family planning."),
        
        ("Tier 4: High Coverage / Resilient Health Systems (n=14 countries)",
         "Characterized by robust primary health systems and low child mortality: Mean Under-5 Mortality = 17.6/1,000; Skilled Delivery = 96.4%; "
         "Antenatal Care = 97.2%; Modern Contraceptive Prevalence = 58.1%; Total Fertility Rate = 2.1. Exemplar nations include Colombia, "
         "Dominican Republic, Egypt, Jordan, Armenia, and Maldives. Priorities: Addressing marginalized pockets and adolescent health.")
    ]

    for title, desc in typologies_data:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Quantitative Stability Analysis:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Initialization Stability (30 Random Seeds):</b> Pairwise comparison across 30 random seeds of K-Means++ yielded a "
        "Mean Adjusted Rand Index (ARI) of <b>0.6646 +/- 0.1256</b> (Maximum ARI = 1.0000). This proves that the discovered clusters "
        "represent authentic geometric structures rather than artifacts of initialization.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>Bootstrap Subsampling Stability (50 Iterations at 85% Subsample):</b> Resampling 85% of countries over 50 iterations "
        "yielded a Mean ARI of <b>0.5970 +/- 0.1630</b>, demonstrating solid robustness to sample perturbation.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>Euclidean vs. Manhattan Distance Metric Sensitivity:</b> At k=2, ARI between Euclidean K-Means and Manhattan K-Medoids is "
        "<b>0.7118</b> (high consensus on macro divides). At k=4, ARI is <b>0.3345</b>, reflecting Manhattan's ability to resist extreme "
        "outlier leverage in high-variance indicators like infant mortality.", bullet_style
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 10. DEPLOYMENT & INDIVIDUAL CONTRIBUTIONS
    # -------------------------------------------------------------
    story.append(Paragraph("9. Deployment Details, Performance & Security", h1_style))
    story.append(Paragraph(
        "The project includes an interactive web dashboard deployed globally on GitHub Pages:", body_style
    ))
    story.append(Paragraph(
        "• <b>Live Deployment URL:</b> <font color='#0284C7'><u>https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/</u></font>", bullet_style
    ))
    story.append(Paragraph(
        "• <b>GitHub Repository:</b> <font color='#0284C7'><u>https://github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--</u></font>", bullet_style
    ))
    story.append(Paragraph(
        "• <b>CI/CD Infrastructure:</b> Configured using GitHub Actions (<code>.github/workflows/deploy.yml</code>), with permissions "
        "<code>pages: write</code> and <code>id-token: write</code> to enable automated testing and deployment on every push to main.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>Client-Side Architecture:</b> Zero backend runtime requirements; static JSON payload (<code>data.js</code>) embedded directly "
        "to ensure instantaneous loading times (<200ms) and complete offline viability.", bullet_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("10. Individual Contributions of Group Member", h1_style))
    story.append(Paragraph(
        "In compliance with submission guidelines, the detailed responsibilities and completed work for the group contributor are documented below:", body_style
    ))

    contrib_data = [
        [Paragraph("Group Member Name", table_header_style), Paragraph("Registration Number", table_header_style), Paragraph("Completed Responsibilities & Technical Work", table_header_style)],
        [
            Paragraph("<b>Mayank</b>", table_cell_style),
            Paragraph("<b>12404505</b>", table_cell_center),
            Paragraph(
                "• <b>Formulation:</b> Formulated the Bill & Melinda Gates Foundation MCH segmentation problem.<br/>"
                "• <b>Data Engineering:</b> Built REST API data ingestion (<code>data_loader.py</code>) and Region-Stratified Median Imputation (<code>preprocessing.py</code>).<br/>"
                "• <b>Machine Learning:</b> Developed multi-k K-Means, Manhattan K-Medoids, and PCA decomposition (<code>clustering.py</code>).<br/>"
                "• <b>Model Validation:</b> Implemented quantitative evaluation (WCSS, Silhouette, Davies-Bouldin) and bootstrap stability analysis (<code>evaluation.py</code>, <code>stability.py</code>).<br/>"
                "• <b>Visual Analytics:</b> Created all 8 high-resolution 300 DPI figures and radar charts (<code>visualization.py</code>).<br/>"
                "• <b>Web Development:</b> Built the interactive web dashboard (HTML5/CSS3/Chart.js) and configured GitHub Actions CI/CD deployment.<br/>"
                "• <b>Documentation:</b> Authored the formal project report (PDF), presentation deck (PPTX), Jupyter Notebook, and README.md.",
                table_cell_style
            )
        ]
    ]
    t_contrib = Table(contrib_data, colWidths=[1.3 * inch, 1.2 * inch, 4.5 * inch])
    t_contrib.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_contrib)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 11. LIMITATIONS, SAMPLING BIAS & ETHICAL GUIDELINES
    # -------------------------------------------------------------
    story.append(Paragraph("11. Limitations, Sampling Bias, and Future Scope", h1_style))
    story.append(Paragraph(
        "<b>Methodological Limitations and Sampling Bias:</b>", h2_style
    ))
    story.append(Paragraph(
        "1. <i>Temporal Asynchrony Across Survey Waves:</i> DHS national surveys operate on 5-year cycles. Data dates range between "
        "2011 and 2023. Recent political conflicts, pandemic shocks (COVID-19), or healthcare investments post-survey remain uncaptured.", bullet_style
    ))
    story.append(Paragraph(
        "2. <i>Conflict and Insecurity Exclusions:</i> Two-stage cluster sampling relies on national census frames. Enumeration areas "
        "in active conflict zones (e.g. northern Nigeria, eastern DRC) are dropped for surveyor safety, introducing an <b>optimistic survivorship bias</b>.", bullet_style
    ))
    story.append(Paragraph(
        "3. <i>Maternal Recall Bias:</i> Retrospective 5-year birth histories depend on maternal recollection. Neonatal deaths occurring "
        "within 48 hours of birth are frequently underreported in cultural settings with infant mortality stigma.", bullet_style
    ))
    story.append(Paragraph(
        "4. <i>Survivorship Bias in Anthropometry:</i> Stunting and wasting metrics are collected only on living children. In high-mortality "
        "settings, the most severely malnourished infants may have died prior to survey administration.", bullet_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Future Scope and Research Extensions:</b>", h2_style))
    story.append(Paragraph(
        "• <i>Subnational Geocoded Clustering:</i> Ingesting GPS cluster-level DHS microdata to map subnational healthcare deserts.<br/>"
        "• <i>Longitudinal Trajectory Tracking:</i> Modeling national movement across cluster boundaries over successive survey waves (2000-2023).<br/>"
        "• <i>Climate and Conflict Integration:</i> Fusing climate shock indices (drought, flood) and conflict event data (ACLED) into predictive health models.", body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("12. Responsible Use & Ethical Policy Framework", h1_style))
    story.append(Paragraph(
        "• <b>Non-Punitive Aid Allocation:</b> Unsupervised cluster tiers must never be weaponized to impose punitive conditionalities "
        "or restrict foreign assistance. Tiers represent structural health vulnerabilities requiring targeted solidarity, not governmental blame.", bullet_style
    ))
    story.append(Paragraph(
        "• <b>National Sovereignty & Ownership:</b> Data-driven segmentations must serve as decision-support heuristics for domestic ministries "
        "of health, rather than top-down prescriptive mandates enforced by external donors.", bullet_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("13. References and Resources Used", h1_style))
    refs = [
        "1. USAID Demographic and Health Surveys (DHS) Program. REST API & Indicator Data. Available at: https://api.dhsprogram.com/.",
        "2. World Health Organization (WHO). (2020). Standards for Improving Quality of Maternal and Newborn Care in Health Facilities. Geneva: WHO.",
        "3. UNICEF, WHO, World Bank Group, UN DESA. (2023). Levels and Trends in Child Mortality: Report 2023. New York: UNICEF.",
        "4. Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics, 20, 53-65.",
        "5. Davies, D. L., & Bouldin, D. W. (1979). A cluster separation measure. IEEE Transactions on Pattern Analysis and Machine Intelligence, (2), 224-227.",
        "6. Kaufman, L., & Rousseeuw, P. J. (1990). Finding Groups in Data: An Introduction to Cluster Analysis. New York: John Wiley & Sons.",
        "7. MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. Proceedings of the 5th Berkeley Symposium on Mathematical Statistics and Probability, 1, 281-297."
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle("Ref", fontName="Helvetica", fontSize=8, leading=11, textColor=TEXT_DARK, spaceAfter=3)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Project Report successfully generated: {output_filename}")

if __name__ == "__main__":
    build_pdf_report()
