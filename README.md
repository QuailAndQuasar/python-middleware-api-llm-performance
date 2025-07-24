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

## Demonstrating Context Window Management

1. **Adjust the Context Size Slider:**
   - Use the "Context Size" slider in the frontend UI to select how many characters of your prompt are sent to the LLM (range: 50–1000 characters).
2. **Submit a Prompt:**
   - Enter a prompt and click "Send to LLM".
   - The backend will only process up to the selected number of characters from your prompt.
3. **Observe Response Time:**
   - The frontend displays the response time for each request.
   - Larger context sizes will result in longer simulated processing times (1s per 200 characters, minimum 1s, maximum 5s).
4. **Experiment:**
   - Try different context sizes and see how it affects the response time and the LLM's output.

This demonstrates how managing the context window can impact LLM performance and user experience.

## Performance and Security Optimizations

This project implements several key optimizations to make LLM API interactions more efficient, responsive, and secure:

### 1. Caching System
- **What**: LRU (Least Recently Used) cache with TTL (Time To Live) expiration
- **Benefits**:
  - ⚡ Faster response times for repeated queries
  - 💰 Reduced API costs through fewer LLM calls
  - 🛡️ Protection against rate limiting by reducing API load

### 2. Rate Limiting
- **What**: Server-side rate limiting (5 requests per minute per user/IP)
- **Benefits**:
  - 🛡️ Prevents abuse and DDoS attacks
  - 💰 Controls operational costs
  - ⚖️ Ensures fair usage among all users

### 3. Asynchronous Processing
- **What**: Non-blocking request handling
- **Benefits**:
  - 🚀 Improved server throughput
  - 💻 Responsive UI during long-running operations
  - 🔄 Supports multiple concurrent requests

### 4. Context Size Management
- **What**: Configurable character limits on prompts
- **Benefits**:
  - ⚡ Faster processing of smaller inputs
  - 💰 Reduced token usage costs
  - ⏱️ More predictable response times

### 5. Security Measures
- **CORS Protection**: Properly configured to prevent CSRF attacks
- **Input Validation**: All user inputs are validated and sanitized
- **Error Handling**: Comprehensive error handling and user feedback
- **Secure Headers**: Added security headers to HTTP responses

### 6. Frontend Optimizations
- **Efficient State Management**: Minimized re-renders for better performance
- **Responsive Design**: Works across different devices and screen sizes
- **Clear Feedback**: Visual indicators for all states (loading, success, error)

### 7. Resource Management
- **Async Task Cleanup**: Prevents memory leaks
- **Connection Pooling**: Efficient database and API connection handling
- **Graceful Shutdown**: Proper cleanup on server shutdown

These optimizations work together to create a robust, efficient, and secure LLM API integration while providing an excellent user experience.
