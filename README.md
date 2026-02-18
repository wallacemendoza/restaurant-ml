# 🍝 Bella Cucina · ML Dashboard

> A data science layer on top of [restaurant-db](https://github.com/wallacemendoza/restaurant-db) — built with Python, Pandas, Streamlit and Plotly.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

**[🚀 Live App →](https://your-app.streamlit.app)**

---

## What This Does

The [restaurant-db](https://github.com/wallacemendoza/restaurant-db) project models the database. This project **analyzes it** — turning raw order and menu data into actionable insights about which items are driving revenue, which ones look good on paper but kill your margins, and what the data automatically tells you about your menu.

---

## Features

- **Top & Bottom performers** — ranked by revenue with drill-down by category and table location
- **Revenue vs Margin bubble chart** — spot high-revenue/low-margin danger zones instantly
- **Category breakdown** — grouped bar + donut chart showing revenue, profit and units by section
- **Full sortable item table** — every metric in one view
- **Auto-generated insights** — written conclusions pulled directly from the data
- **Sidebar filters** — category, table location, minimum order threshold

---

## Stack

| Layer | Tech |
|---|---|
| App framework | Streamlit |
| Data manipulation | Pandas + NumPy |
| Visualizations | Plotly (bar, scatter, pie, subplots) |
| Database (optional) | PostgreSQL via psycopg2 |
| Deployment | Streamlit Cloud |

---

## Run Locally

```bash
# 1. Clone
git clone https://github.com/wallacemendoza/restaurant-ml.git
cd restaurant-ml

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
# → http://localhost:8501
```

---

## Connect to Real PostgreSQL

This app ships with realistic mock data that mirrors the `restaurant_db` schema exactly. To switch to your real database, open `data.py` and change two lines:

```python
USE_REAL_DB  = True                                          # line 14
DATABASE_URL = "postgresql://postgres:yourpw@localhost/restaurant_db"  # line 15
```

That's it. Column names and types are identical to the mock data so nothing else changes.

---

## Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select this repo → `app.py`
4. Hit **Deploy** — live in ~60 seconds

For the real DB on Streamlit Cloud, add your connection string under **Settings → Secrets**:
```toml
# .streamlit/secrets.toml
DATABASE_URL = "postgresql://user:password@host/restaurant_db"
```
Then in `data.py` reference it as:
```python
import streamlit as st
DATABASE_URL = st.secrets["DATABASE_URL"]
```

---

## Related Project

This dashboard is the data science companion to **[restaurant-db](https://github.com/wallacemendoza/restaurant-db)** — a PostgreSQL portfolio project with 13 normalized tables, stored procedures, window functions and a static HTML analytics dashboard.
