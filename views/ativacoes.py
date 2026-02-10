import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from modules.config import ICONS, COLORS
from modules.utils import format_currency

def render_ativacoes(df_ativacoes):
    """Renderiza a página de Ativações em Andamento"""
    
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                Ativações em Andamento
            </h1>
            <p class='page-subtitle'>
                Acompanhamento de clientes em processo de implantação
            </p>
        </div>
    """, unsafe_allow_html=True)

    if df_ativacoes.empty:
        st.warning("⚠️ Nenhuma ativação encontrada na base de dados")
        return
    
    # Métricas
    total_ativacoes = len(df_ativacoes)
    mrr_total = df_ativacoes['VALOR_MRR'].sum()
    ticket_medio = mrr_total / total_ativacoes if total_ativacoes > 0 else 0
    
    data_atual = datetime.now()
    df_ativacoes['DIAS_ATE_ATIVACAO'] = (df_ativacoes['DATA_PREVISTA'] - pd.Timestamp(data_atual)).dt.days
    proximos_30_dias = len(df_ativacoes[df_ativacoes['DIAS_ATE_ATIVACAO'] <= 30])
    
    # Cards com gradiente
    col1, col2, col3, col4 = st.columns(4)
    
    cards_data = [
        (col1, COLORS['info'], COLORS['accent'], 'Total de Ativações', total_ativacoes, 'Clientes em implantação'),
        (col2, COLORS['success'], COLORS['accent'], 'MRR Total', format_currency(mrr_total), 'Faturamento esperado'),
        (col3, COLORS['warning'], COLORS['danger'], 'Ticket Médio', format_currency(ticket_medio), 'Por cliente'),
        (col4, COLORS['danger'], COLORS['warning'], 'Próximos 30 Dias', proximos_30_dias, 'Ativações previstas')
    ]
    
    for col, cor_start, cor_end, label, value, subtitle in cards_data:
        with col:
            st.markdown(f"""
                <div class='gradient-card' style='--gradient-start: {cor_start}; --gradient-end: {cor_end};'>
                    <div class='gradient-card-label'>{label}</div>
                    <div class='gradient-card-value'>{value}</div>
                    <div class='gradient-card-footer'>{subtitle}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Filtros
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['settings']} Filtros
        </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        clientes = ['Todos'] + sorted(df_ativacoes['CLIENTE'].unique().tolist())
        filtro_cliente = st.selectbox("Cliente", clientes, key='filtro_cliente_ativ')
    
    with col_f2:
        produtos = ['Todos'] + sorted(df_ativacoes['PRODUTO'].unique().tolist())
        filtro_produto = st.selectbox("Produto", produtos, key='filtro_produto_ativ')
    
    with col_f3:
        status_list = ['Todos'] + sorted(df_ativacoes['STATUS'].unique().tolist())
        filtro_status = st.selectbox("Status", status_list, key='filtro_status_ativ')
    
    # Aplicar filtros
    df_filtrado = df_ativacoes.copy()
    
    if filtro_cliente != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['CLIENTE'] == filtro_cliente]
    
    if filtro_produto != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['PRODUTO'] == filtro_produto]
    
    if filtro_status != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['STATUS'] == filtro_status]

    st.markdown("---")

    # Tabela
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['file_text']} Lista de Ativações
        </div>
    """, unsafe_allow_html=True)
    
    st.info(f"📊 Mostrando **{len(df_filtrado)}** de **{len(df_ativacoes)}** ativações")
    
    # Preparar dados
    df_exibir = df_filtrado[['CLIENTE', 'PRODUTO', 'DATA_PREVISTA', 'VALOR_MRR', 'STATUS', 'DIAS_ATE_ATIVACAO']].copy()
    df_exibir['DATA_PREVISTA_FMT'] = df_exibir['DATA_PREVISTA'].dt.strftime('%d/%m/%Y')
    df_exibir['VALOR_MRR_FMT'] = df_exibir['VALOR_MRR'].apply(format_currency)
    
    def get_urgencia(dias):
        if dias < 0:
            return ('🔴 Atrasado', '#FEE2E2', '#DC2626')
        elif dias <= 7:
            return ('🟡 Urgente', '#FEF3C7', '#F59E0B')
        elif dias <= 30:
            return ('🟢 Próximo', '#D1FAE5', '#059669')
        else:
            return ('⚪ Futuro', '#F1F5F9', '#64748B')
    
    # Construir HTML - MÉTODO QUE FUNCIONA
    css = """
    <style>
        .table-ativ-container {
            max-height: 600px;
            overflow-y: auto;
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid #CBD5E1;
            position: relative;
        }
        .table-ativ {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            font-family: 'IBM Plex Sans', sans-serif;
        }
        .table-ativ thead {
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .table-ativ th {
            background: linear-gradient(135deg, #1E40AF, #0EA5E9);
            color: white;
            padding: 14px 10px;
            text-align: center;
            font-weight: 600;
            border-bottom: 2px solid #0EA5E9;
        }
        .table-ativ th:first-child {
            text-align: left;
            padding-left: 15px;
        }
        .table-ativ td {
            padding: 12px 10px;
            text-align: center;
            border-bottom: 1px solid #F8FAFC;
            vertical-align: middle;
        }
        .table-ativ td:first-child {
            text-align: left;
            font-weight: 600;
            color: #0F172A;
            padding-left: 15px;
        }
        .table-ativ tbody tr:hover {
            background-color: #F8FAFC;
        }
        .badge-urgencia {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
        }
    </style>
    """
    
    html = css + '<div class="table-ativ-container"><table class="table-ativ">'
    html += '<thead><tr>'
    html += '<th>CLIENTE</th><th>PRODUTO</th><th>DATA PREVISTA</th>'
    html += '<th>VALOR MRR</th><th>STATUS</th><th>URGÊNCIA</th>'
    html += '</tr></thead><tbody>'
    
    for _, row in df_exibir.iterrows():
        urgencia_texto, bg_color, text_color = get_urgencia(row['DIAS_ATE_ATIVACAO'])
        html += '<tr>'
        html += f"<td>{row['CLIENTE']}</td>"
        html += f"<td>{row['PRODUTO']}</td>"
        html += f"<td>{row['DATA_PREVISTA_FMT']}</td>"
        html += f"<td style='font-weight:600;color:#059669;'>{row['VALOR_MRR_FMT']}</td>"
        html += f"<td>{row['STATUS']}</td>"
        html += f"<td><span class='badge-urgencia' style='background:{bg_color};color:{text_color};'>{urgencia_texto}</span></td>"
        html += '</tr>'
    
    html += '</tbody></table></div>'
    
    components.html(html, height=650, scrolling=True)

    st.markdown("---")

    # Download
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['file_text']} Exportar Dados
        </div>
    """, unsafe_allow_html=True)

    csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"ativacoes_em_andamento_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
