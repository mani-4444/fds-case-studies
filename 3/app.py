"""Streamlit app: predict Titanic survival with the refined logistic regression pipeline.

Run from repository root:  streamlit run 3/app.py
"""
import sys
from pathlib import Path

# Add folder to path so joblib can deserialize TitanicFeaturePreprocessor
sys.path.append(str(Path(__file__).resolve().parent))

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from titanic_custom import TitanicFeaturePreprocessor  # noqa: F401

MODEL_PATH = Path(__file__).resolve().parent / "model" / "titanic_logreg.joblib"
FEATURES = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Ticket_Size", "Embarked"]
PORTS = {"Southampton (S)": "S", "Cherbourg (C)": "C", "Queenstown (Q)": "Q"}
CLASSES = {"1st Class (Upper)": 1, "2nd Class (Middle)": 2, "3rd Class (Lower)": 3}
OPTIMAL_THRESHOLD = 0.4066


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


st.set_page_config(page_title="Titanic Survival Predictor", page_icon="🚢", layout="centered")

st.title("🚢 Titanic Survival Predictor")
st.markdown(
    "Estimate a passenger's probability of surviving the Titanic disaster using an "
    "F1-optimized Logistic Regression pipeline."
)

model = load_model()

col1, col2 = st.columns(2)

with col1:
    pclass_label = st.selectbox("Passenger Class", list(CLASSES.keys()), index=2)
    sex = st.radio("Sex", ["male", "female"], horizontal=True)
    
    age_unknown = st.checkbox("Age unknown? (Use Pclass × Sex median)")
    if age_unknown:
        age = np.nan
        st.caption("Missing age will be imputed using the training set median for this class and sex.")
    else:
        age = st.number_input("Age (years)", min_value=0.4, max_value=80.0, value=28.0, step=1.0)
        
    port_label = st.selectbox("Port of Embarkation", list(PORTS.keys()))

with col2:
    fare = st.number_input("Total Ticket Fare ($)", min_value=0.0, max_value=550.0, value=15.0, step=1.0)
    ticket_size = st.number_input("Passengers Sharing Ticket", min_value=1, max_value=10, value=1, step=1,
                                  help="Divides fare by passenger count to compute Fare per person.")
    sibsp = st.number_input("Siblings / Spouses Aboard", min_value=0, max_value=8, value=0, step=1)
    parch = st.number_input("Parents / Children Aboard", min_value=0, max_value=6, value=0, step=1)

fare_pp = fare / max(ticket_size, 1)
st.caption(f"Calculated Fare per person: **${fare_pp:.2f}** (Log Fare per person: **{np.log1p(fare_pp):.3f}**)")

threshold = st.slider("Decision Threshold (F1-optimal = 0.41)", min_value=0.10, max_value=0.90, value=OPTIMAL_THRESHOLD, step=0.01)

if st.button("Predict Survival", type="primary", use_container_width=True):
    input_data = pd.DataFrame([{
        "Pclass": CLASSES[pclass_label],
        "Sex": sex,
        "Age": age,
        "SibSp": sibsp,
        "Parch": parch,
        "Fare": fare,
        "Ticket_Size": ticket_size,
        "Embarked": PORTS[port_label]
    }])[FEATURES]
    
    prob = float(model.predict_proba(input_data)[0, 1])
    is_survived = prob >= threshold

    st.divider()
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("Survival Probability", f"{prob:.1%}")
    with metric_col2:
        if is_survived:
            st.success("Predicted Outcome: **SURVIVED**")
        else:
            st.error("Predicted Outcome: **DID NOT SURVIVE**")

    st.progress(prob)
    st.write(
        f"At threshold **{threshold:.2f}**, the passenger is classified as "
        f"**{'Survived' if is_survived else 'Did not survive'}** (Probability: {prob:.1%})."
    )

with st.expander("About this refined model"):
    st.markdown("""
    **Methodological Features of this Pipeline:**
    * **Fare per Person & Log Transform:** Resolves ticket pooling by computing individual fare (`Fare / Ticket_Size`) and applying `log1p` to reduce skewness from 4.79 to 0.33.
    * **Group-Conditional Imputation:** Imputes missing age values using the specific median of the passenger's `Pclass × Sex` group (fit on training data only) rather than distorting with an overall median.
    * **Optimal PR Threshold (0.41):** Maximizes the F1-score (0.7692) on the Precision-Recall curve, boosting survivor recall to 79.71% compared to 69.57% under the default 0.50 threshold.
    * **Standardized Features:** Numeric variables are scaled with `StandardScaler` for regularized logistic regression prediction.
    """)
