import openai
import os
import json
import numpy as np
import faiss
from tqdm import tqdm

# Configuração da API local do LM Studio para embeddings
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"  # Valor simbólico

def generate_embedding(text):
    try:
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-nomic-embed-text-v1.5"
        )
        return response['data'][0]['embedding']
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
    matched_q = context_data["questions"][I[0][0]]
    matched_a = context_data["answers"][I[0][0]]
    return matched_q, matched_a