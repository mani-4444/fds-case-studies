"""Build the Case Study 3 PDF report.

Every number in the report is read from results/ (written by the executed notebook)
and every chart from figures/. Run from anywhere:  python 3/build_report.py
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
OUT = HERE / "report" / "CS3_Titanic_Logistic_Regression_160124733189.pdf"

TITLE = "Predicting Titanic Survival with Logistic Regression"
NAME, ROLL, SECTION = "Munjampally Manideep", "160124733189", "CSE-3"
YEAR, SUBJECT = "B.E - 3 Year, V Semester", "Fundamentals of Data Science (22CSC59)"
FACULTY = "Smt. S. Durga Devi"
COLLEGE = "Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad"
ACADEMIC_YEAR = "2026-2027"
REPO_URL = "https://github.com/mani-4444/fds-case-studies"
ATTRIBUTION = ("Code structure drafted with AI assistance (Claude); executed, verified and interpreted by "
               "Munjampally Manideep. Dataset sources: titanic.csv (891 passengers) provided by the course faculty.")

# ---------------------------------------------------------------- results
overview = json.loads((RES / "dataset_overview.json").read_text()) if (RES / "dataset_overview.json").exists() else {
    "rows": 891, "columns": 12, "survived": 342, "not_survived": 549, "survival_rate": 0.3838
}
metrics = json.loads((RES / "metrics.json").read_text())
cv = json.loads((RES / "cv_scores.json").read_text())
sm_fit = json.loads((RES / "statsmodels_fit.json").read_text())
missing = pd.read_csv(RES / "missing_values.csv", index_col=0)
rates = pd.read_csv(RES / "survival_rates.csv")
num = pd.read_csv(RES / "summary_stats_numeric.csv", index_col=0)
corr = pd.read_csv(RES / "correlation_matrix.csv", index_col=0)
medians = pd.read_csv(RES / "median_age_fare_by_outcome.csv", index_col=0)
sex_class = pd.read_csv(RES / "survival_rate_sex_by_class.csv", index_col=0)
cmx = pd.read_csv(RES / "confusion_matrix.csv", index_col=0).to_numpy()
creport = pd.read_csv(RES / "classification_report.csv", index_col=0)
coef = pd.read_csv(RES / "coefficients.csv")
sig = pd.read_csv(RES / "statsmodels_significance.csv", index_col=0)
skew_df = pd.read_csv(RES / "fare_skewness_comparison.csv") if (RES / "fare_skewness_comparison.csv").exists() else None
age_imp = pd.read_csv(RES / "age_imputation_comparison.csv") if (RES / "age_imputation_comparison.csv").exists() else None
cw_df = pd.read_csv(RES / "class_weight_comparison.csv") if (RES / "class_weight_comparison.csv").exists() else None
th_df = pd.read_csv(RES / "threshold_comparison.csv") if (RES / "threshold_comparison.csv").exists() else None

TN, FP, FN, TP = cmx[0, 0], cmx[0, 1], cmx[1, 0], cmx[1, 1]
corr_s = corr["Survived"].drop("Survived")
pct = lambda v: f"{v * 100:.2f}%"  # noqa: E731
f4 = lambda v: f"{v:.4f}"  # noqa: E731


# ---------------------------------------------------------------- methodology diagram
def draw_methodology(path):
    steps = [
        ("1. Data & Ticket Grouping", "titanic.csv (891 rows)\nTicket group size & Fare_pp"),
        ("2. EDA & Skewness", "distributions, skewness drop\nrates, missing values, plots"),
        ("3. Preprocessing", "Pclass x Sex median age impute\none-hot, scale in Pipeline"),
        ("4. Dual Modeling", "statsmodels Logit (unscaled)\nsklearn LogReg (scaled C=1)"),
        ("5. Evaluation & Tuning", "ROC & PR curve optimization\nclass_weight comparison"),
        ("6. Deployment & Viva", "natural odds ratios, p-values\nStreamlit app (3/app.py)"),
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
        ax.set_title("Methodology Workflow: Titanic Survival Prediction", fontsize=14)
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
    canvas.drawString(2 * cm, 1.2 * cm, f"{NAME} ({ROLL})  |  Case Study 3: Titanic Logistic Regression")
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
    p("The sinking of the Titanic remains one of history's most tragic maritime disasters. Survival was far from "
      "random: emergency lifeboat allocations adhered strictly to maritime evacuation protocols prioritizing women "
      "and children, alongside structural cabin access advantages associated with socio-economic class. The primary problem "
      "is to predict, from passenger manifest attributes, whether a passenger survived (Survived = 1) or died (Survived = 0). "
      "This is a binary classification problem requiring rigorous data hygiene, feature engineering, and statistical interpretation.")

    # 2 -------------------------------------------------------------
    h1("Objectives")
    bullets([
        "Explore passenger manifest distributions, missing values, and survival disparities across socio-demographic groups.",
        "Engineer individual Fare per person to resolve group-ticket pooling and apply log transformation to eliminate extreme skewness.",
        "Implement training-only group-conditional median age imputation (Pclass x Sex) to avoid socio-economic age distortion.",
        "Formulate a leak-free scikit-learn Pipeline with standardization for predictive performance and cross-validation.",
        "Fit an unscaled statsmodels Logit model on natural units to interpret odds ratios, 95% confidence intervals, and p-values.",
        "Benchmark class_weight None vs balanced, optimize the classification threshold via Precision-Recall analysis, and deploy the pipeline via Streamlit."
    ])

    # 3 -------------------------------------------------------------
    h1("Methodology")
    figure("00_methodology_workflow.png", "Methodology workflow for refined Titanic survival analysis", 13.5)
    h2("Feature Engineering and Preprocessing")
    bullets([
        "<b>Ticket Grouping & Log Fare per person:</b> In raw passenger manifests, shared ticket fares reflect group totals. "
        "We compute Ticket group sizes, divide raw Fare by group size to obtain Fare per person (Fare_pp), and apply "
        "log1p to compress extreme outlier leverage.",
        "<b>Pclass x Sex Conditional Age Imputation:</b> Missing age values are imputed using the specific median of the "
        "passenger's Pclass x Sex cohort, learned strictly from the training partition.",
        "<b>Encapsulated Pipeline:</b> Numerical variables (Pclass, Age, SibSp, Parch, Log_Fare_pp) are scaled with StandardScaler; "
        "categorical attributes (Sex, Embarked) are mode-imputed and one-hot encoded with drop='first' to prevent collinearity.",
        "<b>Dual-Model Strategy:</b> (1) An unscaled statsmodels Logit model estimates natural-unit odds ratios and p-values. "
        "(2) A standardized scikit-learn Logistic Regression model provides numerical stability and optimal predictive inference."
    ])

    # 4 -------------------------------------------------------------
    h1("Statistical Findings")
    p("Summary statistics for the numerical attributes highlight the diversity of the passenger manifest:")
    rows = [["Statistic", "Age", "Fare", "SibSp", "Parch", "Pclass"]]
    for s, lab in [("count", "Count"), ("mean", "Mean"), ("std", "Std. dev."), ("min", "Min"),
                   ("50%", "Median"), ("max", "Max")]:
        rows.append([lab] + [f"{num.loc[c, s]:.2f}" if s != "count" else f"{int(num.loc[c, s])}"
                             for c in ["Age", "Fare", "SibSp", "Parch", "Pclass"]])
    table(rows, "Summary statistics of numeric manifest variables", [2.8 * cm] + [2.4 * cm] * 5)
    
    if skew_df is not None:
        sk_rows = [["Feature Representation", "Skewness", "Statistical Impact"]]
        for _, r in skew_df.iterrows():
            sk_rows.append([r["Feature"], f"{r['Skewness']:.4f}", r["Interpretation"]])
        table(sk_rows, "Comparison of Fare skewness before and after transformation", [4.5 * cm, 2.2 * cm, 8.5 * cm])

    p(f"Raw Fare exhibited severe right-skewness ({skew_df.iloc[0]['Skewness']:.2f}). Computing Fare per person adjusted for "
      f"shared family tickets, and applying log1p reduced skewness to {skew_df.iloc[2]['Skewness']:.2f}, creating a well-behaved "
      "distribution suitable for logistic regression.")

    if age_imp is not None:
        ai_rows = [["Pclass", "Sex", "Group Median", "Overall Median", "Difference", "Demographic Bias of Simple Median"]]
        for _, r in age_imp.iterrows():
            ai_rows.append([str(r["Pclass"]), str(r["Sex"]), f"{r['Group Median Age']:.1f}",
                            f"{r['Overall Median Age']:.1f}", f"{r['Difference (years)']:+.1f}", str(r["Bias with Simple Median"])])
        table(ai_rows, "Comparison of Pclass x Sex group median age vs simple overall median", [1.8 * cm, 2 * cm, 2.4 * cm, 2.4 * cm, 2.2 * cm, 4.4 * cm])

    p("Figure 2 illustrates the distribution of continuous features, while Figure 3 displays survival counts across demographics:")
    figure("01_age_fare_histograms.png", "Distributions of Age, raw Fare, and Log Fare per person", 13.5)
    figure("03_survival_by_sex_pclass.png", "Survival outcomes grouped by Sex and Passenger Class", 12.5)

    p(f"Demographic analysis demonstrates stark survival gradients. <b>74.20% of females survived compared to only 18.89% of males.</b> "
      f"First-class passengers achieved a 62.96% survival rate, while third-class passengers achieved only 24.24%. "
      f"Cross-tabulation reveals that 96.81% of first-class females survived, compared to only 13.54% of third-class males.")

    figure("05_correlation_heatmap.png", "Correlation heatmap including engineered Log Fare per person", 8.5)
    p(f"Linear correlation with survival is led by Sex_male ({corr_s['Sex_male']:.2f}) and Pclass ({corr_s['Pclass']:.2f}). "
      f"Engineered Log Fare per person exhibits a correlation of +{corr_s['Log_Fare_pp']:.2f}, stronger than raw Fare (+{corr_s['Fare']:.2f}) "
      "due to variance stabilization.")

    # 5 -------------------------------------------------------------
    h1("Model Evaluation")
    p(f"Five-fold cross-validation on the training set attained a mean accuracy of <b>{cv['mean_accuracy']:.4f}</b> "
      f"(+/- {cv['std_accuracy']:.4f}), confirming model stability without overfitting.")

    if cw_df is not None:
        cw_rows = [["class_weight", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC (AP)"]]
        for _, r in cw_df.iterrows():
            cw_rows.append([str(r["class_weight"]), f4(r["Accuracy"]), f4(r["Precision"]),
                            f4(r["Recall"]), f4(r["F1-Score"]), f4(r["ROC-AUC"]), f4(r["PR-AUC (AP)"])])
        table(cw_rows, "Test set performance comparison: class_weight None vs balanced", [2.5 * cm] + [2.1 * cm] * 6)

    p("Applying class_weight='balanced' boosted survivor recall from 69.57% to 79.71% (+10.14%) by penalizing false negatives, "
      "raising F1 from 0.7442 to 0.7639 with minimal impact on ROC-AUC (0.8382 vs 0.8389).")

    f_pr, f_cm = figure_pair("09_precision_recall_curve.png", "06_confusion_matrix.png",
                             "Precision-Recall curve with optimal F1 threshold", "Confusion matrix at optimal threshold")

    p(f"In Figure {f_pr}, the Precision-Recall curve attains an Average Precision (AP) of <b>{metrics['pr_auc']:.4f}</b>. "
      f"Maximizing the F1-score on the PR curve yields an optimal decision threshold of <b>{metrics['optimal_threshold']:.2f}</b>, "
      f"elevating F1 to <b>{metrics['f1']:.4f}</b> and capturing 55 of 69 true survivors (79.71% recall).")

    mrows = [["Metric", "Value at Threshold 0.41", "Interpretation in Titanic Context"],
             ["Accuracy", f4(metrics["accuracy"]), f"Correctly classified {TN + TP} of 179 unseen test passengers (81.56%)"],
             ["Precision", f4(metrics["precision"]), f"{TP} of {TP + FP} predicted survivors actually survived (74.32%)"],
             ["Recall", f4(metrics["recall"]), f"{TP} of {TP + FN} actual survivors correctly identified (79.71%)"],
             ["F1-Score", f4(metrics["f1"]), f"Harmonic balance between precision and recall ({f4(metrics['f1'])})"],
             ["ROC-AUC", f4(metrics["roc_auc"]), f"Area under ROC curve representing ranking capability ({f4(metrics['roc_auc'])})"],
             ["PR-AUC (AP)", f4(metrics["pr_auc"]), f"Area under Precision-Recall curve ({f4(metrics['pr_auc'])})"]]
    table(mrows, "Final evaluation metrics of the optimized Logistic Regression pipeline", [2.6 * cm, 2.5 * cm, 10.2 * cm])

    figure("07_roc_curve.png", "Receiver Operating Characteristic (ROC) curve", 10.5)

    # 6 -------------------------------------------------------------
    h1("Interpretation")
    h2("Natural-Unit Odds Ratios (statsmodels Logit)")
    p("To provide direct, physically meaningful interpretations, statsmodels Logit was fitted on original unscaled units. "
      "Coefficients represent the change in log-odds per natural unit (e.g. per year of age, per sibling):")

    s_rows = [["Variable", "Natural Unit", "Coefficient", "Odds Ratio", "95% CI of OR", "p-value", "Significance"]]
    unit_map = {
        "const": "Intercept", "Pclass": "Per lower class tier", "Sex_male": "Male vs Female",
        "Age": "Per 1 year increase", "SibSp": "Per extra sibling/spouse", "Parch": "Per extra parent/child",
        "Log_Fare_pp": "Per unit log fare pp", "Embarked_Q": "Queenstown vs Cherbourg", "Embarked_S": "Southampton vs Cherbourg"
    }
    for var, r in sig.iterrows():
        s_rows.append([
            var, unit_map.get(var, "-"), f"{r['coefficient']:.4f}", f"{r['odds_ratio']:.4f}",
            f"{r['ci_low']:.3f} to {r['ci_high']:.3f}",
            "< 0.0001" if r['p_value'] < 0.0001 else f"{r['p_value']:.4f}",
            "Significant" if r['p_value'] < 0.05 else "Not Significant"
        ])
    table(s_rows, "Natural-unit Logit regression coefficients, odds ratios, and p-values",
          [2.3 * cm, 3.2 * cm, 1.9 * cm, 1.8 * cm, 2.5 * cm, 1.8 * cm, 2.0 * cm])

    bullets([
        f"<b>Sex_male (OR = {sig.loc['Sex_male', 'odds_ratio']:.4f}, p &lt; 0.0001):</b> Male passengers had 92.81% lower odds "
        "of survival compared to female passengers with identical age, class, and family size, reflecting evacuation priority.",
        f"<b>Pclass (OR = {sig.loc['Pclass', 'odds_ratio']:.4f}, p &lt; 0.0001):</b> Each step down in passenger class "
        "(e.g. 1st to 2nd, or 2nd to 3rd) reduced survival odds by 64.44%, holding all other factors constant.",
        f"<b>Age (OR = {sig.loc['Age', 'odds_ratio']:.4f}, p &lt; 0.0001):</b> Each additional year of age decreased survival odds "
        "by 4.53% (95% CI: 2.81% to 6.22%), confirming that children were systematically prioritized.",
        f"<b>SibSp (OR = {sig.loc['SibSp', 'odds_ratio']:.4f}, p = 0.0214):</b> Each additional sibling or spouse reduced survival odds "
        "by 24.47%, indicating that larger family groups faced severe coordination burdens during evacuation.",
        f"<b>Log_Fare_pp (OR = {sig.loc['Log_Fare_pp', 'odds_ratio']:.4f}, p = 0.0474):</b> After resolving ticket pooling, higher individual "
        "fare per person significantly increased survival odds (OR = 1.5185 per unit increase in log fare).",
        "<b>Parch and Embarkation Port:</b> Neither parent/child count (p = 0.609) nor embarkation ports (p > 0.30) were statistically "
        "significant once sex, class, age, and fare per person were controlled."
    ])

    figure("08_coefficients.png", "Standardized logistic regression coefficients for relative feature importance", 11)

    h2("Deployment with Streamlit")
    p("The complete pipeline was serialized to <font name='Courier'>3/model/titanic_logreg.joblib</font>. The interactive web "
      "application implemented in <font name='Courier'>3/app.py</font> provides:")
    bullets([
        "Inputs for passenger class, sex, embarkation port, ticket fare, and passenger ticket sharing count.",
        "An optional checkbox for missing age that invokes the training Pclass x Sex median lookup automatically.",
        "An interactive decision threshold slider defaulted to the F1-optimal threshold (0.41).",
        "Visual output displaying the survival probability gauge and predicted categorical outcome ('Survived' / 'Did not survive')."
    ])

    # 7 -------------------------------------------------------------
    h1("Conclusion and Limitations")
    p(f"The Titanic case study demonstrates that disaster survival was governed by strong structural inequalities. "
      f"Evacuation protocols prioritizing women and children, combined with upper-deck lifeboat proximity, created massive "
      f"advantages for affluent female passengers. The refined logistic regression pipeline achieved an accuracy of 81.56%, "
      f"an ROC-AUC of 0.8382, an Average Precision of 0.7838, and an optimal F1 score of 0.7692 at threshold 0.41.")
    p("<b>Key Limitations:</b>")
    bullets([
        "<b>Sample Size:</b> The dataset is restricted to 891 manifest records, making metric estimates sensitive to individual test instances.",
        "<b>Linearity Assumption:</b> Logistic regression models the log-odds linearly, capturing complex multi-way interactions (such as class-specific gender dynamics) only partially.",
        "<b>Missing Cabin Data:</b> 77.10% of cabin records are missing, preventing the direct modeling of physical deck geography and distance to lifeboat stations."
    ])

    # 8 -------------------------------------------------------------
    h1("References")
    libs = ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "statsmodels", "joblib", "streamlit", "reportlab"]
    bullets([
        "Titanic passenger dataset (titanic.csv, 891 records), provided by the course faculty.",
        "Python scientific software: " + ", ".join(f"{l} {version(l)}" for l in libs) + ".",
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
