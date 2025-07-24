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

# In-memory cache
cache = {}

class QueryRequest(BaseModel):
    prompt: str
    use_cache: bool = True

@app.post("/query")
async def query_llm(request: QueryRequest):
    prompt = request.prompt
    use_cache = request.use_cache
    if use_cache and prompt in cache:
        return JSONResponse(content={"response": cache[prompt], "cached": True})
    # Forward the prompt to the /llm endpoint (mock LLM)
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/llm", json={"prompt": prompt})
        data = response.json()
        if use_cache:
            cache[prompt] = data["response"]
        return JSONResponse(content={"response": data["response"], "cached": False})

@app.post("/llm")
async def mock_llm(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    # Simulate LLM response
    return {"response": f"[MOCK LLM] You said: {prompt}"}
