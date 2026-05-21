import streamlit as st
from utils import API_URL, LISTA_MESES
import requests
import pandas as pd


st.title("Consulta Individual")

ocd_nome = st.text_input("Digite o nome da OCD (Ex: MODERNA, NCC, ICC):").upper()
ano_o = st.number_input("Ano", value=2026,max_value=2026 ,key="ano_o")
mes_o = st.selectbox(
    "Mês",
    LISTA_MESES,
    key="mes_o")

if st.button("Buscar OCD"):

    if not ocd_nome:
        st.warning("Por favor, digite o nome da OCD para realizar a consulta.")
        st.stop()  # Para a execução se o nome da OCD não for fornecido     

    # 1. Monta a URL com os parâmetros que o usuário escolheu
    url_completa = f"{API_URL}/certificados/{ocd_nome.upper()}?ano={ano_o}&mes={mes_o}"

    with st.spinner("Buscando dados na API..."):
        try:
            # 2. Faz a requisição para o Backend
            response = requests.get(url_completa)
            
            if response.status_code == 200:
                dados = response.json()["result"]
                df = pd.DataFrame(dados)

                if not df.empty:
                    total = df.iloc[0]["quantidade_de_certificado"]
                    
                    # 4. Exibe os resultados de forma bonita
                    st.success(f"Dados encontrados para OCD: {ocd_nome.upper()} encontrados!")

                    st.write("---")
                    st.subheader("Total de Certificados Emitidos")
                    st.table(df) # st.table é melhor que st.dataframe para poucas linhas

                else:
                    st.warning(f"Nenhum dado encontrado para OCD: {ocd_nome.upper()} no período selecionado.")
                
            else:
                st.error(f"Erro na API: {response.status_code}")
        
        except Exception as e:
            st.error(f"O Backend está desligado? Erro: {e}")