import faiss
import pickle
import os
import numpy as np
from utils.embedding import get_embedding

SIMILARITY_THRESHOLD = 1.0   # Balanced threshold


def load_faiss_index(sector):
    index_path = f"vector_store/{sector}_faiss"
    faiss_file = os.path.join(index_path, "index.faiss")
    metadata_file = os.path.join(index_path, "metadata.pkl")

    if not os.path.exists(faiss_file):
        raise FileNotFoundError(f"FAISS index for sector '{sector}' not found at {faiss_file}. Please run the indexing script first.")

    index = faiss.read_index(faiss_file)

    with open(metadata_file, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata


def retrieve_chunks(query, sector, top_k=5, start_year=None, end_year=None):
    index, metadata = load_faiss_index(sector)

    query_embedding = np.array([get_embedding(query)]).astype("float32")

    # Search for more initially to allow for re-ranking
    initial_k = 50 
    distances, indices = index.search(query_embedding, initial_k)
    
    results_with_scores = []
    query_terms = set(query.lower().split())

    for score, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue

        chunk_meta = metadata[idx]
        chunk_text_lower = chunk_meta['text'].lower()
        
        # 🟢 Keyword Boosting: Reduce distance if keywords match exactly
        boost = 0
        matches = 0
        for term in query_terms:
            if len(term) > 2 and term in chunk_text_lower: # only boost significant terms
                boost += 0.1
                matches += 1
        
        # Additional boost for specific identifiers if they are found
        if "100" in query and "100" in chunk_text_lower:
            boost += 0.2
        if "bns" in query.lower() and "bns" in chunk_text_lower:
            boost += 0.2

        adjusted_score = score - boost
        
        if adjusted_score <= SIMILARITY_THRESHOLD:
            # Check for year filtering
            if start_year or end_year:
                chunk_year = chunk_meta.get("year")
                if chunk_year is not None:
                    if start_year and chunk_year < start_year:
                        continue
                    if end_year and chunk_year > end_year:
                        continue
                else:
                    continue

            results_with_scores.append((adjusted_score, chunk_meta))

    # Sort by adjusted score and return top_k
    results_with_scores.sort(key=lambda x: x[0])
    return [item[1] for item in results_with_scores[:top_k]]