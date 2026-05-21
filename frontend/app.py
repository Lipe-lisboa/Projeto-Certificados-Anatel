import streamlit as st
import sqlite3
from pathlib import Path
from utils import API_URL, NUM_PARA_MES_PT
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Market Share OCD", layout="wide", initial_sidebar_state="expanded")

st.title("Painel de Controle - Market Share OCD")

# Estilização do Card em CSS
st.markdown("""
    <style>
    .card-principal {
        background-color: #1E222D;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    .card-valor-container {
        display: flex;
        align-items: baseline;
        gap: 10px; 
    }
    .card-titulo {
        font-size: 14px;
        color: #808495;
        margin-bottom: 5px;
    }
    .card-valor {
        font-size: 28px;
        font-weight: bold;
        color: #FFFFFF;
    }
    /* Estilo do indicador de porcentagem */
    .card-delta-positivo {
        font-size: 16px;
        font-weight: bold;
        color: #00E676; /* Verde chamativo para crescimento */
    }
    .card-delta-negativo {
        font-size: 16px;
        font-weight: bold;
        color: #FF1744; /* Vermelho chamativo para queda */
    }
    .card-delta-neutro {
        font-size: 14px;
        color: #808495; /* Cinza para dados informativos adicionais */
    }
    </style>
""", unsafe_allow_html=True)

# 1. Pega o caminho de onde este arquivo .py está
CURRENT_DIR = Path(__file__).resolve().parent

# 2. sobe dois niveis sai de 'app' e sai de 'frontend' para chegar na raiz
ROOT_DIR = CURRENT_DIR.parent


DB_PATH = ROOT_DIR / "backend" / "src" /"banco.db"


conn = sqlite3.connect(DB_PATH) # Conecta ao banco de dados SQLite usando o caminho fornecido

ano_atual = datetime.now().year
mes_atual_int = datetime.now().month

cursor = conn.cursor() # Cria um cursor para executar comandos SQL

cursor.execute(f"SELECT COUNT(*) FROM certificados WHERE ano_filtro = {ano_atual}")
total_certificados = cursor.fetchone()[0]
conn.commit()

cursor.execute("SELECT MAX(data_certificado) FROM certificados")
data_bruta = cursor.fetchone()[0]
conn.commit()

conn.close() 

if data_bruta:
    # Como a string vem com "AAAA-MM-DD 00:00:00", pegamos apenas a parte da data (os primeiros 10 caracteres)
    data_limpa = data_bruta[:10] 
    
    # Converte o padrão "AAAA-MM-DD" para o objeto datetime
    objeto_data = datetime.strptime(data_limpa, "%Y-%m-%d")
    
    # Formata para o padrão brasileiro "DD/MM/AAAA"
    ultima_atualizacao = objeto_data.strftime("%d/%m/%Y")
else:
    # Caso a tabela esteja vazia por algum motivo
    ultima_atualizacao = "Sem dados"

try:
    url_completa = f"{API_URL}/certificados?ano={ano_atual}"

except Exception as e:
    st.error(f"Erro ao montar a URL: {str(e)}")
    st.stop()

with st.spinner("Buscando dados na API..."):
    response = requests.get(url_completa)

if response.status_code == 200:
    ocd_lider = response.json()["result"][0]["ocd"]
    qtd_ocd_lider = response.json()["result"][0]["quantidade_de_certificado"]
    qtd_total_certificados = 0

    dados_gerais = response.json()["result"]
    df = pd.DataFrame(dados_gerais)

    if df.empty:
        st.warning(f"Nenhum dado encontrado para o ano de {ano_atual}.")
        st.stop()

    df_top5 = df.head(5)
    df_outros = df.iloc[5:].sum()
    print(df_top5)


    for ocd in response.json()["result"]:
        qtd_total_certificados += ocd["quantidade_de_certificado"]

    if qtd_total_certificados is not None and qtd_total_certificados != 0:
        porcentagem_share = qtd_ocd_lider / qtd_total_certificados * 100
    else:
        porcentagem_share = 0


elif response.status_code == 404:
    st.warning(response.json().get("mensagem"))
    st.stop()


else:
    st.error(response.json().get("mensagem"))
    st.stop()

# Criando os cards lado a lado
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="card-principal" style="border-left: 5px solid #FF4B4B;">
            <div class="card-titulo">TOTAL DE CERTIFICADOS DE {ano_atual}</div>
            <div class="card-valor">{total_certificados}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="card-principal" style="border-left: 5px solid #00F0FF;">
            <div class="card-titulo">OCD LÍDER DE {ano_atual}</div>
            <div class="card-valor-container">
                <span class="card-valor">{ocd_lider}</span>
                <span class="card-delta-positivo">(+{porcentagem_share:.2f}%)</span>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="card-principal" style="border-left: 5px solid #00F0AF;">
            <div class="card-titulo">ÚLTIMA ATUALIZAÇÃO ANATEL DE {ano_atual}</div>
            <div class="card-valor">{ultima_atualizacao}</div>
        </div>
    """, unsafe_allow_html=True)



st.subheader(f"Top 5 OCDs com mais certificados em {ano_atual}")

df_pizza = pd.concat([df_top5, pd.DataFrame([{'ocd': 'OUTROS', 'quantidade_de_certificado': df_outros['quantidade_de_certificado']}])])

fig = px.pie(df_pizza, values='quantidade_de_certificado', names='ocd')
st.plotly_chart(fig)

dic_top5 = []
ordem_dos_meses = []

for i in range(mes_atual_int):

    mes_nome = NUM_PARA_MES_PT[str(i+1)]
    mes_num = i + 1

    ordem_dos_meses.append(mes_nome)

    for ocd in df_top5['ocd']:

        try:
            url_completa = f"{API_URL}/certificados/{ocd}?ano={ano_atual}&mes={mes_nome}"
            response = requests.get(url_completa)

        except Exception as e:
            st.error(f"Erro ao montar a URL: {str(e)}")
            st.stop()

        if response.status_code == 200:
            quantidade_certificados = response.json()["result"][0]["quantidade_de_certificado"]
            dic_top5.append({
                'ocd': ocd,
                'mes': mes_nome,
                'mes_num': mes_num,
                'quantidade_de_certificado': quantidade_certificados
            })
        elif response.status_code == 404:
            dic_top5.append({
                'ocd': ocd,
                'mes': mes_nome,
                'mes_num': mes_num,
                'quantidade_de_certificado': 0
            })
        else:
            st.error(response.json().get("mensagem"))
            st.stop()

# --- AQUI ENTRA A CRIAÇÃO DO GRÁFICO ---

if dic_top5:
    # Ordena o DataFrame numericamente pelo número do mês
    df_grafico = pd.DataFrame(dic_top5).sort_values(by="mes_num")

    # Define a ordem dos meses usando a lista de meses em português
    df_grafico['mes'] = pd.Categorical(df_grafico['mes'], categories=ordem_dos_meses, ordered=True)
    
    st.subheader("📈 Crescimento do Volume de Certificados (Top 5 OCDs)")
    
    # Renderiza o gráfico
    st.line_chart(
        data=df_grafico,
        x="mes",                                
        y="quantidade_de_certificado",          
        color="ocd",
        x_label="Meses",
        y_label="Quantidade de Certificados",
        height=450,            
        use_container_width=True                
    )
else:
    st.info("Nenhum dado encontrado para gerar o gráfico de evolução.")