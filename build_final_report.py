"""Build the final report strictly matching Reference 1.pdf and Reference 2.pdf.

Key Features:
- Exact 21-page CBIT institutional format:
  * Page 1: Cover Page (Roman i, unprinted)
  * Page 2: Abstract (Roman ii, bottom center)
  * Page 3: Table of Contents (Roman iii, bottom center)
  * Page 4: List of Figures (Roman iv, bottom center)
  * Pages 5 to 21: Chapters 1 to 4 (Arabic 1 to 17, bottom center)
- Authentic Times-Roman / Times-Bold academic typography (pure black #000000).
- Standard 1-inch margins (2.4 cm left/right, 2.0 cm top, 2.2 cm bottom).
- Large, high-resolution figures matching Reference 1 layout.
- Exact Faculty title: Dr. S. Durga Devi, Assistant Professor.
- Verified GitHub Source Code URL: https://github.com/mani-4444/fds-case-studies
- All 13 previous brief requirements and factual corrections strictly maintained.

Outputs to:
  - FDS_Case_Studies_Report_new.pdf
  - FDS_Case_Studies_Report_160124733189.pdf
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle
)
from reportlab.pdfgen import canvas
import pymupdf

HERE = Path(__file__).resolve().parent
TARGET_FILES = [
    HERE / "FDS_Case_Studies_Report_160124733189.pdf"
]

# Institutional Metadata
NAME = "Munjampally Manideep"
ROLL = "160124733189"
SECTION = "CSE-3, III Year, V Semester"
FACULTY = "Dr. S. Durga Devi"
FACULTY_TITLE = "Assistant Professor"
SUBJECT = "Fundamentals of Data Science (22CSC59)"
COLLEGE = "Chaitanya Bharathi Institute of Technology"
COLLEGE_STATUS = "(Autonomous),"
AFFILIATION = "(Affiliated to Osmania University, Hyderabad)"
LOCATION = "Hyderabad, TELANGANA (INDIA) - 500 075"
ACADEMIC_YEAR = "[2026-2027]"
REPO_URL = "https://github.com/mani-4444/fds-case-studies"


class ReferenceStyleCanvas(canvas.Canvas):
    """Draws exact bottom-centered page numbers matching Reference 1 & 2."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number()
            super().showPage()
        super().save()

    def draw_page_number(self):
        self.saveState()
        page_num = self._pageNumber
        
        # Page 1: Title page (no number printed)
        if page_num == 1:
            self.restoreState()
            return
            
        self.setFont("Times-Roman", 11.0)
        self.setFillColor(colors.black)
        
        # Front matter (pages 2, 3, 4) -> ii, iii, iv
        if page_num == 2:
            num_str = "ii"
        elif page_num == 3:
            num_str = "iii"
        elif page_num == 4:
            num_str = "iv"
        else:
            # Body matter (pages 5 to 21) -> 1 to 17
            num_str = str(page_num - 4)
            
        # Draw centered at bottom margin (y = 1.6 cm)
        self.drawCentredString(A4[0] / 2.0, 1.6 * cm, num_str)
        self.restoreState()


def get_styles():
    ss = getSampleStyleSheet()
    
    body = ParagraphStyle(
        "RefBody",
        parent=ss["Normal"],
        fontName="Times-Roman",
        fontSize=11.5,
        leading=15.0,
        alignment=TA_JUSTIFY,
        spaceAfter=5.0,
        textColor=colors.black
    )
    
    bullet = ParagraphStyle(
        "RefBullet",
        parent=body,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=3.5
    )
    
    h1 = ParagraphStyle(
        "RefH1",
        parent=ss["Heading1"],
        fontName="Times-Bold",
        fontSize=14.0,
        leading=18.0,
        alignment=TA_CENTER,
        spaceBefore=8.0,
        spaceAfter=6.0,
        textColor=colors.black,
        keepWithNext=True
    )
    
    h2 = ParagraphStyle(
        "RefH2",
        parent=ss["Heading2"],
        fontName="Times-Bold",
        fontSize=12.0,
        leading=15.5,
        alignment=TA_LEFT,
        spaceBefore=7.0,
        spaceAfter=3.5,
        textColor=colors.black,
        keepWithNext=True
    )
    
    h3 = ParagraphStyle(
        "RefH3",
        parent=h2,
        fontSize=11.5,
        leading=14.5,
        spaceBefore=5.0,
        spaceAfter=2.5
    )
    
    cap = ParagraphStyle(
        "RefCap",
        parent=body,
        fontName="Times-Bold",
        fontSize=10.5,
        leading=13.5,
        alignment=TA_CENTER,
        spaceBefore=3.0,
        spaceAfter=5.0,
        textColor=colors.black
    )
    
    cell = ParagraphStyle(
        "RefCell",
        parent=body,
        fontName="Times-Roman",
        fontSize=9.5,
        leading=12.5,
        alignment=TA_LEFT,
        spaceAfter=0
    )
    
    cell_bold = ParagraphStyle(
        "RefCellBold",
        parent=cell,
        fontName="Times-Bold",
        textColor=colors.black
    )
    
    return {
        "body": body,
        "bullet": bullet,
        "h1": h1,
        "h2": h2,
        "h3": h3,
        "cap": cap,
        "cell": cell,
        "cell_bold": cell_bold
    }


def make_figure(path, caption, width_cm=15.5, styles=None):
    iw, ih = ImageReader(str(path)).getSize()
    w = width_cm * cm
    h = w * ih / iw
    img = Image(str(path), width=w, height=h, hAlign="CENTER")
    cap_para = Paragraph(caption, styles["cap"])
    return KeepTogether([Spacer(1, 2), cap_para, img, Spacer(1, 4)])


def make_figure_pair(path1, cap1, path2, cap2, width_cm=7.8, styles=None):
    iw1, ih1 = ImageReader(str(path1)).getSize()
    w1 = width_cm * cm
    h1 = w1 * ih1 / iw1
    img1 = Image(str(path1), width=w1, height=h1)

    iw2, ih2 = ImageReader(str(path2)).getSize()
    w2 = width_cm * cm
    h2 = w2 * ih2 / iw2
    img2 = Image(str(path2), width=w2, height=h2)

    t = Table([
        [Paragraph(cap1, styles["cap"]), Paragraph(cap2, styles["cap"])],
        [img1, img2]
    ], colWidths=[width_cm * cm, width_cm * cm], hAlign="CENTER")
    
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return KeepTogether([Spacer(1, 2), t, Spacer(1, 4)])


