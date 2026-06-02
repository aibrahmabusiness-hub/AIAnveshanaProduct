import os
import chromadb
import google.generativeai as genai

# Setup Chroma DB persistent client
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("anveshana_kb")

# Default fallback Gemini Key if not configured
DEFAULT_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAYy8GjdrdjijABG7ozk0TKyDon8_4OKjc")

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
    """Generate embedding for text using Gemini's models/embedding-001."""
    key = api_key or DEFAULT_GEMINI_KEY
    genai.configure(api_key=key)
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        # Fallback to local default / mock embedding if API fails (for robustness)
        print(f"[VectorStore] Embedding API error: {e}. Using dummy embedding.")
        return [0.0] * 768

def add_to_vector_store(agent_id: int, doc_id: int, filename: str, content: str, api_key: str = None):
    """Chunk, embed, and store document in ChromaDB."""
    chunks = chunk_text(content)
    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for idx, chunk in enumerate(chunks):
        chunk_id = f"agent_{agent_id}_doc_{doc_id}_chunk_{idx}"
        embedding = get_embedding(chunk, api_key)
        
        ids.append(chunk_id)
        embeddings.append(embedding)
        metadatas.append({
            "agent_id": int(agent_id),
            "doc_id": int(doc_id),
            "filename": filename
        })
        documents.append(chunk)

    if ids:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        print(f"[VectorStore] Added {len(ids)} chunks for doc {filename} (ID: {doc_id})")

def delete_from_vector_store(doc_id: int):
    """Delete all chunks belonging to a document ID."""
    try:
        collection.delete(where={"doc_id": int(doc_id)})
        print(f"[VectorStore] Deleted chunks for doc ID: {doc_id}")
    except Exception as e:
        print(f"[VectorStore] Error deleting doc ID {doc_id}: {e}")

def search_vector_store(agent_id: int, query: str, top_k: int = 5, api_key: str = None) -> list:
    """Search for relevant document chunks matching query."""
    try:
        query_embedding = get_embedding(query, api_key)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"agent_id": int(agent_id)}
        )
        # Return list of text chunks
        if results and 'documents' in results and results['documents']:
            return results['documents'][0]
        return []
    except Exception as e:
        print(f"[VectorStore] Search error: {e}")
        return []
