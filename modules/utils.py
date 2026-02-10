import base64
import unicodedata
import calendar
import pandas as pd
from modules.config import COLORS

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

def normalizar_nome_cliente(nome):
    """Normaliza nome de cliente para matching entre bases"""
    nome = str(nome).upper().strip()
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(char for char in nome if unicodedata.category(char) != 'Mn')
    nome = nome.replace('.', '').replace(',', '').replace('-', '').replace('/', '')
    nome = ' '.join(nome.split())
    mapeamento = {'INTERCEMENT': 'INTERCEMENT', 'KOMECO': 'KOMECO', 'SEBRAE': 'SEBRAE'}
    return mapeamento.get(nome, nome)

def calcular_valor_proporcional(data_ativacao, valor_mrr):
    """Calcula valor proporcional baseado nos dias restantes do mês"""
    data = pd.to_datetime(data_ativacao)
    dias_no_mes = calendar.monthrange(data.year, data.month)[1]
    dias_cobrados = dias_no_mes - data.day
    if dias_cobrados <= 0:
        return 0.0
    return (valor_mrr / dias_no_mes) * dias_cobrados
