import asyncio
from typing import List, Dict
from .ollama_client import OllamaClient
import random

class Agent:
    def __init__(self, name: str, personality: str, model: str):
        self.name = name
        self.personality = personality
        self.model = model
        self.score = 0
        self.alive = True

    def to_dict(self):
        return {
            "name": self.name,
            "personality": self.personality,
            "score": self.score,
            "alive": self.alive,
            "model": self.model
        }

class GameEngine:
    def __init__(self):
        self.agents: List[Agent] = []
        self.round = 0
        self.max_rounds = 8
        self.ollama_client = OllamaClient()
        self.logs = []

    def log(self, message):
        print(message)
        self.logs.append(message)

    def spawn_agents(self, count=5):
        # In a real app, we might generate these personalities using an LLM too!
        personalities = [
            "Aggressive and competitive",
            "Shy and poetic",
            "Logical and cold",
            "Funny and sarcastic",
            "Wise and philosophical",
            "Chaotic and random",
            "Polite and helpful",
            "Suspicious and paranoid"
        ]
        
        for i in range(count):
            p = personalities[i % len(personalities)]
            self.agents.append(Agent(f"District {i+1}", p, "llama3"))
        
        self.log(f"Spawned {count} agents.")

    async def start_round(self, question: str):
        self.round += 1
        self.log(f"Starting Round {self.round}: {question}")
        
        # 1. Get Answers
        answers = {}
        for agent in self.agents:
            if not agent.alive: continue
            prompt = f"Question: {question}\nAnswer as your personality: {agent.personality}"
            response = await self.ollama_client.generate(prompt)
            answers[agent.name] = response
            self.log(f"{agent.name} answered: {response}")

        # 2. Voting (Simplified: Random scores for now, or ask LLM to rate)
        # Let's ask the LLM to rate each answer 1-10
        scores = {}
        for voter in self.agents:
            if not voter.alive: continue
            for candidate_name, answer in answers.items():
                if candidate_name == voter.name: continue # Don't vote for self
                
                vote_prompt = f"""
                You are {voter.name} ({voter.personality}).
                Rate this answer from 1 to 10.
                CRITICAL: You must output ONLY a single integer number. Do not write any words.
                
                Question: {question}
                Answer: {answer}
                
                Score:"""
                try:
                    rating_str = await self.ollama_client.generate(vote_prompt)
                    # Extract number
                    import re
                    match = re.search(r'\d+', rating_str)
                    if match:
                        rating = int(match.group())
                        rating = max(1, min(10, rating))
                    else:
                        self.log(f"VOTE ERROR: Could not parse rating from {voter.name}: '{rating_str}'")
                        rating = 5 # Default
                except Exception as e:
                    self.log(f"VOTE EXCEPTION: {e}")
                    rating = 5
                
                scores[candidate_name] = scores.get(candidate_name, 0) + rating
                self.log(f"{voter.name} rated {candidate_name}: {rating} (Raw: '{rating_str.strip()}')")

        # 3. Update Scores
        for name, score in scores.items():
            for agent in self.agents:
                if agent.name == name:
                    agent.score += score

        # Save interaction history
        self.save_interactions()

        # 4. Check Elimination
        if self.round >= self.max_rounds:
            self.eliminate_weakest()

        return {
            "round": self.round,
            "answers": answers,
            "scores": [a.to_dict() for a in self.agents]
        }

    def save_interactions(self):
        import json
        try:
            with open("interaction_history.json", "w") as f:
                json.dump(self.logs, f, indent=2)
        except Exception as e:
            print(f"Error saving interactions: {e}")

    def eliminate_weakest(self):
        sorted_agents = sorted(self.agents, key=lambda x: x.score)
        # Eliminate bottom 2
        for i in range(min(2, len(sorted_agents))):
            victim = sorted_agents[i]
            victim.alive = False
            self.log(f"ELIMINATED: {victim.name} with score {victim.score}")
            
            # Replace
            new_agent = Agent(f"New District {self.round + i + 100}", "Vengeful Spirit", "llama3")
            self.agents.append(new_agent) # Append new, keep old as dead
            self.log(f"SPAWNED: {new_agent.name}")
