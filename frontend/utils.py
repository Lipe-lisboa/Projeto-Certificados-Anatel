import sqlite3
import pandas as pd
from pathlib import Path

LISTA_MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

NUM_PARA_MES_PT = {
    '1': 'JANEIRO',
    '2': 'FEVEREIRO',
    '3': 'MARÇO',
    '4': 'ABRIL',
    '5': 'MAIO',
    '6': 'JUNHO',
    '7': 'JULHO',
    '8': 'AGOSTO',
    '9': 'SETEMBRO',
    '10': 'OUTUBRO',
    '11': 'NOVEMBRO',
    '12': 'DEZEMBRO',
}

API_URL = "http://127.0.0.1:8000"

# 1. Pega o caminho de onde este arquivo .py está
CURRENT_DIR = Path(__file__).resolve().parent

# 2. sobe dois niveis sai de 'utils' e sai de 'frontend' para chegar na raiz
ROOT_DIR = CURRENT_DIR.parent


DB_PATH = ROOT_DIR / "backend" / "src" /"banco.db"


def comando_sql(comando: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(comando)
        
        # ALTERADO AQUI: fetchall() em vez de fetchone() para trazer todas as linhas
        response = cursor.fetchall() 
        colunas = None

        if cursor.description:
            colunas = [desc[0] for desc in cursor.description]

        conn.commit()
        conn.close()
        return response, colunas
    
    except Exception as e:
        return [], []