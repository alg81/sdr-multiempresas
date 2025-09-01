import requests
from core.config import LM_STUDIO_API_BASE, NOME_MODELO_LLM, DEBUG

def query_general_llm(prompt: str) -> str:
    payload = {
        "model": NOME_MODELO_LLM,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{LM_STUDIO_API_BASE}/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        if DEBUG:
            return f"[ERROR - GENERAL LLM] {str(e)}"
        return "An error occurred while generating the answer."

def generate_answer(question: str, context: str = "") -> str:
    prompt = f"""Use the context below to answer the question. If the context is not relevant, reply based on general knowledge.

Context:
{context}

Question:
{question}"""

    payload = {
        "model": NOME_MODELO_LLM,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(f"{LM_STUDIO_API_BASE}/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        if DEBUG:
            return f"[ERROR - CONTEXTUAL LLM] {str(e)}"
        return "An error occurred while generating the answer."
