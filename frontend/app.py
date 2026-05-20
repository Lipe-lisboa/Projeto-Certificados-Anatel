import streamlit as st
import sqlite3
from pathlib import Path
from utils import API_URL
import requests

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
