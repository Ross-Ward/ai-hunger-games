import React, { useState, useEffect, useRef } from 'react';
import AgentCard from './components/AgentCard';
import './App.css';

function App() {
  const [agents, setAgents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [question, setQuestion] = useState('');
  const [round, setRound] = useState(0);
  const [connected, setConnected] = useState(false);
  const ws = useRef(null);
  const logsEndRef = useRef(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const connectWebSocket = () => {
    ws.current = new WebSocket('ws://localhost:8000/ws');

    ws.current.onopen = () => {
      console.log('Connected to WebSocket');
      setConnected(true);
      // Request initial state
      ws.current.send(JSON.stringify({ action: 'get_state' }));
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'state_update') {
        setAgents(message.agents);
        setLogs(prev => [...prev, ...message.logs]); // Append logs or replace? Replace might be safer for state update
      } else if (message.type === 'round_update') {
        // Merge answers into agents
        const updatedAgents = message.data.scores.map(agent => ({
          ...agent,
          lastAnswer: message.data.answers[agent.name] || "No answer"
        }));
        setAgents(updatedAgents);
        setRound(message.data.round);
        setLogs(prev => [...prev, ...message.logs]);
      }
    };

    ws.current.onclose = () => {
      console.log('Disconnected');
      setConnected(false);
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
  };

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSpawn = async () => {
    try {
      const res = await fetch('http://localhost:8000/spawn?count=5', { method: 'POST' });
      const data = await res.json();
      setAgents(data.agents);
      setLogs(prev => [...prev, "Spawned new agents."]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleStartRound = () => {
    if (!question) return;
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'start_round',
        question: question
      }));
      setLogs(prev => [...prev, `Starting round with question: ${question}`]);
      setQuestion('');
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Hunger Games</h1>
        <div className={`status-indicator ${connected ? 'online' : 'offline'}`}>
          {connected ? 'ONLINE' : 'OFFLINE'}
        </div>
      </header>

      <main className="arena">
        <div className="agents-grid">
          {agents.map((agent, index) => (
            <AgentCard key={index} agent={agent} />
          ))}
          {agents.length === 0 && (
            <div className="empty-state">
              <p>No agents in the arena.</p>
              <button onClick={handleSpawn} className="spawn-btn">SPAWN TRIBUTES</button>
            </div>
          )}
        </div>
      </main>

      <aside className="control-panel">
        <div className="logs-panel">
          <h2>Arena Logs</h2>
          <div className="logs-content">
            {logs.map((log, i) => (
              <div key={i} className="log-entry">{log}</div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        <div className="input-panel">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question to the tributes..."
            onKeyPress={(e) => e.key === 'Enter' && handleStartRound()}
          />
          <button onClick={handleStartRound} disabled={!connected || agents.length === 0}>
            START ROUND {round + 1}
          </button>
        </div>
      </aside>
    </div>
  );
}

export default App;
