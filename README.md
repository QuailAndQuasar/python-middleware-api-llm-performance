# Python Middleware API LLM Performance Demo

## Backend (FastAPI)

1. Create and activate the virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

## Frontend (React)

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The React app will be available at `http://localhost:5173` (default Vite port).

## Usage
- The frontend will connect to the backend at `http://localhost:8000` (default FastAPI port).
- You can submit prompts and see the mock LLM responses.

## Demonstrating the Caching Mechanism

1. **Enable Caching:**
   - Make sure the "Enable Caching" checkbox is checked in the frontend UI.
2. **Submit a Prompt:**
   - Enter a prompt and click "Send to LLM".
   - The first submission will show a **Cache Miss** (orange indicator).
3. **Submit the Same Prompt Again:**
   - Submit the exact same prompt a second time.
   - The response will now show a **Cache Hit** (green indicator), meaning the result was served instantly from the backend cache.
4. **Disable Caching:**
   - Uncheck the "Enable Caching" checkbox.
   - Submitting any prompt (even repeated ones) will always show a **Cache Miss**.

This demonstrates how caching improves performance by avoiding repeated LLM calls for the same prompt.

## Demonstrating the Rate Limiting Mechanism

1. **Enable Rate Limiting:**
   - Check the "Enable Rate Limiting (5 req/min)" checkbox in the frontend UI.
2. **Submit Prompts Rapidly:**
   - Enter and submit prompts quickly (more than 5 times within a minute).
   - After the 5th request, you will see a red error message: "Rate limit exceeded. Please wait and try again."
3. **Wait and Retry:**
   - Wait for about a minute and try again; the limit will reset and you can submit more prompts.
4. **Disable Rate Limiting:**
   - Uncheck the "Enable Rate Limiting" checkbox to remove the restriction and allow unlimited requests.

This demonstrates how rate limiting protects the backend and LLM from overload or abuse.

## Demonstrating Async Processing

1. **Enable Async Processing:**
   - Check the "Enable Async Processing" checkbox in the frontend UI.
2. **Submit a Prompt:**
   - Enter a prompt and click "Send to LLM".
   - The frontend will show "Processing asynchronously..." while the backend processes the request in the background (simulated 3-second delay).
   - When the result is ready, it will appear automatically.
3. **Submit Multiple Prompts Quickly:**
   - Try submitting several prompts in quick succession.
   - Each will be processed in the background, and the frontend will update as results are ready.
4. **Disable Async Processing:**
   - Uncheck the "Enable Async Processing" checkbox to return to normal (synchronous) request/response behavior.

This demonstrates how async processing allows the backend to remain responsive and handle multiple requests concurrently, even when LLM calls are slow.
