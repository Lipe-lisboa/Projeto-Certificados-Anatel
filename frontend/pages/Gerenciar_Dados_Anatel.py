import streamlit as st
from utils import API_URL
import requests

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