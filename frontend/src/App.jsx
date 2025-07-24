import { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [useCache, setUseCache] = useState(true);
  const [useRateLimit, setUseRateLimit] = useState(false);
  const [cacheStatus, setCacheStatus] = useState(null); // 'hit' | 'miss' | null

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');
    setCacheStatus(null);
    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, use_cache: useCache, use_rate_limit: useRateLimit }),
      });
      if (res.status === 429) {
        setError('Rate limit exceeded. Please wait and try again.');
        return;
      }
      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      setResponse(data.response || JSON.stringify(data));
      if (data.cached === true) setCacheStatus('hit');
      else if (data.cached === false) setCacheStatus('miss');
      else setCacheStatus(null);
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
        <label>
          <input
            type="checkbox"
            checked={useCache}
            onChange={e => setUseCache(e.target.checked)}
          />
          Enable Caching
        </label>
        <br />
        <label>
          <input
            type="checkbox"
            checked={useRateLimit}
            onChange={e => setUseRateLimit(e.target.checked)}
          />
          Enable Rate Limiting (5 req/min)
        </label>
        <br />
        <button type="submit" disabled={loading || !prompt.trim()}>
          {loading ? 'Querying...' : 'Send to LLM'}
        </button>
      </form>
      {error && <div style={{ color: 'red', marginTop: 10 }}>{error}</div>}
      {cacheStatus && (
        <div style={{ marginTop: 20, fontWeight: 'bold', color: cacheStatus === 'hit' ? 'green' : 'orange' }}>
          {cacheStatus === 'hit' ? 'Cache Hit' : 'Cache Miss'}
        </div>
      )}
      {response && (
        <div style={{ marginTop: 10 }}>
          <strong>LLM Response:</strong>
          <pre style={{ background: '#f4f4f4', padding: 10 }}>{response}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
