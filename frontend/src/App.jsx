import { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');
    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      setResponse(data.response || JSON.stringify(data));
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>LLM Performance Demo</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Enter your prompt here..."
          rows={4}
          style={{ width: '100%' }}
        />
        <br />
        <button type="submit" disabled={loading || !prompt.trim()}>
          {loading ? 'Querying...' : 'Send to LLM'}
        </button>
      </form>
      {error && <div style={{ color: 'red', marginTop: 10 }}>{error}</div>}
      {response && (
        <div style={{ marginTop: 20 }}>
          <strong>LLM Response:</strong>
          <pre style={{ background: '#f4f4f4', padding: 10 }}>{response}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
