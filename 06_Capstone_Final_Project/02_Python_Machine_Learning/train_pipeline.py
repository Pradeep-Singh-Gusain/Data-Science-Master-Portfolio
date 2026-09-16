import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CSV_PATH = r"E:\Data-Science-Master-Portfolio\03_Real_World_Dataset_Project\Zomato.csv"
OUTPUT_DIR = r"E:\Data-Science-Master-Portfolio\06_Capstone_Final_Project\01_SQL_Database_Analytics\02_Python_Machine_Learning"
MODEL_PATH = os.path.join(OUTPUT_DIR, "model_pipeline.pkl")

print("[1/4] Reading dataset...")
df = pd.read_csv(CSV_PATH)

# Clean target (votes)
df = df.dropna(subset=['votes'])
df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)

# Extract numeric rating
def clean_rate(v):
    if pd.isna(v):
        return np.nan
    v = str(v).split('/')[0].strip()
    try:
        return float(v)
    except ValueError:
        return np.nan

df['clean_rate'] = df['rate'].apply(clean_rate)
df['clean_rate'] = df['clean_rate'].fillna(df['clean_rate'].median())

# Clean cost
df['clean_cost'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')
df['clean_cost'] = df['clean_cost'].fillna(df['clean_cost'].median())

# Categoricals & features
df['location'] = df['location'].fillna('Other').str.strip()
df['rest_type'] = df['rest_type'].fillna('Other').str.strip()
df['listed_in_type'] = df['listed_in(type)'].fillna('Other').str.strip()
df['online_order'] = df['online_order'].fillna('No').str.strip()
df['book_table'] = df['book_table'].fillna('No').str.strip()

df['cuisine_count'] = df['cuisines'].fillna('').apply(lambda x: len([c.strip() for c in str(x).split(',') if c.strip()]))
df['has_dish_liked'] = df['dish_liked'].notna().astype(int)
df['cost_per_cuisine'] = df['clean_cost'] / (df['cuisine_count'] + 1)

# Feature sets
cat_features = ['online_order', 'book_table', 'location', 'rest_type', 'listed_in_type']
num_features = ['clean_cost', 'clean_rate', 'cuisine_count', 'has_dish_liked', 'cost_per_cuisine']

X = df[cat_features + num_features]
y = np.log1p(df['votes'])

print("[2/4] Building pipeline...")
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
    ('num', StandardScaler(), num_features)
])

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=40, max_depth=12, random_state=42, n_jobs=-1))
])

print("[3/4] Fitting model on actual dataset...")
pipeline.fit(X, y)

print("[4/4] Saving model artifact...")
os.makedirs(OUTPUT_DIR, exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)
print(f"[SUCCESS] Model artifact saved to: {MODEL_PATH}")