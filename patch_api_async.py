import sys
import os

file_path = r"c:\Users\Admin\Documents\Agentic AI\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Import BackgroundTasks if not present
if "BackgroundTasks" not in content:
    content = content.replace("from fastapi import FastAPI, UploadFile, File", "from fastapi import FastAPI, UploadFile, File, BackgroundTasks")

# 2. Update upload_knowledge
old_upload = """@app.post("/api/knowledge/{agent_id}")
async def upload_knowledge(agent_id: int, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore")
    
    # Save to database
    doc = add_knowledge(user_id, agent_id, file.filename, text_content)
    
    # Add to ChromaDB vector store
    try:
        add_to_vector_store(agent_id, doc["id"], file.filename, text_content)
    except Exception as e:
        print(f"[Main] Vector store insert warning: {e}")
        
    return doc"""

new_upload = """def process_knowledge_file(agent_id: int, doc_id: int, filename: str, text_content: str):
    from database import update_knowledge_status
    try:
        add_to_vector_store(agent_id, doc_id, filename, text_content)
        update_knowledge_status(doc_id, "synced")
    except Exception as e:
        print(f"[Main] Vector store insert error: {e}")
        update_knowledge_status(doc_id, "failed")

@app.post("/api/knowledge/{agent_id}")
async def upload_knowledge(agent_id: int, background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore")
    
    # Save to database with status 'processing'
    doc = add_knowledge(user_id, agent_id, file.filename, text_content)
    
    # Add to vector store asynchronously
    background_tasks.add_task(process_knowledge_file, agent_id, doc["id"], file.filename, text_content)
        
    return doc

@app.post("/api/knowledge/{agent_id}/sync/{doc_id}")
async def sync_knowledge(agent_id: int, doc_id: int, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    from database import get_knowledge_content_by_id, update_knowledge_status
    
    # Fetch content and verify ownership
    try:
        doc_info = get_knowledge_content_by_id(user_id, doc_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    # Update status back to processing
    update_knowledge_status(doc_id, "processing")
    
    # Re-queue background task
    background_tasks.add_task(process_knowledge_file, agent_id, doc_id, doc_info["filename"], doc_info["content"])
    
    return {"status": "processing"}"""

content = content.replace(old_upload, new_upload)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched main.py successfully.")
