import requests
from core.config import NOME_MODELO_LLM, LM_STUDIO_API_BASE, DEBUG_MODE

def query_general_llm(prompt: str, context: str = None) -> str:
    if context:
        # Formato de prompt com contexto curto
        full_prompt = f"<|context|>\n{context}\n\n<|question|>\n{prompt}"
    else:
        full_prompt = prompt

    payload = {
        "model": NOME_MODELO_LLM,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{LM_STUDIO_API_BASE}/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        if DEBUG_MODE:
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
        if DEBUG_MODE:
            return f"[ERROR - CONTEXTUAL LLM] {str(e)}"
        return "An error occurred while generating the answer."
