import faiss
import numpy as np
import os
import pickle

def build_faiss_index(embeddings, metadatas, save_path):
    """
    Original function for backward compatibility. 
    Builds the entire index at once.
    """
    if not embeddings:
        return
    
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)

    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)
    
    save_index(index, metadatas, save_path)

def create_empty_index(dimension):
    """Initializes a new FAISS index."""
    return faiss.IndexFlatL2(dimension)

def add_to_index(index, embeddings):
    """Adds a batch of embeddings to the index."""
    if not embeddings:
        return
    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)

def save_index(index, metadatas, save_path):
    """Saves the index and metadata to disk."""
    os.makedirs(save_path, exist_ok=True)
    faiss.write_index(index, os.path.join(save_path, "index.faiss"))

    with open(os.path.join(save_path, "metadata.pkl"), "wb") as f:
        pickle.dump(metadatas, f)
