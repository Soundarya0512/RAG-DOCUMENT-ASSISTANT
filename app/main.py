from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag_pipeline import RAGChatbot
from config import *
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="RAG DOCUMENT ASSITANCE")
chatbot=RAGChatbot()
chatbot.load_vector_store()

class QueryRequest(BaseModel):
    question: str

class SourceInfo(BaseModel):
    source: str
    page: str
    preview: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    status: str
    sources: list[SourceInfo]

@app.get("/health")
async def health_check():
    return {"status": "healthy",
            "message":" RAG Chatbot is running"}

@app.post("/query")
async def query_chatbot(request: QueryRequest):
    if len(request.question.strip()) ==0:
        raise HTTPException(status_code=400, detail="Question  cannot be empty!")
    
    if len(request.question)>500:
        raise HTTPException(status_code=400, detail="Question too long!")
    
    if chatbot.vectorstore is None:
        raise HTTPException(status_code=503, detail="System not ready!")
    
    result=chatbot.query(request.question)
    answer=result["answer"]
    sources=result["sources"]
    return QueryResponse(
        question=request.question,
        answer=answer,
        sources=sources,
        status="success"
    )

@app.post('/ingest')
async def ingest():
    success = chatbot.ingest_documents()    
    if success:
        return {"status": "success",
                "message": "Documents loaded successfully!"}
    else:
        return {"status":"error",
                "message": "Failed to load documents"}

@app.post('/query_with_history')
async def query_with_history(request:QueryRequest):
    result=chatbot.query_with_history(request.question)
    answer=result["answer"]
    return {
        "question": request.question,
        "answer": answer,
        "status": "success"
    }
@app.post('/clear_history')
async def clear_history():
    chatbot.clear_history()
    return {"status": "cleared"}

@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):

    filetype=file.content_type
    MAX_SIZE=10 * 1024 * 1024

    if filetype not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Invalid file type.Only PDF and txt files are allowed")

    contents = await file.read()
    if len(contents)>MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size is larger than expected")
    
    file_path=f"data/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(contents)
    
    success = chatbot.ingest_documents()    
    if success:
        return {"status": "success",
                "filesize": len(contents),
                "filetype": filetype,
                "filename": file.filename,
                "message": "File uploaded and processed!"}
    else:
        return {"status":"error",
                "message": "File saved but ingestion failed"}
    
app.mount("/", StaticFiles(directory="static",html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host=SERVER_HOST, port=SERVER_PORT)






