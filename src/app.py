import streamlit as st
import boto3
import pandas as pd
import plotly.graph_objects as go
from boto3.dynamodb.conditions import Key
import urllib3
import json
from textblob import TextBlob

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Stock Watch — Live Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* ===== GLOBAL THEME ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(145deg, #0a0e17 0%, #111827 50%, #0d1321 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px;
    }

    /* ===== HEADER ===== */
    .dashboard-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .dashboard-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 400;
    }


    /* ===== KPI CARDS ===== */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .kpi-card.active {
        border-color: rgba(99, 102, 241, 0.6);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
    }
    .kpi-card.active::before { opacity: 1; }
    .kpi-ticker {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }
    .kpi-ticker-icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem; font-weight: 700; color: white;
    }
    .kpi-ticker-name { font-size: 1rem; font-weight: 600; color: #e2e8f0; }
    .kpi-ticker-label { font-size: 0.75rem; color: #64748b; font-weight: 400; }
    .kpi-price {
        font-size: 1.75rem; font-weight: 700; color: #f1f5f9;
        margin-bottom: 0.25rem; letter-spacing: -0.5px;
    }
    .kpi-delta {
        font-size: 0.85rem; font-weight: 600;
        display: inline-flex; align-items: center; gap: 0.25rem;
        padding: 0.25rem 0.6rem; border-radius: 8px;
    }
    .kpi-delta.up { color: #34d399; background: rgba(52, 211, 153, 0.1); }
    .kpi-delta.down { color: #f87171; background: rgba(248, 113, 113, 0.1); }

    /* ===== STREAMLIT BUTTON OVERRIDES ===== */
    .stButton > button {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 10px !important;
        color: #a5b4fc !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        padding: 0.4rem 0.75rem !important;
        transition: all 0.2s ease !important;
        margin-top: 0.5rem;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.2) 100%) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        color: #c7d2fe !important;
    }
    .stButton > button:active {
        background: rgba(99, 102, 241, 0.4) !important;
    }
    .stButton > button:focus {
        box-shadow: none !important;
    }

    /* ===== FOOTER ===== */
    .dash-footer {
        text-align: center;
        color: #374151;
        font-size: 0.75rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid rgba(99, 102, 241, 0.08);
        margin-top: 2rem;
    }

    /* ===== STREAMLIT OVERRIDES ===== */
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    /* Remove Streamlit element colors */
    .stAlert { display: none; }

    /* ===== SECTION TITLES ===== */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-title span {
        font-size: 0.75rem;
        color: #6366f1;
        background: rgba(99, 102, 241, 0.1);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 500;
    }

    /* ===== CHART CONTAINER ===== */
    .chart-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }

    /* ===== NEWS CARDS ===== */
    .news-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.25rem;
    }
    .news-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(99, 102, 241, 0.1);
        border-radius: 16px;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .news-card:hover {
        border-color: rgba(99, 102, 241, 0.35);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }
    .news-card-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-bottom: 1px solid rgba(99, 102, 241, 0.08);
    }
    .news-card-img-placeholder {
        width: 100%;
        height: 180px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        border-bottom: 1px solid rgba(99, 102, 241, 0.08);
    }
    .news-card-body {
        padding: 1.25rem;
    }
    .news-card-body h4 {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
        line-height: 1.5;
        margin-bottom: 0.75rem;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-card-body h4 a {
        color: #e2e8f0;
        text-decoration: none;
        transition: color 0.2s;
    }
    .news-card-body h4 a:hover {
        color: #818cf8;
    }
    .news-source {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .news-source-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #6366f1;
    }
    .news-source-name {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
    }


    /* Responsive */
    @media (max-width: 768px) {
        .kpi-grid { grid-template-columns: repeat(2, 1fr); }
        .news-grid { grid-template-columns: 1fr; }
    }
</style>
""", unsafe_allow_html=True)

# --- AWS CONNECTION ---
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table('StockPrices')

# --- TICKER CONFIG ---
TICKERS = {
    "NVDA": {"name": "NVIDIA", "icon": "🟢", "color": "#76b900"},
    "TSLA": {"name": "Tesla", "icon": "🔴", "color": "#e31937"},
    "AAPL": {"name": "Apple", "icon": "⚪", "color": "#a2aaad"},
    "BTC-USD": {"name": "Bitcoin", "icon": "🟡", "color": "#f7931a"},
}

# --- SESSION STATE ---
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "NVDA"

# --- DATA FUNCTIONS ---
def get_data(ticker):
    """Fetches stock price history from DynamoDB"""
    try:
        response = table.query(
            KeyConditionExpression=Key('ticker').eq(ticker),
            ScanIndexForward=True
        )
        df = pd.DataFrame(response.get('Items', []))
        if not df.empty:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            df = df.sort_values(by='timestamp')
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_news(ticker):
    """Fetches live news from Yahoo Finance internal API"""
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    http = urllib3.PoolManager()

    try:
        response = http.request('GET', url, headers=headers, timeout=10.0)
        data = json.loads(response.data.decode('utf-8'))
        news = data.get('news', [])[:3]
        if not news:
            st.cache_data.clear()
        return news
    except Exception as e:
        st.cache_data.clear()
        return []

# --- HEADER ---
st.markdown("""
<div class="dashboard-header">
    <h1>📈 Stock Watch</h1>
    <p>Real-time stock market overview • Powered by AWS</p>
</div>
""", unsafe_allow_html=True)

# --- KPI CARDS ---
# Preload all ticker data
ticker_data = {}
for t in TICKERS:
    ticker_data[t] = get_data(t)

# Build KPI card data
def get_kpi_data(ticker, info, df):
    if not df.empty:
        current = df.iloc[-1]['price']
        delta = current - df.iloc[-2]['price'] if len(df) > 1 else 0
        pct = (delta / (current - delta) * 100) if (current - delta) != 0 else 0
        delta_class = "up" if delta >= 0 else "down"
        delta_arrow = "▲" if delta >= 0 else "▼"
        price_str = f"${current:,.2f}"
        delta_str = f"{delta_arrow} {abs(delta):,.2f} ({abs(pct):.2f}%)"
    else:
        price_str = "—"
        delta_str = "Awaiting data"
        delta_class = "down"
    return price_str, delta_str, delta_class

def build_kpi_html(ticker, info, price_str, delta_str, delta_class, is_active):
    active_class = "active" if is_active else ""
    return f"""
    <div class="kpi-card {active_class}">
        <div class="kpi-ticker">
            <div class="kpi-ticker-icon" style="background: {info['color']}20; color: {info['color']};">
                {info['icon']}
            </div>
            <div>
                <div class="kpi-ticker-name">{ticker}</div>
                <div class="kpi-ticker-label">{info['name']}</div>
            </div>
        </div>
        <div class="kpi-price">{price_str}</div>
        <div class="kpi-delta {delta_class}">{delta_str}</div>
    </div>
    """

def select_ticker(ticker):
    st.session_state.selected_ticker = ticker

# Render clickable KPI cards
cols = st.columns(len(TICKERS))
for i, (ticker, info) in enumerate(TICKERS.items()):
    with cols[i]:
        df = ticker_data[ticker]
        is_active = (ticker == st.session_state.selected_ticker)
        price_str, delta_str, delta_class = get_kpi_data(ticker, info, df)
        card_html = build_kpi_html(ticker, info, price_str, delta_str, delta_class, is_active)
        st.markdown(card_html, unsafe_allow_html=True)
        st.button(
            f"Select {ticker}",
            key=f"btn_{ticker}",
            on_click=select_ticker,
            args=(ticker,),
            use_container_width=True
        )

# --- CHART ---
selected = st.session_state.selected_ticker
df_main = ticker_data[selected]
ticker_info = TICKERS[selected]

st.markdown(f"""
<div class="section-title">
    {ticker_info['icon']} {ticker_info['name']} ({selected}) <span>LIVE</span>
</div>
""", unsafe_allow_html=True)

if not df_main.empty and len(df_main) > 1:
    is_up = df_main.iloc[-1]['price'] >= df_main.iloc[0]['price']
    line_color = "#34d399" if is_up else "#f87171"
    fill_color = "rgba(52, 211, 153, 0.08)" if is_up else "rgba(248, 113, 113, 0.08)"

    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=df_main['timestamp'],
        y=df_main['price'],
        fill='tozeroy',
        fillcolor=fill_color,
        line=dict(color=line_color, width=2.5, shape='spline', smoothing=1.0),
        mode='lines',
        name=selected,
        hovertemplate='<b>%{x}</b><br>$%{y:,.2f}<extra></extra>'
    ))

    # SMA 20 Moving Average
    sma_window = min(20, len(df_main))
    df_main['sma_20'] = df_main['price'].rolling(window=sma_window, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=df_main['timestamp'],
        y=df_main['sma_20'],
        line=dict(color='#fbbf24', width=1.5, dash='dash'),
        mode='lines',
        name=f'SMA {sma_window}',
        hovertemplate='<b>%{x}</b><br>SMA: $%{y:,.2f}<extra></extra>'
    ))

    # Latest price annotation
    latest_price = df_main.iloc[-1]['price']
    latest_time = df_main.iloc[-1]['timestamp']
    fig.add_annotation(
        x=latest_time,
        y=latest_price,
        text=f"  ${latest_price:,.2f}",
        showarrow=False,
        font=dict(size=14, color=line_color, family="Inter"),
        xanchor="left"
    )

    # Dot at latest price
    fig.add_trace(go.Scatter(
        x=[latest_time],
        y=[latest_price],
        mode='markers',
        marker=dict(size=10, color=line_color, line=dict(width=2, color='#0f172a')),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#94a3b8"),
        height=420,
        margin=dict(l=0, r=40, t=20, b=40),
        xaxis=dict(
            showgrid=False,
            showline=False,
            tickfont=dict(size=11, color="#4b5563"),
            dtick=None,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(99, 102, 241, 0.06)',
            showline=False,
            tickfont=dict(size=11, color="#4b5563"),
            tickprefix="$",
            side="right",
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#1e293b',
            bordercolor='#334155',
            font=dict(family="Inter", size=13, color="#e2e8f0"),
        ),
        showlegend=False,
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

elif not df_main.empty and len(df_main) == 1:
    st.markdown("""
    <div class="chart-container" style="text-align:center; padding: 4rem 2rem;">
        <p style="color:#64748b; font-size: 1.1rem;">📈 One data point recorded. Waiting for next sync to draw chart...</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="chart-container" style="text-align:center; padding: 4rem 2rem;">
        <p style="color:#64748b; font-size: 1.1rem;">⏳ Waiting for initial data sync...</p>
    </div>
    """, unsafe_allow_html=True)

# --- NEWS FEED ---
st.markdown(f"""
<div class="section-title" style="margin-top: 0.5rem;">
    📰 Latest News <span>{selected}</span>
</div>
""", unsafe_allow_html=True)

news_items = get_news(selected)

if news_items:
    # --- AI SENTIMENT LOGIC ---
    sentiment_scores = []
    for item in news_items:
        analysis = TextBlob(item.get('title', ''))
        sentiment_scores.append(analysis.sentiment.polarity)
    
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Determine the "Mood" styling based on AI score
    if avg_sentiment > 0.1:
        mood_text, mood_color, mood_bg = "BULLISH", "#34d399", "rgba(52, 211, 153, 0.1)"
    elif avg_sentiment < -0.1:
        mood_text, mood_color, mood_bg = "BEARISH", "#f87171", "rgba(248, 113, 113, 0.1)"
    else:
        mood_text, mood_color, mood_bg = "NEUTRAL", "#fbbf24", "rgba(251, 191, 36, 0.1)"
    
    # Render the AI Mood Badge
    st.markdown(f"""
    <div style="background: {mood_bg}; border: 1px solid {mood_color}30; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem;">
        <div style="font-size: 1.5rem;">🤖</div>
        <div>
            <div style="color: {mood_color}; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px;">AI SENTIMENT</div>
            <div style="color: #f1f5f9; font-size: 1.1rem; font-weight: 600;">Current market mood is {mood_text} ({avg_sentiment:.2f})</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- NEWS CARDS RENDERING ---
    news_cards = []
    for item in news_items:
        title = item.get('title', 'Untitled')
        link = item.get('link', '#')
        publisher = item.get('publisher', 'Unknown')

        # Extract thumbnail
        thumbnail = None
        thumbs = item.get('thumbnail', {})
        if isinstance(thumbs, dict):
            resolutions = thumbs.get('resolutions', [])
            if resolutions:
                thumbnail = resolutions[-1].get('url', None)

        if thumbnail:
            img_part = f'<img class="news-card-img" src="{thumbnail}" alt="news" loading="lazy">'
        else:
            img_part = '<div class="news-card-img-placeholder">📄</div>'

        card = (
            f'<div class="news-card">'
            f'{img_part}'
            f'<div class="news-card-body">'
            f'<h4><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a></h4>'
            f'<div class="news-source">'
            f'<div class="news-source-dot"></div>'
            f'<div class="news-source-name">{publisher}</div>'
            f'</div></div></div>'
        )
        news_cards.append(card)

    full_html = '<div class="news-grid">' + ''.join(news_cards) + '</div>'
    st.markdown(full_html, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem; color: #4b5563;">
        <p style="font-size: 1.5rem; margin-bottom: 0.5rem;">📭</p>
        <p>No recent news available for this ticker.</p>
    </div>
    """, unsafe_allow_html=True)