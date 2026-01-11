import pandas as pd
import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt

# =====================================================
# Page Config
# =====================================================
st.set_page_config(
    page_title="E-commerce Insights",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# Load Data
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.xlsx"

df = pd.read_excel(DATA_PATH)

# =====================================================
# Clean Columns
# =====================================================
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(' ', '_')
)

# =====================================================
# Date Handling
# =====================================================
df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
df = df.dropna(subset=['purchase_date'])
df = df.sort_values(by='purchase_date')

# =====================================================
# Sidebar Filters
# =====================================================
st.sidebar.markdown("## 🔍 Filters")

min_date = df['purchase_date'].min().date()
max_date = df['purchase_date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date)
)

categories = st.sidebar.multiselect(
    "Product Categories",
    options=sorted(df['product_category'].unique()),
    default=sorted(df['product_category'].unique())
)

filtered_df = df[
    (df['purchase_date'] >= pd.to_datetime(date_range[0])) &
    (df['purchase_date'] <= pd.to_datetime(date_range[1])) &
    (df['product_category'].isin(categories))
]

# =====================================================
# Header
# =====================================================
st.markdown(
    """
    <h1 style="text-align:center;">🛒 E-commerce Insights Dashboard</h1>
    <p style="text-align:center; color:#6c757d;">
        Sales Performance • Customer Behavior • Revenue Trends
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# KPI SECTION
# =====================================================
k1, k2, k3, k4 = st.columns(4)

k1.metric("📦 Orders", f"{len(filtered_df):,}")
k2.metric("💰 Revenue", f"${filtered_df['total_purchase_amount'].sum():,.0f}")
k3.metric("🧾 Avg Order", f"${filtered_df['total_purchase_amount'].mean():.2f}")
k4.metric("🔁 Return Rate", f"{filtered_df['returns'].mean()*100:.1f}%")

st.divider()

# =====================================================
# ROW 1 — BAR CHART
# =====================================================
st.subheader("📊 Revenue by Product Category")

rev_cat = (
    filtered_df.groupby('product_category')['total_purchase_amount']
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(rev_cat, use_container_width=True)

st.divider()

# =====================================================
# ROW 2 — PIE CHARTS (FIXED SIZE)
# =====================================================
c1, c2 = st.columns(2, gap="large")

with c1:
    st.subheader("💳 Payment Method Distribution")
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    filtered_df['payment_method'].value_counts().plot(
        kind='pie',
        autopct='%1.1f%%',
        startangle=90,
        ax=ax1
    )
    ax1.set_ylabel("")
    st.pyplot(fig1, use_container_width=True)

with c2:
    st.subheader("🧑‍🤝‍🧑 Customer Churn")
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    filtered_df['churn'].value_counts().plot(
        kind='pie',
        autopct='%1.1f%%',
        startangle=90,
        ax=ax2
    )
    ax2.set_ylabel("")
    st.pyplot(fig2, use_container_width=True)

st.divider()

# =====================================================
# ROW 3 — LINE CHART
# =====================================================
st.subheader("📈 Revenue Over Time")

daily_revenue = (
    filtered_df.groupby(filtered_df['purchase_date'].dt.date)
    ['total_purchase_amount']
    .sum()
)

st.line_chart(daily_revenue, use_container_width=True)

st.divider()

# =====================================================
# ROW 4 — QUANTITY BAR
# =====================================================
st.subheader("📦 Quantity Sold by Category")

qty_cat = (
    filtered_df.groupby('product_category')['quantity']
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(qty_cat, use_container_width=True)

st.divider()

# =====================================================
# DATA TABLE
# =====================================================
st.subheader("📋 Orders Data")
st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown(
    """
    <hr>
    <p style="text-align:center; color:#6c757d;">
        Built with Streamlit • Data Source: cleaned_data.xlsx
    </p>
    """,
    unsafe_allow_html=True
)
