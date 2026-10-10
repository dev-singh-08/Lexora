from utils.retriever import retrieve_chunks
from utils.prompt_template import build_prompt
from utils.answer_generator import generate_answer
from utils.logger import log_question, log_unanswered
from utils.query_classifier import is_definition_query

SECTORS=["cases", "laws"]
def rag_answer(query: str, sector: str, start_year: int = None, end_year: int = None, user_id: int = None) -> dict:
    """
    Central RAG pipeline function.
    Controls retrieval, generation, validation and logging.
    """

    # 1️⃣ Retrieve relevant document chunks using FAISS with year range support
    retrieved_chunks = retrieve_chunks(query, sector, start_year=start_year, end_year=end_year)

    used_sector = sector
    # 2️⃣ If not found in primary sector, try fallback sectors (laws usually don't have year filters)
    if not retrieved_chunks:
        for other_sector in SECTORS:
            if other_sector != sector:
                # Fallback search might not need year range if it's laws
                retrieved_chunks = retrieve_chunks(query, other_sector)
                if retrieved_chunks:
                    used_sector = other_sector
                    break

    # 3️⃣ Handle cases with no retrieval
    if not retrieved_chunks:
        if is_definition_query(query):
            prompt = build_prompt([], query)
            answer = generate_answer(prompt)
            # Log successful definition query
            log_question(query, sector, user_id, response=answer)
            return {"answer": answer, "sources": []}

        log_unanswered(query, sector)
        return {
            "answer": "Answer not found in the legal documentation repository for this sector.",
            "sources": []
        }

    # 4️⃣ Build strict RAG prompt using retrieved chunks
    prompt = build_prompt(retrieved_chunks, query)

    # 5️⃣ Generate answer using Gemini
    answer = generate_answer(prompt)

    # 6️⃣ Log question and answer for history
    log_question(query, sector, user_id, response=answer)

    # 7️⃣ Collect unique document sources for citation
    sources = []
    seen_sources = set()
    for chunk in retrieved_chunks:
        src = chunk.get("source", "Unknown Source")
        if src not in seen_sources:
            sources.append(src)
            seen_sources.add(src)

    # 8️⃣ Return final response
    return {
        "answer": answer,
        "sources": sources,
        "sector_used": used_sector
    }
