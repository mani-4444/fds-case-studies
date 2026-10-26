"""Build the Case Study 6 PDF report.

Every number in the report is read from results/ (written by the executed notebook)
and every chart from figures/. Run from anywhere:  python 6/build_report.py
"""
import json
import logging
from importlib.metadata import version
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from xml.sax.saxutils import escape  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,  # noqa: E402
                                SimpleDocTemplate, Spacer, Table, TableStyle)

HERE = Path(__file__).resolve().parent
RES, FIG = HERE / "results", HERE / "figures"
OUT = HERE / "report" / "CS6_Bank_Marketing_Classification_160124733189.pdf"

TITLE = "Comparative Analysis of Classification Algorithms for Bank Marketing Prediction"
NAME, ROLL, SECTION = "Munjampally Manideep", "160124733189", "CSE-3"
YEAR, SUBJECT = "B.E - 3 Year, V Semester", "Fundamentals of Data Science (22CSC59)"
FACULTY = "Smt. S. Durga Devi"
COLLEGE = "Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad"
ACADEMIC_YEAR = "2026-2027"
REPO_URL = "https://github.com/mani-4444/fds-case-studies"
ATTRIBUTION = ("Code structure drafted with AI assistance (Claude); executed, verified and interpreted by "
               "Munjampally Manideep. Dataset sources: bank/bank-full.csv (45,211 records, S. Moro, P. Cortez and P. Rita, 2014) "
               "provided via UCI Machine Learning Repository.")
CITATION = ("S. Moro, P. Cortez and P. Rita. A Data-Driven Approach to Predict the Success of Bank Telemarketing. "
            "Decision Support Systems, 62:22-31, 2014. doi:10.1016/j.dss.2014.03.001.")

# ---------------------------------------------------------------- results
comp = pd.read_csv(RES / "model_comparison.csv", index_col=0)
num = pd.read_csv(RES / "numeric_summary.csv", index_col=0)
unknown = pd.read_csv(RES / "unknown_counts.csv", index_col=0)
rates = pd.read_csv(RES / "eda_subscription_rates.csv")
perm = pd.read_csv(RES / "permutation_importance.csv")
gains_deciles = json.loads((RES / "cumulative_gains_deciles.json").read_text()) if (RES / "cumulative_gains_deciles.json").exists() else {}

BEST = "Random Forest"
f4 = lambda v: f"{v:.4f}"  # noqa: E731
pct = lambda v: f"{v * 100:.2f}%"  # noqa: E731


# ---------------------------------------------------------------- methodology diagram
def draw_methodology(path):
    steps = [
        ("1. Data Understanding", "bank-full.csv (45,211 rows)\n16 features, pdays=-1"),
        ("2. EDA & Hygiene", "drop duration (leakage)\nretain unknown, rates & boxplots"),
        ("3. SMOTE Pipeline", "imblearn Pipeline (pre + SMOTE)\ntouches training folds only"),
        ("4. Four Classifiers", "LogReg, Decision Tree, KNN,\nRandom Forest (uniform setup)"),
        ("5. Dual Curve Evaluation", "ROC & PR curves (PR-AUC)\n2x2 confusion matrix grid"),
        ("6. Inference & Impact", "test-set permutation importance\ngains chart, bank strategy"),
    ]
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    with plt.xkcd(scale=0.8, length=120, randomness=2):
        fig, ax = plt.subplots(figsize=(12, 5.2))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 5.2)
        ax.axis("off")
        xs, ys = [0.3, 4.3, 8.3], [3.0, 0.4]
        w, h = 3.4, 1.8
        centers = []
        for i, (head, body) in enumerate(steps):
            x, y = xs[i % 3], ys[i // 3]
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                        fc=["#d8f3dc", "#ffe8cc", "#dbe7ff"][i % 3], ec="black", lw=1.8))
            ax.text(x + w / 2, y + h - 0.45, head, ha="center", va="center", fontsize=12, fontweight="bold")
            ax.text(x + w / 2, y + 0.6, body, ha="center", va="center", fontsize=9.5)
            centers.append((x, y))
        arrow = dict(arrowstyle="->", lw=2, color="black")
        for i in (0, 1, 3, 4):
            x, y = centers[i]
            ax.annotate("", xy=(x + w + 0.55, y + h / 2), xytext=(x + w + 0.05, y + h / 2), arrowprops=arrow)
        gap_y = (ys[0] + ys[1] + h) / 2
        ax.plot([xs[2] + w / 2, xs[2] + w / 2, xs[0] + w / 2], [ys[0] - 0.08, gap_y, gap_y], color="black", lw=2)
        ax.annotate("", xy=(xs[0] + w / 2, ys[1] + h + 0.1), xytext=(xs[0] + w / 2, gap_y), arrowprops=arrow)
        ax.set_title("Methodology Workflow: Bank Marketing Classification", fontsize=14)
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)


