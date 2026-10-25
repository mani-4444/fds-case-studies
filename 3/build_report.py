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

TITLE = "Case Study 3: Predicting Titanic Survival with Logistic Regression"
NAME, ROLL, SECTION = "Munjampally Manideep", "160124733189", "CSE-3"
YEAR, SUBJECT = "III Year, V Semester (2026-27)", "Fundamentals of Data Science"
FACULTY = "<FACULTY NAME>"
COLLEGE = "Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad"
SUBMISSION_DATE = "26 October 2026"
REPO_URL = "<GITHUB REPO URL>"
ATTRIBUTION = ("Code structure drafted with AI assistance (Claude); executed, verified and interpreted by "
               "Munjampally Manideep. Dataset sources: titanic.csv (891 passengers) provided by the course faculty.")

# ---------------------------------------------------------------- results
overview = json.loads((RES / "dataset_overview.json").read_text())
metrics = json.loads((RES / "metrics.json").read_text())
cv = json.loads((RES / "cv_scores.json").read_text())
sm_fit = json.loads((RES / "statsmodels_fit.json").read_text())
missing = pd.read_csv(RES / "missing_values.csv", index_col=0)
rates = pd.read_csv(RES / "survival_rates.csv", index_col=0)
num = pd.read_csv(RES / "summary_stats_numeric.csv", index_col=0)
corr = pd.read_csv(RES / "correlation_matrix.csv", index_col=0)
medians = pd.read_csv(RES / "median_age_fare_by_outcome.csv", index_col=0)
sex_class = pd.read_csv(RES / "survival_rate_sex_by_class.csv", index_col=0)
cmx = pd.read_csv(RES / "confusion_matrix.csv", index_col=0).to_numpy()
creport = pd.read_csv(RES / "classification_report.csv", index_col=0)
coef = pd.read_csv(RES / "coefficients.csv")
sig = pd.read_csv(RES / "statsmodels_significance.csv", index_col=0)

TN, FP, FN, TP = cmx[0, 0], cmx[0, 1], cmx[1, 0], cmx[1, 1]
rate = rates["survival_rate"]
corr_s = corr["Survived"].drop("Survived")
pct = lambda v: f"{v * 100:.2f}%"  # noqa: E731
f4 = lambda v: f"{v:.4f}"  # noqa: E731


# ---------------------------------------------------------------- methodology diagram
def draw_methodology(path):
    steps = [
        ("1. Data", "titanic.csv\n891 rows, 12 columns"),
        ("2. EDA", "summaries, missing values,\nsurvival rates, plots"),
        ("3. Preprocessing", "drop 4 columns, impute,\none-hot, scale (Pipeline)"),
        ("4. Model", "Logistic Regression\n80:20 stratified split, 5-fold CV"),
        ("5. Evaluation", "accuracy, precision, recall,\nF1, ROC-AUC, confusion matrix"),
        ("6. Interpretation\n& Deployment", "odds ratios, p-values,\njoblib + Streamlit app"),
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
            ax.text(x + w / 2, y + h - 0.45, head, ha="center", va="center", fontsize=13, fontweight="bold")
            ax.text(x + w / 2, y + 0.6, body, ha="center", va="center", fontsize=9.5)
            centers.append((x, y))
        arrow = dict(arrowstyle="->", lw=2, color="black")
        for i in (0, 1, 3, 4):
            x, y = centers[i]
            ax.annotate("", xy=(x + w + 0.55, y + h / 2), xytext=(x + w + 0.05, y + h / 2), arrowprops=arrow)
        # Wrap from step 3 to step 4 through the gap between the two rows.
        gap_y = (ys[0] + ys[1] + h) / 2
        ax.plot([xs[2] + w / 2, xs[2] + w / 2, xs[0] + w / 2], [ys[0] - 0.08, gap_y, gap_y], color="black", lw=2)
        ax.annotate("", xy=(xs[0] + w / 2, ys[1] + h + 0.1), xytext=(xs[0] + w / 2, gap_y), arrowprops=arrow)
        ax.set_title("Methodology Workflow: Titanic Survival Prediction", fontsize=15)
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)


