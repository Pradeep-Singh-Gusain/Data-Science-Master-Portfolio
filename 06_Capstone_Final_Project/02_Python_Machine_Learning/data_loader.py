import pandas as pd
import numpy as np
import streamlit as st
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 01_SQL_Database_Analytics se zomato.csv uthayega:
csv_path = os.path.join(base_dir, "01_SQL_Database_Analytics", "zomato.csv")

@st.cache_data
def load_and_clean_data():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()

    df = pd.read_csv(CSV_PATH)

    # 1. Clean 'rate' column -> extract numeric float
    def extract_rating(val):
        if pd.isna(val):
            return np.nan
        val = str(val).split('/')[0].strip()
        try:
            return float(val)
        except ValueError:
            return np.nan

    df['clean_rate'] = df['rate'].apply(extract_rating)

    # 2. Standardize Cost column
    df['clean_cost'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')

    # 3. Clean categorical text
    df['location'] = df['location'].fillna('Unknown').str.strip()
    df['rest_type'] = df['rest_type'].fillna('Unknown').str.strip()
    df['cuisines'] = df['cuisines'].fillna('Not Specified').str.strip()
    df['online_order'] = df['online_order'].fillna('No').str.strip()
    df['book_table'] = df['book_table'].fillna('No').str.strip()
    df['listed_in_type'] = df['listed_in(type)'].fillna('Other').str.strip()
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)

    # 4. Feature engineering for analysis & ML
    df['cuisine_count'] = df['cuisines'].apply(lambda x: len([c.strip() for c in str(x).split(',') if c.strip()]))
    df['has_dish_liked'] = df['dish_liked'].notna().astype(int)
    df['cost_per_cuisine'] = df['clean_cost'] / (df['cuisine_count'] + 1)

    # 5. Bayesian Weighted Rating (IMDB formula) for reliable ranking
    # WR = (v / (v + m)) * R + (m / (v + m)) * C
    valid_ratings = df['clean_rate'].dropna()
    C = valid_ratings.mean()
    m = df['votes'].quantile(0.60) # 60th percentile threshold
    
    def weighted_rating(row):
        v = row['votes']
        R = row['clean_rate']
        if pd.isna(R) or v == 0:
            return np.nan
        return (v / (v + m)) * R + (m / (v + m)) * C

    df['weighted_score'] = df.apply(weighted_rating, axis=1)

    # Price Segmentation
    q33 = df['clean_cost'].quantile(0.33)
    q66 = df['clean_cost'].quantile(0.66)

    def price_tier(cost):
        if pd.isna(cost):
            return 'Unknown'
        if cost <= q33:
            return 'Budget Friendly'
        elif cost <= q66:
            return 'Mid-Range'
        else:
            return 'Premium'

    df['price_tier'] = df['clean_cost'].apply(price_tier)

    return df