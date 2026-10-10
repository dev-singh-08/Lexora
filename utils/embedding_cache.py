import sqlite3
import json
import hashlib
import os

CACHE_FILE = "vector_store/embedding_cache.db"

def _get_conn():
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    conn = sqlite3.connect(CACHE_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS embeddings (hash TEXT PRIMARY KEY, vector TEXT)")
    return conn

def get_cached_embedding(text):
    if not text: 
        return None
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    with _get_conn() as conn:
        row = conn.execute("SELECT vector FROM embeddings WHERE hash=?", (h,)).fetchone()
        if row:
            return json.loads(row[0])
    return None

def save_cached_embedding(text, vector):
    if not text or not vector: 
        return
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    with _get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO embeddings (hash, vector) VALUES (?, ?)", (h, json.dumps(vector)))