# ---------------------------------------------------------------- styles and helpers
ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica", fontSize=10, leading=13.5,
                      alignment=TA_JUSTIFY, spaceAfter=6)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=14, bulletIndent=4, spaceAfter=3)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=14.5, spaceBefore=10,
                    spaceAfter=6, textColor=colors.HexColor("#1d3557"))
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, spaceBefore=6,
                    spaceAfter=4, textColor=colors.HexColor("#1d3557"))
CAP = ParagraphStyle("cap", parent=BODY, fontName="Helvetica-Oblique", fontSize=9, leading=11.5,
                     alignment=TA_CENTER, spaceBefore=3, spaceAfter=10)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.8, leading=10.5, alignment=0, spaceAfter=0)

story = []
counters = {"fig": 0, "tab": 0, "sec": 0}
pending = []  # headings waiting to be kept on the same page as the next flowable


def add(flowable):
    if pending:
        # Flatten so a heading never wraps another KeepTogether (nesting makes reportlab jump a page).
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


def figure(name, caption, width_cm=15):
    counters["fig"] += 1
    path = FIG / name
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(str(path)).getSize()
    w = width_cm * cm
    img = Image(str(path), width=w, height=w * ih / iw)
    add(KeepTogether([img, Paragraph(f"Figure {counters['fig']}: {caption}", CAP)]))
    return counters["fig"]


def figure_pair(left, right, cap_left, cap_right, width_cm=8):
    """Two figures side by side, each with its own caption."""
    from reportlab.lib.utils import ImageReader
    cells = []
    for name, cap in ((left, cap_left), (right, cap_right)):
        counters["fig"] += 1
        iw, ih = ImageReader(str(FIG / name)).getSize()
        w = width_cm * cm
        cells.append([Image(str(FIG / name), width=w, height=w * ih / iw),
                      Paragraph(f"Figure {counters['fig']}: {cap}", CAP)])
    t = Table([cells], colWidths=[(width_cm + 0.5) * cm] * 2)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
    add(t)
    return counters["fig"] - 1, counters["fig"]


def table(rows, caption, col_widths=None, header=True):
    counters["tab"] += 1
    data = [[Paragraph(str(c), CELL) for c in r] for r in rows]
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0, hAlign="CENTER")
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa5b1")),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9eef6"))]
    t.setStyle(TableStyle(style))
    add(KeepTogether([Paragraph(f"Table {counters['tab']}: {caption}", CAP), t, Spacer(1, 8)]))
    return counters["tab"]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, f"{NAME} ({ROLL})  |  Case Study 3: Titanic Logistic Regression")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def title_page():
    tp = ParagraphStyle("tp", parent=BODY, alignment=TA_CENTER, fontSize=12.5, leading=20)
    story.append(Spacer(1, 4.5 * cm))
    story.append(Paragraph(TITLE, ParagraphStyle("t", parent=H1, fontSize=21, leading=27, alignment=TA_CENTER)))
    story.append(Spacer(1, 1.6 * cm))
    for label, value in [("Name", NAME), ("Roll No", ROLL), ("Section", SECTION), ("Year", YEAR),
                         ("Subject", SUBJECT), ("Faculty", FACULTY), ("College", COLLEGE),
                         ("Date of Submission", SUBMISSION_DATE)]:
        story.append(Paragraph(f"<b>{label}:</b> {escape(value)}", tp))
    story.append(PageBreak())


