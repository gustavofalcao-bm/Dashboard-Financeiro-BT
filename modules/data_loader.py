import streamlit as st
import pandas as pd
from modules.utils import normalizar_nome_cliente, calcular_valor_proporcional

@st.cache_data
def load_data():
    """Carrega e processa a base de dados"""
    try:
        df = pd.read_excel('BD-FATURAMENTO.xlsx')
        
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df['Vlr Valido'] = pd.to_numeric(df['Vlr Valido'], errors='coerce')
        df['MÊS'] = pd.to_numeric(df['MÊS'], errors='coerce')
        df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce')
        df['Periodo'] = df['Descrição'].astype(str) + '/' + df['ANO'].astype(str)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base de dados: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def carregar_ativacoes():
    """Carrega a planilha de ativações em andamento"""
    try:
        df = pd.read_excel('EM-ATIVACAO.xlsx', sheet_name='EM ATIVAÇÃO')
        df['CLIENTE_NORM'] = df['CLIENTE'].apply(normalizar_nome_cliente)
        df['DATA_PREVISTA'] = pd.to_datetime(df['DATA PREVISTA'], errors='coerce')
        df['VALOR_MRR'] = pd.to_numeric(df['VALOR TOTAL'], errors='coerce')
        return df[['CLIENTE', 'CLIENTE_NORM', 'DATA_PREVISTA', 'VALOR_MRR', 'PRODUTO', 'STATUS']].dropna(subset=['DATA_PREVISTA', 'VALOR_MRR'])
    except Exception as e:
        st.warning(f"Não foi possível carregar EM-ATIVACAO.xlsx: {e}")
        return pd.DataFrame()

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
                previsoes.append({
                    'Cliente': cliente,
                    'Periodo': periodo_nome,
                    'MÊS': mes_atual,
                    'ANO': ano_atual,
                    'Valor': valor,
                    'Tipo': 'Previsto'
                })
    
    return pd.DataFrame(previsoes)
