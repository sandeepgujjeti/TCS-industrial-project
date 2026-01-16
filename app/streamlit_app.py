import pandas as pd
import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="E-Commerce Insights",
    page_icon="🛒",
    layout="wide"
)

# =====================================================
# MATPLOTLIB DARK THEME
# =====================================================
mpl.rcParams.update({
    "figure.facecolor": "#0B0F19",
    "axes.facecolor": "#111827",
    "axes.edgecolor": "#374151",
    "axes.labelcolor": "#E5E7EB",
    "axes.titlecolor": "#E5E7EB",
    "text.color": "#E5E7EB",
    "xtick.color": "#D1D5DB",
    "ytick.color": "#D1D5DB",
    "grid.color": "#374151",
    "grid.linestyle": "--",
    "grid.alpha": 0.4,
    "font.size": 10
})

# =====================================================
# COLORS
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
df = pd.read_excel(BASE_DIR / "data" / "processed" / "cleaned_data.xlsx")

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")
df = df.dropna(subset=["purchase_date"])

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    (df["purchase_date"].min().date(), df["purchase_date"].max().date())
)
categories = df["product_category"].unique()
selected_categories = st.sidebar.multiselect(
    "Select Product Category",
    options=categories,
    default=categories
)

filtered_df = df[
    (df["purchase_date"] >= pd.to_datetime(date_range[0])) &
    (df["purchase_date"] <= pd.to_datetime(date_range[1])) &
    (df["product_category"].isin(selected_categories))
]

# =====================================================
# KPIs
# =====================================================
st.title("🛒 E-Commerce Insights Dashboard")
st.subheader("Sales • Customers • Revenue • Trends")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Orders", len(filtered_df))
k2.metric("Revenue", f"${filtered_df['total_purchase_amount'].sum():,.0f}")
k3.metric("Avg Order", f"${filtered_df['total_purchase_amount'].mean():.2f}")
k4.metric("Return Rate", f"{filtered_df['returns'].mean()*100:.1f}%")

st.divider()

# =====================================================
# BAR CHART: Revenue by Category (MULTICOLOR)
# =====================================================
st.subheader("Revenue by Category")
rev_cat = filtered_df.groupby("product_category")["total_purchase_amount"].sum()

col1, col2 = st.columns(2)  # use columns to control width
with col1:
    fig, ax = plt.subplots(figsize=(5,3))
    
    # Assign different colors to each bar
    bar_colors = [COLORS["purple"], COLORS["blue"], COLORS["amber"], COLORS["teal"], COLORS["pink"], COLORS["red"]]
    bar_colors = bar_colors[:len(rev_cat)]  # adjust to number of categories
    
    ax.bar(rev_cat.index, rev_cat.values, color=bar_colors)
    ax.set_ylabel("Revenue")
    ax.grid(axis="y")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig, use_container_width=False)

# =====================================================
# PIE CHART: Payment Method Distribution
# =====================================================
st.subheader("Payment Method Distribution")
payment_data = filtered_df["payment_method"].value_counts()
colors = [COLORS["teal"], COLORS["blue"], COLORS["amber"], COLORS["pink"]]
colors = colors[:len(payment_data)]

with col2:
    fig, ax = plt.subplots(figsize=(4,4))
    wedges, texts, autotexts = ax.pie(
        payment_data.values,
        labels=payment_data.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90
    )
    for t in texts + autotexts:
        t.set_color("#E5E7EB")
    st.pyplot(fig, use_container_width=False)

# =====================================================
# LINE CHART: Monthly Revenue Trend
# =====================================================
st.subheader("Monthly Revenue Trend")
monthly = filtered_df.set_index("purchase_date").resample("M")["total_purchase_amount"].sum()

fig, ax = plt.subplots(figsize=(6,3))
ax.plot(monthly.index, monthly.values, color=COLORS["blue"], marker="o")
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
ax.grid()
st.pyplot(fig, use_container_width=False)

# =====================================================
# DONUT CHART: Quantity Sold by Category
# =====================================================
st.subheader("Quantity Sold by Category")
qty = filtered_df.groupby("product_category")["quantity"].sum()
colors = [COLORS["purple"], COLORS["blue"], COLORS["amber"], COLORS["teal"]]
colors = colors[:len(qty)]

fig, ax = plt.subplots(figsize=(4,4))
wedges, texts, autotexts = ax.pie(
    qty.values,
    labels=qty.index,
    autopct="%1.1f%%",
    colors=colors,
    startangle=90
)
centre = plt.Circle((0, 0), 0.55, fc=COLORS["bg"])
ax.add_artist(centre)
for t in texts + autotexts:
    t.set_color("#E5E7EB")
st.pyplot(fig, use_container_width=False)

# =====================================================
# TABLE: Orders Data
# =====================================================
st.subheader("Orders Data")
st.dataframe(filtered_df, use_container_width=True)