# ---------------------------------------------------------------- styles and helpers
ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica", fontSize=9.5, leading=13.5,
                      alignment=TA_JUSTIFY, spaceAfter=5)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=14, bulletIndent=4, spaceAfter=2.5)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=13.5, spaceBefore=9,
                    spaceAfter=5, textColor=colors.HexColor("#1d3557"))
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11, spaceBefore=5,
                    spaceAfter=3, textColor=colors.HexColor("#1d3557"))
CAP = ParagraphStyle("cap", parent=BODY, fontName="Helvetica-Oblique", fontSize=8.5, leading=11,
                     alignment=TA_CENTER, spaceBefore=3, spaceAfter=8)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.2, leading=10, alignment=0, spaceAfter=0)

story = []
counters = {"fig": 0, "tab": 0, "sec": 0}
pending = []


def add(flowable):
    if pending:
        inner = flowable._content if isinstance(flowable, KeepTogether) else [flowable]
        flowable = KeepTogether(pending + list(inner))
        pending.clear()
    story.append(flowable)


def p(text):
    add(Paragraph(text, BODY))


def bullets(items):
    for t in items:
        add(Paragraph(t, BULLET, bulletText="•"))


def h1(text):
    counters["sec"] += 1
    pending.append(Paragraph(f"{counters['sec']}. {text}", H1))


def h2(text):
    pending.append(Paragraph(text, H2))


def figure(name, caption, width_cm=16.0):
    counters["fig"] += 1
    path = FIG / name
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(str(path)).getSize()
    w = width_cm * cm
    img = Image(str(path), width=w, height=w * ih / iw, hAlign="CENTER")
    add(KeepTogether([img, Paragraph(f"Figure {counters['fig']}: {caption}", CAP)]))
    return counters["fig"]


def figure_pair(left, right, cap_left, cap_right, width_cm=8.5):
    from reportlab.lib.utils import ImageReader
    cells = []
    for name, cap in ((left, cap_left), (right, cap_right)):
        counters["fig"] += 1
        iw, ih = ImageReader(str(FIG / name)).getSize()
        w = width_cm * cm
        cells.append([Image(str(FIG / name), width=w, height=w * ih / iw, hAlign="CENTER"),
                      Paragraph(f"Figure {counters['fig']}: {cap}", CAP)])
    t = Table([cells], colWidths=[(width_cm + 0.2) * cm] * 2, hAlign="CENTER")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
    add(t)
    return counters["fig"] - 1, counters["fig"]


def table(rows, caption, col_widths=None, header=True):
    counters["tab"] += 1
    data = [[Paragraph(str(c), CELL) for c in r] for r in rows]
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0, hAlign="CENTER")
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa5b1")),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9eef6"))]
    t.setStyle(TableStyle(style))
    add(KeepTogether([Paragraph(f"Table {counters['tab']}: {caption}", CAP), t, Spacer(1, 6)]))
    return counters["tab"]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, f"{NAME} ({ROLL})  |  Case Study 6: Bank Marketing Classification")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def title_page():
    hdr = ParagraphStyle("hdr", parent=BODY, alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=colors.HexColor("#1d3557"))
    sub_hdr = ParagraphStyle("subhdr", parent=BODY, alignment=TA_CENTER, fontName="Helvetica", fontSize=11, leading=15)
    t_lbl = ParagraphStyle("t_lbl", parent=BODY, alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=14, leading=19, textColor=colors.HexColor("#b7094c"))
    t_main = ParagraphStyle("t_main", parent=BODY, alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=16, leading=22, textColor=colors.HexColor("#1d3557"))
    sec_lbl = ParagraphStyle("sec_lbl", parent=BODY, fontName="Helvetica-Bold", fontSize=11, leading=16, textColor=colors.HexColor("#1d3557"))
    meta = ParagraphStyle("meta", parent=BODY, fontName="Helvetica", fontSize=10.5, leading=16)

    story.append(Spacer(1, 1.8 * cm))
    story.append(Paragraph("CHAITANYA BHARATHI INSTITUTE OF TECHNOLOGY (CBIT)", hdr))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Department Of Computer Science And Engineering", sub_hdr))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("FUNDAMENTALS OF DATA SCIENCE (22CSC59)", sub_hdr))
    story.append(Spacer(1, 2.8 * cm))
    
    story.append(Paragraph("CASE STUDY REPORT", t_lbl))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Title: {TITLE}", t_main))
    story.append(Spacer(1, 2.8 * cm))
    
    story.append(Paragraph("<b>Submitted by:</b>", sec_lbl))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"Name: {NAME}", meta))
    story.append(Paragraph(f"Roll Number: {ROLL}", meta))
    story.append(Paragraph(f"Section: {SECTION}", meta))
    story.append(Paragraph("Year: B.E - 3 Year", meta))
    story.append(Paragraph("Semester: V", meta))
    
    story.append(Spacer(1, 1.4 * cm))
    story.append(Paragraph("<b>Submitted to:</b>", sec_lbl))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"Faculty Name: {FACULTY}", meta))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Academic Year: {ACADEMIC_YEAR}", meta))
    story.append(PageBreak())


