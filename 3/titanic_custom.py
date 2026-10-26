import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class TitanicFeaturePreprocessor(BaseEstimator, TransformerMixin):
    """
    Custom transformer that:
    1. Computes Fare_pp = Fare / Ticket_Size (or accepts Fare_pp/Log_Fare_pp directly)
       and Log_Fare_pp = np.log1p(Fare_pp).
    2. Imputes missing Age using the Pclass x Sex median lookup learned on the training set only.
    """
    def __init__(self):
        self.age_lookup_ = {}
        self.overall_age_median_ = 28.5

    def fit(self, X, y=None):
        df_in = pd.DataFrame(X)
        self.age_lookup_ = df_in.groupby(['Pclass', 'Sex'])['Age'].median().to_dict()
        self.overall_age_median_ = float(df_in['Age'].median())
        return self

    def transform(self, X):
        df_out = pd.DataFrame(X).copy()
        
        # Calculate Fare_pp and Log_Fare_pp
        if 'Log_Fare_pp' not in df_out.columns:
            if 'Ticket_Group_Size' in df_out.columns:
                fare_pp = df_out['Fare'] / df_out['Ticket_Group_Size'].replace(0, 1)
            elif 'Ticket_Size' in df_out.columns:
                fare_pp = df_out['Fare'] / df_out['Ticket_Size'].replace(0, 1)
            elif 'Fare_pp' in df_out.columns:
                fare_pp = df_out['Fare_pp']
            else:
                fare_pp = df_out['Fare']
            df_out['Log_Fare_pp'] = np.log1p(fare_pp)
            
        # Impute Age using fitted group medians
        def _fill_age(row):
            if pd.isna(row['Age']):
                key = (row['Pclass'], row['Sex'])
                return self.age_lookup_.get(key, self.overall_age_median_)
            return row['Age']

        df_out['Age'] = df_out.apply(_fill_age, axis=1)
        return df_out
