import openai
import os
import json
import requests
import numpy as np
import faiss
from tqdm import tqdm
from core.config import SIMILARITY_THRESHOLD

# Configuração da API local do LM Studio para embeddings
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"  # Valor simbólico

def generate_embedding(text):
    try:
        url = "http://localhost:1234/v1/embeddings"
        headers = {"Content-Type": "application/json"}
        data = {
            "input": text,
            "model": "text-embedding-nomic-embed-text-v1.5"
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"[Embedding Error] {e}")
        return None

def load_qa_pairs(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_faiss_index(embedding_list):
    dimension = len(embedding_list[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embedding_list).astype("float32"))
    return index

def prepare_embeddings(json_path, index_save_path=None):
    qa_pairs = load_qa_pairs(json_path)
    questions = [pair["pergunta"] for pair in qa_pairs]
    answers = [pair["resposta"] for pair in qa_pairs]
    embeddings = []

    print(f"Gerando embeddings para {len(questions)} perguntas...")
    for question in tqdm(questions):
        emb = generate_embedding(question)
        if emb is None:
            raise ValueError(f"Embedding falhou para: {question}")
        embeddings.append(emb)

    index = build_faiss_index(embeddings)
    if index_save_path:
        faiss.write_index(index, index_save_path)

    return {
        "questions": questions,
        "answers": answers,
        "embeddings": embeddings,
        "index": index
    }

def find_similar_question(user_question, context_data, top_k=1):
    user_embedding = generate_embedding(user_question)
    if user_embedding is None:
        return None, None

    D, I = context_data["index"].search(np.array([user_embedding]).astype("float32"), top_k)
    if D[0][0] < SIMILARITY_THRESHOLD:
        matched_q = context_data["questions"][I[0][0]]
        matched_a = context_data["answers"][I[0][0]]
        return matched_q, matched_a
    else:
        return None, None

def rebuild_and_save_faiss_index(company_name, json_dir="data/json", index_dir="data/faiss"):
    """
    Rebuilds the FAISS index from the latest JSON file and saves it.
    
    Parameters:
        company_name (str): The name of the company (used to locate JSON and name the FAISS index).
        json_dir (str): Directory where the company's QA JSON file is stored.
        index_dir (str): Directory to save the FAISS index file.
    """
    json_path = os.path.join(json_dir, f"{company_name}.json")
    index_path = os.path.join(index_dir, f"{company_name}.index")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found for company: {company_name}")

    print(f"[INFO] Rebuilding FAISS index for '{company_name}'...")
    prepare_embeddings(json_path, index_save_path=index_path)
    print(f"[SUCCESS] Index saved to: {index_path}")
