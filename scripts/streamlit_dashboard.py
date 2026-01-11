import pandas as pd
import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="E-Commerce Insights",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# GLOBAL MATPLOTLIB THEME (NON-DEFAULT)
# =====================================================
mpl.rcParams.update({
    "figure.facecolor": "#0B0F19",
    "axes.facecolor": "#111827",
    "axes.edgecolor": "#374151",
    "axes.labelcolor": "#E5E7EB",
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "xtick.color": "#D1D5DB",
    "ytick.color": "#D1D5DB",
    "grid.color": "#374151",
    "grid.linestyle": "--",
    "grid.alpha": 0.4,
    "font.size": 11
})

# =====================================================
# COLOR SYSTEM (INTENTIONAL, NOT DEFAULT)
# =====================================================
COLORS = {
    "blue": "#38BDF8",
    "green": "#22C55E",
    "red": "#EF4444",
    "amber": "#F59E0B",
    "purple": "#A855F7",
    "pink": "#EC4899",
    "teal": "#14B8A6",
    "bg": "#0B0F19"
}

# =====================================================
# LOAD DATA
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.xlsx"
df = pd.read_excel(DATA_PATH)

# =====================================================
# CLEAN DATA
# =====================================================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")
df = df.dropna(subset=["purchase_date"])
df = df.sort_values(by="purchase_date")

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.markdown("##  Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    (df["purchase_date"].min().date(), df["purchase_date"].max().date())
)

categories = st.sidebar.multiselect(
    "Product Categories",
    sorted(df["product_category"].unique()),
    sorted(df["product_category"].unique())
)

filtered_df = df[
    (df["purchase_date"] >= pd.to_datetime(date_range[0])) &
    (df["purchase_date"] <= pd.to_datetime(date_range[1])) &
    (df["product_category"].isin(categories))
]

# =====================================================
# HEADER
# =====================================================
st.markdown(
    """
    <h1 style="text-align:center;">🛒 E-Commerce Insights Dashboard</h1>
    <p style="text-align:center; color:#9CA3AF;">
        Sales • Customers • Revenue • Trends
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# KPI SECTION
# =====================================================
k1, k2, k3, k4 = st.columns(4)

k1.metric(" Orders", f"{len(filtered_df):,}")
k2.metric(" Revenue", f"${filtered_df['total_purchase_amount'].sum():,.0f}")
k3.metric(" Avg Order", f"${filtered_df['total_purchase_amount'].mean():.2f}")
k4.metric(" Return Rate", f"{filtered_df['returns'].mean()*100:.1f}%")

st.divider()

# =====================================================
# REVENUE BY CATEGORY (BAR)
# =====================================================
st.subheader(" Revenue by Product Category")

rev_cat = (
    filtered_df.groupby("product_category")["total_purchase_amount"]
    .sum()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(
    rev_cat.index,
    rev_cat.values,
    color=[COLORS["blue"], COLORS["green"], COLORS["amber"], COLORS["purple"]]
)
ax.set_title("Revenue Contribution by Category")
ax.set_ylabel("Revenue")
ax.grid(axis="y")

st.pyplot(fig, use_container_width=True)

st.divider()

# =====================================================
# PAYMENT METHOD (PIE)
# =====================================================
st.subheader(" Payment Method Distribution")

payment_data = filtered_df["payment_method"].value_counts()

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    payment_data.values,
    labels=payment_data.index,
    autopct="%1.1f%%",
    startangle=120,
    colors=[COLORS["teal"], COLORS["blue"], COLORS["amber"], COLORS["pink"]],
    wedgeprops={"linewidth": 1.5, "edgecolor": COLORS["bg"]}
)
ax.set_title("Customer Payment Preferences")

st.pyplot(fig, use_container_width=True)

st.divider()

# =====================================================
# CUSTOMER CHURN (PIE – 0 & 1 EXPLAINED)
# =====================================================
st.subheader(" Customer Churn")

churn_map = {0: "Retained Customers", 1: "Churned Customers"}
churn_data = filtered_df["churn"].map(churn_map).value_counts()

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    churn_data.values,
    labels=churn_data.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=[COLORS["green"], COLORS["red"]],
    explode=(0, 0.05),
    wedgeprops={"edgecolor": COLORS["bg"]}
)
ax.set_title("Retention vs Churn")

st.pyplot(fig, use_container_width=True)

st.divider()

# =====================================================
# REVENUE OVER TIME (MONTHLY LINE)
# =====================================================
st.subheader(" Revenue Over Time (Monthly Trend)")

monthly_revenue = (
    filtered_df
    .groupby(filtered_df["purchase_date"].dt.to_period("M"))
    ["total_purchase_amount"]
    .sum()
)
monthly_revenue.index = monthly_revenue.index.astype(str)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(
    monthly_revenue.index,
    monthly_revenue.values,
    color=COLORS["blue"],
    linewidth=3,
    marker="o",
    markersize=4
)
ax.set_title("Monthly Revenue Trend")
ax.set_ylabel("Revenue")
ax.grid(True)

st.pyplot(fig, use_container_width=True)

st.divider()

# =====================================================
# QUANTITY SOLD (DONUT – BETTER UX)
# =====================================================
st.subheader(" Quantity Sold by Category")

qty_cat = (
    filtered_df.groupby("product_category")["quantity"]
    .sum()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    qty_cat.values,
    labels=qty_cat.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=[COLORS["purple"], COLORS["blue"], COLORS["amber"], COLORS["teal"]],
    wedgeprops={"edgecolor": COLORS["bg"]}
)

centre = plt.Circle((0, 0), 0.6, fc=COLORS["bg"])
fig.gca().add_artist(centre)

ax.set_title("Category-wise Quantity Contribution")

st.pyplot(fig, use_container_width=True)

st.divider()

# =====================================================
# DATA TABLE
# =====================================================
st.subheader(" Orders Data")
st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown(
    """
    <hr>
    <p style="text-align:center; color:#9CA3AF;">
        Built with Python & Streamlit • Custom Matplotlib Theme
    </p>
    """,
    unsafe_allow_html=True
)
# =====================================================
