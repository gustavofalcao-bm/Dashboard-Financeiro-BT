import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from modules.config import ICONS, COLORS
from modules.utils import format_currency, calcular_valor_proporcional
from modules.data_loader import gerar_previsao_com_ativacoes, carregar_ativacoes

def render_previsao(df, df_ativacoes):
    """Renderiza a página de Previsão de Faturamento - EXATO DO ORIGINAL"""
    
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

    if df.empty:
        st.warning("⚠️ Nenhum dado disponível. Verifique o arquivo BD-FATURAMENTO.xlsx")
        return
    
    # Configurações
    col1, col2 = st.columns([3, 3])
    with col1:
        meses_previsao = st.slider("Meses de Previsão", 3, 12, 6)
    with col2:
        top_n = st.number_input("Top N Clientes", 5, 50, 15, 5)

    st.markdown("---")

    # Gerar previsão
    df_previsao = gerar_previsao_com_ativacoes(df, df_ativacoes, meses_previsao)

    # Agrupar por cliente
    clientes_total = df.groupby('GRUPO CLIENTE')['Vlr Valido'].sum().reset_index()
    clientes_total.columns = ['Cliente', 'Valor_Historico']
    clientes_total = clientes_total.sort_values('Valor_Historico', ascending=False)

    # Top N clientes
    top_clientes = clientes_total.head(top_n)

    # Cards de Pipeline de Ativações
    if not df_ativacoes.empty:
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

    # Adicionar clientes novos e preencher previsões
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

        # Construir HTML - MÉTODO QUE FUNCIONA
        css = """
        <style>
            .table-prev-container {
                max-height: 600px;
                overflow-y: auto;
                overflow-x: auto;
                border-radius: 12px;
                border: 1px solid #CBD5E1;
                position: relative;
            }
            .table-prev {
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                font-family: 'IBM Plex Sans', sans-serif;
            }
            .table-prev thead {
                position: sticky;
                top: 0;
                z-index: 100;
            }
            .table-prev th {
                background: linear-gradient(135deg, #1E40AF, #0EA5E9);
                color: white;
                padding: 14px 10px;
                text-align: center;
                font-weight: 600;
                border-bottom: 2px solid #0EA5E9;
            }
            .table-prev th:first-child {
                text-align: left;
                padding-left: 15px;
                position: sticky;
                left: 0;
                z-index: 101;
                background: linear-gradient(135deg, #1E40AF, #0EA5E9);
            }
            .table-prev td {
                padding: 12px 10px;
                text-align: center;
                border-bottom: 1px solid #F8FAFC;
                vertical-align: middle;
            }
            .table-prev td:first-child {
                text-align: left;
                font-weight: 600;
                color: #0F172A;
                padding-left: 15px;
                position: sticky;
                left: 0;
                background: white;
                z-index: 10;
            }
            .table-prev tbody tr:hover td {
                background-color: #F8FAFC;
            }
            .table-prev tbody tr:hover td:first-child {
                background-color: #F8FAFC;
            }
            .valor-realizado {
                background-color: #D1FAE5;
                color: #059669;
                font-weight: 600;
            }
            .valor-previsto {
                background-color: #FEF3C7;
                color: #F59E0B;
                font-weight: 600;
                font-style: italic;
            }
            .table-prev tbody tr:last-child {
                background-color: #F8FAFC;
                font-weight: bold;
            }
            .table-prev tbody tr:last-child td {
                border-top: 2px solid #CBD5E1;
                padding-top: 14px;
                padding-bottom: 14px;
            }
        </style>
        """
        
        html_table = css + '<div class="table-prev-container"><table class="table-prev">'
        html_table += '<thead><tr><th>CLIENTE</th>'
        
        # Cabeçalhos dos períodos
        periodos_reais = df_real['Periodo'].unique()
        for periodo in periodos_ordenados:
            asterisco = '' if periodo in periodos_reais else ' *'
            html_table += f'<th>{periodo}{asterisco}</th>'
        
        html_table += '</tr></thead><tbody>'
        
        # Linhas de dados
        for cliente in df_pivot.index:
            html_table += f'<tr><td>{cliente}</td>'
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
            html_table += '</tr>'
        
        # Linha de totais
        html_table += '<tr><td>TOTAL</td>'
        for periodo in periodos_ordenados:
            total = df_pivot[periodo].sum()
            tipo_classe = 'valor-realizado' if periodo in periodos_reais else 'valor-previsto'
            html_table += f"<td class='{tipo_classe}'>{format_currency(total)}</td>"
        html_table += '</tr>'
        
        html_table += '</tbody></table></div>'
        
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

