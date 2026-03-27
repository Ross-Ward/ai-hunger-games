import requests
import time
import random

BASE_URL = "http://localhost:8000"

def simulate():
    print("Starting simulation...")
    
    # 1. Spawn if needed (optional, but good to ensure state)
    requests.post(f"{BASE_URL}/spawn?count=5")
    
    questions = [
        "What is the best strategy for survival?",
        "Trust no one or trust everyone?",
        "How do you find food in the wild?",
        "What is your weapon of choice?",
        "Day or Night?",
        "Climb a tree or dig a hole?",
        "Attack or Defend?",
        "Final words before the end?"
    ]

    # We need to use the websocket to drive the game properly as per main.py logic?
    # Actually main.py has a websocket endpoint that calls game_engine.start_round.
    # But wait, main.py DOES NOT have a REST endpoint for start_round, only websocket!
    # I need to add a REST endpoint or use a websocket client.
    # Let's add a REST endpoint to main.py for easier testing/simulation.
    
    for i, q in enumerate(questions):
        print(f"--- Round {i+1} ---")
        print(f"Question: {q}")
        try:
            res = requests.post(f"{BASE_URL}/start_round", params={"question": q})
            if res.status_code == 200:
                data = res.json()
                print("Round complete.")
                # print(data) # Verbose
            else:
                print(f"Error: {res.text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        time.sleep(1) # Brief pause

    print("Simulation complete. Check interaction_history.json")

if __name__ == "__main__":
    simulate()
