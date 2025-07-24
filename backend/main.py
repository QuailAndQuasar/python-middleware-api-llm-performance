from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Or ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str

@app.post("/query")
async def query_llm(request: QueryRequest):
    # Forward the prompt to the /llm endpoint (mock LLM)
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/llm", json={"prompt": request.prompt})
        return JSONResponse(content=response.json())

@app.post("/llm")
async def mock_llm(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    # Simulate LLM response
    return {"response": f"[MOCK LLM] You said: {prompt}"}
