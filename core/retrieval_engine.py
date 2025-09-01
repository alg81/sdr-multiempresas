import os
from typing import Optional, Tuple, List
from core.llm_utils import generate_answer
from core.embeddings_manager import find_similar_question
from core.qa_manager import carregar_base_qa, buscar_resposta_manual
from core.config import NUM_DOCUMENTS_FAISS, BASE_QA_DIR


def load_context_data(company: str):
    """
    Carrega dados de embeddings e índice FAISS para a empresa especificada.
    """
    json_path = os.path.join(BASE_QA_DIR, f"{company}.json")
    return carregar_base_qa(company, with_embeddings=True, json_path_override=json_path)


def get_relevant_answer(question: str, company: Optional[str] = None, show_citations: bool = False) -> Tuple[str, List[str]]:
    citations = []

    # 1. Verifica se há resposta manual
    if company:
        qa_base = carregar_base_qa(company)
        manual_answer = buscar_resposta_manual(question, qa_base)
        if manual_answer:
            return manual_answer, citations

    # 2. Busca semântica com embeddings e LLM
    context = ""
    if company:
        context_data = load_context_data(company)
        matched_q, matched_a = find_similar_question(question, context_data, top_k=NUM_DOCUMENTS_FAISS)
        if matched_q and matched_a:
            context = f"{matched_q}\n{matched_a}"
            if show_citations:
                citations.append(f"{company}.json")

    answer = generate_answer(question, context)
    return answer, citations
