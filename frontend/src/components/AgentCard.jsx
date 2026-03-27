import React from 'react';
import './AgentCard.css';

const AgentCard = ({ agent }) => {
  const { name, personality, score, alive, model } = agent;

  return (
    <div className={`agent-card ${alive ? 'alive' : 'eliminated'}`}>
      <div className="agent-header">
        <h3>{name}</h3>
        <span className="score">Score: {score}</span>
      </div>
      <div className="agent-body">
        <p className="personality">"{personality}"</p>
        {agent.lastAnswer && (
          <div className="last-answer">
            <strong>Last Answer:</strong>
            <p>{agent.lastAnswer}</p>
          </div>
        )}
        <p className="model-info">{model}</p>
        {!alive && <div className="eliminated-badge">ELIMINATED</div>}
      </div>
    </div>
  );
};

export default AgentCard;
