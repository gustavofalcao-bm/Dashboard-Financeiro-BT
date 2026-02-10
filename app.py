import streamlit as st
import pandas as pd
from datetime import datetime

# Imports dos módulos
from modules.config import ICONS, COLORS
from modules.styles import apply_premium_css
from modules.utils import load_logo, format_currency
from modules.data_loader import load_data, carregar_ativacoes

# Imports das views
from views.previsao import render_previsao
from views.consolidado import render_consolidado
from views.mix_produtos import render_mix_produtos
from views.ativacoes import render_ativacoes

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Base Telco | Faturamento & Previsões",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        'ativacoes': ('users', 'Ativações em Andamento'),
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

# ==================== ROTEAMENTO DE PÁGINAS ====================
df = st.session_state.df_base
df_ativacoes = carregar_ativacoes()

if st.session_state.pagina_atual == 'previsao':
    render_previsao(df, df_ativacoes)

elif st.session_state.pagina_atual == 'ativacoes':
    render_ativacoes(df_ativacoes)

elif st.session_state.pagina_atual == 'mix':
    render_mix_produtos(df)

elif st.session_state.pagina_atual == 'consolidado':
    render_consolidado(df)

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
