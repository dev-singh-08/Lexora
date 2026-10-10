import os
from utils.document_loader import load_document
from utils.text_chunker import chunk_text
from utils.embedding import get_embedding
from utils.faiss_indexer import create_empty_index, add_to_index, save_index

SECTORS = {
    "laws": "data/Laws"
}

for sector, path in SECTORS.items():
    print(f"\nIndexing sector: {sector}")

    index = None
    metadatas = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.lower().endswith(('.pdf')): 
                continue
                
            file_path = os.path.join(root, file)
            print(f"  Processing {file}...")
            try:
                text = load_document(file_path)
                if not text or not text.strip():
                    print(f"    Skipped (empty)")
                    continue
                    
                chunks = chunk_text(text)
                print(f"    {len(chunks)} chunks. Embedding...")

                BATCH_SIZE = 50
                for i in range(0, len(chunks), BATCH_SIZE):
                    batch_chunks = chunks[i:i + BATCH_SIZE]
                    try:
                        batch_embeddings = get_embedding(batch_chunks)
                        
                        # Initialize index if not already done
                        if index is None and batch_embeddings:
                            dimension = len(batch_embeddings[0])
                            index = create_empty_index(dimension)
                        
                        # Add to index incrementally
                        if index:
                            add_to_index(index, batch_embeddings)
                        
                        for j, chunk in enumerate(batch_chunks):
                            metadatas.append({
                                "sector": sector,
                                "document": file,
                                "year": None,
                                "chunk_id": i + j,
                                "source": file,
                                "text": chunk
                            })
                    except Exception as api_e:
                        print(f"    Error on batch {i}: {api_e}")

            except Exception as e:
                print(f"    Error: {e}")

    if index:
        save_path = f"vector_store/{sector}_faiss"
        print(f"Saving FAISS index to {save_path}...")
        save_index(index, metadatas, save_path)
        print(f"Done indexing {sector} ({len(metadatas)} chunks)")
    else:
        print(f"No documents indexed for {path}")
