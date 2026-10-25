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
OUT = HERE / "report" / "CS6_Bank_Marketing_Classification_160124733191.pdf"

TITLE = "Case Study 6: Comparative Analysis of Classification Algorithms for Bank Marketing Prediction"
SHORT_TITLE = "Case Study 6: Bank Marketing Classification"
NAME, ROLL, SECTION = "Nikhil Kotte", "160124733191", "CSE-3"
YEAR, SUBJECT = "III Year, V Semester (2026-27)", "Fundamentals of Data Science"
FACULTY = "<FACULTY NAME>"
COLLEGE = "Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad"
SUBMISSION_DATE = "26 October 2026"
REPO_URL = "<GITHUB REPO URL>"
ATTRIBUTION = ("Code structure drafted with AI assistance (Claude); executed, verified and interpreted by "
               "Nikhil Kotte. Dataset sources: Bank Marketing (with social/economic context), UCI Machine "
               "Learning Repository, bank-additional-full.csv; Moro, Cortez and Rita (2014).")
CITATION = ("S. Moro, P. Cortez and P. Rita. A Data-Driven Approach to Predict the Success of Bank Telemarketing. "
            "Decision Support Systems (2014), doi:10.1016/j.dss.2014.03.001.")

# ---------------------------------------------------------------- results
overview = json.loads((RES / "dataset_overview.json").read_text())
best = json.loads((RES / "best_model.json").read_text())
num = pd.read_csv(RES / "summary_stats_numeric.csv", index_col=0)
unknown = pd.read_csv(RES / "unknown_counts.csv", index_col=0)
rates = pd.read_csv(RES / "subscription_rates_by_attribute.csv", index_col=[0, 1])
num_y = pd.read_csv(RES / "numeric_by_outcome.csv", index_col=[0, 1])
comp = pd.read_csv(RES / "model_comparison.csv", index_col=0)
gains = pd.read_csv(RES / "cumulative_gains.csv", index_col=0)
imp = pd.read_csv(RES / "rf_feature_importance_top15.csv", index_col=0)["importance"]

BEST = best["best_model"]
POS = best["test_positives"]
r = lambda attr, cat: rates.loc[(attr, cat), "rate_pct"]  # noqa: E731
f4 = lambda v: f"{v:.4f}"  # noqa: E731
OVERALL = overview["yes_pct"]
top_recall = comp["Recall"].idxmax()
top_acc = comp["Accuracy"].idxmax()

