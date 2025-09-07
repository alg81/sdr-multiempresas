import os
import re
import json
import html
from datetime import datetime
from core.config import DEBUG_MODE, LOGS_DIR


def limpar_texto(texto):
    """Remove espaços em excesso e normaliza o texto."""
    return re.sub(r"\s+", " ", texto.strip())


def formatar_citacoes(citacoes):
    """Formata citações para exibição legível."""
    if not citacoes:
        return ""
    linhas = [f"- {c['fonte']} (trecho: \"{c['trecho'][:100]}...\")" for c in citacoes]
    return "\n".join(linhas)


def log_debug(mensagem):
    """Grava logs de depuração se o modo estiver ativado."""
    if DEBUG_MODE:
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_path = os.path.join(LOGS_DIR, "debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {mensagem}\n")


def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def sanitize_markdown(text):
    """
    Sanitiza a resposta vinda do modelo para exibição no markdown do Streamlit.
    Isso remove tokens HTML inesperados e escapa caracteres que possam quebrar o markdown.
    """
    if not isinstance(text, str):
        return ""
    
    # Remove espaços desnecessários
    text = text.strip()

    # Substitui caracteres perigosos
    text = text.replace("<script", "")
    text = html.escape(text, quote=False)

    # Substitui aspas HTML por normais
    text = text.replace("&quot;", "\"").replace("&#x27;", "'")

    # Reverte negrito/itálico se vier como &ast; ou &lowast;
    text = text.replace("&ast;", "*").replace("&lowast;", "*")

    return text