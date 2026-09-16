import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from data_loader import load_and_clean_data

# ---------------------------------------------------------
# Page Configuration & Executive Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Zomato Bangalore Analytics Platform | Capstone Portfolio",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Clean Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Executive Metric Cards */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetricLabel"] p {
        color: #64748b !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] div {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
    }
    
    /* Typography */
    h1 {
        color: #0f172a !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    h2, h3, h4 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    /* Project Attribution Banner */
    .project-banner {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #e11d48;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 24px;
    }
    
    .stAlert {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-left: 4px solid #2563eb !important;
        color: #1e293b !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Central Data Load
# ---------------------------------------------------------
df = load_and_clean_data()
if df.empty:
    st.error("Dataset not found. Please verify data path inside data_loader.py.")
    st.stop()

# ---------------------------------------------------------
# Sidebar Navigation & Portfolio Attribution
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🍽️ Zomato Bangalore")
    st.markdown("<span style='font-size: 0.85rem; font-weight: 600; color: #e11d48;'>RESTAURANT INTELLIGENCE SUITE</span>", unsafe_allow_html=True)
    st.caption("Capstone Project: Market Analysis & Engagement ML")
    
    view_mode = option_menu(
        menu_title=None,
        options=[
            "Executive Overview",
            "Locality Hubs",
            "Cuisine Dynamics",
            "Rating Reliability",
            "Pricing Economics",
            "Bayesian Rankings",
            "AgGrid Explorer",
            "Benchmark Comparison",
            "ML Traction Predictor"
        ],
        icons=[
            "speedometer2", 
            "geo-alt", 
            "egg-fried", 
            "star", 
            "cash-stack", 
            "trophy", 
            "table", 
            "intersect", 
            "cpu"
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#64748b", "font-size": "15px"},
            "nav-link": {
                "font-size": "13px",
                "text-align": "left",
                "margin": "3px 0px",
                "color": "#334155",
                "border-radius": "8px",
                "padding": "8px 12px"
            },
            "nav-link-selected": {
                "background-color": "#fff1f2",
                "color": "#e11d48",
                "font-weight": "600"
            }
        }
    )
    
    st.markdown("---")
    st.markdown("<p style='font-size: 0.8rem; font-weight: 700; color: #64748b;'>FILTER CONTROLS</p>", unsafe_allow_html=True)

    locations = sorted([l for l in df['location'].unique() if l != 'Unknown'])
    selected_locations = st.multiselect("Localities", locations, default=[])

    tiers = ['Budget Friendly', 'Mid-Range', 'Premium']
    selected_tiers = st.multiselect("Price Segment", tiers, default=[])

    c1, c2 = st.columns(2)
    with c1:
        filter_delivery = st.selectbox("Online Order", ["All", "Yes", "No"])
    with c2:
        filter_booking = st.selectbox("Table Booking", ["All", "Yes", "No"])

    min_rating = st.slider("Min Rating", 1.0, 5.0, 1.0, 0.1)

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.75rem; color: #94a3b8; line-height: 1.4;'>
    <b>Data Source:</b> Zomato Bangalore Open Records<br>
    <b>Scope:</b> 41,000+ Establishments<br>
    <b>Role:</b> Data Analyst Capstone Project
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Apply Global Filtering Pipeline
# ---------------------------------------------------------
filtered_df = df.copy()
if selected_locations:
    filtered_df = filtered_df[filtered_df['location'].isin(selected_locations)]
if selected_tiers:
    filtered_df = filtered_df[filtered_df['price_tier'].isin(selected_tiers)]
if filter_delivery != "All":
    filtered_df = filtered_df[filtered_df['online_order'] == filter_delivery]
if filter_booking != "All":
    filtered_df = filtered_df[filtered_df['book_table'] == filter_booking]
filtered_df = filtered_df[filtered_df['clean_rate'].fillna(0) >= min_rating]

# ---------------------------------------------------------
# Safe Plotly Formatter (Fixes Single-Item Stretch & Histogram Crash)
# ---------------------------------------------------------
def clean_plot(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#475569", size=12),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        bargap=0.3
    )
    # Check specifically for Bar traces to set width without affecting Histograms
    if len(fig.data) > 0 and fig.data[0].type == "bar":
        if hasattr(fig.data[0], "x") and fig.data[0].x is not None and len(fig.data[0].x) == 1:
            fig.update_traces(width=0.3, selector=dict(type="bar"))
    return fig

# ---------------------------------------------------------
# View 1: Executive Overview
# ---------------------------------------------------------
if view_mode == "Executive Overview":
    st.title("Zomato Bangalore Restaurant Intelligence Dashboard")
    st.markdown("""
    <div class="project-banner">
        <span style="font-weight: 700; color: #0f172a;">Capstone Analytics Portfolio:</span> 
        Exploratory Data Analysis, Bayesian Rating Calibration, and Machine Learning on <b>41,000+ Zomato Bangalore Restaurant Records</b>.
    </div>
    """, unsafe_allow_html=True)
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Active Venues", f"{len(filtered_df):,}")
    k2.metric("Mean Rating", f"{filtered_df['clean_rate'].mean():.2f} / 5.0")
    k3.metric("Ticket Size (2 Pax)", f"₹{filtered_df['clean_cost'].mean():.0f}")
    k4.metric("Total Reviews", f"{filtered_df['votes'].sum():,}")
    delivery_pct = (filtered_df['online_order'] == 'Yes').mean() * 100 if len(filtered_df) > 0 else 0
    k5.metric("Delivery Coverage", f"{delivery_pct:.1f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Localities by Restaurant Concentration")
        top_locs = filtered_df['location'].value_counts().head(10).reset_index()
        top_locs.columns = ['Locality', 'Count']
        fig1 = px.bar(top_locs, x='Locality', y='Count', color_discrete_sequence=['#e11d48'])
        st.plotly_chart(clean_plot(fig1), use_container_width=True)

    with col2:
        st.subheader("Zomato Rating Distribution Curve")
        fig2 = px.histogram(filtered_df['clean_rate'].dropna(), x='clean_rate', nbins=20, color_discrete_sequence=['#2563eb'])
        fig2.update_layout(xaxis_title="Rating (1-5)", yaxis_title="Number of Establishments")
        st.plotly_chart(clean_plot(fig2), use_container_width=True)

    top_vol_area = filtered_df.groupby('location')['votes'].sum().idxmax() if len(filtered_df) > 0 else "N/A"
    highest_cost_area = filtered_df.groupby('location')['clean_cost'].mean().idxmax() if len(filtered_df) > 0 else "N/A"
    
    st.info(
        f"**Empirical Strategic Insights (Zomato Dataset):**\n\n"
        f"• **Review Capital:** `{top_vol_area}` commands the highest total consumer review volume across Bangalore.\n"
        f"• **Premium Dining Cluster:** `{highest_cost_area}` records the highest average ticket size for two people."
    )

# ---------------------------------------------------------
# View 2: Locality Hubs
# ---------------------------------------------------------
elif view_mode == "Locality Hubs":
    st.title("Locality Ecosystem Breakdown")
    st.caption("Bangalore Micro-Markets: Establishment Density, Ticket Size, and Engagement Volumes")

    loc_summary = filtered_df.groupby('location').agg(
        Total_Venues=('name', 'count'),
        Avg_Rating=('clean_rate', 'mean'),
        Avg_Cost=('clean_cost', 'mean'),
        Total_Votes=('votes', 'sum')
    ).reset_index()
    loc_summary = loc_summary[loc_summary['Total_Venues'] >= 5].sort_values('Total_Venues', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dense Micro-Markets")
        st.dataframe(loc_summary[['location', 'Total_Venues', 'Avg_Rating', 'Avg_Cost']].head(15).round(2), use_container_width=True)
    with col2:
        st.subheader("Average Cost for Two Across Hubs (INR)")
        fig = px.bar(loc_summary.head(10), x='location', y='Avg_Cost', color_discrete_sequence=['#6366f1'])
        st.plotly_chart(clean_plot(fig), use_container_width=True)

# ---------------------------------------------------------
# View 3: Cuisine Dynamics
# ---------------------------------------------------------
elif view_mode == "Cuisine Dynamics":
    st.title("Bangalore Cuisine Supply & Market Saturation")
    
    cuisines_series = filtered_df['cuisines'].dropna().str.split(', ')
    all_cuisines = [c.strip() for sublist in cuisines_series for c in sublist if c.strip()]
    cuisine_df = pd.Series(all_cuisines).value_counts().reset_index()
    cuisine_df.columns = ['Cuisine', 'Venues']

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dominant Cuisines Across Dataset")
        st.dataframe(cuisine_df.head(15), use_container_width=True)
    with col2:
        st.subheader("Top 10 Offerings by Establishment Count")
        fig = px.bar(cuisine_df.head(10), x='Cuisine', y='Venues', color_discrete_sequence=['#0d9488'])
        st.plotly_chart(clean_plot(fig), use_container_width=True)

# ---------------------------------------------------------
# View 4: Rating Reliability
# ---------------------------------------------------------
elif view_mode == "Rating Reliability":
    st.title("Rating Reliability & Volume Analysis")
    st.caption("Addressing low-sample bias using Zomato review counts.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Rating vs. Customer Review Count")
        sample_data = filtered_df[['clean_rate', 'votes', 'name']].dropna().head(800)
        fig = px.scatter(sample_data, x='clean_rate', y='votes', hover_name='name', color_discrete_sequence=['#f59e0b'])
        st.plotly_chart(clean_plot(fig), use_container_width=True)
    with col2:
        st.subheader("Rating Spread: Table Booking Impact")
        fig_box = px.box(filtered_df.dropna(subset=['clean_rate']), x='book_table', y='clean_rate', color_discrete_sequence=['#2563eb'])
        st.plotly_chart(clean_plot(fig_box), use_container_width=True)

# ---------------------------------------------------------
# View 5: Pricing Economics
# ---------------------------------------------------------
elif view_mode == "Pricing Economics":
    st.title("Pricing Strategy & Ticket Size Segments")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Market Tier Breakdown")
        tier_counts = filtered_df['price_tier'].value_counts().reset_index()
        tier_counts.columns = ['Segment', 'Count']
        fig = px.pie(tier_counts, names='Segment', values='Count', color_discrete_sequence=['#38bdf8', '#818cf8', '#34d399'], hole=0.5)
        st.plotly_chart(clean_plot(fig), use_container_width=True)
    with c2:
        st.subheader("Segment Performance")
        st.dataframe(
            filtered_df.groupby('price_tier').agg(
                Venues=('name', 'count'),
                Mean_Cost=('clean_cost', 'mean'),
                Mean_Rating=('clean_rate', 'mean')
            ).round(2),
            use_container_width=True
        )

# ---------------------------------------------------------
# View 6: Bayesian Rankings
# ---------------------------------------------------------
elif view_mode == "Bayesian Rankings":
    st.title("Bayesian Benchmark Rankings (IMDB Formulation)")
    st.caption("Scored using Bayesian weighting to prevent restaurants with 2 reviews from outranking verified popular venues.")

    top_ranked = filtered_df.sort_values('weighted_score', ascending=False).dropna(subset=['weighted_score'])
    display_cols = ['name', 'location', 'clean_rate', 'votes', 'weighted_score', 'clean_cost', 'cuisines']
    
    st.dataframe(
        top_ranked[display_cols].head(30).round(2).rename(columns={
            'name': 'Establishment',
            'location': 'Locality',
            'clean_rate': 'Raw Rating',
            'votes': 'Reviews',
            'weighted_score': 'Bayesian Index',
            'clean_cost': 'Cost (2 Pax)',
            'cuisines': 'Cuisines'
        }),
        use_container_width=True
    )

# ---------------------------------------------------------
# View 7: AgGrid Explorer
# ---------------------------------------------------------
elif view_mode == "AgGrid Explorer":
    st.title("Interactive Zomato Dataset Explorer")
    st.caption("Multi-column sorting, in-cell searching, and spreadsheet filtering.")

    table_data = filtered_df[['name', 'location', 'clean_rate', 'votes', 'clean_cost', 'cuisines', 'online_order', 'book_table']].copy()
    table_data.columns = ['Restaurant', 'Locality', 'Rating', 'Votes', 'Cost', 'Cuisines', 'Delivery', 'Booking']
    
    gb = GridOptionsBuilder.from_dataframe(table_data.head(200))
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_side_bar()
    gb.configure_default_column(resizable=True, filterable=True, sortable=True)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    grid_options = gb.build()

    AgGrid(
        table_data.head(200),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="alpine",
        height=520,
        width="100%"
    )

    csv_data = table_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Recordset (CSV)",
        data=csv_data,
        file_name="zomato_bangalore_filtered.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# View 8: Benchmark Comparison
# ---------------------------------------------------------
elif view_mode == "Benchmark Comparison":
    st.title("Multi-Establishment Competitive Matrix")
    restaurant_options = sorted(filtered_df['name'].unique())
    selected_restaurants = st.multiselect("Select 2 to 4 Establishments", restaurant_options, max_selections=4)

    if len(selected_restaurants) >= 2:
        comp_df = filtered_df[filtered_df['name'].isin(selected_restaurants)].drop_duplicates(subset=['name'])
        cols = st.columns(len(selected_restaurants))
        for idx, (_, row) in enumerate(comp_df.iterrows()):
            with cols[idx]:
                st.subheader(row['name'])
                st.metric("Rating", f"{row['clean_rate']} / 5.0")
                st.metric("Reviews", f"{row['votes']:,}")
                st.metric("Cost for Two", f"₹{row['clean_cost']}")
                st.markdown(f"**Locality:** {row['location']}")
                st.markdown(f"**Cuisines:** {row['cuisines']}")
                st.markdown(f"**Online Delivery:** {row['online_order']}")
                st.markdown(f"**Reservation:** {row['book_table']}")
    else:
        st.info("Select at least 2 establishments above to launch side-by-side comparison.")

# ---------------------------------------------------------
# View 9: ML Traction Predictor
# ---------------------------------------------------------
elif view_mode == "ML Traction Predictor":
    st.title("Predictive Review Traction Modeling")
    st.caption("Random Forest Regression pipeline trained on 41,000+ Zomato Bangalore establishments.")

    @st.cache_resource
    def load_pipeline():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "model_pipeline.pkl")
        return joblib.load(model_path) if os.path.exists(model_path) else None

    pipeline = load_pipeline()

    if pipeline is None:
        st.error("Model file not found. Ensure model_pipeline.pkl is present.")
    else:
        with st.form("pred_form"):
            c1, c2 = st.columns(2)
            with c1:
                in_order = st.selectbox("Online Order Enabled", ["Yes", "No"])
                in_book = st.selectbox("Table Booking Enabled", ["Yes", "No"])
                in_loc = st.selectbox("Target Locality", sorted(df['location'].unique()))
                in_rest = st.selectbox("Establishment Format", sorted(df['rest_type'].unique()))
                in_cat = st.selectbox("Service Classification", sorted(df['listed_in_type'].unique()))
            with c2:
                in_cost = st.number_input("Target Cost for Two (INR)", 100, 10000, 750, 50)
                in_rate = st.slider("Target Service Quality (Rating)", 1.0, 5.0, 3.9, 0.1)
                in_cuisines = st.slider("Cuisines Count", 1, 10, 2)
                in_dish = st.selectbox("Signature Items Documented", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")

            submit_btn = st.form_submit_button("Compute Estimated Market Traction")

        if submit_btn:
            cost_per_c = in_cost / (in_cuisines + 1)
            pred_payload = pd.DataFrame([{
                'online_order': in_order,
                'book_table': in_book,
                'location': in_loc,
                'rest_type': in_rest,
                'listed_in_type': in_cat,
                'clean_cost': float(in_cost),
                'clean_rate': float(in_rate),
                'cuisine_count': int(in_cuisines),
                'has_dish_liked': int(in_dish),
                'cost_per_cuisine': float(cost_per_c)
            }])

            try:
                log_val = pipeline.predict(pred_payload)[0]
                est_votes = max(0, int(np.expm1(log_val)))
                st.success(f"### Predicted Engagement: ~{est_votes:,} Consumer Review Votes")
            except Exception as e:
                st.error(f"Inference error: {e}")