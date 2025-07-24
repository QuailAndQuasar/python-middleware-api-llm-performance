from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uuid
import asyncio

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
# In-memory async task results
async_results = {}

# Rate limiter (5 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class QueryRequest(BaseModel):
    prompt: str
    use_cache: bool = True
    use_rate_limit: bool = False
    use_async: bool = False

async def process_llm_task(task_id, prompt, use_cache):
    # Simulate slow LLM
    await asyncio.sleep(3)
    # Check cache
    cached = False
    if use_cache and prompt in cache:
        result = cache[prompt]
        cached = True
    else:
        # Call mock LLM
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/llm", json={"prompt": prompt})
            data = response.json()
            result = data["response"]
            if use_cache:
                cache[prompt] = result
    async_results[task_id] = {"status": "completed", "response": result, "cached": cached}

@app.post("/query")
async def query_llm(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    prompt = data.get("prompt", "")
    use_cache = data.get("use_cache", True)
    use_rate_limit = data.get("use_rate_limit", False)
    use_async = data.get("use_async", False)
    # Apply rate limiting if enabled
    if use_rate_limit:
        await limiter.limit("5/minute")(lambda req: None)(request)
    if use_async:
        task_id = str(uuid.uuid4())
        async_results[task_id] = {"status": "processing"}
        background_tasks.add_task(process_llm_task, task_id, prompt, use_cache)
        return JSONResponse(content={"status": "processing", "task_id": task_id})
    if use_cache and prompt in cache:
        return JSONResponse(content={"response": cache[prompt], "cached": True})
    # Forward the prompt to the /llm endpoint (mock LLM)
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/llm", json={"prompt": prompt})
        data = response.json()
        if use_cache:
            cache[prompt] = data["response"]
        return JSONResponse(content={"response": data["response"], "cached": False})

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = async_results.get(task_id)
    if not result:
        return JSONResponse(content={"status": "not_found"}, status_code=404)
    return JSONResponse(content=result)

@app.post("/llm")
async def mock_llm(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    # Simulate LLM response
    return {"response": f"[MOCK LLM] You said: {prompt}"}
