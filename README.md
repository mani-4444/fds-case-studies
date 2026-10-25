# FDS Case Studies 3 and 6

Fundamentals of Data Science, III Year V Semester (2026-27), CBIT Hyderabad
Nikhil Kotte (160124733191), Section CSE-3

| Folder | Case study | Notebook | Report |
|---|---|---|---|
| `3/` | Titanic survival with Logistic Regression + Streamlit app | `3/case_study_3_titanic_logistic_regression.ipynb` | `3/report/CS3_Titanic_Logistic_Regression_160124733191.pdf` |
| `6/` | Bank Marketing: comparing four classifiers | `6/case_study_6_bank_marketing_classification.ipynb` | `6/report/CS6_Bank_Marketing_Classification_160124733191.pdf` |

## Case Study 3: Titanic survival (Logistic Regression)

**Objective:** predict whether a passenger survived from Pclass, Sex, Age, SibSp, Parch, Fare and Embarked, interpret the model and deploy it as a web app.

* Data: `3/titanic.csv` (891 passengers, provided by the faculty).
* Preprocessing in one scikit-learn Pipeline: median imputation and scaling for numeric features, mode imputation and one-hot encoding for Sex and Embarked; stratified 80:20 split.
* Model: `LogisticRegression(max_iter=1000)`, 5-fold stratified CV on the training set, statsmodels Logit for p-values.
* Key findings: test accuracy 0.8045, precision 0.7931, recall 0.6667, F1 0.7244, ROC-AUC 0.8435 (CV accuracy 0.7949). Sex, Pclass, Age and SibSp are significant at 0.05; being male lowers the odds of survival by about 92%.
* Saved model: `3/model/titanic_logreg.joblib` (whole fitted pipeline). App: `3/app.py`.

## Case Study 6: Bank Marketing (four classifiers)

**Objective:** predict whether a customer will subscribe to a term deposit before the call is made, compare Logistic Regression, Decision Tree, KNN and Random Forest, and recommend the most useful model for the bank.

* Data: `6/bank+marketing/bank-additional/bank-additional/bank-additional-full.csv` (41,188 rows, `sep=';'`), UCI Bank Marketing with social/economic context (Moro, Cortez and Rita, 2014).
* `duration` is excluded from all models (it is only known after the call). "unknown" kept as a category, 12 duplicates dropped, one-hot + scaling in a ColumnTransformer, one stratified 80:20 split for all models.
* Key findings: only 11.27% of customers subscribed. Random Forest is the best model (F1 0.5006, ROC-AUC 0.8080, recall 0.6358, precision 0.4129). KNN has the highest accuracy (0.8980) but finds only 26% of subscribers. Calling the top 20% of customers by Random Forest score reaches 66.16% of all subscribers.
* Full comparison: `6/results/model_comparison.csv`.

## Setup (Windows)

```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` pins the exact versions used to train and save the model, so Streamlit Cloud loads it with the same scikit-learn version.

## Run the notebooks

From the repository root, with the virtual environment active:

```
jupyter nbconvert --to notebook --execute --inplace 3/case_study_3_titanic_logistic_regression.ipynb
jupyter nbconvert --to notebook --execute --inplace 6/case_study_6_bank_marketing_classification.ipynb
```

Or open them in VS Code / Jupyter and run all cells. Each notebook writes its charts to `figures/` and its result tables to `results/` inside its own folder.

## Run the Streamlit app (Case Study 3)

```
streamlit run 3/app.py
```

It opens at http://localhost:8501. Enter passenger details and click **Predict** to see the survival probability and predicted class.

Optional deployment on Streamlit Community Cloud: push this repository to GitHub, go to https://share.streamlit.io, click **Create app**, choose this repository, branch `main` and main file path `3/app.py`, then **Deploy**.

## Build the PDF reports

The reports are built with reportlab and read only the saved `figures/` and `results/` files, so every number comes from the executed notebooks. Run the notebooks first, then:

```
python 3/build_report.py
python 6/build_report.py
```

The PDFs are written to `3/report/` and `6/report/`.

## Repository layout

```
3/  titanic.csv, notebook, app.py, build_report.py, model/, figures/, results/, report/
6/  bank+marketing/ (data), notebook, build_report.py, figures/, results/, report/
requirements.txt, README.md
```

## Attribution

Code structure drafted with AI assistance (Claude); executed, verified and interpreted by Nikhil Kotte. Dataset sources: Titanic data provided by the course faculty; Bank Marketing data from the UCI Machine Learning Repository (Moro, Cortez and Rita, 2014).