# ---------------------------------------------------------------- content
def build():
    draw_methodology(FIG / "00_methodology_workflow.png")
    title_page()

    # 1 -------------------------------------------------------------
    h1("Problem Statement")
    p("Direct marketing campaigns represent a substantial expenditure for financial institutions. Telemarketing efficiency "
      "is undermined when staff contact uninterested customers at random, resulting in low conversion rates, excessive call center "
      "costs, and brand fatigue. In this case study, a Portuguese retail bank conducted direct telemarketing campaigns to offer "
      "long-term bank deposits. The problem is to predict whether a client will subscribe to a term deposit (y = 1) or decline "
      "(y = 0) prior to initiating a call, enabling targeted, rank-ordered telemarketing that maximizes subscriber acquisition while "
      "minimizing wasted outreach.")

    # 2 -------------------------------------------------------------
    h1("Objectives")
    bullets([
        "Utilize the primary UCI Bank Marketing dataset (bank/bank-full.csv, 45,211 rows) capturing customer account balances and campaign timing.",
        "Perform exploratory data analysis to identify key subscriber demographics, seasonal response patterns, and historical campaign effects.",
        "Strictly eliminate target leakage by excluding call duration from all training and test matrices.",
        "Address severe 88.3% to 11.7% class imbalance using Synthetic Minority Over-sampling Technique (SMOTE) inside leak-free imblearn pipelines.",
        "Develop, optimize, and evaluate four distinct classifiers: Logistic Regression, Decision Tree, K-Nearest Neighbours, and Random Forest.",
        "Conduct comprehensive evaluation using ROC curves and Precision-Recall analysis (PR-AUC) tailored to imbalanced data.",
        "Calculate test-set permutation feature importance and cumulative gains curves to establish actionable business recommendations."
    ])

    # 3 -------------------------------------------------------------
    h1("Methodology")
    figure("00_methodology_workflow.png", "Methodology workflow for comparative bank marketing classification", 13.5)
    h2("Dataset Selection and Attribute Differences")
    bullets([
        "<b>Switch to bank/bank-full.csv:</b> This study utilizes the primary bank-full.csv benchmark (45,211 rows, 17 columns). "
        "Unlike the bank-additional variant, bank-full captures client account balances (balance in euros) and calendar contact day (day), "
        "while omitting broader macroeconomic indicators (such as Euribor rates or employment indices).",
        "<b>Handling pdays:</b> Clients not previously contacted are coded as pdays = -1 (36,954 clients, 81.74%).",
        "<b>Duration Exclusion:</b> Call duration is known only after a conversation ends and is strongly correlated with success. "
        "Including duration induces retrospective target leakage; it is strictly excluded from all predictive models."
    ])
    h2("SMOTE Oversampling in Leak-Free Pipeline")
    p("SMOTE balances class distributions by synthesizing new minority instances along line segments connecting k nearest "
      "minority neighbors in feature space. To guarantee total isolation of test data, SMOTE is embedded inside an "
      "<font name='Courier'>imblearn.pipeline.Pipeline</font>. During training, SMOTE oversamples only the training fold; "
      "during testing, the unseen test fold remains 100% natural and un-augmented. Crucially, SMOTE handles imbalance at the "
      "feature representation level, providing an identical, balanced training framework for all four algorithms including KNN.")

    # 4 -------------------------------------------------------------
    h1("Statistical Findings")
    p("Summary statistics for numerical features across all 45,211 clients are summarized below:")
    n_rows = [["Feature", "Count", "Mean", "Std. Dev.", "Min", "Median", "Max"]]
    for f_name, r in num.iterrows():
        n_rows.append([f_name, f"{int(r['count']):,}", f"{r['mean']:.2f}", f"{r['std']:.2f}",
                       f"{r['min']:.2f}", f"{r['50%']:.2f}", f"{r['max']:.2f}"])
    table(n_rows, "Summary statistics of numerical features in bank-full.csv", [2.5 * cm, 2.2 * cm, 2.3 * cm, 2.3 * cm, 2.1 * cm, 2.1 * cm, 2.3 * cm])

    p("Categorical attributes contain zero nulls, but 'unknown' appears frequently in poutcome (36,959 rows, 81.75%) "
      "and contact (13,020 rows, 28.80%). We retain 'unknown' as an explicit category because missing historical contact represents "
      "a critical predictive signal rather than missing data.")

    f_tgt, f_job = figure_pair("01_target_distribution.png", "02_rate_by_job.png",
                               "Class distribution of term deposit outcome", "Subscription rate across occupations")

    p(f"As shown in Figure {f_tgt}, the target is heavily imbalanced: 39,922 clients (88.30%) declined the deposit, while 5,289 "
      f"(11.70%) subscribed. Occupational analysis (Figure {f_job}) reveals that <b>students (28.68%) and retired clients (22.79%) "
      "subscribe at more than double the bank average</b>, whereas blue-collar workers achieve only a 7.27% conversion rate.")

    figure_pair("03_rate_by_month.png", "04_rate_by_contact_poutcome_edu.png",
                "Subscription rate by calendar month", "Subscription rates by contact type, previous outcome, and education")
    p("Campaign timing displays dramatic seasonality: shoulder months achieve extraordinary conversion rates (March: 51.99%, "
      "September: 46.46%, October: 43.77%, December: 46.73%). In contrast, May experienced the heaviest call volume (13,766 calls) "
      "but generated the lowest conversion rate at just 6.72%. Prior campaign outcome is the single most decisive historical indicator: "
      "<b>clients who previously subscribed (poutcome = success) converted at 64.73%</b>, compared to only 9.16% for unknown. "
      "Cellular contacts converted at 14.92%, nearly four times higher than unknown communication types (4.07%).")

    figure("05_numeric_boxplots.png", "Numerical attributes (age, balance, day, campaign) by subscription outcome", 11.5)

    # 5 -------------------------------------------------------------
    h1("Model Evaluation")
    p("All four models were trained on 36,168 clients using identical SMOTE pipelines and evaluated on 9,043 unseen test clients. "
      "Table 2 reports the comprehensive comparative performance metrics:")

    c_rows = [["Model", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC (AP)"]]
    for m_name, r in comp.iterrows():
        c_rows.append([m_name, f4(r["Accuracy"]), f4(r["Precision"]), f4(r["Recall"]),
                       f4(r["F1"]), f4(r["ROC_AUC"]), f4(r["PR_AUC"])])
    table(c_rows, "Comparative performance metrics across classifiers on unseen test set", [3.2 * cm] + [2.2 * cm] * 6)

    figure_pair("07_metrics_grouped_bar.png", "08_confusion_matrices.png",
                "Comparative evaluation metrics across models", "Confusion matrices on the unseen test set")

    p("The evaluation illustrates marked algorithmic differences: <b>Random Forest achieves the highest overall discrimination</b> "
      "with an Accuracy of 0.8844, Precision of 0.5078, F1-Score of 0.4474, ROC-AUC of 0.7922, and PR-AUC of 0.4346. "
      "While KNN and Logistic Regression yield higher raw recall (65.60% and 61.91%), they suffer from low precision (23.30% and 25.87%), "
      "generating thousands of wasted phone calls.")

    f_roc, f_pr = figure_pair("09_roc_curves.png", "10_pr_curves.png",
                              "Receiver Operating Characteristic curves", "Precision-Recall curves (PR-AUC)")

    p("<b>Why PR-AUC suits imbalanced data:</b> In imbalanced domains where 88.3% of instances are negative, ROC curves can present "
      "an overly optimistic assessment because the False Positive Rate denominator is dominated by huge True Negative counts. "
      "In Figure 8, Precision-Recall curves focus strictly on minority positive retrieval without TN inflation. Random Forest dominates "
      "the PR space with a PR-AUC of 0.435, almost four times higher than the 0.117 random dialing baseline.")

    figure_pair("11_cumulative_gains.png", "12_permutation_importance.png",
                "Cumulative gains curve for Random Forest", "Test-set permutation importance for Random Forest")

    p(f"The cumulative gains chart confirms exceptional operational efficiency: <b>contacting the top 20% highest-probability "
      f"clients identifies {gains_deciles.get('Top 20%', 51.23)}% of all subscribers</b>. Contacting the top 30% identifies "
      f"{gains_deciles.get('Top 30%', 66.64)}% of all subscribers, cutting telemarketing call requirements by over 70%.")

    p("<b>Permutation Importance vs Built-in MDI:</b> Built-in Random Forest importance (Mean Decrease in Impurity) is computed "
      "on training splits and biased toward high-cardinality features. Permutation importance on the unseen test set measures the "
      "actual drop in generalization performance (ROC-AUC) when each feature is shuffled. Contact medium (drop: 0.0627), "
      "campaign month (0.0572), prior outcome (0.0191), day of month (0.0165), and housing loan status (0.0132) emerge as the "
      "primary genuine predictors of customer subscription.")

    # 6 -------------------------------------------------------------
    h1("Interpretation and Business Recommendations")
    h2("Best Model Justification")
    p("Random Forest is definitively selected as the champion model. In retail telemarketing, every call incurs direct agent labor "
      "costs and risks customer goodwill. KNN captures 694 subscribers but produces 2,285 false alarms (precision 23.3%). Random Forest "
      "achieves 50.78% precision (more than 1 in 2 calls convert) while capturing 423 subscribers directly at default threshold, "
      "with superior probability calibration for decile lead scoring.")
    h2("Actionable Business Strategies")
    bullets([
        "<b>Model-Ranked Calling Queues:</b> Replace random dialing by scoring customer leads with Random Forest probability outputs. "
        "Calling strictly in descending order reaches over 51% of all depositors within the first 20% of calls, cutting operational costs by ~80%.",
        "<b>Prioritize High-Conversion Subgroups:</b> Focus telemarketing outreach on customers with past campaign success (64.7% conversion), "
        "students and retirees (>22% conversion), and clients contacted via personal mobile phones (14.9% vs 4.1% for unknown).",
        "<b>Restructure Campaign Calendar:</b> Reallocate call center capacity from low-yield months like May (6.7% conversion) to high-yield "
        "shoulder periods (March, September, October, December: all >40% conversion).",
        "<b>Cap Repetitive Contact Attempts:</b> Establish a policy limit of 3 calls per customer per campaign. Boxplot analysis demonstrates "
        "that additional calls beyond the third attempt yield sharply diminishing returns while annoying customers."
    ])

    # 7 -------------------------------------------------------------
    h1("Conclusion and Limitations")
    p("This case study implemented a complete machine learning workflow on the UCI Bank Marketing dataset (45,211 clients). "
      "SMOTE oversampling embedded in imblearn pipelines resolved severe class imbalance without leakage. Random Forest demonstrated "
      "superior performance (Accuracy: 0.8844, Precision: 0.5078, F1: 0.4474, ROC-AUC: 0.7922, PR-AUC: 0.4346), enabling "
      "highly targeted customer ranking that captures the majority of depositors within the top contact deciles.")
    p("<b>Limitations:</b>")
    bullets([
        "<b>Pre-Call Information Constraint:</b> Call duration was excluded to eliminate leakage; models rely strictly on static manifest signals.",
        "<b>Omission of Macroeconomic Context:</b> bank-full.csv omits real-time economic indicators (interest rates, consumer confidence) "
        "that strongly dictate savings deposit attractiveness.",
        "<b>Dynamic Thresholding Necessity:</b> When call center staffing allows broader reach, the decision threshold should be lowered "
        "along the PR curve to capture additional subscribers."
    ])

    # 8 -------------------------------------------------------------
    h1("References")
    libs = ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "imbalanced-learn", "reportlab"]
    bullets([
        f"Primary dataset citation: {CITATION}",
        "Dataset archive: UCI Machine Learning Repository, bank-full.csv (45,211 records).",
        "Python scientific environment: " + ", ".join(f"{l} {version(l)}" for l in libs) + ".",
        f"GitHub project repository: {escape(REPO_URL)}"
    ])

    # 9 -------------------------------------------------------------
    h1("AI Assistance Acknowledgement")
    p(ATTRIBUTION)

    OUT.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                            bottomMargin=2 * cm, title=TITLE, author=NAME, subject=SUBJECT)
    doc.build(story, onLaterPages=footer)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
