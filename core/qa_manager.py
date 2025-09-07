import os
import json
import unicodedata
import numpy as np
from difflib import SequenceMatcher
from core.config import BASE_QA_DIR


def normalizar_texto(texto: str) -> str:
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    return texto


def carregar_base_qa(empresa, with_embeddings=False, json_path_override=None):
    """
    Carrega a base de perguntas e respostas para uma empresa.
    Se with_embeddings for True, carrega também os embeddings FAISS.

    Args:
        empresa (str): nome da empresa
        with_embeddings (bool): se deve carregar embeddings
        json_path_override (str or None): caminho personalizado do JSON, se fornecido

    Returns:
        dict com perguntas, respostas, embeddings (se with_embeddings=True) e índice FAISS
    """
    from core.embeddings_manager import prepare_embeddings

    if json_path_override:
        caminho = json_path_override
    else:
        caminho = os.path.join(BASE_QA_DIR, f"{empresa}.json")
    
    print(f"[INFO] Carregando base de QA de: {caminho}")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        base = json.load(f)

    if not with_embeddings:
        return base

    return prepare_embeddings(caminho)



def similaridade(p1: str, p2: str) -> float:
    """Calcula similaridade entre duas strings."""
    return SequenceMatcher(None, normalizar_texto(p1), normalizar_texto(p2)).ratio()


def buscar_resposta_manual(pergunta_usuario: str, base_qa: list, threshold: float = 0.85) -> str:
    """
    Busca a melhor pergunta na base e retorna a resposta, se a similaridade for aceitável.
    """
    melhores = sorted(
        base_qa,
        key=lambda qa: similaridade(pergunta_usuario, qa.get("pergunta", "")),
        reverse=True,
    )

    if not melhores:
        return ""

    score = similaridade(pergunta_usuario, melhores[0]["pergunta"])
    if score >= threshold:
        return melhores[0]["resposta"]

    return ""
