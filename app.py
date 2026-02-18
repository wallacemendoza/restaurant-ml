import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import load_data

# ─── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Bella Cucina · ML Dashboard",
    page_icon="🍝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=DM+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp { background-color: #0f0f13; color: #f1f1f3; }

    section[data-testid="stSidebar"] {
        background-color: #16161d;
        border-right: 1px solid #2a2a38;
    }

    .metric-card {
        background: #16161d;
        border: 1px solid #2a2a38;
        border-radius: 12px;
        padding: 20px 24px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .metric-card.amber::before { background: #f59e0b; }
    .metric-card.green::before { background: #10b981; }
    .metric-card.purple::before { background: #6366f1; }
    .metric-card.red::before    { background: #ef4444; }

    .metric-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #7c7c94; margin-bottom: 6px; }
    .metric-value { font-size: 32px; font-weight: 700; color: #f1f1f3; line-height: 1; }
    .metric-delta { font-size: 12px; margin-top: 6px; }
    .metric-delta.up   { color: #10b981; }
    .metric-delta.down { color: #ef4444; }

    .section-title {
        font-size: 18px; font-weight: 700;
        color: #f1f1f3; margin: 28px 0 4px;
        border-left: 3px solid #f59e0b;
        padding-left: 12px;
    }
    .section-sub { font-size: 13px; color: #7c7c94; margin-bottom: 20px; padding-left: 15px; }

    .insight-box {
        background: #1e1e28;
        border: 1px solid #2a2a38;
        border-left: 3px solid #f59e0b;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 13px;
        color: #c9d1d9;
    }
    .insight-box strong { color: #f59e0b; }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label { color: #7c7c94 !important; font-size: 12px !important; }

    .stPlotlyChart { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ───────────────────────────────────────────────
df_orders, df_items, df_menu = load_data()

# ─── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍝 Bella Cucina")
    st.markdown("<span style='color:#7c7c94;font-size:13px'>ML Analytics Dashboard</span>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<span style='color:#7c7c94;font-size:12px;text-transform:uppercase;letter-spacing:1px'>FILTERS</span>", unsafe_allow_html=True)

    categories = ["All"] + sorted(df_menu["category"].unique().tolist())
    selected_cat = st.selectbox("Category", categories)

    locations = ["All"] + sorted(df_orders["location"].unique().tolist())
    selected_loc = st.selectbox("Table Location", locations)

    min_orders = st.slider("Min orders to show", 1, 10, 1)

    st.divider()
    st.markdown("<span style='color:#7c7c94;font-size:11px'>Data: mock · mirrors restaurant_db schema<br>Switch to live DB in data.py</span>", unsafe_allow_html=True)

# ─── FILTER DATA ─────────────────────────────────────────────
filtered_items = df_items.copy()
if selected_cat != "All":
    filtered_items = filtered_items[filtered_items["category"] == selected_cat]
if selected_loc != "All":
    filtered_items = filtered_items[filtered_items["location"] == selected_loc]

# Aggregate per item
agg = (
    filtered_items.groupby(["menu_item_id", "item_name", "category", "price", "cost"])
    .agg(total_sold=("quantity", "sum"), total_revenue=("line_total", "sum"))
    .reset_index()
)
agg["total_profit"]  = (agg["price"] - agg["cost"]) * agg["total_sold"]
agg["margin_pct"]    = ((agg["price"] - agg["cost"]) / agg["price"] * 100).round(1)
agg["avg_per_order"] = (agg["total_revenue"] / agg["total_sold"]).round(2)
agg = agg[agg["total_sold"] >= min_orders].sort_values("total_revenue", ascending=False)

# ─── HEADER ──────────────────────────────────────────────────
st.markdown("## 📊 Menu Performance Analysis")
st.markdown("<span style='color:#7c7c94'>Best & worst selling items · profit margins · category breakdown</span>", unsafe_allow_html=True)
st.divider()

# ─── KPI CARDS ───────────────────────────────────────────────
total_revenue = agg["total_revenue"].sum()
total_profit  = agg["total_profit"].sum()
total_sold    = agg["total_sold"].sum()
avg_margin    = agg["margin_pct"].mean()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card amber">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">${total_revenue:,.0f}</div>
        <div class="metric-delta up">↑ filtered selection</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card green">
        <div class="metric-label">Total Profit</div>
        <div class="metric-value">${total_profit:,.0f}</div>
        <div class="metric-delta up">after food cost</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card purple">
        <div class="metric-label">Units Sold</div>
        <div class="metric-value">{int(total_sold):,}</div>
        <div class="metric-delta up">across all items</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card red">
        <div class="metric-label">Avg Margin</div>
        <div class="metric-value">{avg_margin:.1f}%</div>
        <div class="metric-delta {'up' if avg_margin > 60 else 'down'}">{'healthy' if avg_margin > 60 else 'watch this'}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── SECTION: TOP & BOTTOM PERFORMERS ───────────────────────
st.markdown('<div class="section-title">🏆 Top vs Bottom Performers</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Ranked by total revenue · use filters to drill into categories</div>', unsafe_allow_html=True)

top10    = agg.nlargest(10, "total_revenue")
bottom10 = agg.nsmallest(10, "total_revenue")

col_top, col_bot = st.columns(2)

PLOT_BG  = "#16161d"
PAPER_BG = "#0f0f13"
GRID_CLR = "#2a2a38"
TEXT_CLR = "#c9d1d9"

def base_layout(title):
    return dict(
        title=dict(text=title, font=dict(color=TEXT_CLR, size=14)),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_CLR, size=11),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
    )

with col_top:
    fig = go.Figure(go.Bar(
        x=top10["total_revenue"],
        y=top10["item_name"],
        orientation="h",
        marker=dict(color=top10["total_revenue"], colorscale="YlOrBr"),
        text=top10["total_revenue"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside", textfont=dict(color=TEXT_CLR, size=11),
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>"
    ))
    fig.update_layout(**base_layout("Top 10 by Revenue"), height=360)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with col_bot:
    fig2 = go.Figure(go.Bar(
        x=bottom10["total_revenue"],
        y=bottom10["item_name"],
        orientation="h",
        marker=dict(color=bottom10["total_revenue"], colorscale="RdPu"),
        text=bottom10["total_revenue"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside", textfont=dict(color=TEXT_CLR, size=11),
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>"
    ))
    fig2.update_layout(**base_layout("Bottom 10 by Revenue"), height=360)
    fig2.update_yaxes(autorange="reversed")
    st.plotly_chart(fig2, use_container_width=True)

# ─── SECTION: MARGIN BUBBLE CHART ────────────────────────────
st.markdown('<div class="section-title">💰 Revenue vs Profit Margin</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Bubble size = units sold · Sweet spot = top-right · Watch for high-revenue, low-margin items</div>', unsafe_allow_html=True)

fig3 = px.scatter(
    agg, x="total_revenue", y="margin_pct",
    size="total_sold", color="category",
    hover_name="item_name",
    hover_data={"total_sold": True, "total_revenue": ":,.0f", "margin_pct": ":.1f"},
    size_max=50,
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={"total_revenue": "Revenue ($)", "margin_pct": "Margin (%)", "total_sold": "Units Sold"}
)
fig3.update_layout(**base_layout(""), height=420,
    legend=dict(bgcolor="#16161d", bordercolor="#2a2a38", borderwidth=1))
fig3.add_hline(y=60, line_dash="dot", line_color="#f59e0b",
               annotation_text="60% margin target", annotation_font_color="#f59e0b")
st.plotly_chart(fig3, use_container_width=True)

# ─── SECTION: CATEGORY BREAKDOWN ─────────────────────────────
st.markdown('<div class="section-title">🗂️ Category Breakdown</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Revenue, profit and units by category</div>', unsafe_allow_html=True)

cat_agg = (
    agg.groupby("category")
    .agg(revenue=("total_revenue","sum"), profit=("total_profit","sum"),
         units=("total_sold","sum"), items=("item_name","count"))
    .reset_index()
    .sort_values("revenue", ascending=False)
)
cat_agg["margin"] = (cat_agg["profit"] / cat_agg["revenue"] * 100).round(1)

col_a, col_b = st.columns([1.4, 1])

with col_a:
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(name="Revenue", x=cat_agg["category"], y=cat_agg["revenue"],
        marker_color="#f59e0b",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>"))
    fig4.add_trace(go.Bar(name="Profit", x=cat_agg["category"], y=cat_agg["profit"],
        marker_color="#10b981",
        hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>"))
    fig4.update_layout(**base_layout("Revenue vs Profit by Category"),
        barmode="group", height=340,
        legend=dict(bgcolor="#16161d", bordercolor="#2a2a38"))
    st.plotly_chart(fig4, use_container_width=True)

with col_b:
    fig5 = px.pie(cat_agg, values="units", names="category",
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Bold)
    fig5.update_layout(**base_layout("Units Sold Share"), height=340,
        legend=dict(bgcolor="#16161d", bordercolor="#2a2a38", borderwidth=1))
    fig5.update_traces(textposition="inside", textinfo="percent+label",
                       hovertemplate="<b>%{label}</b><br>Units: %{value}<extra></extra>")
    st.plotly_chart(fig5, use_container_width=True)

# ─── SECTION: MARGIN RANKING TABLE ───────────────────────────
st.markdown('<div class="section-title">📋 Full Item Ranking</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Sortable · all items in filtered selection</div>', unsafe_allow_html=True)

display_df = agg[["item_name", "category", "price", "cost", "margin_pct",
                   "total_sold", "total_revenue", "total_profit"]].copy()
display_df.columns = ["Item", "Category", "Price", "Cost", "Margin %",
                      "Units Sold", "Revenue", "Profit"]
display_df["Price"]   = display_df["Price"].apply(lambda x: f"${x:.2f}")
display_df["Cost"]    = display_df["Cost"].apply(lambda x: f"${x:.2f}")
display_df["Revenue"] = display_df["Revenue"].apply(lambda x: f"${x:,.2f}")
display_df["Profit"]  = display_df["Profit"].apply(lambda x: f"${x:,.2f}")
display_df["Margin %"] = display_df["Margin %"].apply(lambda x: f"{x:.1f}%")

st.dataframe(display_df, use_container_width=True, height=400,
    column_config={"Margin %": st.column_config.TextColumn("Margin %")})

# ─── SECTION: INSIGHTS ───────────────────────────────────────
st.markdown('<div class="section-title">🧠 Auto Insights</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Generated from the current filtered data</div>', unsafe_allow_html=True)

best_revenue = agg.iloc[0]
best_margin  = agg.nlargest(1, "margin_pct").iloc[0]
worst        = agg.nsmallest(1, "total_revenue").iloc[0]
risky        = agg[(agg["total_revenue"] > agg["total_revenue"].quantile(0.6)) & (agg["margin_pct"] < 50)]

st.markdown(f"""
<div class="insight-box">💰 <strong>{best_revenue['item_name']}</strong> is your top revenue generator 
at <strong>${best_revenue['total_revenue']:,.0f}</strong> with {int(best_revenue['total_sold'])} units sold.</div>

<div class="insight-box">📈 <strong>{best_margin['item_name']}</strong> has the highest margin at 
<strong>{best_margin['margin_pct']:.1f}%</strong> — consider promoting it more aggressively.</div>

<div class="insight-box">⚠️ <strong>{worst['item_name']}</strong> is your lowest performer 
with only <strong>${worst['total_revenue']:,.0f}</strong> in revenue — consider a promotion or menu refresh.</div>
{"<div class='insight-box'>🔴 <strong>" + str(len(risky)) + " item(s)</strong> generate solid revenue but have margins below 50% — review food costs for: <strong>" + ", ".join(risky["item_name"].tolist()[:3]) + "</strong>.</div>" if len(risky) > 0 else ""}
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
