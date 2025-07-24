import { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [useCache, setUseCache] = useState(true);
  const [useAsync, setUseAsync] = useState(false);
  const [useLMStudio, setUseLMStudio] = useState(false);
  const [contextSize, setContextSize] = useState(200);
  const [cacheStatus, setCacheStatus] = useState(null); // 'hit' | 'miss' | null
  const [responseTime, setResponseTime] = useState(null);

  const pollForResult = async (taskId, startTime) => {
    let attempts = 0;
    const maxAttempts = 20; // about 10 seconds total
    const pollInterval = 500; // ms
    
    try {
      while (attempts < maxAttempts) {
        await new Promise(res => setTimeout(res, pollInterval));
        const res = await fetch(`http://localhost:8000/result/${taskId}`);
        
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        
        if (data.status === 'completed') {
          setResponse(data.response || 'No response content');
          setCacheStatus(data.cached === true ? 'hit' : 'miss');
          setResponseTime(Date.now() - startTime);
          setLoading(false);
          return;
        } else if (data.status === 'error') {
          throw new Error(data.message || 'Error processing request');
        }
        
        attempts++;
      }
      
      throw new Error('Processing took too long');
    } catch (err) {
      setError(`Error: ${err.message}. Please try again.`);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResponse('');
    setCacheStatus(null);
    setResponseTime(null);
    const truncatedPrompt = prompt.slice(0, contextSize);
    const startTime = Date.now();
    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: truncatedPrompt, use_cache: useCache, use_async: useAsync, context_size: contextSize, use_lmstudio: useLMStudio }),
      });
      if (res.status === 429) {
        setError('Rate limit exceeded. Please wait and try again.');
        setLoading(false);
        return;
      }
      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      if (data.status === 'processing' && data.task_id) {
        pollForResult(data.task_id, startTime);
        if (useAsync) {
          setPrompt(''); // Clear prompt for next input
        }
        return;
      }
      setResponse(data.response || JSON.stringify(data));
      if (data.cached === true) setCacheStatus('hit');
      else if (data.cached === false) setCacheStatus('miss');
      else setCacheStatus(null);
      setResponseTime(Date.now() - startTime);
    } catch (err) {
      setError('Error: ' + err.message);
      setLoading(false);
    } finally {
      if (!useAsync) setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>LLM Performance Demo</h1>
      <div className="main-card">
        <div className="form-section">
          <h2>Query LLM</h2>
          <form onSubmit={handleSubmit} className="llm-form">
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="Enter your prompt here..."
              rows={4}
              className="prompt-input"
              required
            />
            <button type="submit" className="submit-btn" disabled={loading || !prompt.trim()}>
              {loading ? (useAsync ? 'Processing asynchronously...' : 'Querying...') : 'Send to LLM'}
            </button>
            <label className="form-label">
              Context Size: <span className="context-value">{contextSize} characters</span>
              <input
                type="range"
                min={50}
                max={1000}
                step={50}
                value={contextSize}
                onChange={e => setContextSize(Number(e.target.value))}
                className="slider"
              />
              <div className="context-confirm">
                Using first {contextSize} characters of your prompt
              </div>
            </label>
            <div className="option-section">
              <label className="option-label">
                <input
                  type="checkbox"
                  checked={useCache}
                  onChange={e => setUseCache(e.target.checked)}
                />
                Enable Caching
              </label>
              <div className="metric-desc">
                <div className="metric-what"><strong>What:</strong> Caching stores LLM responses for repeated prompts.</div>
                <div className="metric-why"><strong>Why:</strong> Reduces latency and server load for duplicate requests.</div>
                <div className="metric-how"><strong>How to test:</strong> Submit a prompt twice with caching enabled; first is a <span style={{color:'orange'}}>Cache Miss</span>, second is a <span style={{color:'green'}}>Cache Hit</span> (instant response).</div>
              </div>
            </div>

            <div className="option-section">
              <label className="option-label">
                <input
                  type="checkbox"
                  checked={useAsync}
                  onChange={e => setUseAsync(e.target.checked)}
                />
                Enable Async Processing
              </label>
              <div className="metric-desc">
                <div className="metric-what"><strong>What:</strong> Async processing handles LLM requests in the background.</div>
                <div className="metric-why"><strong>Why:</strong> Prevents UI blocking and allows submitting multiple prompts in quick succession.</div>
                <div className="metric-how">
                  <strong>How to test:</strong>
                  <ol style={{margin: '0.5em 0 0 1em', paddingLeft: '1em'}}>
                    <li>Enable this option</li>
                    <li>Submit a prompt - it will clear immediately</li>
                    <li>Submit more prompts without waiting</li>
                    <li>Watch as responses appear in order when ready</li>
                  </ol>
                </div>
              </div>
            </div>

            <div className="option-section disabled-option">
              <div className="disabled-note">
                ℹ️ Limited local LLM options available for Mac OS X 11.7
              </div>
              <label className="option-label">
                <input
                  type="checkbox"
                  checked={false}
                  disabled
                  onChange={() => {}}
                />
                Use LM Studio (local LLM) - Disabled
              </label>
              <div className="metric-desc">
                <div className="metric-what"><strong>What:</strong> LM Studio switches backend to a local LLM via LM Studio.</div>
                <div className="metric-why"><strong>Why:</strong> Allows comparison between mock and real LLM responses.</div>
                <div className="metric-how">
                  <strong>Note:</strong> This feature is currently disabled due to limited local LLM options for Mac OS X 11.7.
                </div>
              </div>
            </div>
        </form>
        
        <div className="llm-source">
          LLM Source: <span>{useLMStudio ? 'LM Studio' : 'Mock LLM'}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Rate Limiting:</span>
          <span>5 req/min (always on)</span>
        </div>
        <div className="metric-desc">
          <div className="metric-what"><strong>What:</strong> Rate limiting restricts each user to 5 requests per minute.</div>
          <div className="metric-why"><strong>Why:</strong> Prevents abuse and protects server resources.</div>
          <div className="metric-how"><strong>How to test:</strong> Submit {'>'}5 prompts quickly; you'll see an error after the 5th until a minute passes.</div>
        </div>
        {error && <div className="error-msg">{error}</div>}
        </div>
        <div className="result-section">
          <h2>LLM Response</h2>
          {response ? (
            <pre className="llm-response">{response}</pre>
          ) : (
            <div className="placeholder">Your LLM response will appear here.</div>
          )}
          <div className="status-section">
            {cacheStatus && (
              <div className={cacheStatus === 'hit' ? 'cache-hit' : 'cache-miss'}>
                {cacheStatus === 'hit' ? '✓ Cache Hit' : '↻ Cache Miss'}
              </div>
            )}
            {responseTime !== null && (
              <div className="response-time">
                <strong>Response Time:</strong> {responseTime} ms
              </div>
            )}
            {error && <div className="error-msg">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
