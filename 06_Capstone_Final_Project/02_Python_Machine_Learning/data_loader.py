import os
import pandas as pd
import numpy as np

def clean_data_core(df):
    # Standardize column names if needed
    col_map = {
        'listed_in(type)': 'listed_in_type',
        'listed_in(city)': 'listed_in_city',
        'approx_cost(for two people)': 'approx_cost'
    }
    df = df.rename(columns=col_map).copy()
    
    # Drop rows without name or location
    df = df.dropna(subset=['name', 'location']).copy()
    
    # 1. Clean Rating
    def extract_rate(val):
        if pd.isna(val) or val in ['NEW', '-']:
            return np.nan
        val_str = str(val).split('/')[0].strip()
        try:
            return float(val_str)
        except:
            return np.nan
            
    df['clean_rate'] = df['rate'].apply(extract_rate) if 'rate' in df.columns else np.nan
    
    # 2. Clean Cost for Two
    cost_col = 'approx_cost' if 'approx_cost' in df.columns else 'approx_cost(for two people)'
    def extract_cost(val):
        if pd.isna(val):
            return np.nan
        val_str = str(val).replace(',', '').strip()
        try:
            return float(val_str)
        except:
            return np.nan
            
    if cost_col in df.columns:
        df['clean_cost'] = df[cost_col].apply(extract_cost)
    else:
        df['clean_cost'] = 400.0
    
    # 3. Clean Votes
    if 'votes' in df.columns:
        df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    else:
        df['votes'] = 0
    
    # 4. Fill missing categorical values safely
    if 'online_order' in df.columns:
        df['online_order'] = df['online_order'].fillna('No')
    else:
        df['online_order'] = 'No'

    if 'book_table' in df.columns:
        df['book_table'] = df['book_table'].fillna('No')
    else:
        df['book_table'] = 'No'

    if 'rest_type' in df.columns:
        df['rest_type'] = df['rest_type'].fillna('Quick Bites')
    else:
        df['rest_type'] = 'Quick Bites'

    if 'listed_in_type' in df.columns:
        df['listed_in_type'] = df['listed_in_type'].fillna('Delivery')
    else:
        df['listed_in_type'] = 'Delivery'

    if 'cuisines' in df.columns:
        df['cuisines'] = df['cuisines'].fillna('North Indian')
    else:
        df['cuisines'] = 'North Indian'
    
    # 5. Price Tier
    median_cost = df['clean_cost'].median() if not df['clean_cost'].isna().all() else 400.0
    df['clean_cost'] = df['clean_cost'].fillna(median_cost)
    
    def assign_tier(cost):
        if cost <= 400:
            return 'Budget Friendly'
        elif cost <= 800:
            return 'Mid-Range'
        else:
            return 'Premium'
            
    df['price_tier'] = df['clean_cost'].apply(assign_tier)
    
    # 6. Bayesian Weighted Score (IMDB Formula)
    C = df['clean_rate'].mean() if not df['clean_rate'].isna().all() else 3.5
    m = df['votes'].quantile(0.60) if not df['votes'].empty else 50
    
    def bayesian_score(row):
        v = row['votes']
        R = row['clean_rate']
        if pd.isna(R):
            return C
        return (v / (v + m) * R) + (m / (v + m) * C)
        
    df['weighted_score'] = df.apply(bayesian_score, axis=1)
    
    # 7. Additional Engineered Features
    df['cuisine_count'] = df['cuisines'].apply(lambda x: len(str(x).split(',')))
    if 'dish_liked' in df.columns:
        df['has_dish_liked'] = df['dish_liked'].notna().astype(int)
    else:
        df['has_dish_liked'] = 0
    df['cost_per_cuisine'] = df['clean_cost'] / (df['cuisine_count'] + 1)
    
    return df

def get_raw_csv_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "01_SQL_Database_Analytics", "zomato.csv"),
        os.path.join(os.path.dirname(base_dir), "03_Real_World_Dataset_Project", "zomato.csv"),
        os.path.join(os.path.dirname(base_dir), "05_Analytics_Business_Report", "zomato.csv")
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

def load_and_clean_data():
    csv_path = get_raw_csv_path()
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df_raw = pd.read_csv(csv_path)
    return clean_data_core(df_raw)