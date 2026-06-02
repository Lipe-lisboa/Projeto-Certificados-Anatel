import streamlit as st
from utils import API_URL
import requests
from datetime import datetime
from utils import comando_sql
import pandas as pd
import math

st.title("Carregar Dados Anatel")

ano = st.number_input("Ano", value=2026,max_value=2026 ,key="ano_p")

if st.button("Carregar Dados"):
    url_completa = f"{API_URL}/carregar-dados?ano={ano}"

    with st.spinner("Buscando dados na API..."):
        response = requests.get(url_completa)

        if response.status_code == 200:
            st.success(response.json().get("mensagem", "Dados carregados com sucesso!"))
        elif response.status_code == 404:
            st.warning(response.json().get("mensagem", "Dados não encontrados."))
        else:
            # Captura a resposta JSON da API e tenta pegar o campo 'detail' ou 'mensagem'
            try:
                erro_detalhado = response.json()
                # Tenta obter a mensagem de erro detalhada, dando prioridade ao campo 'detail'
                if "detail" in erro_detalhado:
                    mensagem_erro = erro_detalhado["detail"]
                else:
                    mensagem_erro = erro_detalhado.get("mensagem", "Erro desconhecido")
            except Exception:
                mensagem_erro = response.text

            st.error(f"Erro na API (Status {response.status_code}): {mensagem_erro}")


st.subheader("Dados de Mercado")

ano_atual = datetime.now().year
mes_atual_int = datetime.now().month
dia_atual = datetime.now().day
dados, _ = comando_sql("SELECT MIN(ano_filtro) FROM certificados")

if dados:
    ano_minimo = int(dados[0][0])
else:
    ano_minimo = ano_atual

st.info("Selecione o período para visualizar os dados de mercado da Anatel.")

data_inicio_selecionada = st.date_input("Data de Início", value=datetime(ano_atual, 1, 1),min_value=datetime(ano_minimo, 1, 1), max_value=datetime(ano_atual, mes_atual_int, dia_atual), key="data_inicio")
data_fim_selecionada = st.date_input("Data de Fim", value=datetime(ano_atual, mes_atual_int, dia_atual),min_value=datetime(ano_minimo, 1, 1), max_value=datetime(ano_atual, mes_atual_int, dia_atual), key="data_fim")

data_inicio_str = data_inicio_selecionada.strftime("%Y-%m-%d")
data_fim_str = data_fim_selecionada.strftime("%Y-%m-%d")

query = f"SELECT * FROM certificados WHERE DATE(data_certificado) BETWEEN '{data_inicio_str}' AND '{data_fim_str}'"
    
dados, colunas =  comando_sql(query)

# 3. Transforma o resultado em DataFrame usando pd.DataFrame() e NÃO pd.read_sql()

if dados:
    df = pd.DataFrame(dados, columns=colunas)

    linhas_por_pagina = 20

    total_linhas = len(df)
    total_paginas = math.ceil(total_linhas / linhas_por_pagina)

    pagina_atual = st.selectbox(
        "Página", 
        options=range(1, total_paginas + 1), 
        index=0
    )

    inicio = (pagina_atual - 1) * linhas_por_pagina
    fim = inicio + linhas_por_pagina

    st.dataframe(df.iloc[inicio:fim], use_container_width=True)

else:
    st.warning("Nenhum dado encontrado para esse período")