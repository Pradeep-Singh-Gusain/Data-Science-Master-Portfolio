# ==============================================================================
# ENTERPRISE-GRADE CAPSTONE DEPLOYMENT: Zomato Bangalore AI Predictor Web App
# DESCRIPTION: Streamlit production web application for interactive model inference.
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# Page Configuration
st.set_page_config(
    page_title="Zomato Bangalore Market Intelligence Platform",
    page_icon="🍽️",
    layout="wide"
)

# Load Serialized Model Pipeline
@st.cache_resource
def load_model():
    model_path = 'model_pipeline.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

pipeline = load_model()

# App Header
st.title("🍽️ Zomato Bangalore Restaurant Popularity & Market Predictor")
st.markdown("### Enterprise-Grade 15-Layer Data Science Capstone Deployment")
st.write("This interactive application uses a trained Machine Learning pipeline to predict expected customer engagement (`votes`) based on operational parameters, pricing tiers, and micro-market hubs.")

if pipeline is None:
    st.error("[ERROR] Model pipeline file (`model_pipeline.pkl`) not found in the deployment directory!")
else:
    st.sidebar.header("🔍 Input Restaurant Parameters")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        online_order = st.selectbox("Online Order", ["Yes", "No"])
        book_table = st.selectbox("Table Booking", ["Yes", "No"])
        clean_rate = st.slider("Restaurant Rating (/5)", min_value=1.0, max_value=5.0, value=3.8, step=0.1)
        clean_cost = st.number_input("Cost for Two (INR)", min_value=50, max_value=10000, value=600, step=50)
        cuisine_count = st.slider("Cuisine Count", min_value=1, max_value=8, value=2)

    with col2:
        has_dish_liked = st.selectbox("Signature Dish Flag", [1, 0], format_func=lambda x: "Yes (Available)" if x == 1 else "None Documented")
        location = st.selectbox("Micro-Market Hub", [
            'BTM', 'Koramangala 5th Block', 'Indiranagar', 'Whitefield', 
            'Jayanagar', 'Marathahalli', 'Bannerghatta Road', 'JP Nagar', 'HSR', 'Other'
        ])
        rest_type = st.selectbox("Restaurant Type", [
            'Casual Dining', 'Quick Bites', 'Cafe', 'Dessert Parlor', 
            'Delivery', 'Bar', 'Beverage Shop', 'Fine Dining', 'Other'
        ])
        listed_in_type = st.selectbox("Service Category", [
            'Dine-out', 'Delivery', 'Buffet', 'Cafes', 'Drinks & nightlife', 'Desserts', 'Pubs and bars'
        ])

    # Derived Feature calculation
    cost_per_cuisine = clean_cost / (cuisine_count + 1)

    # Prediction Trigger
    if st.sidebar.button("Predict Market Viability & Votes", type="primary"):
        input_data = pd.DataFrame([{
            'online_order': online_order,
            'book_table': book_table,
            'location': location,
            'rest_type': rest_type,
            'listed_in_type': listed_in_type,
            'clean_cost': float(clean_cost),
            'clean_rate': float(clean_rate),
            'cuisine_count': int(cuisine_count),
            'has_dish_liked': int(has_dish_liked),
            'cost_per_cuisine': float(cost_per_cuisine)
        }])

        try:
            log_pred = pipeline.predict(input_data)[0]
            predicted_votes = max(0, int(np.expm1(log_pred)))

            st.divider()
            st.subheader("📊 Executive Prediction Output")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Predicted User Votes", f"{predicted_votes} Votes", help="Estimated customer engagement volume")
            res_col2.metric("Pricing Tier (Cost/2)", f"₹{clean_cost}")
            res_col3.metric("Service Quality Index", f"{clean_rate} / 5.0")

            if predicted_votes > 500:
                st.success("🌟 **High-Impact Market Segment:** This restaurant profile indicates exceptional market traction and high viral visibility in Bangalore.")
            elif predicted_votes > 150:
                st.info("👍 **Moderate Viability:** Standard performance tier. Optimizing menu diversification or table booking could elevate engagement.")
            else:
                st.warning("⚠️ **Niche / Low Engagement Profile:** High risk of low customer visibility unless paired with aggressive delivery promotions.")

        except Exception as ex:
            st.error(f"[INFERENCE ERROR]: {ex}")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>Zomato Bangalore Data Science Master Portfolio | Built with Streamlit & Scikit-Learn</p>", unsafe_allow_html=True)
