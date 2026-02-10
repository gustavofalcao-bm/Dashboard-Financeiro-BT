import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.config import ICONS, COLORS, CORES_SERVICOS
from modules.utils import format_currency, format_percentage

def render_mix_produtos(df):
    """Renderiza a página de Mix de Produtos - EXATO DO ORIGINAL"""
    
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

    if df.empty:
        st.warning("⚠️ Nenhum dado disponível.")
        return
    
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

