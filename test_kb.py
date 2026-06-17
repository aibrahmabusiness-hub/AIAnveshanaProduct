import sys
import os

# Add backend directory to sys.path so we can import
sys.path.append(r"c:\Users\Admin\Documents\Agentic AI\backend")

from vector_store import add_to_vector_store, search_vector_store

def test_kb():
    print("Testing Mistral Embedding + Supabase pgvector...")
    agent_id = 999  # dummy agent id
    doc_id = 9999   # dummy doc id
    filename = "test_kb_doc.txt"
    content = "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel."
    
    print("1. Adding document to vector store...")
    add_to_vector_store(agent_id, doc_id, filename, content)
    
    print("\n2. Searching vector store...")
    query = "Where is the Eiffel Tower?"
    results = search_vector_store(agent_id, query, top_k=2)
    
    print("\n--- Search Results ---")
    if results:
        for idx, res in enumerate(results):
            print(f"Result {idx+1}: {res}")
    else:
        print("No results found.")
        
    print("\nTest completed.")

if __name__ == "__main__":
    test_kb()
