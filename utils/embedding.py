from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
from utils.embedding_cache import get_cached_embedding, save_cached_embedding

# Load the local offline model
print(f"Loading local embedding model: {EMBEDDING_MODEL} ...")
model = SentenceTransformer(EMBEDDING_MODEL)

def get_embedding(text):
    if isinstance(text, list):
        results = []
        uncached_indices = []
        uncached_texts = []
        
        # 1. Check cache for all texts
        for i, t in enumerate(text):
            cached = get_cached_embedding(t)
            if cached:
                results.append(cached)
            else:
                results.append(None) # placeholder
                uncached_indices.append(i)
                uncached_texts.append(t)
                
        # 2. Fetch uncached using local model
        if uncached_texts:
            # model.encode supports list natively and works much faster
            vectors = model.encode(uncached_texts).tolist()
            
            # Map back to results and save to cache
            for i, idx in enumerate(uncached_indices):
                vector = vectors[i]
                results[idx] = vector
                save_cached_embedding(uncached_texts[i], vector)
                
        return results
    else:
        # Single text handling
        cached = get_cached_embedding(text)
        if cached:
            return cached
            
        vector = model.encode(text).tolist()
        save_cached_embedding(text, vector)
        return vector

