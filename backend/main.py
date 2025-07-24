from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from typing import Optional
from slowapi.errors import RateLimitExceeded
import uuid
import asyncio

import time

app = FastAPI()

# Add CORS middleware with more permissive settings for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to the browser
)

# Add CORS headers to all responses as a fallback
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    return response

from cachetools import TTLCache
# LRU cache with 10-minute expiry, max 128 entries
cache = TTLCache(maxsize=128, ttl=600)
# In-memory async task results
async_results = {}
# Store timestamps for each task
async_task_timestamps = {}

# Rate limiter (5 requests per minute per user or IP)
def get_key(request: Request) -> str:
    try:
        data = request._json if hasattr(request, '_json') else None
        if not data:
            data = request._body if hasattr(request, '_body') else None
        if not data:
            data = {}
        user_id = data.get("user_id") if isinstance(data, dict) else None
    except Exception:
        user_id = None
    if user_id:
        return f"user:{user_id}"
    return get_remote_address(request)

limiter = Limiter(key_func=get_key)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class QueryRequest(BaseModel):
    prompt: str
    use_cache: bool = True
    use_async: bool = False
    context_size: int = 200
    use_lmstudio: bool = False
    user_id: Optional[str] = None

def get_delay_for_context(context_size):
    # 1s per 200 chars, min 1s, max 5s
    return min(max(1, context_size // 200), 5)

async def call_lmstudio(prompt):
    # LM Studio OpenAI-compatible endpoint
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama2",  # Default model name; LM Studio will use the first available if not found
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        # Extract the response text
        return result["choices"][0]["message"]["content"]

async def process_llm_task(task_id, prompt, use_cache, context_size, use_lmstudio):
    truncated_prompt = prompt[:context_size]
    delay = get_delay_for_context(context_size)
    await asyncio.sleep(delay)
    cached = False
    if use_cache and truncated_prompt in cache:
        result = cache[truncated_prompt]
        cached = True
    else:
        if use_lmstudio:
            result = await call_lmstudio(truncated_prompt)
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8000/llm", json={"prompt": truncated_prompt})
                data = response.json()
                result = data["response"]
        if use_cache:
            cache[truncated_prompt] = result
    async_results[task_id] = {"status": "completed", "response": result, "cached": cached}
    async_task_timestamps[task_id] = time.time()

@app.post("/query")
@limiter.limit("5/minute")
async def query_llm(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    prompt = data.get("prompt", "")
    use_cache = data.get("use_cache", True)
    use_async = data.get("use_async", False)
    context_size = data.get("context_size", 200)
    use_lmstudio = data.get("use_lmstudio", False)
    truncated_prompt = prompt[:context_size]
    if use_async:
        task_id = str(uuid.uuid4())
        async_results[task_id] = {"status": "processing"}
        async_task_timestamps[task_id] = time.time()
        background_tasks.add_task(process_llm_task, task_id, prompt, use_cache, context_size, use_lmstudio)
        return JSONResponse(content={"status": "processing", "task_id": task_id})
    if use_cache and truncated_prompt in cache:
        return JSONResponse(content={"response": cache[truncated_prompt], "cached": True})
    delay = get_delay_for_context(context_size)
    await asyncio.sleep(delay)
    if use_lmstudio:
        result = await call_lmstudio(truncated_prompt)
        if use_cache:
            cache[truncated_prompt] = result
        return JSONResponse(content={"response": result, "cached": False})
    # Forward the prompt to the /llm endpoint (mock LLM)
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/llm", json={"prompt": truncated_prompt})
        data = response.json()
        if use_cache:
            cache[truncated_prompt] = data["response"]
        return JSONResponse(content={"response": data["response"], "cached": False})

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = async_results.get(task_id)
    if not result:
        return JSONResponse(content={"status": "not_found"}, status_code=404)
    return JSONResponse(content=result)

@app.on_event("startup")
async def cleanup_async_tasks():
    async def cleanup_loop():
        while True:
            now = time.time()
            to_delete = []
            for task_id, timestamp in list(async_task_timestamps.items()):
                # Remove tasks: completed >10min, or any >15min old
                status = async_results.get(task_id, {}).get("status")
                if (status == "completed" and now - timestamp > 600) or (now - timestamp > 900):
                    to_delete.append(task_id)
            for task_id in to_delete:
                async_results.pop(task_id, None)
                async_task_timestamps.pop(task_id, None)
            await asyncio.sleep(600)  # Run every 10 minutes
    asyncio.create_task(cleanup_loop())

@app.post("/llm")
async def mock_llm(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    # Simulate LLM response
    return {"response": f"[MOCK LLM] You said: {prompt}"}
