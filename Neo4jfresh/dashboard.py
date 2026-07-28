import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from neo4j import GraphDatabase
import re
from collections import Counter
from datetime import datetime, timedelta

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Restaurant Chain Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── DARK PREMIUM CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background-color: #0a0e1a; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0f172a,#1e293b); border-right:1px solid #334155; }
[data-testid="stSidebar"] * { color:#e2e8f0 !important; }
.kpi-card {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    border: 1px solid #334155; border-radius:14px;
    padding:20px 24px; text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);
    transition: transform 0.2s ease;
}
.kpi-card:hover { transform:translateY(-3px); }
.kpi-title { color:#94a3b8; font-size:13px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:6px; }
.kpi-value { color:#f1f5f9; font-size:32px; font-weight:700; }
.kpi-delta { font-size:12px; margin-top:4px; }
.kpi-pos { color:#22c55e; } .kpi-neg { color:#ef4444; } .kpi-neu { color:#94a3b8; }
.alert-banner {
    background: linear-gradient(90deg,#7f1d1d,#991b1b);
    border:1px solid #ef4444; border-radius:10px;
    padding:12px 20px; margin-bottom:16px;
    color:#fca5a5; font-weight:600; font-size:14px;
}
.section-header { color:#e2e8f0; font-size:20px; font-weight:700; margin:16px 0 10px 0; padding-bottom:6px; border-bottom:2px solid #334155; }
.badge-pos { background:#14532d; color:#86efac; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600; }
.badge-neg { background:#7f1d1d; color:#fca5a5; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600; }
.badge-neu { background:#1e3a5f; color:#93c5fd; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600; }
stTabs [data-baseweb="tab"] { color:#94a3b8; font-weight:600; }
stTabs [aria-selected="true"] { color:#38bdf8; border-bottom-color:#38bdf8; }
</style>
""", unsafe_allow_html=True)

# ─── NEO4J CONNECTION ───────────────────────────────────────────────────────
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"

@st.cache_resource
def get_driver():
    return GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def run_query(query, params=None):
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(query, params or {})
            return [r.data() for r in result]
    except Exception as e:
        st.error(f"DB Error: {e}")
        return []

# ─── FOOD CATEGORY MAP ──────────────────────────────────────────────────────
FOOD_CATEGORIES = {
    "Chicken Items": ["chicken biryani","butter chicken","chicken curry","kadai chicken","chicken tikka","tandoori chicken","grilled chicken","fried chicken","chicken 65","chicken kebab","chicken wings","chicken burger","chicken shawarma","chicken fried rice","chicken noodles","chilli chicken","dragon chicken","pepper chicken"],
    "Mutton Items": ["mutton biryani","mutton curry","mutton rogan josh","mutton masala","mutton keema","mutton haleem","mutton kebab","mutton soup","mutton thali","mutton mandi"],
    "Fried Rice": ["fried rice","jeera rice","steam rice","plain rice","curd rice","veg pulao","coconut rice","egg biryani","veg biryani","paneer biryani","chicken fried rice","bagara rice"],
    "Noodles": ["hakka noodles","schezwan noodles","garlic noodles","veg noodles","chicken noodles","egg noodles","ramen noodles","alfredo pasta","white sauce pasta","red sauce pasta","penne pasta","spaghetti"],
    "Desserts": ["ice cream","gulab jamun","kheer","apricot pudding","brownie","chocolate cake","lassi","butter milk","shikanji"],
    "Chats & Snacks": ["crispy corn","corn cheese balls","chilli paneer","spring roll","manchurian","gobi manchurian","nachos","french fries","potato wedges","paneer 65","fish fry","fish fingers"],
    "Meals": ["veg thali","mutton thali","chicken platter","paneer butter masala","dal makhani","dal tadka","chole","mix veg","veg combo","rajma chawal"],
    "Other": ["soup","manchow soup","sweet corn soup","hot and sour soup","tomato soup","butter naan","garlic naan","tandoori roti","paratha","pizza","burger"],
}

def get_food_category(food_name):
    food_lower = food_name.lower()
    for cat, items in FOOD_CATEGORIES.items():
        if any(item in food_lower or food_lower in item for item in items):
            return cat
    return "Other"

# ─── CACHED DATA FETCHERS ────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_all_restaurants():
    r = run_query("MATCH (r:Restaurant) RETURN r.name as name ORDER BY r.name")
    return [x["name"] for x in r if x.get("name")]

@st.cache_data(ttl=300)
def fetch_kpi_data():
    return run_query("""
        MATCH (r:Review)
        OPTIONAL MATCH (r)-[:HAS_SENTIMENT]->(s:Sentiment)
        RETURN
            count(r) as total_reviews,
            avg(r.rating) as avg_rating,
            sum(CASE WHEN s.type='Positive' THEN 1 ELSE 0 END) as positive,
            sum(CASE WHEN s.type='Negative' THEN 1 ELSE 0 END) as negative,
            sum(CASE WHEN s.type='Neutral'  THEN 1 ELSE 0 END) as neutral
    """)

@st.cache_data(ttl=300)
def fetch_best_worst():
    best = run_query("""
        MATCH (res:Restaurant)<-[:FOR]-(r:Review)
        WITH res.name as name, avg(r.rating) as avg_r, count(r) as cnt
        WHERE cnt >= 3
        RETURN name, round(avg_r,2) as avg_rating, cnt
        ORDER BY avg_r DESC LIMIT 1
    """)
    worst = run_query("""
        MATCH (res:Restaurant)<-[:FOR]-(r:Review)
        WITH res.name as name, avg(r.rating) as avg_r, count(r) as cnt
        WHERE cnt >= 3
        RETURN name, round(avg_r,2) as avg_rating, cnt
        ORDER BY avg_r ASC LIMIT 1
    """)
    return best, worst

@st.cache_data(ttl=300)
def fetch_branch_performance():
    return run_query("""
        MATCH (res:Restaurant)<-[:FOR]-(r:Review)
        OPTIONAL MATCH (r)-[:HAS_SENTIMENT]->(s:Sentiment)
        WITH res.name as restaurant,
             avg(r.rating) as avg_rating,
             count(r) as total_orders,
             sum(CASE WHEN s.type='Positive' THEN 1 ELSE 0 END) as positive,
             sum(CASE WHEN s.type='Negative' THEN 1 ELSE 0 END) as negative
        RETURN restaurant, round(avg_rating,2) as avg_rating, total_orders,
               positive, negative
        ORDER BY avg_rating DESC
    """)

@st.cache_data(ttl=300)
def fetch_rating_distribution():
    return run_query("""
        MATCH (r:Review)
        WHERE r.rating IS NOT NULL
        RETURN toInteger(r.rating) as rating, count(r) as count
        ORDER BY rating
    """)

@st.cache_data(ttl=300)
def fetch_monthly_trends():
    return run_query("""
        MATCH (r:Review)
        WHERE r.date IS NOT NULL AND r.date <> 'Unknown'
        WITH substring(toString(r.date),0,7) as month, count(r) as count
        RETURN month, count ORDER BY month
    """)

@st.cache_data(ttl=300)
def fetch_daily_trends():
    return run_query("""
        MATCH (r:Review)
        WHERE r.date IS NOT NULL AND r.date <> 'Unknown'
        WITH date(r.date) as d, count(r) as count
        RETURN d.dayOfWeek as day_num, count ORDER BY day_num
    """)

@st.cache_data(ttl=300)
def fetch_weekly_trends():
    return run_query("""
        MATCH (r:Review)
        WHERE r.date IS NOT NULL AND r.date <> 'Unknown'
        WITH date(r.date) as d, count(r) as count
        RETURN d.week as week, d.year as year, count
        ORDER BY year, week
    """)

@st.cache_data(ttl=300)
def fetch_date_heatmap():
    return run_query("""
        MATCH (r:Review)
        WHERE r.date IS NOT NULL AND r.date <> 'Unknown'
        RETURN r.date as date, count(r) as count
        ORDER BY count DESC LIMIT 30
    """)

@st.cache_data(ttl=300)
def fetch_sentiment_data():
    return run_query("""
        MATCH (r:Review)-[:HAS_SENTIMENT]->(s:Sentiment)
        RETURN s.type as sentiment, count(r) as count
    """)

@st.cache_data(ttl=300)
def fetch_food_mentions():
    return run_query("""
        MATCH (f:Food)<-[:MENTIONS]-(r:Review)
        RETURN f.name as food, count(r) as mentions
        ORDER BY mentions DESC LIMIT 50
    """)

@st.cache_data(ttl=300)
def fetch_food_trends():
    return run_query("""
        MATCH (f:Food)<-[:MENTIONS]-(r:Review)
        WHERE r.date IS NOT NULL AND r.date <> 'Unknown'
        WITH f.name as food, substring(r.date,0,7) as month, count(r) as count
        RETURN food, month, count
        ORDER BY month
    """)

@st.cache_data(ttl=300)
def fetch_all_reviews():
    return run_query("""
        MATCH (r:Review)-[:FOR]->(res:Restaurant)
        OPTIONAL MATCH (r)-[:HAS_SENTIMENT]->(s:Sentiment)
        RETURN res.name as restaurant,
               r.rating as rating,
               r.date as date,
               r.time as time,
               r.text as review,
               s.type as sentiment
        ORDER BY r.date DESC LIMIT 500
    """)

@st.cache_data(ttl=300)
def fetch_rating_alerts():
    return run_query("""
        MATCH (res:Restaurant)<-[:FOR]-(r:Review)
        WITH res.name as name, avg(r.rating) as avg_r, count(r) as cnt
        WHERE avg_r < 2.0 AND cnt >= 3
        RETURN name, round(avg_r,2) as avg_rating, cnt
        ORDER BY avg_r ASC
    """)

@st.cache_data(ttl=300)
def fetch_filtered_reviews(restaurants):
    if not restaurants:
        return fetch_all_reviews()
    return run_query("""
        MATCH (r:Review)-[:FOR]->(res:Restaurant)
        WHERE res.name IN $restaurants
        OPTIONAL MATCH (r)-[:HAS_SENTIMENT]->(s:Sentiment)
        RETURN res.name as restaurant, r.rating as rating,
               r.date as date, r.time as time,
               r.text as review, s.type as sentiment
        ORDER BY r.date DESC
    """, {"restaurants": restaurants})

# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────

def make_kpi_html(title, value, delta="", delta_type="neu"):
    delta_html = f'<div class="kpi-delta kpi-{delta_type}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""

def parse_time_bucket(time_str):
    if not time_str or time_str == "Unknown":
        return "Unknown"
    try:
        t = datetime.strptime(time_str.strip(), "%H:%M")
        h = t.hour
        if 6 <= h < 12: return "Morning"
        elif 12 <= h < 17: return "Afternoon"
        elif 17 <= h < 21: return "Evening"
        else: return "Night"
    except:
        tl = str(time_str).lower()
        if "morning" in tl: return "Morning"
        if "afternoon" in tl or "lunch" in tl: return "Afternoon"
        if "evening" in tl or "dinner" in tl: return "Evening"
        if "night" in tl: return "Night"
        return "Unknown"

def extract_keywords(reviews_list):
    complaint_words = ["slow","cold","bad","dirty","rude","wait","delay","tasteless","undercooked",
                       "overpriced","stale","unhygienic","noisy","poor","awful","worst","disappointed",
                       "unclean","late","missing","wrong","burnt","salty","bland","hard","tough"]
    counter = Counter()
    for rev in reviews_list:
        if not isinstance(rev, str): continue
        words = re.findall(r'\b[a-z]+\b', rev.lower())
        for w in words:
            if w in complaint_words:
                counter[w] += 1
    return counter

def categorize_issue(word):
    food_words = {"cold","tasteless","undercooked","stale","bland","salty","burnt","hard","tough","overcooked"}
    service_words = {"slow","rude","wait","delay","late","missing","wrong","poor","awful"}
    clean_words = {"dirty","unclean","unhygienic","noisy"}
    if word in food_words: return "Food Quality"
    if word in service_words: return "Service"
    if word in clean_words: return "Cleanliness"
    return "Other"

def build_wordcloud_fig(text_list):
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        import io, base64
        STOP = {"the","and","was","for","this","that","with","have","had","very","are","but",
                "not","all","were","from","they","their","our","its","been","has","also",
                "we","it","is","to","a","in","of","i","my","me","he","she","so","on","at",
                "an","be","as","by","or","do","if","up","no","go","us","am","than","then","too"}
        combined = " ".join([str(r) for r in text_list if isinstance(r, str)])
        wc = WordCloud(width=800, height=350, background_color="#0f172a",
                       colormap="cool", stopwords=STOP, max_words=80,
                       font_path=None).generate(combined)
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#0f172a")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", facecolor="#0f172a")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()
        plt.close()
        return f'<img src="data:image/png;base64,{img_b64}" style="width:100%;border-radius:12px;">'
    except ImportError:
        return '<div style="color:#94a3b8;padding:20px;">Install wordcloud: <code>pip install wordcloud matplotlib</code></div>'

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="#0f172a",
    plot_bgcolor="#0f172a",
    font=dict(color="#e2e8f0", family="Inter"),
    margin=dict(l=20, r=20, t=40, b=20),
)
COLOR_SEQ = ["#38bdf8","#818cf8","#34d399","#fb923c","#f472b6","#a78bfa","#facc15","#4ade80"]

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
all_restaurants = fetch_all_restaurants()

with st.sidebar:
    st.markdown("## 🍽️ Restaurant Analytics")
    st.markdown("---")

    st.markdown("### 🏢 Restaurant Filter")
    select_all = st.checkbox("Select All Branches", value=True)
    if select_all:
        selected_restaurants = all_restaurants
    else:
        selected_restaurants = st.multiselect(
            "Choose Branches",
            options=all_restaurants,
            default=all_restaurants[:5] if all_restaurants else [],
            help="Select one or more restaurant branches"
        )

    st.markdown("### ⭐ Rating Filter")
    rating_range = st.slider("Rating Range", 1, 5, (1, 5))

    st.markdown("### 🍕 Food Category")
    selected_categories = st.multiselect(
        "Categories",
        options=list(FOOD_CATEGORIES.keys()),
        default=list(FOOD_CATEGORIES.keys()),
    )

    st.markdown("### 📅 Date Range")
    date_filter = st.selectbox("Period", ["All Time", "Last 7 Days", "Last 30 Days", "Last 3 Months"])

    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"<div style='color:#475569;font-size:11px;margin-top:16px;'>Branches loaded: {len(all_restaurants)}</div>", unsafe_allow_html=True)

# ─── ALERT BANNER ───────────────────────────────────────────────────────────
alert_branches = fetch_rating_alerts()
if alert_branches:
    names = ", ".join([f"{b['name']} ({b['avg_rating']}⭐)" for b in alert_branches])
    st.markdown(f'<div class="alert-banner">🚨 ALERT: Low Rating Detected! — {names} — Immediate attention required!</div>', unsafe_allow_html=True)

# ─── TITLE ──────────────────────────────────────────────────────────────────
st.markdown("# 🍽️ Restaurant Chain Analytics Dashboard")
st.markdown(f"<div style='color:#64748b;margin-bottom:16px;'>Showing data for <b style='color:#38bdf8'>{len(selected_restaurants)} branch(es)</b></div>", unsafe_allow_html=True)

# ─── FETCH FILTERED DATA ────────────────────────────────────────────────────
reviews_raw = fetch_filtered_reviews(selected_restaurants if not select_all else [])
df = pd.DataFrame(reviews_raw) if reviews_raw else pd.DataFrame()

if not df.empty:
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df[df["rating"].between(rating_range[0], rating_range[1])]
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        now = pd.Timestamp.now()
        if date_filter == "Last 7 Days":
            df = df[df["date"] >= now - pd.Timedelta(days=7)]
        elif date_filter == "Last 30 Days":
            df = df[df["date"] >= now - pd.Timedelta(days=30)]
        elif date_filter == "Last 3 Months":
            df = df[df["date"] >= now - pd.Timedelta(days=90)]

# ─── TABS ────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 KPIs",
    "🏢 Branch Performance",
    "⭐ Rating Analysis",
    "📅 Time Analysis",
    "🍽️ Food Categories",
    "🥘 Food Items",
    "💬 Sentiment",
    "⚠️ Issue Detection",
    "⏰ Peak Time",
    "📋 Reviews",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — KPIs
# ════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    kpi_data = fetch_kpi_data()
    best_res, worst_res = fetch_best_worst()

    if kpi_data:
        k = kpi_data[0]
        total = k.get("total_reviews", 0) or 0
        avg_r = k.get("avg_rating") or 0
        pos = k.get("positive", 0) or 0
        neg = k.get("negative", 0) or 0
        neu = k.get("neutral", 0) or 0
        pct_pos = round(pos / total * 100, 1) if total else 0
        pct_neg = round(neg / total * 100, 1) if total else 0

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        cols = [c1, c2, c3, c4, c5, c6]
        cards = [
            ("Total Reviews",   f"{total:,}",       "All time",         "neu"),
            ("Avg Rating",      f"{avg_r:.2f} ⭐",   "Out of 5.0",       "pos" if avg_r >= 4 else "neg"),
            ("Positive Reviews",f"{pct_pos}%",       f"{pos:,} reviews",  "pos"),
            ("Negative Reviews",f"{pct_neg}%",       f"{neg:,} reviews",  "neg"),
            ("Total Orders",    f"{total:,}",        "Review-based",      "neu"),
            ("Branches",        f"{len(all_restaurants)}",  "Active branches","neu"),
        ]
        for col, (title, val, delta, dtype) in zip(cols, cards):
            with col:
                st.markdown(make_kpi_html(title, val, delta, dtype), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_best, col_worst = st.columns(2)
    with col_best:
        st.markdown('<div class="section-header">🏆 Best Performing Branch</div>', unsafe_allow_html=True)
        if best_res:
            b = best_res[0]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#052e16,#14532d);border:1px solid #22c55e;border-radius:12px;padding:20px;">
                <div style="color:#86efac;font-size:22px;font-weight:700;">🥇 {b['name']}</div>
                <div style="color:#4ade80;font-size:16px;margin-top:8px;">Rating: {b['avg_rating']} ⭐  |  Reviews: {b['cnt']:,}</div>
            </div>""", unsafe_allow_html=True)

    with col_worst:
        st.markdown('<div class="section-header">📉 Worst Performing Branch</div>', unsafe_allow_html=True)
        if worst_res:
            w = worst_res[0]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#450a0a,#7f1d1d);border:1px solid #ef4444;border-radius:12px;padding:20px;">
                <div style="color:#fca5a5;font-size:22px;font-weight:700;">⚠️ {w['name']}</div>
                <div style="color:#f87171;font-size:16px;margin-top:8px;">Rating: {w['avg_rating']} ⭐  |  Reviews: {w['cnt']:,}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 Monthly Growth Trend</div>', unsafe_allow_html=True)
    monthly = fetch_monthly_trends()
    if monthly:
        df_m = pd.DataFrame(monthly)
        fig = px.area(df_m, x="month", y="count", color_discrete_sequence=["#38bdf8"],
                      labels={"month": "Month", "count": "Review Volume"})
        fig.update_layout(**PLOTLY_DARK)
        fig.update_traces(fill='tozeroy', line=dict(width=2))
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — BRANCH PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    branch_data = fetch_branch_performance()
    if branch_data:
        df_branch = pd.DataFrame(branch_data)
        if selected_restaurants and not select_all:
            df_branch = df_branch[df_branch["restaurant"].isin(selected_restaurants)]

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-header">⭐ Avg Rating by Branch</div>', unsafe_allow_html=True)
            df_plot = df_branch.sort_values("avg_rating", ascending=True).tail(20)
            fig = px.bar(df_plot, x="avg_rating", y="restaurant", orientation="h",
                         color="avg_rating", color_continuous_scale="RdYlGn",
                         range_color=[1, 5],
                         labels={"avg_rating": "Avg Rating", "restaurant": "Branch"})
            fig.update_layout(**PLOTLY_DARK, height=500)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">📦 Total Orders by Branch</div>', unsafe_allow_html=True)
            df_plot2 = df_branch.sort_values("total_orders", ascending=True).tail(20)
            fig2 = px.bar(df_plot2, x="total_orders", y="restaurant", orientation="h",
                          color="total_orders", color_continuous_scale="Blues",
                          labels={"total_orders": "Orders", "restaurant": "Branch"})
            fig2.update_layout(**PLOTLY_DARK, height=500)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        top_col, bot_col = st.columns(2)

        with top_col:
            st.markdown('<div class="section-header">🏆 Top 10 Branches</div>', unsafe_allow_html=True)
            top10 = df_branch.head(10)[["restaurant", "avg_rating", "total_orders", "positive"]].reset_index(drop=True)
            top10.index += 1
            st.dataframe(top10.style.background_gradient(subset=["avg_rating"], cmap="Greens"),
                         use_container_width=True)

        with bot_col:
            st.markdown('<div class="section-header">📉 Bottom 10 Branches</div>', unsafe_allow_html=True)
            bot10 = df_branch.tail(10)[["restaurant", "avg_rating", "total_orders", "negative"]].reset_index(drop=True)
            bot10.index += 1
            st.dataframe(bot10.style.background_gradient(subset=["avg_rating"], cmap="Reds_r"),
                         use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — RATING ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    dist_data = fetch_rating_distribution()

    col_hist, col_donut = st.columns(2)
    with col_hist:
        st.markdown('<div class="section-header">📊 Rating Distribution (1–5)</div>', unsafe_allow_html=True)
        if dist_data:
            df_dist = pd.DataFrame(dist_data)
            df_dist["label"] = df_dist["rating"].astype(str) + " ⭐"
            fig = px.bar(df_dist, x="label", y="count",
                         color="rating", color_continuous_scale="RdYlGn",
                         range_color=[1, 5],
                         labels={"label": "Rating", "count": "Reviews"})
            fig.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    with col_donut:
        st.markdown('<div class="section-header">🍩 Rating Share</div>', unsafe_allow_html=True)
        if dist_data:
            df_dist2 = pd.DataFrame(dist_data)
            df_dist2["label"] = df_dist2["rating"].astype(str) + " Star"
            fig2 = px.pie(df_dist2, values="count", names="label", hole=0.5,
                          color_discrete_sequence=COLOR_SEQ)
            fig2.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">📈 Rating Trends Over Time</div>', unsafe_allow_html=True)
    trend_tab = st.radio("View by:", ["Monthly", "Weekly", "Daily"], horizontal=True, key="rating_trend")

    if trend_tab == "Monthly":
        data = fetch_monthly_trends()
        if data:
            df_t = pd.DataFrame(data)
            fig = px.line(df_t, x="month", y="count", markers=True,
                          color_discrete_sequence=["#38bdf8"],
                          labels={"month": "Month", "count": "Reviews"})
            fig.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    elif trend_tab == "Weekly":
        data = fetch_weekly_trends()
        if data:
            df_t = pd.DataFrame(data)
            df_t["period"] = df_t["year"].astype(str) + "-W" + df_t["week"].astype(str).str.zfill(2)
            fig = px.line(df_t, x="period", y="count", markers=True,
                          color_discrete_sequence=["#818cf8"],
                          labels={"period": "Week", "count": "Reviews"})
            fig.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    elif trend_tab == "Daily":
        data = fetch_daily_trends()
        if data:
            df_t = pd.DataFrame(data)
            day_map = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
            df_t["day"] = df_t["day_num"].map(day_map)
            fig = px.bar(df_t, x="day", y="count",
                         color="count", color_continuous_scale="Teal",
                         labels={"day": "Day", "count": "Reviews"})
            fig.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — TIME ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-header">📅 Orders Over Time</div>', unsafe_allow_html=True)
    time_view = st.radio("Granularity:", ["Monthly", "Weekly", "Daily Weekday"], horizontal=True, key="time_view")

    if time_view == "Monthly":
        data = fetch_monthly_trends()
        if data:
            df_t = pd.DataFrame(data)
            fig = px.area(df_t, x="month", y="count", color_discrete_sequence=["#34d399"],
                          labels={"month": "Month", "count": "Orders"})
            fig.update_layout(**PLOTLY_DARK)
            fig.update_traces(fill="tozeroy")
            st.plotly_chart(fig, use_container_width=True)

    elif time_view == "Weekly":
        data = fetch_weekly_trends()
        if data:
            df_t = pd.DataFrame(data)
            df_t["period"] = df_t["year"].astype(str) + "-W" + df_t["week"].astype(str).str.zfill(2)
            fig = px.bar(df_t, x="period", y="count", color_discrete_sequence=["#818cf8"],
                         labels={"period": "Week", "count": "Orders"})
            fig.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    elif time_view == "Daily Weekday":
        data = fetch_daily_trends()
        if data:
            df_t = pd.DataFrame(data)
            day_map = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
            df_t["day"] = df_t["day_num"].map(day_map)
            df_t["is_weekend"] = df_t["day_num"].isin([6, 7])
            df_t["type"] = df_t["is_weekend"].map({True: "Weekend", False: "Weekday"})
            fig = px.bar(df_t, x="day", y="count", color="type",
                         color_discrete_map={"Weekend": "#f472b6", "Weekday": "#38bdf8"},
                         labels={"day": "Day", "count": "Orders"})
            fig.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    # Weekday vs Weekend
    st.markdown('<div class="section-header">📊 Weekday vs Weekend Comparison</div>', unsafe_allow_html=True)
    daily_d = fetch_daily_trends()
    if daily_d:
        df_dw = pd.DataFrame(daily_d)
        weekday_total = int(df_dw[df_dw["day_num"].isin([1,2,3,4,5])]["count"].sum())
        weekend_total = int(df_dw[df_dw["day_num"].isin([6,7])]["count"].sum())
        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            st.markdown(make_kpi_html("Weekday Orders", f"{weekday_total:,}", "Mon-Fri", "neu"), unsafe_allow_html=True)
        with wc2:
            st.markdown(make_kpi_html("Weekend Orders", f"{weekend_total:,}", "Sat-Sun", "pos"), unsafe_allow_html=True)
        with wc3:
            ratio = round(weekend_total / weekday_total * 100, 1) if weekday_total else 0
            st.markdown(make_kpi_html("Weekend Lift", f"{ratio}%", "vs weekday avg", "pos" if ratio > 100 else "neg"), unsafe_allow_html=True)

    # Peak dates
    st.markdown('<div class="section-header">🔥 Top Peak Dates</div>', unsafe_allow_html=True)
    peak_data = fetch_date_heatmap()
    if peak_data:
        df_peak = pd.DataFrame(peak_data).head(10)
        fig = px.bar(df_peak, x="date", y="count", color="count",
                     color_continuous_scale="Hot",
                     labels={"date": "Date", "count": "Orders"})
        fig.update_layout(**PLOTLY_DARK)
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — FOOD CATEGORIES
# ════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    food_data = fetch_food_mentions()
    if food_data:
        df_food = pd.DataFrame(food_data)
        df_food["category"] = df_food["food"].apply(get_food_category)

        if selected_categories:
            df_food = df_food[df_food["category"].isin(selected_categories)]

        cat_summary = df_food.groupby("category")["mentions"].sum().reset_index()
        cat_summary = cat_summary.sort_values("mentions", ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">🍕 Orders by Category</div>', unsafe_allow_html=True)
            fig = px.bar(cat_summary, x="mentions", y="category", orientation="h",
                         color="category", color_discrete_sequence=COLOR_SEQ,
                         labels={"mentions": "Mentions", "category": "Category"})
            fig.update_layout(**PLOTLY_DARK, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">🥧 Category Contribution</div>', unsafe_allow_html=True)
            fig2 = px.pie(cat_summary, values="mentions", names="category", hole=0.4,
                          color_discrete_sequence=COLOR_SEQ)
            fig2.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-header">🗺️ Category Treemap</div>', unsafe_allow_html=True)
        fig3 = px.treemap(df_food, path=["category", "food"], values="mentions",
                          color="mentions", color_continuous_scale="Teal")
        fig3.update_layout(**PLOTLY_DARK, height=450)
        st.plotly_chart(fig3, use_container_width=True)

        # Most popular category KPI
        if not cat_summary.empty:
            top_cat = cat_summary.iloc[0]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);border:1px solid #38bdf8;border-radius:12px;padding:16px;margin-top:8px;">
                <span style="color:#94a3b8;">🏆 Most Popular Category: </span>
                <span style="color:#38bdf8;font-size:20px;font-weight:700;">{top_cat['category']}</span>
                <span style="color:#94a3b8;margin-left:16px;">{int(top_cat['mentions']):,} mentions</span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — FOOD ITEMS
# ════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    food_data = fetch_food_mentions()
    if food_data:
        df_food_all = pd.DataFrame(food_data)

        col_top, col_bot = st.columns(2)
        with col_top:
            st.markdown('<div class="section-header">🔝 Top 10 Most Ordered Items</div>', unsafe_allow_html=True)
            top10 = df_food_all.head(10)
            fig = px.bar(top10, x="mentions", y="food", orientation="h",
                         color="mentions", color_continuous_scale="Viridis",
                         labels={"mentions": "Mentions", "food": "Item"})
            fig.update_layout(**PLOTLY_DARK, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        with col_bot:
            st.markdown('<div class="section-header">📉 Least Ordered Items</div>', unsafe_allow_html=True)
            least10 = df_food_all.tail(10).sort_values("mentions")
            fig2 = px.bar(least10, x="mentions", y="food", orientation="h",
                          color="mentions", color_continuous_scale="Reds",
                          labels={"mentions": "Mentions", "food": "Item"})
            fig2.update_layout(**PLOTLY_DARK, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-header">📈 Item Demand Trend Over Time</div>', unsafe_allow_html=True)
        trend_data = fetch_food_trends()
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            # Show top 5 food items trend
            top5_foods = df_food_all.head(5)["food"].tolist()
            df_trend_top = df_trend[df_trend["food"].isin(top5_foods)]
            if not df_trend_top.empty:
                fig3 = px.line(df_trend_top, x="month", y="count", color="food",
                               markers=True, color_discrete_sequence=COLOR_SEQ,
                               labels={"month": "Month", "count": "Mentions", "food": "Item"})
                fig3.update_layout(**PLOTLY_DARK)
                st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 7 — SENTIMENT & WORD CLOUD
# ════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    sent_data = fetch_sentiment_data()
    col_sent, col_wc = st.columns([1, 2])

    with col_sent:
        st.markdown('<div class="section-header">😊 Sentiment Breakdown</div>', unsafe_allow_html=True)
        if sent_data:
            df_sent = pd.DataFrame(sent_data)
            fig = px.pie(df_sent, values="count", names="sentiment", hole=0.5,
                         color="sentiment",
                         color_discrete_map={"Positive": "#22c55e", "Negative": "#ef4444", "Neutral": "#38bdf8"})
            fig.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

            for _, row in df_sent.iterrows():
                badge = {"Positive": "pos", "Negative": "neg", "Neutral": "neu"}.get(row["sentiment"], "neu")
                st.markdown(f'<span class="badge-{badge}">{row["sentiment"]}: {int(row["count"]):,}</span><br>', unsafe_allow_html=True)

    with col_wc:
        st.markdown('<div class="section-header">☁️ Word Cloud — Common Topics</div>', unsafe_allow_html=True)
        all_reviews_raw = fetch_all_reviews()
        if all_reviews_raw:
            review_texts = [r.get("review", "") for r in all_reviews_raw]
            wc_html = build_wordcloud_fig(review_texts)
            st.markdown(wc_html, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📢 Frequent Complaint Keywords</div>', unsafe_allow_html=True)
    if all_reviews_raw:
        texts = [r.get("review", "") for r in all_reviews_raw]
        kw_counter = extract_keywords(texts)
        if kw_counter:
            df_kw = pd.DataFrame(kw_counter.most_common(15), columns=["keyword", "frequency"])
            fig4 = px.bar(df_kw, x="frequency", y="keyword", orientation="h",
                          color="frequency", color_continuous_scale="Reds",
                          labels={"frequency": "Frequency", "keyword": "Complaint Word"})
            fig4.update_layout(**PLOTLY_DARK, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 8 — ISSUE DETECTION
# ════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown('<div class="section-header">⚠️ Detected Issues by Category</div>', unsafe_allow_html=True)
    all_reviews_raw = fetch_all_reviews()
    if all_reviews_raw:
        texts = [r.get("review", "") for r in all_reviews_raw]
        kw_counter = extract_keywords(texts)

        issue_rows = []
        for word, freq in kw_counter.most_common(30):
            cat = categorize_issue(word)
            issue_rows.append({"keyword": word, "frequency": freq, "issue_category": cat})

        if issue_rows:
            df_issues = pd.DataFrame(issue_rows)

            col_i1, col_i2 = st.columns(2)
            with col_i1:
                fig = px.bar(df_issues, x="frequency", y="keyword", orientation="h",
                             color="issue_category",
                             color_discrete_map={
                                 "Food Quality": "#f97316",
                                 "Service": "#818cf8",
                                 "Cleanliness": "#34d399",
                                 "Other": "#94a3b8"
                             },
                             labels={"frequency": "Frequency", "keyword": "Issue Keyword"})
                fig.update_layout(**PLOTLY_DARK, yaxis={"categoryorder": "total ascending"}, height=500)
                st.plotly_chart(fig, use_container_width=True)

            with col_i2:
                cat_summary_issues = df_issues.groupby("issue_category")["frequency"].sum().reset_index()
                fig2 = px.pie(cat_summary_issues, values="frequency", names="issue_category", hole=0.4,
                              color="issue_category",
                              color_discrete_map={
                                  "Food Quality": "#f97316",
                                  "Service": "#818cf8",
                                  "Cleanliness": "#34d399",
                                  "Other": "#94a3b8"
                              })
                fig2.update_layout(**PLOTLY_DARK)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<div class="section-header">📋 Issue Detail Table</div>', unsafe_allow_html=True)
            st.dataframe(df_issues.sort_values("frequency", ascending=False).reset_index(drop=True),
                         use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 9 — PEAK TIME ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown('<div class="section-header">⏰ Orders by Time of Day</div>', unsafe_allow_html=True)
    all_reviews_raw = fetch_all_reviews()

    if all_reviews_raw:
        df_time = pd.DataFrame(all_reviews_raw)
        df_time["time_bucket"] = df_time["time"].apply(parse_time_bucket)
        bucket_counts = df_time["time_bucket"].value_counts().reset_index()
        bucket_counts.columns = ["time_of_day", "count"]

        BUCKET_ORDER = ["Morning", "Afternoon", "Evening", "Night", "Unknown"]
        bucket_counts["sort_key"] = bucket_counts["time_of_day"].apply(
            lambda x: BUCKET_ORDER.index(x) if x in BUCKET_ORDER else 99
        )
        bucket_counts = bucket_counts.sort_values("sort_key")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig = px.bar(bucket_counts, x="time_of_day", y="count",
                         color="time_of_day", color_discrete_sequence=COLOR_SEQ,
                         labels={"time_of_day": "Time of Day", "count": "Orders"})
            fig.update_layout(**PLOTLY_DARK, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_p2:
            fig2 = px.pie(bucket_counts, values="count", names="time_of_day",
                          hole=0.45, color_discrete_sequence=COLOR_SEQ)
            fig2.update_layout(**PLOTLY_DARK)
            st.plotly_chart(fig2, use_container_width=True)

        # Peak KPIs
        if not bucket_counts.empty:
            valid = bucket_counts[bucket_counts["time_of_day"] != "Unknown"]
            if not valid.empty:
                busiest = valid.loc[valid["count"].idxmax()]
                slowest = valid.loc[valid["count"].idxmin()]
                pk1, pk2, pk3 = st.columns(3)
                with pk1:
                    st.markdown(make_kpi_html("🔥 Busiest Period", busiest["time_of_day"], f"{int(busiest['count']):,} orders", "pos"), unsafe_allow_html=True)
                with pk2:
                    st.markdown(make_kpi_html("🌙 Slowest Period", slowest["time_of_day"], f"{int(slowest['count']):,} orders", "neg"), unsafe_allow_html=True)
                with pk3:
                    total_known = int(valid["count"].sum())
                    st.markdown(make_kpi_html("📦 Total Orders", f"{total_known:,}", "All periods", "neu"), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 10 — REVIEWS TABLE
# ════════════════════════════════════════════════════════════════════════════
with tabs[9]:
    st.markdown('<div class="section-header">📋 Customer Reviews</div>', unsafe_allow_html=True)

    if not df.empty:
        search_term = st.text_input("🔍 Search reviews...", placeholder="Type keyword to filter")
        df_show = df.copy()

        if search_term:
            df_show = df_show[df_show["review"].str.contains(search_term, case=False, na=False)]

        sent_filter = st.multiselect("Filter by Sentiment", ["Positive", "Negative", "Neutral"],
                                     default=["Positive", "Negative", "Neutral"])
        if sent_filter:
            df_show = df_show[df_show["sentiment"].isin(sent_filter)]

        st.markdown(f"<div style='color:#64748b;margin-bottom:8px;'>Showing {len(df_show):,} reviews</div>", unsafe_allow_html=True)

        def color_rating(val):
            try:
                v = float(val)
                if v >= 4: return "color:#22c55e;font-weight:700"
                if v <= 2: return "color:#ef4444;font-weight:700"
                return "color:#facc15;font-weight:700"
            except:
                return ""

        display_cols = [c for c in ["restaurant", "date", "rating", "sentiment", "review"] if c in df_show.columns]
        df_display = df_show[display_cols].head(200).reset_index(drop=True)

        if "rating" in df_display.columns:
            st.dataframe(
                df_display.style.map(color_rating, subset=["rating"]),
                use_container_width=True, hide_index=True
            )
        else:
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No reviews match the current filters.")

# ─── FOOTER ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#475569;font-size:12px;'>"
    "🍽️ Restaurant Chain Analytics Dashboard &nbsp;|&nbsp; Built with Neo4j + Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True
)
