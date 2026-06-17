import os
import requests
from database import get_conn

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def get_embedding(text: str, api_key: str = None) -> list:
    """Generate embedding for text using Mistral's mistral-embed."""
    key = api_key or MISTRAL_API_KEY
    if not key:
        print("[VectorStore] MISTRAL_API_KEY not found. Using dummy embedding.")
        return [0.0] * 1024
        
    try:
        url = "https://api.mistral.ai/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "model": "mistral-embed",
            "input": [text]
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['data'][0]['embedding']
    except Exception as e:
        print(f"[VectorStore] Mistral Embedding API error: {e}. Using dummy embedding.")
        return [0.0] * 1024

def add_to_vector_store(agent_id: int, doc_id: int, filename: str, content: str, api_key: str = None):
    """Chunk, embed, and store document in Supabase pgvector."""
    chunks = chunk_text(content)
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        for chunk in chunks:
            embedding = get_embedding(chunk, api_key)
            # pgvector accepts arrays like '[0.1, 0.2, ...]'
            embedding_str = f"[{','.join(map(str, embedding))}]"
            
            cur.execute(
                "INSERT INTO vector_documents (doc_id, agent_id, content, embedding) VALUES (%s, %s, %s, %s)",
                (doc_id, agent_id, chunk, embedding_str)
            )
        conn.commit()
        print(f"[VectorStore] Added {len(chunks)} chunks for doc {filename} to pgvector (ID: {doc_id})")
    except Exception as e:
        conn.rollback()
        print(f"[VectorStore] Error adding to pgvector: {e}")
    finally:
        conn.close()

def delete_from_vector_store(doc_id: int):
    """Delete all chunks belonging to a document ID."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM vector_documents WHERE doc_id = %s", (doc_id,))
        conn.commit()
        print(f"[VectorStore] Deleted chunks for doc ID: {doc_id}")
    except Exception as e:
        conn.rollback()
        print(f"[VectorStore] Error deleting doc ID {doc_id}: {e}")
    finally:
        conn.close()

def search_vector_store(agent_id: int, query: str, top_k: int = 5, api_key: str = None) -> list:
    """Search for relevant document chunks matching query using pgvector <=> operator."""
    query_embedding = get_embedding(query, api_key)
    embedding_str = f"[{','.join(map(str, query_embedding))}]"
    
    conn = get_conn()
    cur = conn.cursor()
    results = []
    try:
        # Use pgvector's cosine distance operator <=>
        cur.execute('''
            SELECT content 
            FROM vector_documents 
            WHERE agent_id = %s 
            ORDER BY embedding <=> %s 
            LIMIT %s
        ''', (agent_id, embedding_str, top_k))
        
        rows = cur.fetchall()
        results = [row[0] for row in rows]
    except Exception as e:
        print(f"[VectorStore] Search error in pgvector: {e}")
    finally:
        conn.close()
        
    return results
