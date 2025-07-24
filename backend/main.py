from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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

# Rate limiter (5 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class QueryRequest(BaseModel):
    prompt: str
    use_cache: bool = True
    use_rate_limit: bool = False

@app.post("/query")
async def query_llm(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    use_cache = data.get("use_cache", True)
    use_rate_limit = data.get("use_rate_limit", False)
    # Apply rate limiting if enabled
    if use_rate_limit:
        # 5 requests per minute per IP
        await limiter.limit("5/minute")(lambda req: None)(request)
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
