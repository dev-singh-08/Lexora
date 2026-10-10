import faiss
import pickle
import numpy as np
import os
from utils.embedding import get_embedding

def test():
    query = "What is bns 100"
    sector = "laws"
    
    index_path = f"vector_store/{sector}_faiss"
    faiss_file = os.path.join(index_path, "index.faiss")
    metadata_file = os.path.join(index_path, "metadata.pkl")

    index = faiss.read_index(faiss_file)
    with open(metadata_file, "rb") as f:
        metadata = pickle.load(f)

    query_embedding = np.array([get_embedding(query)]).astype("float32")
    distances, indices = index.search(query_embedding, 5)

    print(f"Results for query: '{query}'")
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx == -1: continue
        meta = metadata[idx]
        print(f"\n[Rank {i}] Distance: {dist:.4f}")
        print(f"SOURCE: {meta['document']}")
        print(f"TEXT: {meta['text'][:300]}...")

if __name__ == "__main__":
    test()