# ---------------------------------------------------------------- methodology diagram
def draw_methodology(path):
    steps = [
        ("1. Data", "bank-additional-full.csv\n41,188 rows, 21 columns"),
        ("2. EDA", "target balance, subscription\nrates, numeric vs outcome"),
        ("3. Preprocessing", "drop duplicates and duration,\none-hot + scaling (Pipeline)"),
        ("4. Four Models", "LR, Decision Tree, KNN,\nRandom Forest, same 80:20 split"),
        ("5. Evaluation", "precision, recall, F1, ROC-AUC,\nconfusion matrices, gains"),
        ("6. Interpretation", "best model, business\nrecommendations, limitations"),
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
        ax.set_title("Methodology Workflow: Bank Marketing Classification", fontsize=15)
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
    widths = width_cm if isinstance(width_cm, tuple) else (width_cm, width_cm)
    """Two figures side by side, each with its own caption."""
    from reportlab.lib.utils import ImageReader
    cells = []
    for (name, cap), width_cm in zip(((left, cap_left), (right, cap_right)), widths):
        counters["fig"] += 1
        iw, ih = ImageReader(str(FIG / name)).getSize()
        w = width_cm * cm
        cells.append([Image(str(FIG / name), width=w, height=w * ih / iw),
                      Paragraph(f"Figure {counters['fig']}: {cap}", CAP)])
    t = Table([cells], colWidths=[(wc + 0.4) * cm for wc in widths])
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
    canvas.drawString(2 * cm, 1.2 * cm, f"{NAME} ({ROLL})  |  {SHORT_TITLE}")
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
    p("A Portuguese bank sells term deposits through telephone campaigns. Most calls do not lead to a sale, so "
      "the bank wants to know in advance which customers are likely to subscribe. The problem is to build and "
      "compare classification models that predict, before a call is made, whether a customer will subscribe "
      "(y = yes), and to recommend the model that is most useful for the campaign.")
    p("The objectives were to explore and preprocess the data, implement Logistic Regression, a Decision Tree, "
      "K-Nearest Neighbours and a Random Forest on one common train/test split, compare them with accuracy, "
      "precision, recall, F1-score, ROC-AUC and confusion matrices, choose the best model using these metrics and "
      "the business cost of errors (not accuracy alone), and turn the results into recommendations for the bank.")

    # 2 -------------------------------------------------------------
    h1("Dataset Description")
    p(f"The data is the UCI <i>Bank Marketing (with social/economic context)</i> dataset, file "
      f"bank-additional-full.csv: <b>{overview['rows_raw']:,} rows and {overview['columns']} columns</b>, ordered "
      "by date from May 2008 to November 2010. It was chosen over the older bank-full.csv because it is the newer "
      "UCI version and adds five social and economic context attributes, which the dataset authors found improve "
      "prediction even without call duration.")
    feats = [["Group", "Attributes", "Type"],
             ["Client", "age; job, marital, education, default, housing, loan", "1 numeric, 6 categorical"],
             ["Last contact", "contact, month, day_of_week; duration", "3 categorical, 1 numeric"],
             ["Campaign history", "campaign, pdays, previous; poutcome", "3 numeric, 1 categorical"],
             ["Economic context", "emp.var.rate, cons.price.idx, cons.conf.idx, euribor3m, nr.employed", "5 numeric"],
             ["Target", "y: subscribed to a term deposit (yes / no)", "Binary"]]
    table(feats, f"Attribute groups ({overview['n_numerical']} numerical, {overview['n_categorical']} categorical "
                 "and the target)", [3.2 * cm, 9.2 * cm, 4 * cm])
    p(f"<b>Class balance:</b> only <b>{overview['yes']:,} customers ({overview['yes_pct']:.2f}%) subscribed</b> and "
      f"{overview['no']:,} ({100 - overview['yes_pct']:.2f}%) did not, so the data is strongly imbalanced.")
    unk = unknown[unknown["unknown_count"] > 0]
    p("<b>Data quality issues:</b> there are no NaN values, but missing categorical information is coded as "
      "'unknown': " + ", ".join(f"{c} {int(v.unknown_count):,} ({v.unknown_pct:.2f}%)" for c, v in unk.iterrows())
      + f". There were <b>{overview['duplicates_dropped']} duplicate rows</b> (dropped, leaving "
      f"{overview['rows_clean']:,}). In pdays the value 999 means 'not previously contacted' and applies to "
      f"{overview['pdays_999_pct']:.2f}% of customers.")

    # 3 -------------------------------------------------------------
    h1("Methodology")
    figure("00_methodology_workflow.png", "Methodology workflow followed in this case study", 11.5)
    bullets([
        "<b>duration excluded:</b> the length of the last call is only known after the call, when the outcome is "
        "also known. The UCI notes say it should be discarded for a realistic model, so it is used in the EDA only.",
        "<b>'unknown' kept as its own category:</b> dropping those rows would lose over a fifth of the data, and "
        "'unknown' behaves differently (for example, customers with unknown default status subscribe less often).",
        "<b>pdays = 999</b> is kept as a numeric value; after scaling it acts as a 'not contacted before' flag.",
        "<b>Encoding and scaling:</b> OneHotEncoder(handle_unknown='ignore') for the 10 categorical attributes and "
        "StandardScaler for the 9 numeric ones, combined in a ColumnTransformer inside each model's Pipeline, so they "
        "are fit on training data only (no leakage). y is mapped to 1 (yes) and 0 (no).",
        f"<b>Split:</b> one stratified 80:20 split (random_state=42), reused by all four models; the test set has "
        f"{POS} actual subscribers."])
    hp = [["Model", "Hyperparameters", "Reason"],
          ["Logistic Regression", "max_iter=1000, class_weight='balanced'", "Linear, explainable baseline; weights the rare 'yes' class"],
          ["Decision Tree", "max_depth=6, class_weight='balanced'", "Readable rules; depth limit reduces overfitting"],
          ["KNN", "n_neighbors=15", "Votes of 15 similar customers; has no class_weight option"],
          ["Random Forest", "n_estimators=300, min_samples_leaf=5, class_weight='balanced'", "Ensemble of trees, captures interactions"]]
    table(hp, "Models and hyperparameters", [3.2 * cm, 6.4 * cm, 6.8 * cm])
    p("<b>Metrics:</b> the positive class is 'subscribed'. <b>Precision</b> is the share of predicted subscribers "
      "who really subscribe (how many calls are not wasted); <b>recall</b> is the share of real subscribers the model "
      "finds; <b>F1</b> balances the two; <b>ROC-AUC</b> measures how well the scores rank subscribers above "
      "non-subscribers, independent of the 0.5 threshold. Accuracy is reported but not used alone, because always "
      f"predicting 'no' would already give {best['baseline_accuracy_all_no']:.4f}.")

    # 4 -------------------------------------------------------------
    h1("Statistical Findings")
    cols = ["age", "campaign", "pdays", "previous", "euribor3m", "nr.employed"]
    rows = [["Statistic"] + cols]
    for s_, lab in [("mean", "Mean"), ("std", "Std. dev."), ("min", "Min"), ("50%", "Median"), ("max", "Max")]:
        rows.append([lab] + [f"{num.loc[c, s_]:,.2f}" for c in cols])
    table(rows, "Summary statistics of selected numeric attributes (before removing duplicates)",
          [2.4 * cm] + [2.35 * cm] * 6)
    figure_pair("01_target_distribution.png", "06_numeric_vs_outcome.png",
                "Distribution of the target y", "Numeric attributes by subscription", width_cm=(6.6, 9.6))
    nm = lambda c, s_, o: num_y.loc[(c, s_), o]  # noqa: E731
    p(f"Only {overview['yes_pct']:.2f}% of customers subscribed (about one call in nine). Among the numeric "
      f"attributes, the economic indicators separate the classes best: subscribers have a <b>median Euribor 3 month "
      f"rate of {nm('euribor3m', 'median', 'Yes'):.2f} against {nm('euribor3m', 'median', 'No'):.2f}</b> and a lower "
      f"number of employees ({nm('nr.employed', 'median', 'Yes'):,.1f} vs {nm('nr.employed', 'median', 'No'):,.1f}). "
      f"Age barely differs (median {nm('age', 'median', 'Yes'):.0f} vs {nm('age', 'median', 'No'):.0f}), and "
      f"non-subscribers were called more often on average ({nm('campaign', 'mean', 'No'):.2f} vs "
      f"{nm('campaign', 'mean', 'Yes'):.2f} calls), so repeated calls do not seem to help. Call duration (EDA only) "
      f"has median {nm('duration', 'median', 'Yes'):.0f} seconds for subscribers against "
      f"{nm('duration', 'median', 'No'):.0f}, which shows why it would leak the outcome.")
    figure("03_rate_by_month.png", "Subscription rate by month of last contact (dashed line: overall rate)", 11)
    may = rates.loc[("month", "may")]
    hi = rates.loc["month"].sort_values("rate_pct", ascending=False).head(4)
    p(f"May had the most calls ({int(may.customers):,}) but the <b>lowest rate ({may.rate_pct:.2f}%)</b>, while "
      "the quiet months had very high rates: " + ", ".join(f"{m.capitalize()} {v:.2f}%" for m, v in hi["rate_pct"].items())
      + ". Mass calling in busy months reaches many uninterested customers.")
    figure("04_rate_by_contact_poutcome.png", "Subscription rate by contact type and previous campaign outcome", 12.5)
    p(f"Customers whose <b>previous campaign outcome was success subscribed at {r('poutcome', 'success'):.2f}%</b>, "
      f"against {r('poutcome', 'failure'):.2f}% after a failure and {r('poutcome', 'nonexistent'):.2f}% for customers "
      f"never contacted before. Cellular contacts subscribed at {r('contact', 'cellular'):.2f}% against "
      f"{r('contact', 'telephone'):.2f}% for landline. By job (not plotted here), students "
      f"({r('job', 'student'):.2f}%) and retired customers ({r('job', 'retired'):.2f}%) had the highest rates and "
      f"blue-collar workers the lowest ({r('job', 'blue-collar'):.2f}%).")
    p("<b>Evidence-based observations:</b>")
    bullets([f"The target is strongly imbalanced ({overview['yes_pct']:.2f}% yes), so accuracy is a weak measure.",
             f"Previous success is the strongest single signal: {r('poutcome', 'success'):.2f}% subscription, about "
             f"{r('poutcome', 'success') / OVERALL:.1f} times the overall {OVERALL:.2f}%.",
             f"Economic conditions matter: subscriptions were concentrated at low Euribor rates (median "
             f"{nm('euribor3m', 'median', 'Yes'):.2f} vs {nm('euribor3m', 'median', 'No'):.2f}).",
             f"Timing and channel matter: May {may.rate_pct:.2f}% vs over {hi['rate_pct'].min():.0f}% in the four best "
             f"months; cellular {r('contact', 'cellular'):.2f}% vs landline {r('contact', 'telephone'):.2f}%."])

    # 5 -------------------------------------------------------------
    h1("Model Evaluation")
    mt = [["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "TP / FN", "FP", "Calls / sub."]]
    for m, v in comp.iterrows():
        mt.append([f"<b>{m}</b>" if m == BEST else m, f4(v.Accuracy), f4(v.Precision), f4(v.Recall), f4(v.F1),
                   f4(v.ROC_AUC), f"{int(v.TP)} / {int(v.FN)}", f"{int(v.FP):,}", f"{v.Calls_per_subscriber:.2f}"])
    table(mt, f"Final performance comparison on the test set ({POS} actual subscribers; positive class = yes)",
          [3.3 * cm, 1.8 * cm, 1.8 * cm, 1.5 * cm, 1.4 * cm, 2.0 * cm, 2.0 * cm, 1.3 * cm, 1.5 * cm])
    figure("08_metrics_grouped_bar.png", "Accuracy, precision, recall and F1 of the four classifiers", 12)
    L, K, R = comp.loc["Logistic Regression"], comp.loc["KNN"], comp.loc[BEST]
    p(f"Accuracy hardly separates the models ({comp['Accuracy'].min():.2f} to {comp['Accuracy'].max():.2f}) and three "
      f"of them are below the {best['baseline_accuracy_all_no']:.4f} of always predicting 'no'. Recall and F1 tell a "
      f"different story: <b>{top_acc} has the highest accuracy ({K.Accuracy:.4f}) and precision ({K.Precision:.4f}) "
      f"but finds only {int(K.TP)} of {POS} subscribers (recall {K.Recall:.4f})</b>, because it has no class weights "
      "and most neighbours of any customer are non-subscribers. The three balanced models all find about "
      f"{comp.drop('KNN')['Recall'].min() * 100:.0f}% to {comp.drop('KNN')['Recall'].max() * 100:.0f}% of subscribers.")
    figure("09_confusion_matrices.png", "Confusion matrices of the four classifiers (TN, FP, FN, TP)", 10)
    p("In practice a <b>false negative</b> is a customer who would have subscribed but is never called, a lost "
      "deposit; a <b>false positive</b> is a call to a customer who says no, a few minutes of an agent's time. "
      f"Logistic Regression misses the fewest subscribers ({int(L.FN)}) but wastes the most calls ({int(L.FP):,}). "
      f"{BEST} misses only {int(R.FN - L.FN)} more ({int(R.FN)}) while making {int(L.FP - R.FP)} fewer wasted calls "
      f"({int(R.FP):,}). KNN wastes only {int(K.FP)} calls but misses {int(K.FN)} subscribers, the most expensive "
      "kind of error. For every model false positives outnumber true positives, the price of finding rare subscribers.")
    figure_pair("10_roc_curves.png", "12_cumulative_gains.png", "ROC curves with AUC", f"Cumulative gains of {BEST}",
                width_cm=7.9)
    g = gains["pct_subscribers_reached"]
    p(f"All ROC curves are well above the diagonal; {BEST} has the highest AUC ({R.ROC_AUC:.4f}), just ahead of "
      f"Logistic Regression ({L.ROC_AUC:.4f}). The gains chart shows the value of ranking: calling the top 10% of "
      f"customers by {BEST} score reaches <b>{g[10]:.2f}%</b> of all subscribers (lift "
      f"{gains.loc[10, 'lift']:.2f}), the top 20% reaches {g[20]:.2f}% and the top 30% reaches {g[30]:.2f}%.")

    # 6 -------------------------------------------------------------
    h1("Interpretation and Business Recommendations")
    h2("Best model")
    p(f"<b>{BEST} is the best model.</b> It has the best F1 ({R.F1:.4f}) and ROC-AUC ({R.ROC_AUC:.4f}), recall of "
      f"{R.Recall:.4f} ({int(R.TP)} of {POS} subscribers) and the best precision of the three balanced models "
      f"({R.Precision:.4f}), needing {R.Calls_per_subscriber:.2f} calls per subscriber found against "
      f"{L.Calls_per_subscriber:.2f} for Logistic Regression. Since missing a subscriber costs more than one extra "
      f"call, KNN is rejected despite its accuracy. {BEST} suits the bank because it handles the imbalance with class "
      "weights, uses only information available before the call, captures interactions between economic conditions, "
      "timing and customer history, and produces scores that rank customers well. Logistic Regression is a close "
      "second and would be preferred if a simpler, fully explainable model were required.")
    figure("13_rf_feature_importance.png", "Random Forest: top 15 feature importances", 9)
    top3 = ", ".join(f"{f} ({v:.4f})" for f, v in imp.head(3).items())
    p(f"The most important features are the economic indicators {top3}, followed by "
      f"{', '.join(imp.index[3:6])}. Campaign history (campaign, pdays, poutcome_success) and the contact month and "
      "type also appear in the top 15, in agreement with the EDA. Impurity-based importance favours continuous "
      "features, so binary columns such as poutcome_success may be under-rated.")
    h2("Business recommendations")
    bullets([f"<b>Call customers in score order.</b> Rank customers by the {BEST} score and call from the top. On the "
             f"test set the top 20% of the list held {g[20]:.2f}% of all subscribers, so the bank could reach about "
             "two thirds of potential subscribers with one fifth of the calls, and set the cut-off by agent capacity.",
             f"<b>Prioritise previous successes and mobile numbers.</b> Previous-success customers subscribed at "
             f"{r('poutcome', 'success'):.2f}% and cellular contacts at {r('contact', 'cellular'):.2f}%.",
             f"<b>Avoid repeat calls and over-concentration in one month.</b> May produced {int(may.customers):,} "
             f"calls at {may.rate_pct:.2f}%; spreading calls and capping repeat attempts would save effort.",
             "<b>Time campaigns with economic conditions.</b> Euribor and employment indicators were the strongest "
             "predictors, so campaign size can be raised when these are favourable."])

    # 7 -------------------------------------------------------------
    h1("Conclusion and Limitations")
    p(f"On {overview['rows_clean']:,} customers with only {overview['yes_pct']:.2f}% subscribers, four classifiers "
      f"were compared on one leak-free pipeline without call duration. <b>{BEST}</b> gave the best balance (F1 "
      f"{R.F1:.4f}, ROC-AUC {R.ROC_AUC:.4f}, recall {R.Recall:.4f}, precision {R.Precision:.4f}) and, used as a "
      f"ranking tool, reaches {g[30]:.2f}% of subscribers with 30% of the calls. KNN showed how misleading accuracy "
      "is on imbalanced data.")
    bullets(["<b>2008 to 2010 data:</b> the data comes from one bank during the financial crisis and the top features "
             "are economic indicators, so the model must be retrained if conditions change.",
             f"<b>duration excluded:</b> correct for pre-call use, but it removes the strongest signal, which limits F1 "
             f"to {R.F1:.4f}.",
             "<b>Default 0.5 threshold:</b> precision and recall depend on the cut-off (KNN's low recall is largely a "
             "threshold effect); the bank should choose it from call capacity.",
             f"<b>Limited tuning and one split; 'unknown' values:</b> hyperparameters were not searched, and "
             f"{unknown.loc['default', 'unknown_pct']:.2f}% of default values are unknown, which adds noise."])

    # 8 -------------------------------------------------------------
    h1("References")
    libs = ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "reportlab"]
    bullets([CITATION,
             "Bank Marketing dataset, UCI Machine Learning Repository: http://archive.ics.uci.edu/ml/datasets/Bank+Marketing "
             "(social and economic attributes published by Banco de Portugal).",
             "Libraries: " + ", ".join(f"{lib} {version(lib)}" for lib in libs) + ".",
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
