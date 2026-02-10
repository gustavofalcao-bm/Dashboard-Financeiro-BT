import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from modules.config import ICONS, COLORS, CORES_SERVICOS
from modules.utils import format_currency, format_percentage, get_color_by_growth
from modules.data_loader import gerar_previsao_com_ativacoes, carregar_ativacoes

def render_consolidado(df):
    """Renderiza a página de Consolidado & Projeção - EXATO DO ORIGINAL"""
    
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

    if df.empty:
        st.warning("⚠️ Nenhum dado disponível.")
        return
    
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
                valor_formatado = value
            elif isinstance(value, (int, float)):
                valor_formatado = format_currency(value)
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

    altura_resumo = min(600, len(df_resumo) * 50 + 100)
    components.html(html_resumo, height=altura_resumo, scrolling=True)