# ---------------------------------------------------------------- content
def build():
    draw_methodology(FIG / "00_methodology_workflow.png")
    title_page()

    # 1 -------------------------------------------------------------
    h1("Problem Statement and Objectives")
    p("The sinking of the Titanic is one of the best known shipwrecks, and survival was not random: some "
      "groups of passengers had far better chances than others. The problem in this case study is to "
      "predict, from basic passenger details, whether a passenger survived (Survived = 1) or not (0). "
      "This is a binary classification problem, and logistic regression is a natural first model because "
      "it gives a survival probability and coefficients that can be interpreted.")
    p("The objectives, following the brief, were to:")
    bullets(["explore the data with summary statistics and visualisations and describe the patterns found;",
             "handle missing values and encode categorical variables without leaking test data;",
             "build and train a logistic regression model with scikit-learn;",
             "evaluate it on unseen test data with accuracy, precision, recall, F1-score, ROC-AUC and the ROC curve;",
             "interpret the coefficients and test which features are statistically significant; and",
             "deploy the trained model as a Streamlit web app."])

    # 2 -------------------------------------------------------------
    h1("Dataset Description")
    p(f"The dataset (titanic.csv) was provided by the course faculty. It has <b>{overview['rows']} rows</b> "
      f"(one per passenger) and <b>{overview['columns']} columns</b>. The target is <b>Survived</b>: "
      f"{overview['survived']} passengers survived and {overview['not_survived']} did not, an overall "
      f"survival rate of <b>{pct(overview['survival_rate'])}</b>. The classes are moderately imbalanced, so a "
      f"model that always predicts 'did not survive' would already be about "
      f"{pct(overview['not_survived'] / overview['rows'])} accurate.")
    feats = [["Feature", "Type", "Meaning", "Used in model"],
             ["Pclass", "Integer (ordinal)", "Ticket class: 1 upper, 2 middle, 3 lower", "Yes"],
             ["Sex", "Categorical", "male / female", "Yes"],
             ["Age", "Numeric", "Age in years", "Yes"],
             ["SibSp", "Integer", "Siblings or spouses on board", "Yes"],
             ["Parch", "Integer", "Parents or children on board", "Yes"],
             ["Fare", "Numeric", "Ticket fare", "Yes"],
             ["Embarked", "Categorical", "Port: C Cherbourg, Q Queenstown, S Southampton", "Yes"],
             ["PassengerId, Name, Ticket", "ID / text", "Identifiers, unique or almost unique", "No"],
             ["Cabin", "Text", "Cabin number, mostly missing", "No"],
             ["Survived", "Binary", "Target: 1 survived, 0 did not", "Target"]]
    table(feats, "Features of the Titanic dataset", [3.6 * cm, 2.7 * cm, 7.2 * cm, 2.3 * cm])
    miss = missing[missing["missing_count"] > 0]
    p("<b>Data quality issues.</b> " + ", ".join(
        f"{c} is missing for {int(r.missing_count)} passengers ({r.missing_pct:.2f}%)" for c, r in miss.iterrows())
      + ". All other columns are complete. Fare is strongly right skewed (median "
      f"{num.loc['Fare', '50%']:.2f}, mean {num.loc['Fare', 'mean']:.2f}, maximum {num.loc['Fare', 'max']:.2f}).")

    # 3 -------------------------------------------------------------
    h1("Methodology")
    figure("00_methodology_workflow.png", "Methodology workflow followed in this case study", 14)
    h2("Preprocessing")
    bullets([
        "<b>Dropped columns:</b> PassengerId (row number), Name and Ticket (almost unique text) and Cabin "
        f"({missing.loc['Cabin', 'missing_pct']:.2f}% missing, so imputing it would mostly be guessing).",
        "<b>Numeric features</b> (Pclass, Age, SibSp, Parch, Fare): median imputation (only Age has gaps; the "
        "median is robust to skew), then StandardScaler so that every coefficient means the effect of a one "
        "standard deviation increase and the coefficients can be compared.",
        "<b>Categorical features</b> (Sex, Embarked): most frequent value imputation (Embarked has 2 gaps), "
        "then one-hot encoding with the first level dropped (baselines: female, Cherbourg). Dropping one level "
        "avoids perfectly collinear dummies, which is needed for the statsmodels significance test.",
        "<b>No leakage:</b> all steps sit in one scikit-learn Pipeline (ColumnTransformer + model), so medians, "
        "modes, means and standard deviations are learned from the training data only."])
    h2("Train/test split and model")
    p(f"The data was split 80:20 with stratification on Survived and random_state=42, giving "
      f"{metrics['n_train']} training and {metrics['n_test']} test passengers with the same survival rate. "
      "The model is LogisticRegression(max_iter=1000) with scikit-learn's default L2 penalty (C=1). Stability "
      "was checked with 5-fold stratified cross-validation on the training set, refitting the whole pipeline in "
      "every fold. For p-values and confidence intervals a statsmodels Logit model was fitted on the same "
      "preprocessed training data.")
    h2("Evaluation metrics and why they were chosen")
    bullets(["<b>Accuracy</b>: share of all passengers classified correctly; easy to read but hides which class the errors come from.",
             "<b>Precision</b>: of the passengers predicted to survive, how many really did.",
             "<b>Recall</b>: of the passengers who really survived, how many the model found.",
             "<b>F1-score</b>: harmonic mean of precision and recall, a single score for the survivor class.",
             "<b>ROC-AUC</b>: how well the predicted probabilities rank survivors above non-survivors, independent of the 0.5 threshold.",
             "<b>Confusion matrix</b>: the exact counts of correct and wrong predictions of each kind."])

    # 4 -------------------------------------------------------------
    h1("Statistical Findings")
    rows = [["Statistic", "Age", "Fare", "SibSp", "Parch", "Pclass"]]
    for s, lab in [("count", "Count"), ("mean", "Mean"), ("std", "Std. dev."), ("min", "Min"),
                   ("50%", "Median"), ("max", "Max")]:
        rows.append([lab] + [f"{num.loc[c, s]:.2f}" if s != "count" else f"{int(num.loc[c, s])}"
                             for c in ["Age", "Fare", "SibSp", "Parch", "Pclass"]])
    table(rows, "Summary statistics of the numeric features", [3 * cm] + [2.4 * cm] * 5)
    p(f"Age has only {int(num.loc['Age', 'count'])} known values and ranges from {num.loc['Age', 'min']:.2f} to "
      f"{num.loc['Age', 'max']:.0f} years (median {num.loc['Age', '50%']:.0f}). Most passengers travelled without "
      "siblings, spouses, parents or children (median 0 for SibSp and Parch), and the Pclass median of 3 shows that "
      "at least half of them were in third class.")
    rr = [["Group", "Passengers", "Survived", "Survival rate"]]
    rr += [[g, int(r.passengers), int(r.survived), f"{r.survival_rate:.2f}%"] for g, r in rates.iterrows()]
    trates = table(rr, "Survival rate by sex, passenger class and port of embarkation",
          [4.2 * cm, 3 * cm, 3 * cm, 3.2 * cm])
    p(f"The differences between groups are large. <b>{rate['Sex = female']:.2f}% of females survived against "
      f"only {rate['Sex = male']:.2f}% of males.</b> Survival also falls steadily with class: "
      f"{rate['Pclass = 1']:.2f}% in first class, {rate['Pclass = 2']:.2f}% in second and "
      f"{rate['Pclass = 3']:.2f}% in third. Passengers who boarded at Cherbourg survived at "
      f"{rate['Embarked = C']:.2f}% compared with {rate['Embarked = S']:.2f}% at Southampton.")
    figure("03_survival_by_sex_pclass.png", "Survival counts by sex and by passenger class", 14)
    p(f"Figure {counters['fig']} shows the same pattern in counts. Sex and class also combine: "
      f"<b>{sex_class.loc['female', '1'] * 100:.1f}% of first class females survived but only "
      f"{sex_class.loc['male', '3'] * 100:.1f}% of third class males did</b>, and third class females "
      f"({sex_class.loc['female', '3'] * 100:.1f}%) still did better than first class males "
      f"({sex_class.loc['male', '1'] * 100:.1f}%).")
    fbox = figure("02_age_fare_boxplots.png", "Age and Fare by survival outcome", 12)
    p(f"The median age is {medians.loc['Survived', 'median_Age']:.1f} for survivors and "
      f"{medians.loc['Did not survive', 'median_Age']:.1f} for non-survivors, so age alone does not separate "
      f"the groups. Fare shows a clear shift: survivors paid a median of {medians.loc['Survived', 'median_Fare']:.1f} "
      f"against {medians.loc['Did not survive', 'median_Fare']:.1f}, consistent with wealthier passengers "
      "having better access to lifeboats.")
    figure("05_correlation_heatmap.png", "Correlation heatmap of numeric features, Sex (1 = male) and survival", 8.5)
    p(f"Sex_male has the strongest correlation with survival ({corr_s['Sex_male']:.3f}), followed by Pclass "
      f"({corr_s['Pclass']:.3f}) and Fare ({corr_s['Fare']:.3f}). Age ({corr_s['Age']:.3f}), SibSp "
      f"({corr_s['SibSp']:.3f}) and Parch ({corr_s['Parch']:.3f}) are only weakly correlated with it. Pclass and "
      f"Fare are strongly correlated with each other ({corr.loc['Pclass', 'Fare']:.3f}), so they carry overlapping "
      "information, which becomes important when testing significance in Section 6.")

    # 5 -------------------------------------------------------------
    h1("Model Evaluation")
    p(f"Five-fold cross-validation on the training set gave fold accuracies of "
      f"{', '.join(f'{a:.4f}' for a in cv['fold_accuracy'])}, a mean of <b>{cv['mean']:.4f}</b> with standard "
      f"deviation {cv['std']:.4f}. The training accuracy was {metrics['train_accuracy']:.4f}, close to the CV mean, "
      "so the model is stable and not overfitting. Table "
      f"{counters['tab'] + 1} gives the results on the {metrics['n_test']} unseen test passengers.")
    mrows = [["Metric", "Value", "Meaning here"],
             ["Accuracy", f4(metrics["accuracy"]), f"Correct for {TN + TP} of {metrics['n_test']} passengers (baseline {f4(metrics['baseline_accuracy_majority_class'])})"],
             ["Precision", f4(metrics["precision"]), f"{TP} of {TP + FP} predicted survivors really survived"],
             ["Recall", f4(metrics["recall"]), f"{TP} of {TP + FN} real survivors were found"],
             ["F1-score", f4(metrics["f1"]), "Balance of precision and recall for survivors"],
             ["ROC-AUC", f4(metrics["roc_auc"]), "Ranking quality of the survival probabilities"]]
    table(mrows, "Test set performance of the logistic regression model", [2.8 * cm, 2.2 * cm, 10.5 * cm])
    cr = creport
    p(f"The model is clearly better than the {f4(metrics['baseline_accuracy_majority_class'])} majority baseline. "
      f"The classification report shows it is stronger on non-survivors (recall "
      f"{cr.loc['Did not survive', 'recall']:.4f}, F1 {cr.loc['Did not survive', 'f1-score']:.4f}) than on "
      f"survivors (recall {cr.loc['Survived', 'recall']:.4f}, F1 {cr.loc['Survived', 'f1-score']:.4f}), which "
      "is expected because non-survivors are the majority class and the default 0.5 threshold favours them.")
    fcm, froc = figure_pair("06_confusion_matrix.png", "07_roc_curve.png", "Confusion matrix on the test set",
                            "ROC curve with the random-chance diagonal")
    p(f"In Figure {fcm}, of the {metrics['n_test']} test passengers, {TN} non-survivors and {TP} survivors were classified "
      f"correctly. <b>The {FP} false positives</b> are passengers the model was too optimistic about (predicted to "
      f"survive but died). <b>The {FN} false negatives</b> are real survivors the model wrote off. Missed survivors "
      "are the more common error, which is why recall is the weakest metric. If finding survivors mattered more, "
      "the threshold could be lowered below 0.5 to raise recall at the cost of precision.")
    p(f"The ROC curve in Figure {froc} stays well above the diagonal. An <b>AUC of {metrics['roc_auc']:.4f}</b> means that for a "
      f"random survivor and a random non-survivor, the model gives the survivor the higher probability about "
      f"{metrics['roc_auc'] * 100:.0f}% of the time.")

    # 6 -------------------------------------------------------------
    h1("Interpretation")
    h2("Coefficients and odds ratios")
    p("Numeric features were standardised, so their coefficients are the change in the log-odds of survival for a "
      "one standard deviation (SD) increase; for dummy columns they compare with the baseline (female, Cherbourg). "
      "An odds ratio below 1 lowers the odds of survival and above 1 raises them.")
    srow = {f: sig.loc[f] for f in sig.index}
    crow = [["Feature", "Coefficient", "Odds ratio", "p-value", "95% CI of odds ratio", "Significant (0.05)"]]
    for _, r in coef.iterrows():
        s = srow[r.feature]
        crow.append([r.feature, f"{r.coefficient:.4f}", f"{r.odds_ratio:.4f}",
                     "&lt; 0.0001" if s.p_value < 0.0001 else f"{s.p_value:.4f}",
                     f"{s.or_ci_low:.3f} to {s.or_ci_high:.3f}", s["significant_at_0.05"]])
    table(crow, "Scikit-learn coefficients and odds ratios (sorted by size) with statsmodels p-values and "
                "95% confidence intervals", [2.6 * cm, 2.3 * cm, 2.2 * cm, 2.2 * cm, 3.6 * cm, 2.8 * cm])
    c = coef.set_index("feature")
    sd = {r.feature: r.one_unit_means.split("(")[-1].rstrip(")") for _, r in coef.iterrows() if "SD" in r.one_unit_means}
    figure("08_coefficients.png", "Logistic regression coefficients with odds ratios (OR)", 11)
    bullets([
        f"<b>Sex_male</b> (coefficient {c.loc['Sex_male', 'coefficient']:.4f}, OR {c.loc['Sex_male', 'odds_ratio']:.4f}): "
        f"being male multiplies the odds of survival by about {c.loc['Sex_male', 'odds_ratio']:.2f}, roughly "
        f"{(1 - c.loc['Sex_male', 'odds_ratio']) * 100:.0f}% lower odds than a female with the same other details. "
        "This is by far the largest effect.",
        f"<b>Pclass</b> (OR {c.loc['Pclass', 'odds_ratio']:.4f}, 1 SD = {sd['Pclass']} classes): moving towards third class "
        f"cuts the odds by about {(1 - c.loc['Pclass', 'odds_ratio']) * 100:.0f}% per SD.",
        f"<b>Age</b> (OR {c.loc['Age', 'odds_ratio']:.4f}, 1 SD = {sd['Age']} years): older passengers had about "
        f"{(1 - c.loc['Age', 'odds_ratio']) * 100:.0f}% lower odds per SD. Age matters once sex and class are "
        f"controlled, even though the medians in Figure {fbox} were equal.",
        f"<b>SibSp</b> (OR {c.loc['SibSp', 'odds_ratio']:.4f}, 1 SD = {sd['SibSp']}): more siblings or spouses lowered the odds by about "
        f"{(1 - c.loc['SibSp', 'odds_ratio']) * 100:.0f}% per SD.",
        f"<b>Embarked, Fare and Parch</b> have smaller effects (Embarked_S OR {c.loc['Embarked_S', 'odds_ratio']:.2f}, "
        f"Embarked_Q OR {c.loc['Embarked_Q', 'odds_ratio']:.2f}, Fare OR {c.loc['Fare', 'odds_ratio']:.2f}, "
        f"Parch OR {c.loc['Parch', 'odds_ratio']:.2f})."])
    h2("Statistical significance")
    sig_yes = [f for f in sig.index if f != "const" and sig.loc[f, "significant_at_0.05"] == "Yes"]
    sig_no = [f for f in sig.index if f != "const" and sig.loc[f, "significant_at_0.05"] == "No"]
    p(f"The statsmodels Logit model converged with a pseudo R-squared of {sm_fit['pseudo_r2']:.4f} and a "
      f"likelihood ratio test p-value of {sm_fit['llr_p_value']:.3g}, so the features together explain survival "
      f"far better than an intercept-only model. At the 0.05 level, <b>{', '.join(sig_yes)}</b> are significant. "
      f"SibSp is only just significant (p = {sig.loc['SibSp', 'p_value']:.4f}, upper CI of the odds ratio "
      f"{sig.loc['SibSp', 'or_ci_high']:.3f}). {', '.join(sig_no)} are <b>not</b> significant: their odds ratio "
      "confidence intervals include 1. Fare was correlated with survival in the EDA "
      f"({corr_s['Fare']:.3f}), but once Pclass is in the model it adds little because the two overlap "
      f"(correlation {corr.loc['Pclass', 'Fare']:.3f}). Likewise, the port differences seen in Table {trates} mostly "
      "disappear once sex and class are accounted for. The unpenalised statsmodels coefficients are slightly larger "
      f"than scikit-learn's (Sex_male {sig.loc['Sex_male', 'coefficient']:.4f} vs "
      f"{c.loc['Sex_male', 'coefficient']:.4f}) because of the L2 penalty, but all signs and the ranking agree.")
    h2("Deployment with Streamlit")
    shot = FIG / "streamlit_app.png"
    p("The complete fitted pipeline (imputers, encoder, scaler and model) was saved with joblib to "
      "<font name='Courier'>3/model/titanic_logreg.joblib</font>. The Streamlit app "
      "<font name='Courier'>3/app.py</font> loads it once with <font name='Courier'>st.cache_resource</font> "
      "(path relative to the app file), offers inputs for passenger class, sex, age, fare, siblings/spouses, "
      "parents/children and port of embarkation (shown by full name), and on clicking <b>Predict</b> shows the "
      "survival probability, a progress bar and the predicted class. Because the whole pipeline is saved, raw "
      "inputs are processed exactly as in training. It runs locally with "
      "<font name='Courier'>streamlit run 3/app.py</font> and can be deployed on Streamlit Community Cloud by "
      "selecting the GitHub repository, branch main and main file path 3/app.py.")
    if shot.exists():
        figure("streamlit_app.png", "The Streamlit app predicting survival for one passenger", 13)

    # 7 -------------------------------------------------------------
    h1("Conclusion and Limitations")
    p(f"Survival on the Titanic was strongly linked to sex and class: {rate['Sex = female']:.2f}% of females and "
      f"{rate['Pclass = 1']:.2f}% of first class passengers survived against {rate['Sex = male']:.2f}% of males and "
      f"{rate['Pclass = 3']:.2f}% of third class passengers. A leak-free logistic regression pipeline reached "
      f"<b>accuracy {f4(metrics['accuracy'])}, precision {f4(metrics['precision'])}, recall "
      f"{f4(metrics['recall'])}, F1 {f4(metrics['f1'])} and ROC-AUC {f4(metrics['roc_auc'])}</b> on unseen data, with "
      f"a stable cross-validation accuracy of {cv['mean']:.4f}. Sex, passenger class, age and number of "
      "siblings/spouses were the significant predictors, and the model was deployed as a working Streamlit app.")
    p("<b>Limitations:</b>")
    bullets([f"The dataset is small ({overview['rows']} passengers, {metrics['n_test']} in the test set), so each "
             "test error changes the metrics noticeably.",
             f"Age is {missing.loc['Age', 'missing_pct']:.2f}% missing and was filled with one median value, which "
             "hides real variation; Cabin information was discarded entirely.",
             f"Recall for survivors is only {f4(metrics['recall'])} at the default 0.5 threshold; {FN} survivors in "
             "the test set were missed.",
             "Logistic regression assumes each feature has a linear effect on the log-odds, so interactions such as "
             "sex combined with class are only partly captured."])

    # 8 -------------------------------------------------------------
    h1("References")
    libs = ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "statsmodels", "joblib", "streamlit", "reportlab"]
    bullets(["Titanic passenger dataset (titanic.csv, 891 rows), provided by the course faculty for this case study.",
             "Libraries: " + ", ".join(f"{l} {version(l)}" for l in libs) + ".",
             "Streamlit Community Cloud deployment documentation: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app",
             f"GitHub repository: {escape(REPO_URL)}"])

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
