import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import warnings
import base64

warnings.filterwarnings('ignore')

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Base Telco | Faturamento & Previsões",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ÍCONES SVG PROFISSIONAIS ====================
ICONS = {
    'calendar': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>''',
    
    'target': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>''',
    
    'chart': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>''',
    
    'trending_up': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>''',
    
    'dollar': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>''',
    
    'users': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>''',
    
    'credit_card': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg>''',
    
    'settings': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6m5.2-14.8l-4.2 4.2m0 5.2l-4.2 4.2M1 12h6m6 0h6M6.8 6.8l4.2 4.2m0 5.2l4.2 4.2"></path></svg>''',
    
    'bar_chart': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>''',
    
    'pie_chart': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>''',
    
    'file_text': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>''',
}

# ==================== PALETA DE CORES PREMIUM ====================
COLORS = {
    'primary': '#0F172A',       # Slate 900 - Texto principal
    'secondary': '#1E40AF',     # Blue 700 - Ação principal
    'accent': '#0EA5E9',        # Sky 500 - Destaque
    'success': '#059669',       # Emerald 600 - Sucesso
    'warning': '#F59E0B',       # Amber 500 - Atenção
    'danger': '#DC2626',        # Red 600 - Perigo
    'info': '#3B82F6',          # Blue 500 - Informação
    'light': '#F8FAFC',         # Slate 50 - Background
    'gray': '#64748B',          # Slate 500 - Texto secundário
    'gray_light': '#CBD5E1',    # Slate 300 - Bordas
    'dark_gray': '#475569',     # Slate 600
    'white': '#FFFFFF',
    # Serviços
    'toip': '#3B82F6',          # Blue 500
    'cldpbx': '#10B981',        # Emerald 500
    'video': '#A855F7',         # Purple 500
    'ip': '#F97316',            # Orange 500
    'ccenter': '#EF4444',       # Red 500
    'out': '#6B7280'            # Gray 500
}

CORES_SERVICOS = {
    'TOIP': COLORS['toip'],
    'CLDPBX': COLORS['cldpbx'],
    'VIDEO': COLORS['video'],
    'IP': COLORS['ip'],
    'CCENTER': COLORS['ccenter'],
    'OUT': COLORS['out']
}

# ==================== CSS PREMIUM ====================
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

# ==================== FUNÇÕES UTILITÁRIAS ====================

def load_logo():
    """Carrega a logo da Base Telco"""
    try:
        with open("logo.gif", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def format_currency(value):
    """Formata valor como moeda brasileira"""
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

def format_number(num):
    """Formata número com separador de milhares"""
    try:
        return f"{int(num):,}".replace(',', '.')
    except:
        return str(num)

def format_percentage(value):
    """Formata percentual"""
    try:
        return f"{float(value):.1f}%"
    except:
        return "0.0%"

def get_color_by_growth(value):
    """Retorna cor baseada no crescimento"""
    if value > 5:
        return COLORS['success']
    elif value > 0:
        return COLORS['warning']
    else:
        return COLORS['danger']

@st.cache_data
def load_data():
    """Carrega e processa a base de dados"""
    try:
        df = pd.read_excel('BD-FATURAMENTO.xlsx')

        # Garantir que as colunas essenciais existam
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df['Vlr Valido'] = pd.to_numeric(df['Vlr Valido'], errors='coerce')
        df['MÊS'] = pd.to_numeric(df['MÊS'], errors='coerce')
        df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce')

        # Criar coluna de período (MÊS/ANO)
        df['Periodo'] = df['Descrição'].astype(str) + '/' + df['ANO'].astype(str)

        return df
    except Exception as e:
        st.error(f"Erro ao carregar base de dados: {e}")
        return pd.DataFrame()

def normalizar_nome_cliente(nome):
    """Normaliza nome de cliente para matching entre bases"""
    import unicodedata
    nome = str(nome).upper().strip()
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(char for char in nome if unicodedata.category(char) != 'Mn')
    nome = nome.replace('.', '').replace(',', '').replace('-', '').replace('/', '')
    nome = ' '.join(nome.split())
    mapeamento = {'INTERCEMENT': 'INTERCEMENT', 'KOMECO': 'KOMECO', 'SEBRAE': 'SEBRAE'}
    return mapeamento.get(nome, nome)

@st.cache_data(ttl=600)
def carregar_ativacoes():
    """Carrega a planilha de ativações em andamento"""
    try:
        df = pd.read_excel('EM-ATIVACAO.xlsx', sheet_name='EM ATIVAÇÃO')
        df['CLIENTE_NORM'] = df['CLIENTE'].apply(normalizar_nome_cliente)
        df['DATA_PREVISTA'] = pd.to_datetime(df['DATA PREVISTA'], errors='coerce')
        df['VALOR_MRR'] = pd.to_numeric(df['VALOR TOTAL'], errors='coerce')
        return df[['CLIENTE', 'CLIENTE_NORM', 'DATA_PREVISTA', 'VALOR_MRR']].dropna()
    except Exception as e:
        st.warning(f"Não foi possível carregar EM-ATIVACAO.xlsx: {e}")
        return pd.DataFrame()

def calcular_valor_proporcional(data_ativacao, valor_mrr):
    """Calcula valor proporcional baseado nos dias restantes do mês"""
    import calendar
    data = pd.to_datetime(data_ativacao)
    dias_no_mes = calendar.monthrange(data.year, data.month)[1]
    dias_cobrados = dias_no_mes - data.day
    if dias_cobrados <= 0:
        return 0.0
    return (valor_mrr / dias_no_mes) * dias_cobrados

def gerar_previsao_com_ativacoes(df, df_ativacoes, meses_futuros=6):
    """Gera previsão baseada em ativações reais"""
    if df.empty:
        return pd.DataFrame()
    ultimo_mes = df['MÊS'].max()
    ultimo_ano = df['ANO'].max()
    df_ultimo = df[(df['MÊS'] == ultimo_mes) & (df['ANO'] == ultimo_ano)]
    base_clientes = df_ultimo.groupby('GRUPO CLIENTE')['Vlr Valido'].sum().to_dict()
    previsoes = []
    mes_atual = ultimo_mes
    ano_atual = ultimo_ano
    meses_nome = ['', 'JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                  'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    for i in range(1, meses_futuros + 1):
        mes_atual += 1
        if mes_atual > 12:
            mes_atual = 1
            ano_atual += 1
        periodo_nome = f"{meses_nome[mes_atual]}/{ano_atual}"
        data_mes = pd.Timestamp(year=ano_atual, month=mes_atual, day=1)
        previsao_mes = base_clientes.copy()
        if not df_ativacoes.empty:
            for _, ativ in df_ativacoes.iterrows():
                data_ativ = ativ['DATA_PREVISTA']
                if pd.notna(data_ativ) and data_ativ < data_mes + pd.DateOffset(months=1):
                    if data_ativ.year == ano_atual and data_ativ.month == mes_atual:
                        valor = calcular_valor_proporcional(data_ativ, ativ['VALOR_MRR'])
                    elif data_ativ < data_mes:
                        valor = ativ['VALOR_MRR']
                    else:
                        continue
                    cliente_key = None
                    for k in previsao_mes.keys():
                        if normalizar_nome_cliente(k) == ativ['CLIENTE_NORM']:
                            cliente_key = k
                            break
                    if cliente_key:
                        previsao_mes[cliente_key] += valor
                    else:
                        previsao_mes[ativ['CLIENTE']] = valor
        for cliente, valor in previsao_mes.items():
            if valor > 0:
                previsoes.append({'Cliente': cliente, 'Periodo': periodo_nome, 'MÊS': mes_atual, 
                                'ANO': ano_atual, 'Valor': valor, 'Tipo': 'Previsto'})
    return pd.DataFrame(previsoes)




# ==================== APLICAR CSS ====================
apply_premium_css()

# ==================== INICIALIZAÇÃO DO SESSION STATE ====================
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'previsao'

if 'df_base' not in st.session_state:
    st.session_state.df_base = load_data()

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo
    logo_base64 = load_logo()
    if logo_base64:
        st.markdown(f"""
            <div style='text-align: center; padding: 1.5rem 0 2rem 0;'>
                <img src='data:image/gif;base64,{logo_base64}' style='max-width: 280px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));'>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='text-align: center; padding: 1.5rem 0 2rem 0;'>
                <h2 style='font-family: Sora; color: {COLORS['secondary']}; font-weight: 800;'>Base Telco</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown(f"""
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='font-family: Sora; font-size: 1rem; font-weight: 700; color: {COLORS['primary']}; margin-bottom: 1rem;'>
                Navegação
            </h3>
        </div>
    """, unsafe_allow_html=True)

    # Menu de navegação
    menu_options = {
        'previsao': ('calendar', 'Previsão de Faturamento'),
        'mix': ('pie_chart', 'Mix de Produtos'),
        'consolidado': ('bar_chart', 'Consolidado & Projeção')
    }

    for key, (icon, label) in menu_options.items():
        if st.button(f"{label}", key=f"btn_{key}", use_container_width=True):
            st.session_state.pagina_atual = key

    st.markdown("---")

    # Informações da base
    if not st.session_state.df_base.empty:
        st.markdown(f"""
            <div style='margin-bottom: 1rem;'>
                <h3 style='font-family: Sora; font-size: 0.95rem; font-weight: 700; color: {COLORS['primary']};'>
                    {ICONS['file_text']} Informações
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        df = st.session_state.df_base

        total_fat = df['Vlr Valido'].sum()
        qtd_clientes = df['GRUPO CLIENTE'].nunique()
        qtd_servicos = df['tpServ'].nunique()

        st.metric("Faturamento Total", format_currency(total_fat))
        st.metric("Clientes Ativos", qtd_clientes)
        st.metric("Tipos de Serviços", qtd_servicos)

        # Período da base
        periodos = sorted(df['Periodo'].unique())
        st.markdown(f"""
            <div style='margin-top: 1rem; padding: 0.75rem; background: {COLORS['light']}; border-radius: 8px; border-left: 3px solid {COLORS['secondary']};'>
                <div style='font-size: 0.75rem; color: {COLORS['gray']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Período</div>
                <div style='font-size: 0.85rem; color: {COLORS['primary']}; font-weight: 600; margin-top: 0.25rem;'>
                    {periodos[0]} → {periodos[-1] if len(periodos) > 1 else periodos[0]}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
        <div style='text-align: center; font-size: 0.75rem; color: {COLORS["gray"]}; font-weight: 500;'>
            Base Telco v2.0<br>
            <span style='font-size: 0.7rem; opacity: 0.8;'>{datetime.now().strftime('%d/%m/%Y')}</span>
        </div>
    """, unsafe_allow_html=True)

# ==================== PÁGINA: PREVISÃO DE FATURAMENTO ====================
if st.session_state.pagina_atual == 'previsao':
    # Header da página
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                Previsão de Faturamento
            </h1>
            <p class='page-subtitle'>
                Análise preditiva por cliente com projeções de crescimento
            </p>
        </div>
    """, unsafe_allow_html=True)

    df = st.session_state.df_base

    if df.empty:
        st.warning("⚠️ Nenhum dado disponível. Verifique o arquivo BD-FATURAMENTO.xlsx")
    else:
        # Configurações
        col1, col2 = st.columns([3, 3])
        with col1:
            meses_previsao = st.slider("Meses de Previsão", 3, 12, 6)
        with col2:
            top_n = st.number_input("Top N Clientes", 5, 50, 15, 5)

        st.markdown("---")

        # Gerar previsão
        df_ativacoes = carregar_ativacoes()
        df_previsao = gerar_previsao_com_ativacoes(df, df_ativacoes, meses_previsao)

        # Agrupar por cliente
        clientes_total = df.groupby('GRUPO CLIENTE')['Vlr Valido'].sum().reset_index()
        clientes_total.columns = ['Cliente', 'Valor_Historico']
        clientes_total = clientes_total.sort_values('Valor_Historico', ascending=False)

        # Top N clientes
        top_clientes = clientes_total.head(top_n)


        # Cards de Pipeline de Ativações
        if not df_ativacoes.empty:
            from datetime import datetime
            pipeline_total = df_ativacoes['VALOR_MRR'].sum()
            data_atual = datetime.now()
            proximo_mes = data_atual.month + 1 if data_atual.month < 12 else 1
            proximo_ano = data_atual.year if data_atual.month < 12 else data_atual.year + 1

            ativacoes_proximo_mes = df_ativacoes[
                (df_ativacoes['DATA_PREVISTA'].dt.month == proximo_mes) & 
                (df_ativacoes['DATA_PREVISTA'].dt.year == proximo_ano)
            ]
            qtd_ativacoes_mes = len(ativacoes_proximo_mes)
            valor_prop_mes = sum([calcular_valor_proporcional(row['DATA_PREVISTA'], row['VALOR_MRR']) 
                                  for _, row in ativacoes_proximo_mes.iterrows()])

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent']}); 
                         padding: 1.5rem; border-radius: 12px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 8px;'>
                            {ICONS['trending_up']}
                            <span style='font-size: 14px; opacity: 0.95; font-weight: 500;'>Pipeline de Ativações</span>
                        </div>
                        <div style='font-size: 28px; font-weight: 700; font-family: Sora, sans-serif; margin: 8px 0;'>
                            {format_currency(pipeline_total)}
                        </div>
                        <div style='font-size: 12px; opacity: 0.9;'>MRR em implantação</div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {COLORS['success']}, {COLORS['accent']}); 
                         padding: 1.5rem; border-radius: 12px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 8px;'>
                            {ICONS['users']}
                            <span style='font-size: 14px; opacity: 0.95; font-weight: 500;'>Ativações Próximo Mês</span>
                        </div>
                        <div style='font-size: 28px; font-weight: 700; font-family: Sora, sans-serif; margin: 8px 0;'>
                            {qtd_ativacoes_mes}
                        </div>
                        <div style='font-size: 12px; opacity: 0.9;'>
                            {['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][proximo_mes-1]}/{proximo_ano}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {COLORS['warning']}, {COLORS['danger']}); 
                         padding: 1.5rem; border-radius: 12px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 8px;'>
                            {ICONS['dollar']}
                            <span style='font-size: 14px; opacity: 0.95; font-weight: 500;'>Incremento Próximo Mês</span>
                        </div>
                        <div style='font-size: 28px; font-weight: 700; font-family: Sora, sans-serif; margin: 8px 0;'>
                            {format_currency(valor_prop_mes)}
                        </div>
                        <div style='font-size: 12px; opacity: 0.9;'>Previsão proporcional</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

        # Preparar dados para a tabela de previsão mês a mês


        # UPGRADE 2: Mapear ativações por cliente e período
        mapa_ativacoes = {}
        if not df_ativacoes.empty:
            meses_map = {1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL', 5: 'MAIO', 6: 'JUNHO',
                        7: 'JULHO', 8: 'AGOSTO', 9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'}
            for _, ativ in df_ativacoes.iterrows():
                cliente = ativ['CLIENTE']
                if pd.notna(ativ['DATA_PREVISTA']):
                    periodo = f"{meses_map[ativ['DATA_PREVISTA'].month]}/{ativ['DATA_PREVISTA'].year}"
                    if cliente not in mapa_ativacoes:
                        mapa_ativacoes[cliente] = []
                    mapa_ativacoes[cliente].append(periodo)

        df_real = df.groupby(['GRUPO CLIENTE', 'Periodo', 'MÊS', 'ANO'])['Vlr Valido'].sum().reset_index()
        df_real['Tipo'] = 'Realizado'
        df_real.columns = ['Cliente', 'Periodo', 'MÊS', 'ANO', 'Valor', 'Tipo']

        # Criar tabela pivotada para a tabela HTML
        df_filtrado_tabela = pd.concat([df_real, df_previsao], ignore_index=True)
        df_filtrado_tabela = df_filtrado_tabela[df_filtrado_tabela['Cliente'].isin(top_clientes['Cliente'])]

        df_pivot = df_filtrado_tabela.pivot_table(
            index='Cliente',
            columns='Periodo',
            values='Valor',
            aggfunc='sum',
            fill_value=0
        )


        # UPGRADE 3: Adicionar clientes novos e preencher previsões
        if not df_ativacoes.empty:
            for _, ativ in df_ativacoes.iterrows():
                cliente = ativ['CLIENTE']
                if cliente not in df_pivot.index:
                    nova_linha = pd.Series(0.0, index=df_pivot.columns, name=cliente)
                    df_pivot = pd.concat([df_pivot, nova_linha.to_frame().T])

            if not df_previsao.empty:
                for _, prev in df_previsao.iterrows():
                    cliente_prev = prev['Cliente']
                    periodo_prev = prev['Periodo']
                    valor_prev = prev['Valor']
                    if cliente_prev in df_pivot.index and periodo_prev in df_pivot.columns:
                        df_pivot.loc[cliente_prev, periodo_prev] = valor_prev


        # Ordenar períodos corretamente
        periodos_ordenados = sorted(df_pivot.columns, 
                                    key=lambda x: (int(x.split('/')[1]), 
                                                  ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                                                   'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'].index(x.split('/')[0])))
        df_pivot = df_pivot[periodos_ordenados]

        # Ordenar por valor total (maior para menor)
        df_pivot['Total'] = df_pivot.sum(axis=1)
        df_pivot = df_pivot.sort_values('Total', ascending=False)
        df_pivot = df_pivot.drop('Total', axis=1)

        # Criar tabs para diferentes visualizações
        tab1, tab2 = st.tabs(["📊 Visão por Cliente", "📈 Evolução Temporal"])

        with tab1:
            # TABELA DE PREVISÃO MÊS A MÊS
            st.markdown(f"""
                <div class='section-title'>
                    {ICONS['file_text']} Previsão Mês a Mês - Top {top_n} Clientes
                </div>
            """, unsafe_allow_html=True)

            # Criar HTML da tabela
            html_table = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{
                    margin: 0;
                    padding: 10px;
                    font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }}
                .fat-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                    border-radius: 12px;
                    overflow: hidden;
                }}
                .fat-table th {{
                    background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent']});
                    color: white;
                    padding: 14px 10px;
                    text-align: right;
                    font-weight: 600;
                    position: sticky;
                    top: 0;
                    z-index: 10;
                }}
                .fat-table th:first-child {{
                    text-align: left;
                    padding-left: 15px;
                }}
                .fat-table td {{
                    padding: 12px 10px;
                    text-align: right;
                    border-bottom: 1px solid {COLORS['light']};
                }}
                .fat-table td:first-child {{
                    text-align: left;
                    font-weight: 600;
                    color: {COLORS['primary']};
                    padding-left: 15px;
                }}
                .fat-table tr:hover {{
                    background-color: {COLORS['light']};
                }}
                .valor-realizado {{
                    background-color: #D1FAE5;
                    color: {COLORS['success']};
                    font-weight: 600;
                }}
                .valor-previsto {{
                    background-color: #FEF3C7;
                    color: {COLORS['warning']};
                    font-weight: 600;
                    font-style: italic;
                }}
                .table-container {{
                    max-height: 600px;
                    overflow-y: auto;
                    border-radius: 12px;
                    border: 1px solid {COLORS['gray_light']};
                }}
            </style>
            </head>
            <body>
            <div class='table-container'>
            <table class='fat-table'>
                <thead>
                    <tr>
                        <th>CLIENTE</th>
            """

            # Cabeçalhos dos períodos
            periodos_reais = df_real['Periodo'].unique()
            for periodo in periodos_ordenados:
                asterisco = '' if periodo in periodos_reais else ' *'
                html_table += f"<th>{periodo}{asterisco}</th>"

            html_table += "</tr></thead><tbody>"

            # Linhas de dados
            for cliente in df_pivot.index:
                html_table += f"<tr><td>{cliente}</td>"
                for periodo in periodos_ordenados:
                    valor = df_pivot.loc[cliente, periodo]
                    
                    # Calcular ícone de variação
                    icone = ''
                    idx_periodo = list(periodos_ordenados).index(periodo)
                    if idx_periodo > 0:
                        periodo_anterior = periodos_ordenados[idx_periodo - 1]
                        valor_anterior = df_pivot.loc[cliente, periodo_anterior]
                        diferenca = valor - valor_anterior
                        if diferenca > 100:
                            icone = ' <span style="color:#10b981;font-size:18px;font-weight:bold;">↑</span>'
                        elif diferenca < -100:
                            icone = ' <span style="color:#ef4444;font-size:18px;font-weight:bold;">↓</span>'

                    tipo_classe = 'valor-realizado' if periodo in periodos_reais else 'valor-previsto'
                    html_table += f"<td class='{tipo_classe}'>{format_currency(valor)}{icone}</td>"
                html_table += "</tr>"

            # Linha de totais
            html_table += f"<tr style='background-color: {COLORS['light']}; font-weight: bold;'><td>TOTAL</td>"
            for periodo in periodos_ordenados:
                total = df_pivot[periodo].sum()
                tipo_classe = 'valor-realizado' if periodo in periodos_reais else 'valor-previsto'
                html_table += f"<td class='{tipo_classe}'>{format_currency(total)}</td>"
            html_table += "</tr>"

            html_table += """
                </tbody>
            </table>
            </div>
            <p style='font-size: 11px; color: #64748B; margin-top: 10px; font-family: inherit;'>
            </p>
            </body>
            </html>
            """

            components.html(html_table, height=650, scrolling=True)

            # GRÁFICO TOP N CLIENTES
            st.markdown(f"""
                <div class='section-title' style='margin-top: 2.5rem;'>
                    {ICONS['users']} Top {top_n} Clientes
                </div>
            """, unsafe_allow_html=True)

            # Gráfico de barras horizontal
            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=top_clientes['Cliente'],
                x=top_clientes['Valor_Historico'],
                orientation='h',
                marker=dict(
                    color=top_clientes['Valor_Historico'],
                    colorscale='Blues',
                    showscale=False
                ),
                text=[format_currency(v) for v in top_clientes['Valor_Historico']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Faturamento: %{text}<extra></extra>'
            ))

            fig.update_layout(
                height=max(400, top_n * 35),
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(
                    title="Faturamento (R$)",
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(title="", autorange='reversed'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='IBM Plex Sans')
            )

            st.plotly_chart(fig, use_container_width=True)




        with tab2:
            st.markdown(f"""
                <div class='section-title'>
                    {ICONS['chart']} Evolução Temporal
                </div>
            """, unsafe_allow_html=True)

            # Selecionar cliente
            cliente_selecionado = st.selectbox(
                "Selecione um cliente",
                options=top_clientes['Cliente'].tolist()
            )

            # Dados históricos do cliente
            df_cliente_hist = df[df['GRUPO CLIENTE'] == cliente_selecionado].groupby('Periodo')['Vlr Valido'].sum().reset_index()
            df_cliente_hist['Tipo'] = 'Histórico'

            # Dados de previsão do cliente
            df_cliente_prev = df_previsao[df_previsao['Cliente'] == cliente_selecionado][['Periodo', 'Valor']].copy()
            df_cliente_prev.columns = ['Periodo', 'Vlr Valido']
            df_cliente_prev['Tipo'] = 'Previsão'

            # Combinar
            df_cliente_completo = pd.concat([df_cliente_hist, df_cliente_prev], ignore_index=True)

            # Gráfico
            fig = go.Figure()

            # Linha histórica
            df_hist = df_cliente_completo[df_cliente_completo['Tipo'] == 'Histórico']
            fig.add_trace(go.Scatter(
                x=df_hist['Periodo'],
                y=df_hist['Vlr Valido'],
                mode='lines+markers',
                name='Histórico',
                line=dict(color=COLORS['success'], width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor=f"rgba(5, 150, 105, 0.1)"
            ))

            # Linha de previsão
            df_prev = df_cliente_completo[df_cliente_completo['Tipo'] == 'Previsão']
            if not df_prev.empty and not df_hist.empty:
                # Conectar último ponto histórico
                ultimo_hist = df_hist.iloc[-1]
                df_prev_plot = pd.concat([
                    pd.DataFrame([ultimo_hist]),
                    df_prev
                ])

                fig.add_trace(go.Scatter(
                    x=df_prev_plot['Periodo'],
                    y=df_prev_plot['Vlr Valido'],
                    mode='lines+markers',
                    name='Previsão',
                    line=dict(color=COLORS['warning'], width=3, dash='dash'),
                    marker=dict(size=8, symbol='diamond'),
                    fill='tozeroy',
                    fillcolor=f"rgba(245, 158, 11, 0.1)"
                ))

            fig.update_layout(
                height=450,
                xaxis_title="Período",
                yaxis_title="Faturamento (R$)",
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                font=dict(family='IBM Plex Sans')
            )

            st.plotly_chart(fig, use_container_width=True)

# ==================== PÁGINA: MIX DE PRODUTOS ====================
elif st.session_state.pagina_atual == 'mix':
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                Mix de Produtos
            </h1>
            <p class='page-subtitle'>
                Distribuição de receita por tipo de serviço
            </p>
        </div>
    """, unsafe_allow_html=True)

    df = st.session_state.df_base

    if df.empty:
        st.warning("⚠️ Nenhum dado disponível.")
    else:
        # Agrupar por serviço
        df_servicos = df.groupby('tpServ')['Vlr Valido'].sum().reset_index()
        df_servicos = df_servicos.sort_values('Vlr Valido', ascending=False)
        df_servicos['Percentual'] = (df_servicos['Vlr Valido'] / df_servicos['Vlr Valido'].sum()) * 100

        # Cards de métricas por serviço
        st.markdown(f"""
            <div class='section-title'>
                {ICONS['target']} Principais Serviços
            </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for idx, (_, row) in enumerate(df_servicos.head(6).iterrows()):
            with cols[idx % 3]:
                servico = row['tpServ']
                valor = row['Vlr Valido']
                perc = row['Percentual']
                cor = CORES_SERVICOS.get(servico, COLORS['gray'])

                st.markdown(f"""
                    <div class='metric-card' style='--card-color: {cor}; --card-color-light: {cor}88;'>
                        <div class='metric-icon'>
                            {ICONS['chart']}
                        </div>
                        <div class='metric-label'>{servico}</div>
                        <div class='metric-value'>{format_currency(valor)}</div>
                        <div class='metric-subtitle'>{format_percentage(perc)} do total</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
                <div class='section-title'>
                    {ICONS['pie_chart']} Distribuição Percentual
                </div>
            """, unsafe_allow_html=True)

            fig = go.Figure(data=[go.Pie(
                labels=df_servicos['tpServ'],
                values=df_servicos['Vlr Valido'],
                hole=0.4,
                marker=dict(
                    colors=[CORES_SERVICOS.get(s, COLORS['gray']) for s in df_servicos['tpServ']]
                ),
                textinfo='label+percent',
                textfont=dict(size=12, family='IBM Plex Sans'),
                hovertemplate='<b>%{label}</b><br>%{value:,.2f}<br>%{percent}<extra></extra>'
            )])

            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='IBM Plex Sans')
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"""
                <div class='section-title'>
                    {ICONS['bar_chart']} Ranking de Serviços
                </div>
            """, unsafe_allow_html=True)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=df_servicos['tpServ'],
                x=df_servicos['Vlr Valido'],
                orientation='h',
                marker=dict(
                    color=[CORES_SERVICOS.get(s, COLORS['gray']) for s in df_servicos['tpServ']]
                ),
                text=[format_currency(v) for v in df_servicos['Vlr Valido']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>%{text}<extra></extra>'
            ))

            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(
                    title="Faturamento (R$)",
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                yaxis=dict(title="", autorange='reversed'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='IBM Plex Sans')
            )

            st.plotly_chart(fig, use_container_width=True)

        # Evolução por serviço
        st.markdown(f"""
            <div class='section-title' style='margin-top: 2.5rem;'>
                {ICONS['trending_up']} Evolução por Serviço
            </div>
        """, unsafe_allow_html=True)

        df_evolucao = df.groupby(['Periodo', 'tpServ'])['Vlr Valido'].sum().reset_index()

        fig = go.Figure()

        for servico in sorted(df['tpServ'].unique()):
            df_serv = df_evolucao[df_evolucao['tpServ'] == servico]
            fig.add_trace(go.Scatter(
                x=df_serv['Periodo'],
                y=df_serv['Vlr Valido'],
                mode='lines+markers',
                name=servico,
                line=dict(width=2.5, color=CORES_SERVICOS.get(servico, COLORS['gray'])),
                marker=dict(size=6)
            ))

        fig.update_layout(
            height=450,
            xaxis_title="Período",
            yaxis_title="Faturamento (R$)",
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(family='IBM Plex Sans')
        )

        st.plotly_chart(fig, use_container_width=True)

# ==================== PÁGINA: CONSOLIDADO & PROJEÇÃO ====================
elif st.session_state.pagina_atual == 'consolidado':
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                Consolidado & Projeção
            </h1>
            <p class='page-subtitle'>
                Visão geral do faturamento com projeções futuras
            </p>
        </div>
    """, unsafe_allow_html=True)

    df = st.session_state.df_base

    if df.empty:
        st.warning("⚠️ Nenhum dado disponível.")
    else:
        # Métricas principais
        faturamento_total = df['Vlr Valido'].sum()
        qtd_clientes = df['GRUPO CLIENTE'].nunique()
        
        # Último período
        ultimo_periodo = df.sort_values(['ANO', 'MÊS']).iloc[-1]['Periodo']
        faturamento_ultimo_mes = df[df['Periodo'] == ultimo_periodo]['Vlr Valido'].sum()
        
        # Penúltimo período para calcular crescimento
        periodos_ordenados = sorted(df['Periodo'].unique())
        if len(periodos_ordenados) >= 2:
            penultimo_periodo = periodos_ordenados[-2]
            faturamento_penultimo_mes = df[df['Periodo'] == penultimo_periodo]['Vlr Valido'].sum()
            crescimento = ((faturamento_ultimo_mes / faturamento_penultimo_mes) - 1) * 100 if faturamento_penultimo_mes > 0 else 0
        else:
            crescimento = 3.0

        # Projeção próximo mês
        previsao_prox_mes = faturamento_ultimo_mes * 1.03
        ticket_medio = faturamento_total / qtd_clientes if qtd_clientes > 0 else 0

        # Cards principais
        col1, col2, col3, col4 = st.columns(4)

        cards_data = [
            (col1, COLORS['secondary'], COLORS['accent'], 'Faturamento Total', faturamento_total, 'Acumulado', 'dollar'),
            (col2, COLORS['warning'], COLORS['danger'], 'Previsão Próximo Mês', previsao_prox_mes, f'+{format_percentage(crescimento)}', 'trending_up'),
            (col3, COLORS['info'], COLORS['secondary'], 'Clientes Ativos', qtd_clientes, ultimo_periodo, 'users'),
            (col4, COLORS['accent'], COLORS['success'], 'Ticket Médio', ticket_medio, 'por cliente', 'credit_card')
        ]

        for col, cor_start, cor_end, label, value, subtitle, icon in cards_data:
            with col:
                # Formatação específica por tipo de card
                if label == 'Clientes Ativos':
                    valor_formatado = value  # Apenas número inteiro, sem formatação
                elif isinstance(value, (int, float)):
                    valor_formatado = format_currency(value)  # Valores monetários
                else:
                    valor_formatado = value
                
                st.markdown(f"""
                    <div class='gradient-card' style='--gradient-start: {cor_start}; --gradient-end: {cor_end};'>
                        <div class='gradient-card-label'>{label}</div>
                        <div class='gradient-card-value'>{valor_formatado}</div>
                        <div class='gradient-card-footer'>{subtitle}</div>
                    </div>
                """, unsafe_allow_html=True)


        st.markdown("---")

        # Configuração de projeção
        col1, col2 = st.columns([4, 2])
        with col1:
            st.markdown(f"""
                <div class='section-title'>
                    {ICONS['settings']} Configuração de Projeção
                </div>
            """, unsafe_allow_html=True)
        with col2:
            meses_projecao = st.slider("Meses para projetar", 3, 12, 6)

        # Gerar dados históricos + projeção
        df_historico = df.groupby(['MÊS', 'ANO', 'Periodo'])['Vlr Valido'].sum().reset_index()
        df_historico = df_historico.sort_values(['ANO', 'MÊS'])
        df_historico['Tipo'] = 'Realizado'

        # Gerar projeção total
        df_ativacoes_cons = carregar_ativacoes()
        df_previsao_total = gerar_previsao_com_ativacoes(df, df_ativacoes_cons, meses_projecao)
        df_proj_agregado = df_previsao_total.groupby(['Periodo', 'MÊS', 'ANO'])['Valor'].sum().reset_index()
        df_proj_agregado['Tipo'] = 'Projetado'
        df_proj_agregado.columns = ['Periodo', 'MÊS', 'ANO', 'Vlr Valido', 'Tipo']

        # Combinar
        df_completo = pd.concat([df_historico[['Periodo', 'MÊS', 'ANO', 'Vlr Valido', 'Tipo']], 
                                df_proj_agregado], ignore_index=True)

        # Gráfico de linha temporal
        st.markdown(f"""
            <div class='section-title'>
                {ICONS['trending_up']} Evolução e Projeção de Faturamento
            </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()

        # Linha realizada
        df_real = df_completo[df_completo['Tipo'] == 'Realizado']
        fig.add_trace(go.Scatter(
            x=df_real['Periodo'],
            y=df_real['Vlr Valido'],
            mode='lines+markers',
            name='Faturamento Realizado',
            line=dict(color=COLORS['success'], width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor=f"rgba(5, 150, 105, 0.1)"
        ))

        # Linha projetada
        df_proj = df_completo[df_completo['Tipo'] == 'Projetado']
        if not df_proj.empty and not df_real.empty:
            # Conectar último ponto real
            ultimo_real = df_real.iloc[-1]
            df_proj_plot = pd.concat([
                pd.DataFrame([ultimo_real]),
                df_proj
            ])

            fig.add_trace(go.Scatter(
                x=df_proj_plot['Periodo'],
                y=df_proj_plot['Vlr Valido'],
                mode='lines+markers',
                name='Projeção',
                line=dict(color=COLORS['warning'], width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond'),
                fill='tozeroy',
                fillcolor=f"rgba(245, 158, 11, 0.1)"
            ))

        fig.update_layout(
            height=500,
            xaxis_title="Período",
            yaxis_title="Faturamento (R$)",
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(family='IBM Plex Sans')
        )

        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de área empilhado por serviço
        st.markdown(f"""
            <div class='section-title' style='margin-top: 2.5rem;'>
                {ICONS['pie_chart']} Breakdown por Tipo de Serviço
            </div>
        """, unsafe_allow_html=True)

        df_servicos = df.groupby(['Periodo', 'tpServ'])['Vlr Valido'].sum().reset_index()

        fig = go.Figure()

        for servico in sorted(df['tpServ'].unique()):
            df_serv = df_servicos[df_servicos['tpServ'] == servico]
            fig.add_trace(go.Scatter(
                x=df_serv['Periodo'],
                y=df_serv['Vlr Valido'],
                mode='lines',
                name=servico,
                stackgroup='one',
                line=dict(width=0.5, color=CORES_SERVICOS.get(servico, COLORS['gray'])),
                fillcolor=CORES_SERVICOS.get(servico, COLORS['gray'])
            ))

        fig.update_layout(
            height=400,
            xaxis_title="Período",
            yaxis_title="Faturamento (R$)",
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='IBM Plex Sans')
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela resumo
        st.markdown(f"""
            <div class='section-title' style='margin-top: 2.5rem;'>
                {ICONS['file_text']} Resumo por Período
            </div>
        """, unsafe_allow_html=True)

        df_resumo = df_completo.copy()
        df_resumo = df_resumo.sort_values(['ANO', 'MÊS'])

        # Calcular variação
        df_resumo['Variacao'] = df_resumo['Vlr Valido'].pct_change() * 100

        # Gerar HTML completo
        html_resumo = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }}
            .resumo-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9rem;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }}
            .resumo-table thead {{
                background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
            }}
            .resumo-table th {{
                color: white;
                padding: 1rem;
                text-align: center;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.8rem;
            }}
            .resumo-table td {{
                padding: 0.9rem;
                text-align: center;
                border-bottom: 1px solid {COLORS['gray_light']};
                font-size: 0.85rem;
            }}
            .resumo-table tbody tr {{
                transition: background-color 0.2s;
            }}
            .resumo-table tbody tr:hover {{
                background-color: {COLORS['light']};
            }}
            .tipo-real {{
                background-color: rgba(5, 150, 105, 0.05);
            }}
            .tipo-proj {{
                background-color: rgba(245, 158, 11, 0.05);
            }}
            .badge {{
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 600;
            }}
            .badge-real {{
                background: rgba(5, 150, 105, 0.1);
                color: {COLORS['success']};
            }}
            .badge-proj {{
                background: rgba(245, 158, 11, 0.1);
                color: {COLORS['warning']};
            }}
        </style>
        </head>
        <body>
        <table class='resumo-table'>
            <thead>
                <tr>
                    <th>Período</th>
                    <th>Tipo</th>
                    <th>Faturamento</th>
                    <th>Variação MoM</th>
                </tr>
            </thead>
            <tbody>
        """

        for _, row in df_resumo.iterrows():
            tipo_classe = 'tipo-real' if row['Tipo'] == 'Realizado' else 'tipo-proj'
            badge_classe = 'badge-real' if row['Tipo'] == 'Realizado' else 'badge-proj'
            variacao = row['Variacao']

            if pd.notna(variacao):
                if variacao > 5:
                    cor_variacao = COLORS['success']
                elif variacao > 0:
                    cor_variacao = COLORS['warning']
                else:
                    cor_variacao = COLORS['danger']
                variacao_str = f"<span style='color: {cor_variacao}; font-weight: 700;'>{variacao:+.1f}%</span>"
            else:
                variacao_str = "<span style='color: #9CA3AF;'>—</span>"

            html_resumo += f"""
            <tr class='{tipo_classe}'>
                <td style='font-weight: 600; color: {COLORS['primary']};'>{row['Periodo']}</td>
                <td><span class='badge {badge_classe}'>{row['Tipo']}</span></td>
                <td style='font-weight: 600; font-family: Sora;'>{format_currency(row['Vlr Valido'])}</td>
                <td>{variacao_str}</td>
            </tr>
            """

        html_resumo += """
            </tbody>
        </table>
        </body>
        </html>
        """

        # Calcular altura da tabela
        altura_resumo = min(600, len(df_resumo) * 50 + 100)
        components.html(html_resumo, height=altura_resumo, scrolling=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <div style='font-family: Sora; font-weight: 700; color: {COLORS["primary"]}; font-size: 0.95rem; margin-bottom: 0.5rem;'>
            Base Telco v2.0
        </div>
        <div style='color: {COLORS["gray"]}; font-size: 0.8rem; font-weight: 500;'>
            Analytics & Business Intelligence
        </div>
        <div style='color: {COLORS["gray"]}; font-size: 0.75rem; margin-top: 0.5rem; opacity: 0.8;'>
            {datetime.now().strftime("%d/%m/%Y %H:%M")} • Todos os direitos reservados
        </div>
    </div>
""", unsafe_allow_html=True)
