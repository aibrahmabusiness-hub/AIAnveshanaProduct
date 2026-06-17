import re

file_path = r"c:\Users\Admin\Documents\Agentic AI\backend\vector_store.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace Gemini imports and keys
content = content.replace("import google.generativeai as genai", "import requests\nimport json")
content = content.replace("DEFAULT_GEMINI_KEY = os.getenv(\"GEMINI_API_KEY\", \"AIzaSyAYy8GjdrdjijABG7ozk0TKyDon8_4OKjc\")", "MISTRAL_API_KEY = os.getenv(\"MISTRAL_API_KEY\", \"\")")

# Replace get_embedding
old_get_embedding = """def get_embedding(text: str, api_key: str = None) -> list:
    \"\"\"Generate embedding for text using Gemini's models/embedding-001.\"\"\"
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
        print(f"[VectorStore] Embedding API error: {e}. Using dummy embedding.")
        return [0.0] * 768"""

new_get_embedding = """def get_embedding(text: str, api_key: str = None) -> list:
    \"\"\"Generate embedding for text using Mistral's mistral-embed.\"\"\"
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
            "inputs": [text]
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['data'][0]['embedding']
    except Exception as e:
        print(f"[VectorStore] Mistral Embedding API error: {e}. Using dummy embedding.")
        return [0.0] * 1024"""

content = content.replace(old_get_embedding, new_get_embedding)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched vector_store.py successfully.")
