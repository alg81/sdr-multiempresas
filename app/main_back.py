import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from core.retrieval_engine import get_relevant_answer
from core.config import EMPRESAS_DISPONIVEIS, DEBUG as DEBUG_MODE
from core.llm_utils import query_general_llm

# Configuração do layout da página
st.set_page_config(page_title="SDR Inteligente", page_icon="🤖", layout="centered")
st.title("🤖 SDR Inteligente")

# Estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_company" not in st.session_state:
    st.session_state.selected_company = ""
if "show_citations" not in st.session_state:
    st.session_state.show_citations = False

# Lista de frases genéricas que vão direto para o LLM
GENERIC_PHRASES = [
    "oi", "olá", "bom dia", "boa tarde", "boa noite",
    "e aí", "tudo bem?", "beleza?", "valeu", "obrigado", "agradecido",
    "como vai?", "como está?"
]

def is_small_talk(question):
    return question.lower().strip() in GENERIC_PHRASES

# Empresa selecionada
disponiveis = EMPRESAS_DISPONIVEIS
st.session_state.selected_company = st.selectbox("Selecione a empresa (opcional):", ["Nenhuma"] + disponiveis)

# Alternar exibição de citações
st.session_state.show_citations = st.toggle("Mostrar citações", value=False)

# Entrada do usuário
user_input = st.chat_input("Digite sua pergunta")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Frase genérica? Usa LLM diretamente
    if is_small_talk(user_input):
        resposta = query_general_llm(user_input)
    else:
        company = st.session_state.selected_company
        if company == "Nenhuma":
            company = None

        with st.spinner("Buscando resposta..."):
            relevant_answer, citations = get_relevant_answer(user_input, company)

        if DEBUG_MODE:
            print(f"[DEBUG] Resposta relevante bruta: {repr(relevant_answer)}")

        if relevant_answer is not None and relevant_answer.strip() != "":
            resposta = relevant_answer
            if st.session_state.show_citations and citations:
                resposta += "\n\n📚 *Fontes:* " + ", ".join(citations)
        else:
            resposta = query_general_llm(user_input)

    # Exibir resposta
    st.session_state.messages.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)

# Debug sidebar
if DEBUG_MODE:
    st.sidebar.title("Debug")
    st.sidebar.write("Histórico de mensagens")
    for msg in st.session_state.messages:
        st.sidebar.write(msg)
