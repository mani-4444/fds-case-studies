"""Streamlit app: predict Titanic survival with the saved logistic regression pipeline.

Run from the repository root:  streamlit run 3/app.py
"""
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

MODEL_PATH = Path(__file__).parent / "model" / "titanic_logreg.joblib"
FEATURES = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
PORTS = {"Southampton": "S", "Cherbourg": "C", "Queenstown": "Q"}
CLASSES = {"1st (Upper)": 1, "2nd (Middle)": 2, "3rd (Lower)": 3}


@st.cache_resource
def load_model():
    # The file holds the whole fitted Pipeline (imputers, encoder, scaler, model),
    # so raw inputs can be passed in exactly as they look in titanic.csv.
    return joblib.load(MODEL_PATH)


st.set_page_config(page_title="Titanic Survival Predictor", page_icon="🚢")
st.title("Titanic Survival Predictor")
st.write(
    "Enter a passenger's details and click **Predict** to estimate their chance of "
    "surviving the Titanic disaster."
)

model = load_model()

col1, col2 = st.columns(2)
with col1:
    pclass_label = st.selectbox("Passenger class", list(CLASSES), index=2)
    sex = st.radio("Sex", ["male", "female"], horizontal=True)
    age = st.number_input("Age (years)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    fare = st.number_input("Fare paid", min_value=0.0, max_value=600.0, value=15.0, step=1.0)
with col2:
    sibsp = st.number_input("Siblings / spouses on board", min_value=0, max_value=10, value=0, step=1)
    parch = st.number_input("Parents / children on board", min_value=0, max_value=10, value=0, step=1)
    port_label = st.selectbox("Port of embarkation", list(PORTS))

if st.button("Predict", type="primary"):
    passenger = pd.DataFrame([{
        "Pclass": CLASSES[pclass_label],
        "Sex": sex,
        "Age": age,
        "SibSp": sibsp,
        "Parch": parch,
        "Fare": fare,
        "Embarked": PORTS[port_label],
    }])[FEATURES]
    prob = float(model.predict_proba(passenger)[0, 1])
    pred = int(model.predict(passenger)[0])

    st.metric("Survival probability", f"{prob:.1%}")
    st.progress(prob)
    if pred == 1:
        st.success("Predicted class: Survived")
    else:
        st.error("Predicted class: Did not survive")

with st.expander("About this model"):
    st.write(
        "This is a logistic regression model trained on 80% of the 891-passenger Titanic "
        "dataset (Fundamentals of Data Science, Case Study 3). Missing values are filled with "
        "the training median (Age) or most common value (Embarked), Sex and port are one-hot "
        "encoded and numeric features are standardised, all inside one scikit-learn Pipeline. "
        "The predicted class is 'Survived' when the probability is at least 50%. "
        "It is a teaching model and reflects patterns in historical data only."
    )