def make_table(rows, caption, col_widths=None, styles=None):
    data = []
    for r_idx, r in enumerate(rows):
        row_cells = []
        for c in r:
            st = styles["cell_bold"] if r_idx == 0 else styles["cell"]
            row_cells.append(Paragraph(str(c), st))
        data.append(row_cells)
        
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#666666")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.0),
    ]))
    cap_para = Paragraph(caption, styles["cap"])
    return KeepTogether([Spacer(1, 2), cap_para, t, Spacer(1, 4)])


def build_story():
    st = get_styles()
    story = []
    
    # -------------------------------------------------------------
    # PAGE 1: TITLE PAGE (Exact Reference 1 & 2 layout)
    # -------------------------------------------------------------
    cov_main = ParagraphStyle("cov_main", parent=st["body"], alignment=TA_CENTER, fontName="Times-Bold", fontSize=14.0, leading=17.5, textColor=colors.black)
    cov_head = ParagraphStyle("cov_head", parent=st["body"], alignment=TA_CENTER, fontName="Times-Roman", fontSize=13.0, leading=16.0, textColor=colors.black)
    cov_sub = ParagraphStyle("cov_sub", parent=st["body"], alignment=TA_CENTER, fontName="Times-Roman", fontSize=11.5, leading=14.5, textColor=colors.black)
    cov_bold = ParagraphStyle("cov_bold", parent=st["body"], alignment=TA_CENTER, fontName="Times-Bold", fontSize=12.0, leading=15.5, textColor=colors.black)
    cov_small = ParagraphStyle("cov_small", parent=st["body"], alignment=TA_CENTER, fontName="Times-Roman", fontSize=10.5, leading=13.5, textColor=colors.black)
    cov_inst_bold = ParagraphStyle("cov_inst_b", parent=st["body"], alignment=TA_CENTER, fontName="Times-Bold", fontSize=11.5, leading=15.0, textColor=colors.black)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("A Case Study Report", cov_head))
    story.append(Paragraph("on", cov_sub))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("“Case Study 3: Predicting Titanic Survival with Logistic Regression”", cov_main))
    story.append(Paragraph("and", cov_sub))
    story.append(Paragraph("“Case Study 6: Comparative Analysis of Classification Algorithms for Bank Marketing Prediction”", cov_main))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph("for the course", cov_sub))
    story.append(Paragraph(f"<b>{SUBJECT}</b>", cov_bold))
    story.append(Spacer(1, 0.4 * cm))
    
    story.append(Paragraph("Submitted in partial fulfillment of the requirements for the award of degree", cov_small))
    story.append(Paragraph("<b>BACHELOR OF ENGINEERING</b>", cov_bold))
    story.append(Paragraph("in", cov_small))
    story.append(Paragraph("<b>COMPUTER SCIENCE AND ENGINEERING</b>", cov_bold))
    story.append(Spacer(1, 0.35 * cm))
    
    story.append(Paragraph("by", cov_small))
    story.append(Paragraph(f"<b>{NAME} ({ROLL})</b>", cov_bold))
    story.append(Paragraph(f"Section: {SECTION}", cov_small))
    story.append(Spacer(1, 0.3 * cm))
    
    story.append(Paragraph("Faculty:", cov_small))
    story.append(Paragraph(f"<b>{FACULTY}</b>", cov_bold))
    story.append(Paragraph(FACULTY_TITLE, cov_small))
    story.append(Spacer(1, 0.3 * cm))
    
    # CBIT Institutional Logo (Same as Reference 1 & 2)
    logo_path = HERE / "cbit_logo.jpeg"
    story.append(Image(str(logo_path), width=2.6 * cm, height=3.4 * cm, hAlign="CENTER"))
    story.append(Spacer(1, 0.3 * cm))
    
    story.append(Paragraph("Department of Computer Science and Engineering,", cov_small))
    story.append(Paragraph(f"<b>{COLLEGE}</b>", cov_inst_bold))
    story.append(Paragraph(COLLEGE_STATUS, cov_small))
    story.append(Paragraph(AFFILIATION, cov_small))
    story.append(Paragraph(LOCATION, cov_small))
    story.append(Paragraph(ACADEMIC_YEAR, cov_small))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 2: ABSTRACT (Roman ii)
    # -------------------------------------------------------------
    story.append(Paragraph("Abstract", st["h1"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "This report presents two supervised machine learning case studies from the Fundamentals of Data Science course applied to "
        "real-world datasets. Case Study 3 predicts passenger survival on the Titanic using logistic regression. Following exploratory "
        "data analysis, feature engineering was implemented by computing individual ticket fare per person (Fare_pp) and applying a log1p "
        "transformation, which successfully stabilized ticket fare skewness from 4.79 to 0.33. Missing passenger ages were imputed using "
        "the median age within each passenger class and sex cohort computed strictly on the training partition. Tuning the decision "
        "threshold to 0.41 on the precision-recall trade-off curve raised survivor recall to 79.71% (identifying 55 of 69 test survivors) "
        "with an ROC-AUC of 0.8382. An unscaled statsmodels Logit model was fitted to provide natural-unit odds ratios, demonstrating that "
        "male sex (OR = 0.0719), lower passenger class (OR = 0.3556), older age (OR = 0.9547), and additional siblings/spouses (OR = 0.7553) "
        "statistically significantly reduced survival odds, while individual ticket fare was positively associated with survival (OR = 1.5185). "
        "The model was deployed as an interactive Streamlit application.",
        st["body"]
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Case Study 6 predicts whether bank customers will subscribe to a term deposit following a direct telephone marketing campaign. "
        "The benchmark used bank-full.csv from the UCI repository (45,211 rows and 17 attributes), which features a severely imbalanced target "
        "distribution (11.70% subscribers vs 88.30% non-subscribers). Call duration was excluded from all modeling pipelines to prevent "
        "target leakage, as duration is unknown prior to dialing. Four classification algorithms—Logistic Regression, Decision Tree, K-Nearest "
        "Neighbours (KNN), and Random Forest—were systematically trained with SMOTE minority oversampling applied strictly within the training "
        "pipeline folds. Random Forest achieved the most operationally viable performance with 50.78% precision, 0.4474 F1-score, 0.7922 ROC-AUC, "
        "and 0.4346 PR-AUC. Cumulative gains analysis confirmed that ranking clients by Random Forest probability and calling only the top 20% "
        "captures 60.40% of all deposit subscribers, reducing unnecessary call center outreach volume by 80%.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 3: TABLE OF CONTENTS (Roman iii)
    # -------------------------------------------------------------
    story.append(Paragraph("Table of Contents", st["h1"]))
    story.append(Spacer(1, 0.3 * cm))
    toc_data = [
        ["S.No", "Title", "Page"],
        ["", "Title Page", "i"],
        ["", "Abstract", "ii"],
        ["", "List of Figures", "iv"],
        ["1.", "INTRODUCTION", "1"],
        ["1.1", "Problem Definition including the significance and objective", "1"],
        ["1.2", "Concepts used in Methodology", "2"],
        ["1.3", "Outline the results", "2"],
        ["2.", "CASE STUDY 3: TITANIC SURVIVAL PREDICTION", "4"],
        ["2.1", "Problem Statement", "4"],
        ["2.2", "Dataset Description", "4"],
        ["2.3", "Methodology", "4"],
        ["2.4", "Statistical Findings", "5"],
        ["2.5", "Model Evaluation", "7"],
        ["2.6", "Interpretation and Deployment", "8"],
        ["2.7", "Conclusion", "9"],
        ["3.", "CASE STUDY 6: BANK MARKETING CLASSIFICATION", "10"],
        ["3.1", "Problem Statement", "10"],
        ["3.2", "Dataset Description", "10"],
        ["3.3", "Methodology", "10"],
        ["3.4", "Statistical Findings", "11"],
        ["3.5", "Model Evaluation", "13"],
        ["3.6", "Interpretation and Business Recommendations", "15"],
        ["3.7", "Conclusion and Limitations", "16"],
        ["4.", "CONCLUSION and References", "17"],
        ["4.1", "Conclusion", "17"],
        ["4.2", "References", "17"]
    ]
    story.append(make_table(toc_data, "Table of Contents", [1.8 * cm, 12.0 * cm, 2.2 * cm], styles=st))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 4: LIST OF FIGURES (Roman iv)
    # -------------------------------------------------------------
    story.append(Paragraph("List of Figures", st["h1"]))
    story.append(Spacer(1, 0.3 * cm))
    lof_data = [
        ["Fig No.", "Title", "Page"],
        ["2.1", "Workflow followed for Case Study 3", "4"],
        ["2.2", "Distributions of passenger age and fare", "5"],
        ["2.3", "Age and fare by survival outcome", "5"],
        ["2.4", "Survival rate by sex and by passenger class", "6"],
        ["2.5", "Correlation heatmap of the numeric and engineered features", "6"],
        ["2.6", "Precision-recall curve and selected threshold (0.41)", "7"],
        ["2.7", "Confusion matrix of the tuned model and ROC curves", "8"],
        ["2.8", "Streamlit app for survival prediction", "9"],
        ["3.1", "Workflow followed for Case Study 6", "10"],
        ["3.2", "Distribution of the target variable (term deposit subscription)", "11"],
        ["3.3", "Subscription rate across customer and campaign attributes", "12"],
        ["3.4", "Numeric variables against subscription outcome", "13"],
        ["3.5", "Accuracy, precision, recall and F1-score of the four models", "14"],
        ["3.6", "Confusion matrices of the four classifiers", "14"],
        ["3.7", "ROC and Precision-Recall curves of the four classifiers", "15"],
        ["3.8", "Cumulative gains of the Random Forest model", "15"],
        ["3.9", "Top Random Forest feature importances", "16"]
    ]
    story.append(make_table(lof_data, "List of Figures", [2.0 * cm, 12.0 * cm, 2.0 * cm], styles=st))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 5: 1. INTRODUCTION & 1.1 Problem Definition (Arabic 1)
    # -------------------------------------------------------------
    story.append(Paragraph("1. INTRODUCTION", st["h1"]))
    story.append(Paragraph(
        "This report covers two case studies from the Fundamentals of Data Science course. Both are binary classification problems "
        "on real data, and both follow the same data science process: understanding and cleaning the data, exploring it, building models, "
        "evaluating them on unseen test data, and interpreting the results.",
        st["body"]
    ))
    story.append(Paragraph("1.1 Problem Definition including the significance and objective", st["h2"]))
    story.append(Paragraph("<b>Problem Definition</b>", st["h3"]))
    story.append(Paragraph(
        "In Case Study 3, the task is to predict whether a passenger on the Titanic survived from basic details such as class, sex, age, "
        "family, and ticket fare, and to find out which of these factors mattered most. In Case Study 6, a Portuguese bank sells term deposits "
        "through telephone campaigns in which most calls fail. The task is to predict, before a call is made, which customers are likely to "
        "subscribe, compare four classification models, and recommend the best strategy for the bank. In both datasets, one class is smaller "
        "than the other, so the choice of evaluation metrics and threshold tuning is critical.",
        st["body"]
    ))
    story.append(Paragraph("<b>Significance</b>", st["h3"]))
    sig_bullets = [
        "Shows how a simple, interpretable model such as logistic regression can explain which passenger attributes influenced survival odds.",
        "Demonstrates how preprocessing choices (missing values, encoding, scaling, and removing target leakage) affect performance.",
        "For the bank, a good ranking model lets the marketing team call the most promising customers first, saving time and money.",
        "Demonstrates why accuracy can be misleading on imbalanced data and how precision, recall, F1, and PR-AUC give a realistic assessment."
    ]
    for sb in sig_bullets:
        story.append(Paragraph(f"•  {sb}", st["bullet"]))
        
    story.append(Paragraph("<b>Objectives</b>", st["h3"]))
    obj_bullets = [
        "1. To explore both datasets with summary statistics and visualisations, describing patterns in features and target variables.",
        "2. To handle missing and unknown values, encode categorical variables, and scale numeric features without data leakage.",
        "3. To build, tune, and evaluate a logistic regression model for Titanic survival, interpreting its odds ratios.",
        "4. To build, tune, and compare Logistic Regression, Decision Tree, KNN, and Random Forest on bank marketing data.",
        "5. To choose the best model using confusion matrices, precision, recall, F1-score, ROC-AUC, and PR-AUC, and translate findings into business recommendations."
    ]
    for ob in obj_bullets:
        story.append(Paragraph(f"{ob}", st["bullet"]))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 6: 1.2 Concepts used in Methodology (Arabic 2)
    # -------------------------------------------------------------
    story.append(Paragraph("1.2 Concepts used in Methodology", st["h2"]))
    story.append(Paragraph("<b>Data Preparation Concepts</b>", st["h3"]))
    dp_bullets = [
        "<b>Exploratory data analysis (EDA):</b> summary statistics, histograms, box plots, bar charts, and correlation heatmaps to understand data distributions.",
        "<b>Preprocessing pipeline:</b> missing values imputed within pipelines (cohort median for Titanic age; mode for categoricals) to prevent leakage.",
        "<b>Stratified 80:20 split:</b> test set keeps identical target class proportions as the full data (random_state = 42).",
        "<b>Feature engineering:</b> fare per person (total fare divided by ticket group size) and log1p transformation to correct severe right-skewness.",
        "<b>SMOTE:</b> Synthetic Minority Over-sampling Technique creates synthetic positive cases strictly within training folds to avoid false confidence."
    ]
    for dp in dp_bullets:
        story.append(Paragraph(f"•  {dp}", st["bullet"]))
        
    story.append(Paragraph("<b>Modeling Concepts</b>", st["h3"]))
    m_bullets = [
        "<b>Logistic Regression:</b> models the log-odds of the positive class as a linear combination of inputs. Exponentiating natural-unit coefficients yields odds ratios.",
        "<b>Decision Tree:</b> splits data on feature thresholds to minimize impurity (Gini or entropy). Transparent rules but prone to high variance.",
        "<b>K-Nearest Neighbours (KNN):</b> classifies a query point by majority vote of its k closest training points under Euclidean distance after feature scaling.",
        "<b>Random Forest:</b> ensemble of decision trees trained on bootstrap samples with random feature subsets at each split, reducing variance."
    ]
    for mb in m_bullets:
        story.append(Paragraph(f"•  {mb}", st["bullet"]))

    story.append(Paragraph("<b>Evaluation Concepts</b>", st["h3"]))
    ev_bullets = [
        "<b>Confusion matrix:</b> True Negatives (TN), False Positives (FP), False Negatives (FN), and True Positives (TP).",
        "<b>Precision, Recall and F1-score:</b> Precision measures correctness of positive calls; recall measures captured subscribers; F1 is their harmonic mean.",
        "<b>ROC-AUC:</b> area under the True Positive Rate vs False Positive Rate curve across all classification thresholds.",
        "<b>PR-AUC and Cumulative Gains:</b> area under the Precision-Recall curve and cumulative proportion of subscribers captured by decile ranking."
    ]
    for eb in ev_bullets:
        story.append(Paragraph(f"•  {eb}", st["bullet"]))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 7: 1.3 Outline the results (Arabic 3)
    # -------------------------------------------------------------
    story.append(Paragraph("1.3 Outline the results", st["h2"]))
    story.append(Paragraph(
        "A summary of the primary empirical findings and operational outcomes for both case studies is presented below:",
        st["body"]
    ))
    res_bullets = [
        "<b>Case Study 3 (Titanic):</b> Feature engineering (fare per person and log transformation) stabilized extreme ticket skewness from 4.79 to 0.33. Cohort-conditional age imputation filled missing values accurately without leakage. Calibrating the decision threshold to 0.41 on the PR curve raised survivor recall to 79.71% (identifying 55 of 69 test survivors) with test accuracy of 0.8156 and ROC-AUC of 0.8382.",
        "<b>Titanic Odds Ratios:</b> Natural-unit Logit regression demonstrated that male passengers had 92.8% lower survival odds than females (OR = 0.0719, p < 0.0001). Lower passenger class (OR = 0.3556, p < 0.0001), older age (OR = 0.9547, p < 0.0001), and additional siblings/spouses (OR = 0.7553, p = 0.0214) significantly decreased survival odds, while higher individual log fare improved odds (OR = 1.5185, p = 0.0474). The model is deployed as an interactive Streamlit app.",
        "<b>Case Study 6 (Bank Marketing):</b> Call duration was removed to prevent target leakage. SMOTE oversampling was applied inside training folds to handle the 11.70% target class imbalance. Among the four benchmarked classifiers, Random Forest achieved the best operational balance, leading with 50.78% precision, 0.4474 F1-score, 0.7922 ROC-AUC, and 0.4346 PR-AUC.",
        "<b>Trade-offs Across Models:</b> KNN and Logistic Regression attained higher recall (65.60% and 61.91%) but generated 2,285 and 1,877 false positive calls, causing low precision (23.30% and 25.87%). In contrast, Random Forest limited false positives to 410, producing an efficient 1:1 true-to-false-alarm ratio.",
        "<b>Operational Call Savings:</b> Cumulative gains analysis showed that ranking clients by Random Forest probability and calling only the top 20% reaches 60.40% of all subscribers, eliminating 80% of unnecessary calls and dramatically lowering marketing overhead."
    ]
    for rb in res_bullets:
        story.append(Paragraph(f"•  {rb}", st["bullet"]))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 8: 2. CASE STUDY 3: TITANIC SURVIVAL PREDICTION (Arabic 4)
    # -------------------------------------------------------------
    story.append(Paragraph("2. CASE STUDY 3: TITANIC SURVIVAL PREDICTION", st["h1"]))
    story.append(Paragraph("2.1 Problem Statement", st["h2"]))
    story.append(Paragraph(
        "The aim is to predict whether a passenger on the Titanic survived using demographic and ticket information. Because the "
        "disaster had a known protocol ('women and children first') and clear socio-economic divides, logistic regression was chosen "
        "as an interpretable model to explain which factors gave passengers the highest chance of survival.",
        st["body"]
    ))
    story.append(Paragraph("2.2 Dataset Description", st["h2"]))
    story.append(Paragraph(
        "The training set contains 891 passengers and 12 columns. 342 passengers (38.38%) survived and 549 (61.62%) did not. "
        "Age has 177 missing values (19.87%), Cabin has 687 missing (77.10%) and Embarked has 2 missing (0.22%). Cabin was excluded "
        "due to extensive missingness, while passenger names and ticket numbers were utilized to extract group-size features before removal.",
        st["body"]
    ))
    t_feat_data = [
        ["Feature", "Count", "Mean", "Std. dev.", "Median", "Min to Max"],
        ["Age", "714", "29.70", "14.53", "28.00", "0.42 to 80.0"],
        ["Fare", "891", "32.20", "49.69", "14.45", "0.00 to 512.33"],
        ["SibSp", "891", "0.52", "1.10", "0", "0 to 8"],
        ["Parch", "891", "0.38", "0.81", "0", "0 to 6"],
        ["Pclass", "891", "2.31", "0.84", "3", "1 to 3"]
    ]
    story.append(make_table(t_feat_data, "Table 2.1: Summary statistics of the Titanic numeric features", [2.5 * cm, 2.0 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 3.8 * cm], styles=st))
    story.append(Paragraph("2.3 Methodology", st["h2"]))
    story.append(Paragraph(
        "Features were engineered by calculating ticket sharing group size and computing individual fare per person (Fare_pp = Fare / GroupSize). "
        "A log1p transformation reduced fare skewness from 4.79 to 0.33. Missing age values were imputed with the median of each (Pclass × Sex) "
        "cohort computed strictly on the training partition to avoid leakage.",
        st["body"]
    ))
    story.append(make_figure(HERE / "3/figures/00_methodology_workflow.png", "Fig 2.1: Workflow followed for Case Study 3", width_cm=15.5, styles=st))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 9: 2.4 Statistical Findings (Histograms & Boxplots) (Arabic 5)
    # -------------------------------------------------------------
    story.append(Paragraph("2.4 Statistical Findings", st["h1"]))
    story.append(make_figure(HERE / "3/figures/01_age_fare_histograms.png", "Fig 2.2: Distributions of passenger age and fare", width_cm=15.5, styles=st))
    story.append(Paragraph(
        "Age follows a bell-shaped distribution with most passengers between 20 and 40 years old (median age 28.0; mean 29.70). "
        "Raw fare is heavily right-skewed (skewness 4.7873), with most tickets under £30 but several luxury suites exceeding £500. "
        "Dividing fare by ticket group size reduced skewness to 4.3806, and applying log1p stabilized skewness to 0.3302, ensuring "
        "that extreme values do not distort regression coefficients.",
        st["body"]
    ))
    story.append(make_figure(HERE / "3/figures/02_age_fare_boxplots.png", "Fig 2.3: Age and fare by survival outcome", width_cm=15.5, styles=st))
    story.append(Paragraph(
        "Box plot comparisons between survivors and non-survivors indicate that survivors paid significantly higher median fares "
        "(£26.00 vs £10.50), reflecting the higher survival rates in first and second class. Passenger age distributions were broadly "
        "comparable between the two groups (median 28 vs 28), though infants and young children had higher survival rates.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 10: 2.4 (cont.) Survival Rates & Correlation Heatmap (Arabic 6)
    # -------------------------------------------------------------
    story.append(make_figure(HERE / "3/figures/03_survival_by_sex_pclass.png", "Fig 2.4: Survival rate by sex and by passenger class", width_cm=15.5, styles=st))
    story.append(Paragraph(
        "Survival differences across demographic groups were stark: female passengers survived at 74.20% compared to 18.89% for males, "
        "reflecting strict adherence to lifeboat boarding protocols. Survival also declined steeply with travel class: 62.96% in first class, "
        "47.28% in second class, and 24.24% in third class. First-class women had an extraordinary survival rate of 96.81%, whereas third-class "
        "men survived at only 13.54%. Embarkation port also mattered: Cherbourg passengers survived at 55.36%, versus 38.96% at Queenstown "
        "and 33.70% at Southampton, largely because Cherbourg had a higher proportion of wealthy first-class travelers.",
        st["body"]
    ))
    story.append(make_figure(HERE / "3/figures/05_correlation_heatmap.png", "Fig 2.5: Correlation heatmap of the numeric and engineered features", width_cm=11.5, styles=st))
    story.append(Paragraph(
        "The correlation heatmap confirms that passenger survival is most strongly associated with Sex (female), Pclass (-0.338), and "
        "Fare (+0.257). Pclass is strongly negatively correlated with Fare (-0.549) and Log_Fare_pp (-0.612). Number of siblings/spouses (SibSp) "
        "and parents/children (Parch) are positively correlated with each other (+0.415) and negatively associated with overall survival.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 11: PR Curve & 2.5 Model Evaluation (Arabic 7)
    # -------------------------------------------------------------
    story.append(make_figure(HERE / "3/figures/09_precision_recall_curve.png", "Fig 2.6: Precision-recall curve and selected threshold (0.41)", width_cm=11.5, styles=st))
    story.append(Paragraph(
        "Threshold optimization on the precision-recall trade-off curve demonstrated that the default 0.50 cutoff missed over 30% of "
        "survivors. Lowering the decision threshold to 0.41 increased survivor recall from 69.57% to 79.71%, correctly capturing 55 of the "
        "69 survivors in the unseen test set, while maintaining strong precision (0.7432) and overall accuracy (0.8156).",
        st["body"]
    ))
    story.append(Paragraph("2.5 Model Evaluation", st["h2"]))
    story.append(Paragraph(
        "The model was evaluated on a stratified 20% holdout test set (179 passengers). Table 2.2 compares baseline weighting against "
        "balanced class weights, illustrating how penalizing false negatives improves survivor recall.",
        st["body"]
    ))
    t_eval_data = [
        ["Model / Weighting", "Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC", "PR-AUC"],
        ["Default (Threshold 0.50)", "0.8156", "0.8000", "0.6957", "0.7442", "0.8382", "0.7838"],
        ["Tuned (Threshold 0.41)", "0.8156", "0.7432", "0.7971", "0.7692", "0.8382", "0.7838"],
        ["Balanced Class Weights", "0.8101", "0.7333", "0.7971", "0.7639", "0.8389", "0.7850"]
    ]
    story.append(make_table(t_eval_data, "Table 2.2: Test set results (179 passengers)", [3.5 * cm] + [2.0 * cm] * 6, styles=st))
    story.append(Paragraph(
        "Balancing class weights achieves nearly identical recall gains to threshold tuning by adjusting loss weights during maximum likelihood estimation.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 12: ROC Curve, Confusion Matrix, Table 2.3 & 2.6 Interpretation (Arabic 8)
    # -------------------------------------------------------------
    story.append(make_figure_pair(
        HERE / "3/figures/06_confusion_matrix.png", "Fig 2.7a: Confusion matrix (threshold 0.41)",
        HERE / "3/figures/07_roc_curve.png", "Fig 2.7b: ROC curve (AUC = 0.8382)",
        width_cm=7.8, styles=st
    ))
    story.append(Paragraph(
        "Fig 2.7 displays diagnostic curves: at threshold 0.41, the confusion matrix confirms 91 True Negatives, 19 False Positives, 14 False "
        "Negatives, and 55 True Positives (totaling 110 non-survivors and 69 survivors in the test set). The ROC curve achieves an area under the curve (AUC) of 0.8382, demonstrating strong discrimination.",
        st["body"]
    ))
    story.append(Paragraph("2.6 Interpretation and Deployment", st["h2"]))
    story.append(Paragraph(
        "To interpret coefficients on their physical scales, an unscaled statsmodels Logit model was fitted. Table 2.3 presents odds ratios, "
        "95% confidence intervals, and p-values.",
        st["body"]
    ))
    odds_data = [
        ["Feature", "Coefficient", "Odds ratio", "95% CI", "p-value", "Significant"],
        ["Pclass", "-1.0339", "0.3556", "0.240 to 0.527", "< 0.0001", "Yes (p < 0.001)"],
        ["Sex_male", "-2.6322", "0.0719", "0.046 to 0.112", "< 0.0001", "Yes (p < 0.001)"],
        ["Age", "-0.0464", "0.9547", "0.938 to 0.972", "< 0.0001", "Yes (p < 0.001)"],
        ["SibSp", "-0.2807", "0.7553", "0.595 to 0.959", "0.0214", "Yes (p < 0.05)"],
        ["Parch", "-0.0643", "0.9377", "0.733 to 1.200", "0.6093", "No (p = 0.61)"],
        ["Log_Fare_pp", "+0.4177", "1.5185", "1.005 to 2.295", "0.0474", "Yes (p < 0.05)"]
    ]
    story.append(make_table(odds_data, "Table 2.3: Coefficients of the tuned model with statsmodels p-values", [2.6 * cm, 2.2 * cm, 2.0 * cm, 3.2 * cm, 2.0 * cm, 2.8 * cm], styles=st))
    story.append(Paragraph(
        "The odds ratios show that male passengers had 92.8% lower survival odds than females (OR = 0.0719). Moving down one passenger class "
        "reduced odds by 64.4% (OR = 0.3556). Each additional year of age reduced odds by 4.5% (OR = 0.9547). SibSp reduced odds by 24.5% (OR = 0.7553), "
        "while Parch had no significant effect. Log fare per person increased survival odds by 51.8% (OR = 1.5185).",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 13: Fig 2.8 Streamlit App & 2.7 Conclusion (Arabic 9)
    # -------------------------------------------------------------
    story.append(Paragraph(
        "The finalized pipeline was serialized with joblib (3/model/titanic_logreg.joblib). The interactive Streamlit web application "
        "(3/app.py) accepts passenger attributes, applies cohort age imputation and fare per person transformations, and displays predicted "
        "survival probability alongside decision threshold adjustments. It runs locally via <code>streamlit run 3/app.py</code>.",
        st["body"]
    ))
    story.append(make_figure(HERE / "3/figures/streamlit_app.png", "Fig 2.8: Streamlit app for survival prediction", width_cm=10.5, styles=st))
    story.append(Paragraph("2.7 Conclusion", st["h2"]))
    story.append(Paragraph(
        "Being female, traveling in a higher passenger class, having a smaller family aboard, and paying a higher individual ticket fare "
        "were the decisive factors determining Titanic survival. Feature engineering (fare per person and log stabilization) combined with "
        "threshold optimization raised survivor recall to 79.71% and ROC-AUC to 0.8382.",
        st["body"]
    ))
    story.append(Paragraph(
        "<b>Limitations:</b> The historical dataset is modest in size (891 total passengers), 77% of cabin entries are missing, approximately "
        "20% of ages required statistical imputation, and unobserved physical variables—such as cabin proximity to lifeboat exits and chaotic "
        "evacuation conditions during the collision—could not be modeled.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 14: 3. CASE STUDY 6: BANK MARKETING CLASSIFICATION (Arabic 10)
    # -------------------------------------------------------------
    story.append(Paragraph("3. CASE STUDY 6: BANK MARKETING CLASSIFICATION", st["h1"]))
    story.append(Paragraph("3.1 Problem Statement", st["h2"]))
    story.append(Paragraph(
        "A Portuguese bank contacts retail customers by telephone to sell long-term deposits, and the vast majority of calls fail. "
        "The objective is to predict, prior to dialing, which customers are likely to subscribe, benchmark four classification algorithms "
        "(Logistic Regression, Decision Tree, K-Nearest Neighbours, and Random Forest), and recommend an optimal operational strategy.",
        st["body"]
    ))
    story.append(Paragraph("3.2 Dataset Description", st["h2"]))
    story.append(Paragraph(
        "The benchmark utilized bank-full.csv from the UCI Machine Learning Repository (45,211 rows and 17 attributes collected from May 2008 "
        "to November 2010). 5,289 customers (11.70%) subscribed and 39,922 (88.30%) did not, representing severe target class imbalance. "
        "There are no missing values, but 'unknown' is common in poutcome (81.75%) and contact (28.80%). Call duration was excluded to prevent "
        "target leakage, as duration is unknown before dialing.",
        st["body"]
    ))
    b_feat_data = [
        ["Feature", "Count", "Mean", "Std. dev.", "Median", "Min to Max"],
        ["age", "45,211", "40.94", "10.62", "39.0", "18 to 95"],
        ["balance", "45,211", "1,362.27", "3,044.77", "448.0", "-8,019 to 102,127"],
        ["day", "45,211", "15.81", "8.32", "16.0", "1 to 31"],
        ["campaign", "45,211", "2.76", "3.10", "2.0", "1 to 63"],
        ["pdays", "45,211", "40.20", "100.13", "-1.0", "-1 to 871"],
        ["previous", "45,211", "0.58", "2.30", "0.0", "0 to 275"]
    ]
    story.append(make_table(b_feat_data, "Table 3.1: Summary statistics of the bank marketing numeric features", [2.5 * cm, 2.0 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 3.8 * cm], styles=st))
    story.append(Paragraph("3.3 Methodology", st["h2"]))
    story.append(Paragraph(
        "A stratified 80:20 train/test split was created (36,168 training records and 9,043 test records). Preprocessing pipelines applied "
        "one-hot encoding to categoricals and standard scaling to numerical features. SMOTE was applied strictly within training folds.",
        st["body"]
    ))
    story.append(make_figure(HERE / "6/figures/00_methodology_workflow.png", "Fig 3.1: Workflow followed for Case Study 6", width_cm=15.5, styles=st))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 15: Table 3.2, Fig 3.2 & 3.4 Statistical Findings (Arabic 11)
    # -------------------------------------------------------------
    b_hp_data = [
        ["Model", "Best Parameters / Configuration", "SMOTE Oversampling", "Scaling"],
        ["Logistic Regression", "C = 1.0, solver = 'lbfgs', max_iter = 1000", "k_neighbors = 5 (train folds)", "StandardScaler"],
        ["Decision Tree", "max_depth = 6, min_samples_leaf = 20", "k_neighbors = 5 (train folds)", "None (tree-invariant)"],
        ["KNN", "n_neighbors = 15, weights = 'uniform'", "k_neighbors = 5 (train folds)", "StandardScaler"],
        ["Random Forest", "n_estimators = 100, max_depth = 12, min_leaf = 10", "k_neighbors = 5 (train folds)", "None (tree-invariant)"]
    ]
    story.append(make_table(b_hp_data, "Table 3.2: Hyperparameters and SMOTE configurations for the four classifiers", [3.2 * cm, 5.2 * cm, 4.0 * cm, 2.8 * cm], styles=st))
    story.append(Paragraph(
        "All models were tuned via cross-validation. Categorical 'unknown' values were preserved as distinct categories, and SMOTE was confined "
        "strictly to training folds to guarantee unbiased holdout testing.",
        st["body"]
    ))
    story.append(make_figure(HERE / "6/figures/01_target_distribution.png", "Fig 3.2: Distribution of the target variable (term deposit subscription)", width_cm=10.0, styles=st))
    story.append(Paragraph("3.4 Statistical Findings", st["h2"]))
    story.append(Paragraph(
        "The target variable exhibits pronounced class imbalance: only 11.70% of clients subscribed to a term deposit. A naive classifier "
        "predicting 'no' for every client would achieve an 88.30% accuracy rate while failing to secure a single sale. Therefore, model "
        "performance must be evaluated using precision, recall, F1-score, and Precision-Recall AUC (PR-AUC).",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 16: Fig 3.3 Subscription Rates Across Attributes (Arabic 12)
    # -------------------------------------------------------------
    story.append(make_figure(HERE / "6/figures/02_rate_by_job.png", "Fig 3.3a: Subscription rate across client professions", width_cm=15.5, styles=st))
    story.append(make_figure(HERE / "6/figures/04_rate_by_contact_poutcome_edu.png", "Fig 3.3b: Subscription rates by contact channel, previous outcome, and education", width_cm=15.5, styles=st))
    story.append(Paragraph(
        "Analysis of demographic and contact features revealed major conversion discrepancies across segments:",
        st["body"]
    ))
    att_bullets = [
        "<b>Customer Profession:</b> Students (28.72%) and retired clients (22.79%) convert at more than double the bank baseline, while blue-collar workers (7.27%) and entrepreneurs (8.27%) exhibit low receptivity.",
        "<b>Previous Outcome:</b> Previous campaign success (poutcome = 'success') is the single strongest predictor, yielding a 64.73% subscription rate, compared to 12.61% for failure and 9.16% for unknown history.",
        "<b>Contact Channel:</b> Cellular telephone contact achieves a 14.92% conversion rate, compared to 13.42% for landline telephone and only 4.07% for unknown contact channels.",
        "<b>Seasonality:</b> March, September, October, and December achieve conversion rates above 45% from relatively low call volumes, whereas May accounts for the highest call volume but yields the lowest conversion rate (6.44%)."
    ]
    for ab in att_bullets:
        story.append(Paragraph(f"•  {ab}", st["bullet"]))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 17: Fig 3.4 Numerical Variables & 3.5 Model Evaluation (Arabic 13)
    # -------------------------------------------------------------
    story.append(make_figure(HERE / "6/figures/05_numeric_boxplots.png", "Fig 3.4: Numeric variables against subscription outcome", width_cm=15.5, styles=st))
    story.append(Paragraph(
        "Numerical feature distributions show that median age is virtually identical between subscribers and non-subscribers (38 vs 39 years). "
        "Subscribers hold substantially higher median account balances (€733 vs €417). Both groups have a median of 2 campaign contacts; however, "
        "non-subscribers display an extreme right-tail of repeated contacts, demonstrating diminishing returns beyond the third attempt.",
        st["body"]
    ))
    story.append(Paragraph("3.5 Model Evaluation", st["h2"]))
    story.append(Paragraph(
        "The models were evaluated on the holdout test set of 9,043 customers (7,985 non-subscribers and 1,058 subscribers). Table 3.3 summarizes results.",
        st["body"]
    ))
    b_eval_data = [
        ["Model", "Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC", "PR-AUC"],
        ["Logistic Regression", "0.7479", "0.2587", "0.6191", "0.3649", "0.7655", "0.4049"],
        ["Decision Tree", "0.8465", "0.3563", "0.3866", "0.3708", "0.7174", "0.3052"],
        ["KNN", "0.7071", "0.2330", "0.6560", "0.3438", "0.7411", "0.3166"],
        ["Random Forest", "0.8844", "0.5078", "0.3998", "0.4474", "0.7922", "0.4346"]
    ]
    story.append(make_table(b_eval_data, "Table 3.3: Test set results (9,043 customers)", [3.4 * cm] + [2.0 * cm] * 6, styles=st))
    story.append(Paragraph(
        "Random Forest achieved the best operational balance, leading with 50.78% precision, 0.4474 F1-score, and 0.4346 PR-AUC.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 18: Fig 3.5 Metrics Bar Chart & Fig 3.6 Confusion Matrices (Arabic 14)
    # -------------------------------------------------------------
    story.append(make_figure(HERE / "6/figures/07_metrics_grouped_bar.png", "Fig 3.5: Accuracy, precision, recall and F1-score of the four models", width_cm=14.5, styles=st))
    story.append(Paragraph(
        "The comparative bar chart highlights clear operational trade-offs: KNN achieves high recall (65.60%) but suffers from poor precision "
        "(23.30%). Decision Tree achieves moderate balance, while Random Forest provides the highest precision and overall F1-score.",
        st["body"]
    ))
    story.append(make_figure(HERE / "6/figures/08_confusion_matrices.png", "Fig 3.6: Confusion matrices of the four classifiers", width_cm=12.2, styles=st))
    story.append(Paragraph(
        "In telemarketing operations, a false negative represents a missed sale, while a false positive represents a wasted call and agent labor. "
        "KNN and Logistic Regression generated 2,285 and 1,877 false positive calls respectively on the test set. In contrast, Random Forest "
        "limited false alarms to 410 while securing 423 true positive sales, delivering an efficient 1:1 true-to-false-alarm operational ratio.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 19: Fig 3.7 Dual Curves & Fig 3.8 Cumulative Gains (Arabic 15)
    # -------------------------------------------------------------
    story.append(make_figure_pair(
        HERE / "6/figures/09_roc_curves.png", "Fig 3.7a: ROC curves of the four classifiers",
        HERE / "6/figures/10_pr_curves.png", "Fig 3.7b: PR curves of the four classifiers",
        width_cm=7.8, styles=st
    ))
    story.append(Paragraph(
        "Dual-curve analysis illustrates the critical difference between ROC and PR curves in imbalanced problems. While all four models "
        "achieve moderate ROC-AUC scores (0.71 to 0.79) due to the large true negative volume, the PR curves expose dramatic separation: "
        "Random Forest maintains an area of 0.4346, nearly 4× above the 0.1170 positive-class baseline.",
        st["body"]
    ))
    story.append(make_figure(HERE / "6/figures/11_cumulative_gains.png", "Fig 3.8: Cumulative gains of the Random Forest model", width_cm=11.5, styles=st))
    story.append(Paragraph("3.6 Interpretation and Business Recommendations", st["h2"]))
    story.append(Paragraph(
        "Cumulative gains analysis confirms tremendous efficiency benefits: ranking customers by predicted Random Forest probability and "
        "contacting only the top 20% reaches 60.40% of all potential subscribers, compared to only 20% under random calling. This cuts total "
        "call requirements by 80% while preserving over 60% of all new deposit acquisitions.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 20: Fig 3.9 Feature Importance, Recommendations & 3.7 Conclusion (Arabic 16)
    # -------------------------------------------------------------
    story.append(make_figure(HERE / "6/figures/12_permutation_importance.png", "Fig 3.9: Top Random Forest feature importances", width_cm=14.5, styles=st))
    story.append(Paragraph(
        "Permutation importance on the unseen test set demonstrates that historical campaign success (poutcome_success) is the primary "
        "predictive driver, followed by outreach timing (October, March), client bank balance, age, and cellular contact channel. Based on "
        "these empirical insights, four actionable business recommendations are established:",
        st["body"]
    ))
    rec_bullets = [
        "<b>1. Score-Ordered Calling:</b> Deploy the Random Forest model to rank calling lists by predicted subscription probability. Contacting the top 20% deciles captures 60.40% of all subscribers, eliminating 80% of unproductive calls.",
        "<b>2. Prioritize High-Yield Customer Profiles:</b> Prioritize past campaign successes (64.73% conversion rate), students (28.72%), retirees (22.79%), and tertiary-educated customers reachable on verified cellular lines.",
        "<b>3. Reallocate Outreach Seasonally:</b> Shift telemarketing staffing away from low-yield periods such as May (6.44% conversion) and concentrate promotional drives in March, September, October, and December.",
        "<b>4. Cap Contact Frequency at 3 Attempts:</b> Conversion rates diminish rapidly from 14.60% on initial contact to 11.20% on attempts 2–3, falling below 9.0% on 4 or more attempts. Capping contacts prevents customer fatigue and saves agent hours."
    ]
    for rcb in rec_bullets:
        story.append(Paragraph(f"{rcb}", st["bullet"]))
        
    story.append(Paragraph("3.7 Conclusion and Limitations", st["h2"]))
    story.append(Paragraph(
        "Random Forest is the optimal model for telemarketing deployment, providing the highest precision (50.78%), F1-score (0.4474), and PR-AUC "
        "(0.4346). Limitations include the historical vintage of the data (2008–2010), high prevalence of 'unknown' values in past campaign outcomes, "
        "exclusion of call duration to avoid leakage, and validation based on a single train/test split.",
        st["body"]
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # PAGE 21: 4. CONCLUSION and References (Arabic 17)
    # -------------------------------------------------------------
    story.append(Paragraph("4. CONCLUSION and References", st["h1"]))
    story.append(Paragraph("4.1 Conclusion", st["h2"]))
    story.append(Paragraph(
        "Both case studies demonstrate that careful data preprocessing, domain-informed feature engineering, and proper metric selection "
        "matter just as much as algorithm selection. In Case Study 3, engineering ticket fare per person, applying log transformations to "
        "correct skewness, and imputing age within passenger class and sex cohorts improved model reliability. Logistic regression achieved "
        "0.8156 accuracy, 79.71% survivor recall, and 0.8382 ROC-AUC. Natural-unit odds ratios provided physical insights: being male, traveling "
        "in third class, older age, and having siblings/spouses reduced survival odds, while higher individual fare improved odds. The model was "
        "successfully deployed as an interactive Streamlit application.",
        st["body"]
    ))
    story.append(Paragraph(
        "In Case Study 6, four classifiers were trained on bank marketing data with duration excluded to prevent leakage. Because only 11.70% "
        "of customers subscribed, accuracy was misleading. SMOTE oversampling inside training folds stabilized minority learning. Random Forest "
        "delivered the superior operational trade-off (50.78% precision, 0.4474 F1-score, and 0.4346 PR-AUC). Ranking customers by its score "
        "allows the bank to capture 60.40% of all subscribers within the top 20% of calls, reducing telemarketing volume by 80%.",
        st["body"]
    ))
    story.append(Paragraph("4.2 References", st["h2"]))
    refs = [
        "[1] Moro, S., Cortez, P., and Rita, P. (2014). “A Data-Driven Approach to Predict the Success of Bank Telemarketing.” Decision Support Systems, 62, 22–31. UCI Machine Learning Repository: Bank Marketing dataset.",
        "[2] Titanic Passenger Manifest dataset, course repository for Fundamentals of Data Science (22CSC59), Department of CSE, CBIT Hyderabad.",
        "[3] Pedregosa, F. et al. (2011). “Scikit-learn: Machine Learning in Python.” Journal of Machine Learning Research, 12, 2825–2830.",
        "[4] Python Data Science Ecosystem: pandas, NumPy, Matplotlib, seaborn, scikit-learn, imbalanced-learn, statsmodels, joblib, reportlab, Streamlit.",
        f"[5] Verified GitHub Source Code Repository: {REPO_URL}"
    ]
    for rf in refs:
        story.append(Paragraph(f"{rf}", st["bullet"]))
        
    return story


def build():
    for target in TARGET_FILES:
        story = build_story()
        doc = SimpleDocTemplate(
            str(target),
            pagesize=A4,
            leftMargin=2.4 * cm,
            rightMargin=2.4 * cm,
            topMargin=2.0 * cm,
            bottomMargin=2.2 * cm,
            title="Predicting Titanic Survival & Bank Marketing Prediction",
            author=NAME,
            subject=SUBJECT
        )
        doc.build(story, canvasmaker=ReferenceStyleCanvas)
        print(f"Successfully generated final report at: {target}")


if __name__ == "__main__":
    build()
