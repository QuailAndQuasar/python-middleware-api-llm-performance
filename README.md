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
