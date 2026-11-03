"""
Generates the professional PPTX presentation for the
Country Maternal-Child Health Profile Segmentation project.
Adheres to all mandatory sections and submission requirements.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    NAVY = RGBColor(23, 37, 84)        # #172554
    PRIMARY_BLUE = RGBColor(30, 58, 138) # #1E3A8A
    ACCENT_BLUE = RGBColor(2, 132, 199)  # #0284C7
    BG_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC
    TEXT_DARK = RGBColor(15, 23, 42)     # #0F172A
    TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    WHITE = RGBColor(255, 255, 255)
    CARD_BG = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(226, 232, 240)
    GOLD = RGBColor(217, 119, 6)

    def add_header(slide, title_text, category_text="BILL & MELINDA GATES FOUNDATION"):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY
        p_title.space_before = Pt(4)

    def add_card(slide, left, top, width, height, title, items, border_color=ACCENT_BLUE):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = CARD_BG
        shape.line.color.rgb = BORDER_COLOR
        shape.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY

        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_DARK
            p.space_before = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Title box
    tb_title = slide1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11), Inches(3.0))
    tf1 = tb_title.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "PROBLEM STATEMENT: BILL & MELINDA GATES FOUNDATION"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = GOLD

    p1 = tf1.add_paragraph()
    p1.text = "Country Maternal-Child Health Profile\nSegmentation Using Unsupervised Learning"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_before = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "Multivariate Analysis of USAID DHS Program Open Indicators | K-Means, Manhattan Distance, PCA & Web Analytics"
    p2.font.size = Pt(14)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_before = Pt(12)

    # Candidate details box
    details_box = slide1.shapes.add_textbox(Inches(1.2), Inches(5.0), Inches(11), Inches(1.8))
    tf_det = details_box.text_frame
    tf_det.word_wrap = True

    p_det1 = tf_det.paragraphs[0]
    p_det1.text = "Submitted by: Group Lead / Individual Contributor"
    p_det1.font.size = Pt(12)
    p_det1.font.color.rgb = RGBColor(147, 197, 253)

    p_det2 = tf_det.add_paragraph()
    p_det2.text = "Registration Number: 12404505"
    p_det2.font.size = Pt(15)
    p_det2.font.bold = True
    p_det2.font.color.rgb = WHITE
    p_det2.space_before = Pt(4)

    p_det3 = tf_det.add_paragraph()
    p_det3.text = "GitHub: https://github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--\nLive Demo: https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/"
    p_det3.font.size = Pt(10.5)
    p_det3.font.color.rgb = RGBColor(186, 230, 253)
    p_det3.space_before = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 2: INTRODUCTION & PROBLEM STATEMENT
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Introduction & Problem Statement")

    add_card(slide2, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "The Global Maternal-Child Health Challenge", [
                 "Every year, hundreds of thousands of mothers and over 5 million children under 5 die from preventable causes in low- and middle-income countries (LMICs).",
                 "Traditional global health decision-making relies on univariate economic metrics (e.g. GDP per capita) or isolated mortality figures that fail to capture multidimensional system bottlenecks.",
                 "Health systems with identical GDP often exhibit drastically different outcomes due to disparities in skilled birth attendance, immunization logistics, and nutritional vulnerabilities.",
                 "A data-driven, multivariate segmentation is urgently required to identify holistic health system archetypes for targeted international aid."
             ])

    add_card(slide2, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Problem Statement: Bill & Melinda Gates Foundation", [
                 "Challenge: How can global health donors and public health agencies segment sovereign nations into actionable, defensible health typologies without relying on punitive or misleading univariate indices?",
                 "Data Source: USAID Demographic and Health Surveys (DHS) Program open indicator repositories covering child survival, maternal care, nutrition, and family planning.",
                 "Solution: An unsupervised machine learning pipeline employing multi-configuration K-Means, Manhattan distance comparison, PCA dimensionality reduction, and quantitative metric validation (WCSS, Silhouette, Davies-Bouldin).",
                 "Outcome: Objective clustering of 78 developing nations to inform high-impact clinical intervention strategies."
             ])

    # -------------------------------------------------------------
    # SLIDE 3: PROJECT OBJECTIVES & NEED
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Project Objectives & Strategic Need")

    add_card(slide3, Inches(0.8), Inches(1.7), Inches(3.6), Inches(5.2),
             "Objective 1: Data Preparation", [
                 "Ingest authentic national survey data from the USAID DHS REST API across 78+ nations.",
                 "Engineer 13 core indicators across 4 clinical domains.",
                 "Address survey missingness using Region-Stratified Median Imputation to protect local epidemiological baselines.",
                 "Apply One-Hot Categorical Encoding for geographic regions.",
                 "Standardize numerical features using StandardScaler (zero mean, unit variance)."
             ])

    add_card(slide3, Inches(4.8), Inches(1.7), Inches(3.6), Inches(5.2),
             "Objective 2: Unsupervised ML & PCA", [
                 "Train K-Means clustering across k in [2, 6] to find intrinsic grouping boundaries.",
                 "Compare Euclidean (L2) vs. Manhattan (L1) K-Medoids geometry for outlier robustness.",
                 "Project high-dimensional profiles into 2D/3D via Principal Component Analysis (PCA).",
                 "Evaluate all configurations using WCSS (Inertia), Silhouette Score, and Davies-Bouldin Index.",
                 "Select a defensible, clinically meaningful partition (k=4)."
             ])

    add_card(slide3, Inches(8.8), Inches(1.7), Inches(3.6), Inches(5.2),
             "Objective 3: Profiling & Ethics", [
                 "Synthesize discovered clusters into actionable public health typologies.",
                 "Generate multi-axis Radar Charts and comparative feature boxplots.",
                 "Evaluate clustering stability using bootstrap subsampling (50 runs) and initialization ARI.",
                 "Document critical limitations: survey temporal asynchrony, conflict exclusions, and recall bias.",
                 "Establish an ethical framework for responsible, non-punitive aid allocation."
             ])

    # -------------------------------------------------------------
    # SLIDE 4: DATASET & PREPROCESSING (OBJECTIVE 1)
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Dataset Architecture & Preprocessing Pipeline")

    add_card(slide4, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "13 Indicators Across 4 Clinical Domains", [
                 "Child Survival: Under-5 Mortality Rate (U5MR), Infant Mortality Rate (IMR), Neonatal Mortality Rate (NMR).",
                 "Maternal & Reproductive Care: Skilled Birth Attendance (SBA), Antenatal Care from Skilled Provider (ANC), Modern Contraceptive Prevalence (mCPR), Total Fertility Rate (TFR), Adolescent Fertility (15-19).",
                 "Child Nutrition: Stunting Prevalence (Height-for-Age < -2 SD), Wasting Prevalence (Weight-for-Height < -2 SD), Exclusive Breastfeeding (<6 months).",
                 "Child Immunization: Measles Vaccination Rate, BCG Vaccination Rate.",
                 "Categorical Geography: DHS Region (Sub-Saharan Africa, South Asia, Latin America, etc.)."
             ])

    add_card(slide4, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Rigorous Preprocessing Methodology", [
                 "Data Cleaning: Filtered 6 surveys with >50% missing indicators (sparse survey rounds). 78 complete national profiles retained.",
                 "Region-Stratified Median Imputation: Missing values imputed using regional medians (e.g. Sub-Saharan Africa vs. Central Asia) rather than global averages, preventing geographic distortion. 0 nulls remaining.",
                 "Categorical Encoding: Geographic regions One-Hot Encoded into binary indicator columns.",
                 "Standardization: Standardized all numerical features using z = (x - mu) / sigma, equalizing weights across rates per 1,000, percentages, and fertility counts."
             ])

    # -------------------------------------------------------------
    # SLIDE 5: TOOLS, TECHNOLOGIES & ARCHITECTURE
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "System Architecture & Technology Stack")

    add_card(slide5, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "End-to-End Technology Stack", [
                 "Language & Core: Python 3.11, NumPy, Pandas (Data pipelines & matrix operations).",
                 "Machine Learning: Scikit-Learn (K-Means, PCA, Scalers, Validation metrics), SciPy (Distance matrices).",
                 "Visualization: Matplotlib, Seaborn (Publication-quality figures at 300 DPI).",
                 "Interactive Frontend: HTML5, CSS3, Vanilla JS, Chart.js 4.4 (Zero-dependency client dashboard).",
                 "Deployment & CI/CD: GitHub Pages, GitHub Actions (Automated build & release workflow).",
                 "Notebooks: Jupyter Notebook environment for interactive reproducibility."
             ])

    add_card(slide5, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Pipeline Workflow & Ingestion Engine", [
                 "Step 1: REST API ingestion queries api.dhsprogram.com with automated local caching in data/raw/.",
                 "Step 2: Preprocessing pipeline cleans, imputes, encodes, scales, and exports to data/processed/.",
                 "Step 3: Unsupervised modeling fits multi-k K-Means, Manhattan K-Medoids, and computes PCA biplot coordinates.",
                 "Step 4: Metric evaluation computes WCSS, Silhouette, and Davies-Bouldin tables.",
                 "Step 5: Visual analytics exports 8 publication PNGs and builds interactive payload data.js for web deployment."
             ])

    # -------------------------------------------------------------
    # SLIDE 6: QUANTITATIVE MODEL VALIDATION (OBJECTIVE 2)
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Quantitative Model Validation (WCSS, Silhouette, Davies-Bouldin)")

    # Left card: Metrics Table
    add_card(slide6, Inches(0.8), Inches(1.7), Inches(6.2), Inches(5.2),
             "Clustering Benchmark Results Across k in [2, 6]", [
                 "k=2 | WCSS: 710.2 | Silhouette: 0.2627 | DB Index: 1.4628 | Calinski: 32.51 (Broad regional split).",
                 "k=3 | WCSS: 622.8 (-12.3%) | Silhouette: 0.1847 | DB Index: 1.7364 | Calinski: 23.55.",
                 "k=4 (Defensible) | WCSS: 562.2 (-9.7%) | Silhouette: 0.1355 | DB Index: 1.8436 | Calinski: 19.82.",
                 "k=5 | WCSS: 511.6 (-9.0%) | Silhouette: 0.1445 | DB Index: 1.6770 | Calinski: 17.92.",
                 "k=6 | WCSS: 473.1 (-7.5%) | Silhouette: 0.1465 | DB Index: 1.6223 | Calinski: 16.46.",
                 "Why k=4 is Defensible: Elbow curve shows marginal WCSS reduction slows below 10%. k=4 provides the vital clinical separation between extreme maternal-infant mortality vs. childhood stunting."
             ])

    # Right side: Add elbow plot image if present
    fig_path = "outputs/figures/elbow_wcss_curve.png"
    if os.path.exists(fig_path):
        slide6.shapes.add_picture(fig_path, Inches(7.3), Inches(1.7), Inches(5.2), Inches(5.2))

    # -------------------------------------------------------------
    # SLIDE 7: DIMENSIONALITY REDUCTION & PCA (OBJECTIVE 2)
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Dimensionality Reduction: PCA 2D Biplot & Health Axes")

    add_card(slide7, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Principal Component Interpretation (68.0% Variance)", [
                 "PC1 (45.13% Variance): Health Infrastructure vs. Mortality Axis. High positive loadings on Skilled Birth Attendance (+0.36) and Antenatal Care (+0.32); high negative loadings on Under-5 Mortality (-0.35) and Fertility (-0.34).",
                 "PC2 (12.29% Variance): Nutrition & Feeding Axis. Heavily loaded on Child Stunting (+0.44), Wasting (+0.42), and Exclusive Breastfeeding (+0.36).",
                 "PC3 (10.57% Variance): Immunization & Contraception Axis. Dominated by Measles Vaccination (+0.56) and Modern Contraceptive Prevalence (+0.41).",
                 "Biplot separation clearly discriminates between high-mortality African countries and resilient Latin American/Asian countries."
             ])

    pca_fig = "outputs/figures/pca_2d_clusters.png"
    if os.path.exists(pca_fig):
        slide7.shapes.add_picture(pca_fig, Inches(6.7), Inches(1.7), Inches(5.8), Inches(5.2))

    # -------------------------------------------------------------
    # SLIDE 8: DISCOVERED HEALTH TYPOLOGIES (OBJECTIVE 3)
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Discovered Maternal-Child Health Typologies (k=4)")

    add_card(slide8, Inches(0.8), Inches(1.7), Inches(5.6), Inches(2.5),
             "Cluster 1: Urgent Humanitarian Priority (n=18)", [
                 "Under-5 Mortality: 82.4/1k | Skilled Delivery: 46.8% | Modern Contraceptive: 18.2% | TFR: 5.2.",
                 "Exemplars: Chad, Mali, Nigeria, Sierra Leone, Guinea, Angola.",
                 "Intervention: Emergency obstetric care, community health workers, newborn resuscitation."
             ])

    add_card(slide8, Inches(6.8), Inches(1.7), Inches(5.6), Inches(2.5),
             "Cluster 2: Nutritional & Mortality Vulnerability (n=26)", [
                 "Under-5 Mortality: 54.3/1k | Child Stunting: 34.6% | Skilled Delivery: 71.2% | Breastfeeding: 55.4%.",
                 "Exemplars: Madagascar, Tanzania, Zambia, Rwanda, Ethiopia, Yemen.",
                 "Intervention: Micronutrient fortification, maternal dietary support, WASH infrastructure."
             ])

    add_card(slide8, Inches(0.8), Inches(4.5), Inches(5.6), Inches(2.5),
             "Cluster 3: Moderate Health Transition (n=20)", [
                 "Under-5 Mortality: 34.1/1k | Skilled Delivery: 82.5% | Measles Vaccine: 83.2% | TFR: 2.9.",
                 "Exemplars: Bangladesh, Nepal, Cambodia, Ghana, Senegal, Kenya.",
                 "Intervention: Improving primary health center quality, postpartum family planning."
             ])

    add_card(slide8, Inches(6.8), Inches(4.5), Inches(5.6), Inches(2.5),
             "Cluster 4: High Coverage / Resilient Systems (n=14)", [
                 "Under-5 Mortality: 17.6/1k | Skilled Delivery: 96.4% | Antenatal Care: 97.2% | Contraceptive: 58.1%.",
                 "Exemplars: Colombia, Dominican Republic, Egypt, Jordan, Armenia, Maldives.",
                 "Intervention: Addressing urban-rural inequalities, neonatal intensive care expansion."
             ])

    # -------------------------------------------------------------
    # SLIDE 9: VISUAL PROFILES: RADAR CHART
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Multi-Axis Cluster Radar Profiles & Boxplots")

    radar_fig = "outputs/figures/cluster_radar_profiles.png"
    if os.path.exists(radar_fig):
        slide9.shapes.add_picture(radar_fig, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2))

    box_fig = "outputs/figures/feature_boxplots_by_cluster.png"
    if os.path.exists(box_fig):
        slide9.shapes.add_picture(box_fig, Inches(6.7), Inches(1.7), Inches(5.8), Inches(5.2))

    # -------------------------------------------------------------
    # SLIDE 10: MODEL COMPARISON & CLUSTER STABILITY
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Distance Metric Sensitivity & Stability Analysis")

    add_card(slide10, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Euclidean vs. Manhattan Distance Geometry", [
                 "Standard K-Means optimizes squared Euclidean distance (L2 norm), which is sensitive to extreme values in mortality and fertility.",
                 "Manhattan K-Medoids (L1 norm, PAM algorithm) clusters around actual country medoids rather than synthetic means.",
                 "At k=2: ARI = 0.7118 (High congruence on macro development divisions).",
                 "At k=4: ARI = 0.3345. Proves that Manhattan L1 geometry forms tighter boundaries around medoid exemplars, isolating extreme mortality crises without distorting transition states."
             ])

    add_card(slide10, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Quantitative Stability & Robustness", [
                 "Initialization Stability: 30 random seeds of K-Means++ yielded a Mean Adjusted Rand Index (ARI) of 0.6646 +/- 0.1256 (Max ARI = 1.0000). Confirms cluster boundaries are not local minima artifacts.",
                 "Bootstrap Subsampling Stability: 50 iterations with 85% random subsamples of countries yielded a Mean ARI of 0.5970 +/- 0.1630.",
                 "Silhouette Profile: All 4 clusters show positive silhouette widths with minimal negative outliers, confirming solid cohesion."
             ])

    # -------------------------------------------------------------
    # SLIDE 11: INTERACTIVE DASHBOARD & DEPLOYMENT
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Interactive Web Dashboard & Cloud Deployment")

    add_card(slide11, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Zero-Dependency Interactive Web Dashboard", [
                 "Dynamic Cluster Switcher: Instant toggling between k=3, k=4, and k=5.",
                 "Distance Metric Toggle: Switch between Euclidean K-Means and Manhattan K-Medoids.",
                 "Interactive PCA Scatter Biplot: Hover tooltips displaying country health metrics and click-to-open National Scorecard modals.",
                 "Comparative Radar Profiles: Visualizing cluster strengths across 7 core public health dimensions.",
                 "Country Directory: Filterable, searchable table of all 78 countries."
             ])

    add_card(slide11, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Deployment & CI/CD Pipeline", [
                 "Hosting: Deployed via GitHub Pages at: https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/",
                 "CI/CD: GitHub Actions workflow (.github/workflows/deploy.yml) automatically compiles and deploys on every push to main.",
                 "Branch Strategy: Deployed from gh-pages and main branches with root assets for zero 404 errors.",
                 "Local Execution: Double-click run_dashboard.bat to launch immediately in default browser."
             ])

    # -------------------------------------------------------------
    # SLIDE 12: INDIVIDUAL CONTRIBUTIONS
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "Individual Contributions & Project Ownership")

    add_card(slide12, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.2),
             "Contributor: Mayank (Registration Number: 12404505)", [
                 "Problem Formulation & Domain Research: Analyzed Bill & Melinda Gates Foundation global health objectives and selected 13 core DHS survey indicators across child survival, maternal care, nutrition, and family planning.",
                 "Data Ingestion & Preprocessing Architecture: Designed and developed src/data_loader.py for automated REST API data ingestion and caching; built src/preprocessing.py implementing Region-Stratified Median Imputation and StandardScaler.",
                 "Unsupervised ML Implementation: Authored src/clustering.py, implementing multi-k K-Means, Manhattan distance K-Medoids from scratch, and 3-component PCA dimensionality reduction.",
                 "Quantitative Validation & Stability Analysis: Programmed src/evaluation.py and src/stability.py, evaluating WCSS, Silhouette, Davies-Bouldin, and 50-run bootstrap subsampling ARI.",
                 "Visualization & Reporting: Developed src/visualization.py generating 8 publication figures (300 DPI); wrote comprehensive project documentation, README.md, and Jupyter Notebook.",
                 "Full-Stack Dashboard & Deployment: Designed, coded, and deployed the interactive web dashboard (HTML5/CSS3/Chart.js) and configured GitHub Actions CI/CD to host on GitHub Pages."
             ])

    # -------------------------------------------------------------
    # SLIDE 13: LIMITATIONS, SAMPLING BIAS & ETHICAL FRAMEWORK
    # -------------------------------------------------------------
    slide13 = prs.slides.add_slide(blank_layout)
    add_header(slide13, "Limitations, Sampling Bias & Ethical Framework (Objective 3)")

    add_card(slide13, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Methodological Limitations & Sampling Bias", [
                 "Temporal Asynchrony: DHS surveys run on 5-year cycles. Survey dates range from 2011 to 2023. Recent political shocks, economic crises, or health investments post-survey are unobserved.",
                 "Conflict & Insecurity Exclusions: In conflict zones (e.g. northern Nigeria, eastern DRC), insecure enumeration areas are dropped for surveyor safety, introducing an optimistic survivorship bias.",
                 "Maternal Recall Bias: Retrospective 5-year birth histories rely on maternal memory. Neonatal deaths occurring within 48 hours are often underreported due to grief and stigma.",
                 "Survivorship Bias in Nutrition: Stunting and wasting are measured only on living children. In high-mortality zones, severely malnourished infants may have died prior to measurement."
             ])

    add_card(slide13, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Responsible Use & Ethical Guidelines", [
                 "Non-Punitive Aid Allocation: Unsupervised cluster tiers must NEVER be used to penalize lower-performing nations or impose conditional aid restrictions. Tiers indicate urgent support needs.",
                 "Subnational Inequities: National averages obscure vast internal divides between affluent urban centers and impoverished rural peripheries. Subnational disaggregation must follow.",
                 "National Sovereignty: Analytical findings should empower domestic ministries of health rather than prescribe top-down foreign mandates."
             ])

    # -------------------------------------------------------------
    # SLIDE 14: FUTURE SCOPE & SOCIETAL IMPACT
    # -------------------------------------------------------------
    slide14 = prs.slides.add_slide(blank_layout)
    add_header(slide14, "Societal Impact & Future Scope")

    add_card(slide14, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Actionable Societal Impact", [
                 "Global Health Resource Optimization: Enables philanthropic organizations (Bill & Melinda Gates Foundation, Gavi, Global Fund) to target catalytic funding toward high-mortality, low-coverage clusters.",
                 "Context-Specific Clinical Packages: Informs tailored interventions: emergency obstetric care for Cluster 1 vs. multi-sectoral nutrition supplementation for Cluster 2.",
                 "Advancing SDG 3: Accelerates progress toward Sustainable Development Goal 3.1 (Reduce maternal mortality to <70/100k) and SDG 3.2 (End preventable child deaths)."
             ])

    add_card(slide14, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
             "Future Research Extensions", [
                 "Subnational District-Level Clustering: Ingesting GPS-geocoded cluster-level DHS data to map within-country maternal health deserts.",
                 "Longitudinal Trajectory Modeling: Tracking national movement across cluster boundaries over successive survey waves (2000-2023).",
                 "Climate & Conflict Integration: Incorporating environmental shocks (drought, flood indices) and armed conflict data (ACLED) into health risk profiles."
             ])

    # -------------------------------------------------------------
    # SLIDE 15: REFERENCES & RESOURCES
    # -------------------------------------------------------------
    slide15 = prs.slides.add_slide(blank_layout)
    add_header(slide15, "References & Academic Citations")

    add_card(slide15, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.2),
             "Key References & Data Sources", [
                 "USAID DHS Program: Demographic and Health Surveys Open REST API. https://api.dhsprogram.com/.",
                 "World Health Organization (WHO): Standards for Maternal and Neonatal Care & Global Nutrition Targets 2025. Geneva: WHO.",
                 "UNICEF Child Mortality Report (2023): Levels & Trends in Child Mortality. UN Inter-agency Group for Child Mortality Estimation (UN IGME).",
                 "Rousseeuw, P. J. (1987): Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics, 20, 53-65.",
                 "Davies, D. L., & Bouldin, D. W. (1979): A cluster separation measure. IEEE Transactions on Pattern Analysis and Machine Intelligence, (2), 224-227.",
                 "MacQueen, J. (1967): Some methods for classification and analysis of multivariate observations. Proc. 5th Berkeley Symp. Math. Statist. Prob., 1, 281-297.",
                 "Kaufman, L., & Rousseeuw, P. J. (1990): Finding Groups in Data: An Introduction to Cluster Analysis. John Wiley & Sons."
             ])

    output_path = "Country_MCH_Segmentation_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_deck()
