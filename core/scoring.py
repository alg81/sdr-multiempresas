# scoring.py

import json
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from nltk.translate.bleu_score import sentence_bleu
from llm_utils import query_general_llm
import numpy as np
import os


class RAGEvaluator:
    def __init__(self, embedding_model: Optional[str] = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model)

    def compute_cosine_similarity(self, answer: str, ideal: str) -> float:
        vectors = self.model.encode([answer, ideal])
        return cosine_similarity([vectors[0]], [vectors[1]])[0][0]

    def compute_bleu_score(self, answer: str, ideal: str) -> float:
        reference = ideal.split()
        hypothesis = answer.split()
        return sentence_bleu([reference], hypothesis)

    def evaluate_batch(self, data: List[Dict[str, str]]) -> List[Dict[str, float]]:
        results = []
        for item in data:
            bleu = self.compute_bleu_score(item['rag_answer'], item['ideal_answer'])
            cosine = self.compute_cosine_similarity(item['rag_answer'], item['ideal_answer'])
            results.append({
                "question": item["question"],
                "bleu_score": bleu,
                "cosine_similarity": cosine
            })
        return results

    def judge_with_llm(self, question: str, rag_answer: str, ideal_answer: str) -> str:
        prompt = (
            f"Pergunta: {question}\n"
            f"Resposta gerada via RAG: {rag_answer}\n"
            f"Resposta ideal: {ideal_answer}\n"
            f"Com base na clareza, completude e precisão, avalie de 0 a 10 a resposta gerada. "
            f"Explique brevemente sua nota."
        )
        response = query_general_llm(prompt)
        return response

    def evaluate_with_judge(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        judged_results = []
        for item in data:
            judgement = self.judge_with_llm(
                question=item['question'],
                rag_answer=item['rag_answer'],
                ideal_answer=item['ideal_answer']
            )
            judged_results.append({
                "question": item['question'],
                "judge_response": judgement
            })
        return judged_results


# Exemplo de uso (pode ser removido se for importar em outro módulo)
if __name__ == "__main__":
    example_data_path = "data/avaliacoes/exemplo_respostas.json"
    if os.path.exists(example_data_path):
        with open(example_data_path, "r", encoding="utf-8") as f:
            qa_data = json.load(f)

        evaluator = RAGEvaluator()
        metrics = evaluator.evaluate_batch(qa_data)
        print("Métricas quantitativas:")
        for m in metrics:
            print(m)

        print("\nAvaliação por LLM:")
        llm_feedback = evaluator.evaluate_with_judge(qa_data)
        for j in llm_feedback:
            print(j)
    else:
        print("Arquivo de exemplo de avaliação não encontrado.")
