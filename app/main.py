import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import time
from core.retrieval_engine import get_relevant_answer
from core.config import EMPRESAS_DISPONIVEIS
from core.llm_utils import query_general_llm
from core.config import DEBUG as DEBUG_MODE


st.set_page_config(page_title="SDR Inteligente", page_icon="🤖", layout="centered")
st.title("🤖 SDR Inteligente")

# Estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_company" not in st.session_state:
    st.session_state.selected_company = ""

if "show_citations" not in st.session_state:
    st.session_state.show_citations = False

# Frases genéricas que devem ir direto para o LLM geral
GENERIC_PHRASES = [
    "oi", "olá", "bom dia", "boa tarde", "boa noite",
    "e aí", "tudo bem?", "beleza?", "valeu", "obrigado", "agradecido",
    "como vai?", "como está?"
]

def is_small_talk(question):
    return question.lower().strip() in GENERIC_PHRASES

# Lista de empresas
disponiveis = EMPRESAS_DISPONIVEIS
st.session_state.selected_company = st.selectbox("Selecione a empresa (opcional):", ["Nenhuma"] + disponiveis)

# Alternar visualização de citações
st.session_state.show_citations = st.toggle("Mostrar citações", value=False)

# Campo de entrada do usuário
user_input = st.chat_input("Digite sua pergunta")

if user_input:
    # Exibir a pergunta no chat do usuário imediatamente
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Verificar se é uma frase genérica
    if is_small_talk(user_input):
        answer = query_general_llm(user_input)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
    else:
        # Recuperar empresa selecionada
        company = st.session_state.selected_company
        if company == "Nenhuma":
            company = None

        # Obter resposta usando o pipeline RAG
        with st.spinner("Buscando resposta..."):
            resposta = get_relevant_answer(user_input, company)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            st.chat_message("assistant").write(resposta)

if DEBUG_MODE:
    st.sidebar.title("Debug")
    st.sidebar.write("Histórico de mensagens")
    for msg in st.session_state.messages:
        st.sidebar.write(msg)
