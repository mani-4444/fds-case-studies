# Fundamentals of Data Science (22CSC59) - Case Studies 3 & 6

Chaitanya Bharathi Institute of Technology (Autonomous), Hyderabad  
Department of Computer Science and Engineering  
Student: Munjampally Manideep | Roll No: 160124733189 | Section: CSE-3 (III Year, V Sem)  
Faculty Guide: Dr. S. Durga Devi, Assistant Professor  

---

## Deliverables Summary

* **Combined Notebook (Both Case Studies):** [`FDS_Case_Studies_3_and_6_160124733189.ipynb`](FDS_Case_Studies_3_and_6_160124733189.ipynb)
* **Single Combined PDF Report:** [`FDS_Case_Studies_Report_160124733189.pdf`](FDS_Case_Studies_Report_160124733189.pdf)
* **Titanic Web App:** [`3/app.py`](3/app.py)

*(Individual case study folders `3/` and `6/` are also preserved with their separate notebooks, figures, and models).*

---

## 1. Case Study 3: Titanic Survival Prediction (Logistic Regression)

* **Dataset:** `3/titanic.csv` (891 passengers).
* **Key Steps:**
  * **Fare per person:** Divided raw ticket fare by the number of passengers sharing the ticket (`Fare / Ticket_Size`) and took `log1p`. Skewness dropped from **4.79** to **0.33**, removing extreme fare outliers.
  * **Group Age Imputation:** Filled missing ages using the median age of each passenger's `(Pclass x Sex)` group from the training data only. This avoided distorting ages across social classes (1st-class men were median 40 years, 3rd-class women were 21.5 years).
  * **Two Model Fits:**
    * *statsmodels Logit (unscaled):* Used to interpret real units. Each additional year of age reduces survival odds by **4.53%** ($p < 0.0001$), moving down one class tier reduces odds by **64.44%** ($p < 0.0001$), being male reduces odds by **92.81%** ($p < 0.0001$), and higher individual log fare increases survival odds by **51.85%** ($p = 0.0474$).
    * *scikit-learn Logistic Regression (scaled):* Used for prediction with StandardScaler and L2 penalty.
  * **Precision-Recall Threshold:** Shifting the threshold to **0.41** maximized the F1 score to **0.7692** and raised survivor recall to **79.71%** (accuracy 81.56%, ROC-AUC 0.8382, Average Precision 0.7838).
* **Streamlit App:** Run locally with `streamlit run 3/app.py`.

---

## 2. Case Study 6: Bank Marketing Classification (SMOTE)

* **Dataset:** `6/bank+marketing/bank/bank-full.csv` (45,211 rows, 17 columns).
* **Key Steps:**
  * **Data Hygiene:** Dropped `duration` to prevent data leakage because call duration is not known before calling. Kept 'unknown' as its own category. Clients with no prior contact are coded as `pdays = -1` (81.74%).
  * **Class Imbalance with SMOTE:** Only 11.70% of clients subscribed. We used SMOTE inside an `imblearn` pipeline so synthetic minority points are created strictly during training, allowing all 4 models (including KNN) to be benchmarked fairly.
  * **Model Comparison:**
    * **Random Forest (Selected / Best-Performing):** Accuracy **88.44%**, Precision **50.78%**, Recall 39.98%, F1 **0.4474**, ROC-AUC **0.7922**, PR-AUC **0.4346**.
    * **Decision Tree:** Accuracy 84.65%, Precision 35.63%, F1 0.3708, ROC-AUC 0.7174.
    * **Logistic Regression:** Accuracy 74.79%, Precision 25.87%, Recall 61.91%, F1 0.3649.
    * **KNN (k=15):** Accuracy 70.71%, Precision 23.30%, Recall 65.60%, F1 0.3438 (2,285 false calls).
  * **Cumulative Gains:** Contacting the top **20%** of customers ranked by Random Forest captures **60.40%** of all term deposit subscribers while requiring 80% fewer calls.
  * **Permutation Importance on Test Set:** Top real-world predictors are contact type, campaign month, prior outcome, contact day, and housing loan.

---

## How to Run

### Setup Environment

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Combined Notebook

```bash
jupyter nbconvert --to notebook --execute --inplace FDS_Case_Studies_3_and_6_160124733189.ipynb
```

### Build the Combined PDF Report

```bash
python build_final_report.py
```

### Run the Titanic Streamlit App

```bash
streamlit run 3/app.py
```
