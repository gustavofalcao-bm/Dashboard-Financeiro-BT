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

# ==================== PALETA DE CORES ====================
COLORS = {
    'primary': '#1a1a1a',
    'secondary': '#0288D1',
    'accent': '#00ACC1',
    'success': '#4CAF50',
    'warning': '#FFB74D',
    'danger': '#E57373',
    'info': '#64B5F6',
    'light': '#FAFAFA',
    'gray': '#BDBDBD',
    'dark_gray': '#616161',
    'white': '#FFFFFF',
    # Serviços
    'toip': '#2196F3',
    'cldpbx': '#4CAF50',
    'video': '#9C27B0',
    'ip': '#FF9800',
    'ccenter': '#F44336',
    'out': '#607D8B'
}

CORES_SERVICOS = {
    'TOIP': COLORS['toip'],
    'CLDPBX': COLORS['cldpbx'],
    'VIDEO': COLORS['video'],
    'IP': COLORS['ip'],
    'CCENTER': COLORS['ccenter'],
    'OUT': COLORS['out']
}

# ==================== FUNÇÕES UTILITÁRIAS ====================

def load_logo():
    """Carrega a logo da Base Telco"""
    try:
        with open("logo.png", "rb") as f:
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

def gerar_previsao_simples(df, meses_futuros=6):
    """Gera previsão simples baseada no último mês conhecido com crescimento fixo de 3%"""
    # Agrupa por cliente e pega o valor do último mês
    ultima_base = df.groupby('GRUPO CLIENTE')['Vlr Valido'].sum().reset_index()
    ultima_base.columns = ['Cliente', 'Valor_Base']

    # Taxa de crescimento padrão (3% ao mês) - FIXO, sem input do usuário
    taxa_crescimento = 1.03

    previsoes = []
    mes_atual = df['MÊS'].max() if not df.empty else 1
    ano_atual = df['ANO'].max() if not df.empty else 2026

    for i in range(1, meses_futuros + 1):
        mes = mes_atual + i
        ano = ano_atual

        # Ajustar ano se passar de 12 meses
        while mes > 12:
            mes -= 12
            ano += 1

        # Nome do mês
        meses_nome = ['', 'JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                      'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        periodo_nome = f"{meses_nome[mes]}/{ano}"

        # Calcular previsão com crescimento
        for _, row in ultima_base.iterrows():
            valor_previsto = row['Valor_Base'] * (taxa_crescimento ** i)
            previsoes.append({
                'Cliente': row['Cliente'],
                'Periodo': periodo_nome,
                'MÊS': mes,
                'ANO': ano,
                'Valor': valor_previsto,
                'Tipo': 'Previsto'
            })

    return pd.DataFrame(previsoes)

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
            <div style='text-align: center; padding: 20px 0;'>
                <img src='data:image/png;base64,{logo_base64}' style='max-width: 180px;'>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 📊 Base Telco")

    st.markdown("---")
    st.markdown("### 📈 Faturamento & BI")

    # Menu de navegação - CORRIGIDO
    menu_options = {
        'previsao': '📅 Previsão de Faturamento',
        'mix': '🎯 Mix de Produtos',
        'consolidado': '📊 Consolidado & Projeção'
    }

    for key, label in menu_options.items():
        if st.button(label, key=f"btn_{key}", use_container_width=True):
            st.session_state.pagina_atual = key

    st.markdown("---")

    # Informações da base
    if not st.session_state.df_base.empty:
        st.markdown("### 📋 Informações")
        df = st.session_state.df_base

        total_fat = df['Vlr Valido'].sum()
        qtd_clientes = df['GRUPO CLIENTE'].nunique()
        qtd_servicos = df['tpServ'].nunique()

        st.metric("Faturamento Total", format_currency(total_fat))
        st.metric("Clientes Ativos", qtd_clientes)
        st.metric("Tipos de Serviços", qtd_servicos)

        # Período da base
        periodos = sorted(df['Periodo'].unique())
        st.markdown(f"**Período:** {periodos[0]} a {periodos[-1]}" if len(periodos) > 1 else f"**Período:** {periodos[0]}")

    st.markdown("---")
    st.markdown(f"""
        <div style='text-align: center; font-size: 11px; color: {COLORS["gray"]}'>
            Base Telco v1.0<br>
            {datetime.now().strftime('%d/%m/%Y')}
        </div>
    """, unsafe_allow_html=True)

# ==================== PÁGINA: PREVISÃO DE FATURAMENTO ====================
if st.session_state.pagina_atual == 'previsao':
    st.markdown(f"""
        <h1 style='color: {COLORS["secondary"]}; margin-bottom: 30px;'>
            📅 Previsão de Faturamento por Cliente
        </h1>
    """, unsafe_allow_html=True)

    df = st.session_state.df_base

    if df.empty:
        st.warning("Nenhum dado disponível. Verifique o arquivo BD-FATURAMENTO.xlsx")
    else:
        # Configurações
        col1, col2 = st.columns([3, 3])
        with col1:
            meses_previsao = st.slider("Meses de Previsão", 3, 12, 6)
        with col2:
            top_n = st.number_input("Top N Clientes", 5, 50, 15, 5)

        st.markdown("---")

        # Processar dados reais (TODOS os meses da base)
        df_real = df.groupby(['GRUPO CLIENTE', 'Periodo', 'MÊS', 'ANO'])['Vlr Valido'].sum().reset_index()
        df_real['Tipo'] = 'Realizado'
        df_real.columns = ['Cliente', 'Periodo', 'MÊS', 'ANO', 'Valor', 'Tipo']

        # Gerar previsões (sempre a partir do último mês da base)
        df_previsao = gerar_previsao_simples(df, meses_previsao)

        # Combinar dados
        df_completo = pd.concat([df_real, df_previsao], ignore_index=True)

        # Filtrar top N clientes por valor total
        top_clientes = df_real.groupby('Cliente')['Valor'].sum().nlargest(top_n).index
        df_filtrado = df_completo[df_completo['Cliente'].isin(top_clientes)]

        # Criar tabela pivotada
        df_pivot = df_filtrado.pivot_table(
            index='Cliente',
            columns='Periodo',
            values='Valor',
            aggfunc='sum',
            fill_value=0
        )

        # Ordenar períodos corretamente
        periodos_ordenados = sorted(df_pivot.columns, 
                                    key=lambda x: (int(x.split('/')[1]), 
                                                  ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                                                   'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'].index(x.split('/')[0])))
        df_pivot = df_pivot[periodos_ordenados]

        # Ordenar por valor total
        df_pivot['Total'] = df_pivot.sum(axis=1)
        df_pivot = df_pivot.sort_values('Total', ascending=False)
        df_pivot = df_pivot.drop('Total', axis=1)

        # Criar HTML da tabela - FONTE NORMALIZADA
        html_table = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
            }}
            .fat-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                font-family: inherit;
            }}
            .fat-table th {{
                background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent']});
                color: white;
                padding: 12px 8px;
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
                padding: 10px 8px;
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
                background-color: #E8F5E9;
                color: {COLORS['success']};
                font-weight: 600;
            }}
            .valor-previsto {{
                background-color: #FFF3E0;
                color: {COLORS['warning']};
                font-weight: 600;
                font-style: italic;
            }}
            .table-container {{
                max-height: 600px;
                overflow-y: auto;
                border-radius: 8px;
                border: 1px solid {COLORS['gray']};
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
            tipo_classe = 'realizado' if periodo in periodos_reais else 'previsto'
            asterisco = '' if periodo in periodos_reais else ' *'
            html_table += f"<th>{periodo}{asterisco}</th>"

        html_table += "</tr></thead><tbody>"

        # Linhas de dados
        for cliente in df_pivot.index:
            html_table += f"<tr><td>{cliente}</td>"
            for periodo in periodos_ordenados:
                valor = df_pivot.loc[cliente, periodo]
                tipo_classe = 'valor-realizado' if periodo in periodos_reais else 'valor-previsto'
                html_table += f"<td class='{tipo_classe}'>{format_currency(valor)}</td>"
            html_table += "</tr>"

        # Linha de totais
        html_table += "<tr style='background-color: #F5F5F5; font-weight: bold;'><td>TOTAL</td>"
        for periodo in periodos_ordenados:
            total = df_pivot[periodo].sum()
            tipo_classe = 'valor-realizado' if periodo in periodos_reais else 'valor-previsto'
            html_table += f"<td class='{tipo_classe}'>{format_currency(total)}</td>"
        html_table += "</tr>"

        html_table += """
            </tbody>
        </table>
        </div>
        <p style='font-size: 11px; color: gray; margin-top: 10px; font-family: inherit;'>
            * Valores previstos com crescimento de 3% a.m. (serão ajustados conforme ativações futuras)
        </p>
        </body>
        </html>
        """

        components.html(html_table, height=650, scrolling=True)

        # Gráfico de evolução - MELHORADO
        st.markdown("### 📈 Evolução Temporal - Top 5 Clientes")

        col1, col2 = st.columns([4, 2])
        with col1:
            st.info("💡 Gráfico com escala logarítmica para melhor visualização quando há grande disparidade de valores")
        with col2:
            usar_log = st.checkbox("Usar escala logarítmica", value=True)

        top5_clientes = df_pivot.head(5).index
        df_grafico = df_filtrado[df_filtrado['Cliente'].isin(top5_clientes)]

        fig = go.Figure()

        for cliente in top5_clientes:
            df_cliente = df_grafico[df_grafico['Cliente'] == cliente].sort_values(['ANO', 'MÊS'])

            # Separar realizado e previsto
            df_real_cliente = df_cliente[df_cliente['Tipo'] == 'Realizado']
            df_prev_cliente = df_cliente[df_cliente['Tipo'] == 'Previsto']

            # Linha realizada - MELHORADA
            if not df_real_cliente.empty:
                fig.add_trace(go.Scatter(
                    x=df_real_cliente['Periodo'],
                    y=df_real_cliente['Valor'],
                    mode='lines+markers',
                    name=cliente,
                    line=dict(width=4),
                    marker=dict(size=10)
                ))

            # Linha prevista (tracejada) - MELHORADA
            if not df_prev_cliente.empty:
                # Conectar último ponto real com primeiro previsto
                ultimo_real = df_real_cliente.iloc[-1] if not df_real_cliente.empty else None
                if ultimo_real is not None:
                    df_prev_plot = pd.concat([
                        pd.DataFrame([ultimo_real]),
                        df_prev_cliente
                    ])
                else:
                    df_prev_plot = df_prev_cliente

                fig.add_trace(go.Scatter(
                    x=df_prev_plot['Periodo'],
                    y=df_prev_plot['Valor'],
                    mode='lines+markers',
                    name=f"{cliente} (Previsão)",
                    line=dict(width=3, dash='dash'),
                    marker=dict(size=8, symbol='circle-open'),
                    showlegend=False
                ))

        # Aplicar escala logarítmica se selecionado
        yaxis_config = dict(title="Faturamento (R$)", gridcolor='rgba(0,0,0,0.05)')
        if usar_log:
            yaxis_config['type'] = 'log'

        fig.update_layout(
            height=500,
            xaxis_title="Período",
            yaxis=yaxis_config,
            hovermode='x unified',
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=False,
                showline=True,
                linewidth=1,
                linecolor='rgba(0,0,0,0.2)'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='rgba(0,0,0,0.1)',
                borderwidth=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

# ==================== PÁGINA: MIX DE PRODUTOS ====================
elif st.session_state.pagina_atual == 'mix':
    st.markdown(f"""
        <h1 style='color: {COLORS["secondary"]}; margin-bottom: 30px;'>
            🎯 Mix de Produtos por Cliente
        </h1>
    """, unsafe_allow_html=True)

    df = st.session_state.df_base

    if df.empty:
        st.warning("Nenhum dado disponível.")
    else:
        # Filtros
        col1, col2 = st.columns([3, 3])
        with col1:
            top_n = st.slider("Top N Clientes", 5, 30, 15, 5)
        with col2:
            servicos_selecionados = st.multiselect(
                "Filtrar Serviços",
                options=sorted(df['tpServ'].unique()),
                default=sorted(df['tpServ'].unique())
            )

        st.markdown("---")

        # Filtrar por serviços
        df_filtrado = df[df['tpServ'].isin(servicos_selecionados)] if servicos_selecionados else df

        # Criar matriz cliente x serviço
        df_mix = df_filtrado.groupby(['GRUPO CLIENTE', 'tpServ'])['Vlr Valido'].sum().reset_index()
        df_pivot = df_mix.pivot_table(
            index='GRUPO CLIENTE',
            columns='tpServ',
            values='Vlr Valido',
            fill_value=0
        )

        # Calcular total por cliente
        df_pivot['TOTAL'] = df_pivot.sum(axis=1)
        df_pivot = df_pivot.sort_values('TOTAL', ascending=False).head(top_n)

        # Criar tabela HTML
        servicos_ordem = sorted([col for col in df_pivot.columns if col != 'TOTAL'])

        html_table = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {
                margin: 0;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            .mix-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .mix-table th {
                background: linear-gradient(135deg, #0288D1, #00ACC1);
                color: white;
                padding: 12px 8px;
                text-align: center;
                font-weight: 600;
            }
            .mix-table th:first-child {
                text-align: left;
                padding-left: 15px;
            }
            .mix-table td {
                padding: 8px;
                text-align: center;
                border-bottom: 1px solid #FAFAFA;
            }
            .mix-table td:first-child {
                text-align: left;
                font-weight: 600;
                padding-left: 15px;
                color: #1a1a1a;
            }
            .mix-table tr:hover {
                background-color: #FAFAFA;
            }
            .valor-cell {
                font-weight: 600;
            }
            .pct-cell {
                font-size: 11px;
                color: #616161;
            }
            .total-col {
                background-color: #F5F5F5;
                font-weight: bold;
            }
        </style>
        </head>
        <body>
        <table class='mix-table'>
            <thead>
                <tr>
                    <th>CLIENTE</th>
        """

        cores_servicos_map = {
            'CCENTER': '#F44336',
            'CLDPBX': '#4CAF50',
            'IP': '#FF9800',
            'OUT': '#607D8B',
            'TOIP': '#2196F3',
            'VIDEO': '#9C27B0'
        }

        for servico in servicos_ordem:
            cor = cores_servicos_map.get(servico, '#BDBDBD')
            html_table += f"<th style='background-color: {cor};'>{servico}</th>"

        html_table += "<th style='background-color: #424242;'>TOTAL</th></tr></thead><tbody>"

        # Linhas de dados
        for cliente in df_pivot.index:
            html_table += f"<tr><td>{cliente}</td>"
            total_cliente = df_pivot.loc[cliente, 'TOTAL']

            for servico in servicos_ordem:
                valor = df_pivot.loc[cliente, servico]
                pct = (valor / total_cliente * 100) if total_cliente > 0 else 0

                # Cor de fundo baseada no valor (heatmap)
                if valor > 0:
                    cor_servico = cores_servicos_map.get(servico, '#BDBDBD')
                    # Converter hex para rgb
                    cor_hex = cor_servico.lstrip('#')
                    r, g, b = tuple(int(cor_hex[i:i+2], 16) for i in (0, 2, 4))
                    opacity = min(0.2 + (pct / 100), 0.8)
                    bg_color = f"background-color: rgba({r}, {g}, {b}, {opacity});"
                else:
                    bg_color = ""

                if valor > 0:
                    html_table += f"""
                    <td style='{bg_color}'>
                        <div class='valor-cell'>{format_currency(valor)}</div>
                        <div class='pct-cell'>({format_percentage(pct)})</div>
                    </td>
                    """
                else:
                    html_table += "<td style='color: #E0E0E0;'>-</td>"

            html_table += f"<td class='total-col'>{format_currency(total_cliente)}</td></tr>"

        # Linha de totais
        html_table += "<tr style='background-color: #EEEEEE; font-weight: bold;'><td>TOTAL</td>"
        for servico in servicos_ordem:
            total_servico = df_pivot[servico].sum()
            html_table += f"<td>{format_currency(total_servico)}</td>"

        total_geral = df_pivot['TOTAL'].sum()
        html_table += f"<td class='total-col'>{format_currency(total_geral)}</td></tr>"

        html_table += "</tbody></table></body></html>"

        # Usar components.html para renderizar
        altura_tabela = min(600, (top_n + 3) * 50)
        components.html(html_table, height=altura_tabela, scrolling=True)

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Distribuição por Serviço")
            df_servico_total = df_filtrado.groupby('tpServ')['Vlr Valido'].sum().reset_index()

            fig = go.Figure(data=[go.Pie(
                labels=df_servico_total['tpServ'],
                values=df_servico_total['Vlr Valido'],
                hole=0.4,
                marker=dict(colors=[CORES_SERVICOS.get(s, COLORS['gray']) for s in df_servico_total['tpServ']])
            )])

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📈 Top 10 por Serviço")
            df_top_servico = df_filtrado.groupby('tpServ')['Vlr Valido'].sum().sort_values(ascending=True).tail(10)

            fig = go.Figure(data=[go.Bar(
                x=df_top_servico.values,
                y=df_top_servico.index,
                orientation='h',
                marker=dict(color=[CORES_SERVICOS.get(s, COLORS['gray']) for s in df_top_servico.index])
            )])

            fig.update_layout(
                height=400,
                xaxis_title="Faturamento (R$)",
                yaxis_title="",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

# ==================== PÁGINA: CONSOLIDADO ====================
elif st.session_state.pagina_atual == 'consolidado':
    st.markdown(f"""
        <h1 style='color: {COLORS["secondary"]}; margin-bottom: 30px;'>
            📊 Consolidado & Projeção
        </h1>
    """, unsafe_allow_html=True)

    df = st.session_state.df_base

    if df.empty:
        st.warning("Nenhum dado disponível.")
    else:
        # KPIs no topo - usa o último mês disponível na base
        ultimo_mes = df[df['MÊS'] == df['MÊS'].max()]
        total_fat = ultimo_mes['Vlr Valido'].sum()
        qtd_clientes = ultimo_mes['GRUPO CLIENTE'].nunique()
        ticket_medio = total_fat / qtd_clientes if qtd_clientes > 0 else 0

        # Previsão próximo mês (crescimento de 3%)
        previsao_prox_mes = total_fat * 1.03
        crescimento = 3.0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ultimo_periodo = df['Periodo'].iloc[-1] if not df.empty else "N/A"
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {COLORS['success']}, {COLORS['accent']}); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;'>
                    <div style='font-size: 14px; opacity: 0.9;'>Faturamento Atual</div>
                    <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>{format_currency(total_fat)}</div>
                    <div style='font-size: 12px; opacity: 0.8;'>{ultimo_periodo}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {COLORS['warning']}, {COLORS['danger']}); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;'>
                    <div style='font-size: 14px; opacity: 0.9;'>Previsão Próximo Mês</div>
                    <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>{format_currency(previsao_prox_mes)}</div>
                    <div style='font-size: 12px; opacity: 0.8;'>+{format_percentage(crescimento)}</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {COLORS['info']}, {COLORS['secondary']}); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;'>
                    <div style='font-size: 14px; opacity: 0.9;'>Clientes Ativos</div>
                    <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>{qtd_clientes}</div>
                    <div style='font-size: 12px; opacity: 0.8;'>{ultimo_periodo}</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {COLORS['accent']}, {COLORS['success']}); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;'>
                    <div style='font-size: 14px; opacity: 0.9;'>Ticket Médio</div>
                    <div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>{format_currency(ticket_medio)}</div>
                    <div style='font-size: 12px; opacity: 0.8;'>por cliente</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Configuração de projeção
        col1, col2 = st.columns([4, 2])
        with col1:
            st.markdown("### ⚙️ Configuração de Projeção")
        with col2:
            meses_projecao = st.slider("Meses para projetar", 3, 12, 6)

        # Gerar dados históricos + projeção
        df_historico = df.groupby(['MÊS', 'ANO', 'Periodo'])['Vlr Valido'].sum().reset_index()
        df_historico = df_historico.sort_values(['ANO', 'MÊS'])
        df_historico['Tipo'] = 'Realizado'

        # Gerar projeção total
        df_previsao_total = gerar_previsao_simples(df, meses_projecao)
        df_proj_agregado = df_previsao_total.groupby(['Periodo', 'MÊS', 'ANO'])['Valor'].sum().reset_index()
        df_proj_agregado['Tipo'] = 'Projetado'
        df_proj_agregado.columns = ['Periodo', 'MÊS', 'ANO', 'Vlr Valido', 'Tipo']

        # Combinar
        df_completo = pd.concat([df_historico[['Periodo', 'MÊS', 'ANO', 'Vlr Valido', 'Tipo']], 
                                df_proj_agregado], ignore_index=True)

        # Gráfico de linha temporal
        st.markdown("### 📈 Evolução e Projeção de Faturamento")

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
            fillcolor=f"rgba(76, 175, 80, 0.1)"
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
                fillcolor=f"rgba(255, 183, 77, 0.1)"
            ))

        fig.update_layout(
            height=500,
            xaxis_title="Período",
            yaxis_title="Faturamento (R$)",
            hovermode='x unified',
            plot_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de área empilhado por serviço
        st.markdown("### 📊 Breakdown por Tipo de Serviço")

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
            plot_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela resumo
        st.markdown("### 📋 Resumo por Período")

        df_resumo = df_completo.copy()
        df_resumo = df_resumo.sort_values(['ANO', 'MÊS'])

        # Calcular variação
        df_resumo['Variacao'] = df_resumo['Vlr Valido'].pct_change() * 100

        # Gerar HTML completo
        html_resumo = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {
                margin: 0;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            .resumo-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }
            .resumo-table th {
                background: #1a1a1a;
                color: white;
                padding: 12px;
                text-align: center;
            }
            .resumo-table td {
                padding: 10px;
                text-align: center;
                border-bottom: 1px solid #FAFAFA;
            }
            .tipo-real {
                background-color: #E8F5E9;
            }
            .tipo-proj {
                background-color: #FFF3E0;
            }
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
            variacao = row['Variacao']

            if pd.notna(variacao):
                if variacao > 5:
                    cor_variacao = '#4CAF50'
                elif variacao > 0:
                    cor_variacao = '#FFB74D'
                else:
                    cor_variacao = '#E57373'
                variacao_str = f"<span style='color: {cor_variacao}; font-weight: bold;'>{variacao:+.1f}%</span>"
            else:
                variacao_str = "-"

            html_resumo += f"""
            <tr class='{tipo_classe}'>
                <td><strong>{row['Periodo']}</strong></td>
                <td>{row['Tipo']}</td>
                <td>{format_currency(row['Vlr Valido'])}</td>
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
        altura_resumo = min(500, len(df_resumo) * 45 + 100)
        components.html(html_resumo, height=altura_resumo, scrolling=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: {COLORS["gray"]}; font-size: 12px; padding: 20px 0;'>
        <strong>Base Telco v1.0</strong> • Analytics & Business Intelligence<br>
        {datetime.now().strftime("%d/%m/%Y %H:%M")} • Todos os direitos reservados
    </div>
""", unsafe_allow_html=True)
