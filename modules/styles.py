import streamlit as st
from modules.config import COLORS

def apply_premium_css():
    st.markdown(f"""
    <style>
    /* ========== FONTS ========== */
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    
    /* ========== GLOBAL ========== */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    
    /* ========== MAIN APP ========== */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['light']} 0%, #EFF6FF 50%, {COLORS['light']} 100%);
    }}
    
    .main .block-container {{
        padding: 2rem 2.5rem;
        max-width: 1400px;
    }}
    
    /* ========== SIDEBAR PREMIUM ========== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['white']} 0%, {COLORS['light']} 100%);
        border-right: 1px solid {COLORS['gray_light']};
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.03);
    }}
    
    [data-testid="stSidebar"] .element-container {{
        margin-bottom: 0.5rem;
    }}
    
    /* ========== BUTTONS SIDEBAR ========== */
    .stButton button {{
        width: 100%;
        background: {COLORS['white']};
        border: 1.5px solid {COLORS['gray_light']};
        border-radius: 12px;
        padding: 0.85rem 1.2rem;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: {COLORS['primary']};
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        text-align: left;
    }}
    
    .stButton button:hover {{
        background: linear-gradient(135deg, {COLORS['secondary']} 0%, {COLORS['accent']} 100%);
        border-color: {COLORS['secondary']};
        color: {COLORS['white']};
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
    }}
    
    /* ========== METRICS CARDS ========== */
    [data-testid="stMetric"] {{
        background: {COLORS['white']};
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid {COLORS['gray_light']};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    
    [data-testid="stMetric"]:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
        border-color: {COLORS['accent']};
    }}
    
    [data-testid="stMetric"] > div {{
        font-family: 'IBM Plex Sans', sans-serif;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: 0.8rem;
        font-weight: 600;
        color: {COLORS['gray']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    [data-testid="stMetricValue"] {{
        font-family: 'Sora', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    
    /* ========== INPUTS ========== */
    .stSlider {{
        padding: 1rem 0;
    }}
    
    .stSlider > div > div > div > div {{
        background: {COLORS['secondary']};
    }}
    
    .stNumberInput > div > div > input {{
        border: 1.5px solid {COLORS['gray_light']};
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 500;
        transition: all 0.2s;
    }}
    
    .stNumberInput > div > div > input:focus {{
        border-color: {COLORS['secondary']};
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
    }}
    
    .stSelectbox > div > div {{
        border: 1.5px solid {COLORS['gray_light']};
        border-radius: 10px;
        font-family: 'IBM Plex Sans', sans-serif;
        transition: all 0.2s;
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: {COLORS['secondary']};
    }}
    
    /* ========== DIVIDER ========== */
    hr {{
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, {COLORS['gray_light']} 50%, transparent 100%);
    }}
    
    /* ========== CUSTOM CARDS ========== */
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['white']} 0%, {COLORS['light']} 100%);
        border: 1.5px solid {COLORS['gray_light']};
        border-radius: 16px;
        padding: 1.8rem 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--card-color);
        transform: scaleY(0);
        transform-origin: bottom;
        transition: transform 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
        border-color: var(--card-color);
    }}
    
    .metric-card:hover::before {{
        transform: scaleY(1);
        transform-origin: top;
    }}
    
    .metric-icon {{
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--card-color), var(--card-color-light));
        color: white;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover .metric-icon {{
        transform: scale(1.1) rotate(5deg);
    }}
    
    .metric-value {{
        font-family: 'Sora', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary']};
        margin: 0.5rem 0;
        letter-spacing: -0.02em;
    }}
    
    .metric-label {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: {COLORS['gray']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .metric-subtitle {{
        font-size: 0.85rem;
        color: {COLORS['dark_gray']};
        margin-top: 0.5rem;
    }}
    
    /* ========== PLOTLY CHARTS ========== */
    .js-plotly-plot {{
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid {COLORS['gray_light']};
    }}
    
    /* ========== HEADINGS ========== */
    .section-title {{
        font-family: 'Sora', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: {COLORS['primary']};
        margin: 2rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        letter-spacing: -0.02em;
    }}
    
    .section-title svg {{
        width: 28px;
        height: 28px;
        color: {COLORS['secondary']};
    }}
    
    .page-title {{
        font-family: 'Sora', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: {COLORS['primary']};
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .page-subtitle {{
        font-size: 1rem;
        color: {COLORS['gray']};
        margin-bottom: 2rem;
        font-weight: 500;
    }}
    
    /* ========== ANIMATIONS ========== */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .metric-card {{
        animation: fadeInUp 0.5s ease-out;
    }}
    
    /* ========== CUSTOM GRADIENT CARDS ========== */
    .gradient-card {{
        background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
        padding: 1.8rem 1.5rem;
        border-radius: 16px;
        color: white;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .gradient-card::after {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s;
    }}
    
    .gradient-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.2);
    }}
    
    .gradient-card:hover::after {{
        opacity: 1;
    }}
    
    .gradient-card-label {{
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }}
    
    .gradient-card-value {{
        font-family: 'Sora', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        letter-spacing: -0.02em;
    }}
    
    .gradient-card-footer {{
        font-size: 0.8rem;
        opacity: 0.85;
        margin-top: 0.5rem;
    }}
    </style>
    """, unsafe_allow_html=True)
