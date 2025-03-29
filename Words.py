import requests
from time import sleep
import random

# API endpoints
host = "http://172.18.4.158:8000"
post_url = f"{host}/submit-word"
get_url = f"{host}/get-word"
status_url = f"{host}/status"

NUM_ROUNDS = 5
PENALTY_COST = 30

# Define the player word list and their costs
player_words = {
    "1": {"text": "Feather", "cost": 1},
    "2": {"text": "Coal", "cost": 1},
    "3": {"text": "Pebble", "cost": 1},
    "4": {"text": "Leaf", "cost": 2},
    "5": {"text": "Paper", "cost": 2},
    "6": {"text": "Rock", "cost": 2},
    "7": {"text": "Water", "cost": 3},
    "8": {"text": "Twig", "cost": 3},
    "9": {"text": "Sword", "cost": 4},
    "10": {"text": "Shield", "cost": 4},
    "11": {"text": "Gun", "cost": 5},
    "12": {"text": "Flame", "cost": 5},
    "13": {"text": "Rope", "cost": 5},
    "14": {"text": "Disease", "cost": 6},
    "15": {"text": "Cure", "cost": 6},
    "16": {"text": "Bacteria", "cost": 6},
    "17": {"text": "Shadow", "cost": 7},
    "18": {"text": "Light", "cost": 7},
    "19": {"text": "Virus", "cost": 7},
    "20": {"text": "Sound", "cost": 8},
    "21": {"text": "Time", "cost": 8},
    "22": {"text": "Fate", "cost": 8},
    "23": {"text": "Earthquake", "cost": 9},
    "24": {"text": "Storm", "cost": 9},
    "25": {"text": "Vaccine", "cost": 9},
    "26": {"text": "Logic", "cost": 10},
    "27": {"text": "Gravity", "cost": 10},
    "28": {"text": "Robots", "cost": 10},
    "29": {"text": "Stone", "cost": 11},
    "30": {"text": "Echo", "cost": 11},
    "31": {"text": "Thunder", "cost": 12},
    "32": {"text": "Karma", "cost": 12},
    "33": {"text": "Wind", "cost": 13},
    "34": {"text": "Ice", "cost": 13},
    "35": {"text": "Sandstorm", "cost": 13},
    "36": {"text": "Laser", "cost": 14},
    "37": {"text": "Magma", "cost": 14},
    "38": {"text": "Peace", "cost": 14},
    "39": {"text": "Explosion", "cost": 15},
    "40": {"text": "War", "cost": 15},
    "41": {"text": "Enlightenment", "cost": 15},
    "42": {"text": "Nuclear Bomb", "cost": 16},
    "43": {"text": "Volcano", "cost": 16},
    "44": {"text": "Whale", "cost": 17},
    "45": {"text": "Earth", "cost": 17},
    "46": {"text": "Moon", "cost": 17},
    "47": {"text": "Star", "cost": 18},
    "48": {"text": "Tsunami", "cost": 18},
    "49": {"text": "Supernova", "cost": 19},
    "50": {"text": "Antimatter", "cost": 19},
    "51": {"text": "Plague", "cost": 20},
    "52": {"text": "Rebirth", "cost": 20},
    "53": {"text": "Tectonic Shift", "cost": 21},
    "54": {"text": "Gamma-Ray Burst", "cost": 22},
    "55": {"text": "Human Spirit", "cost": 23},
    "56": {"text": "Apocalyptic Meteor", "cost": 24},
    "57": {"text": "Earth’s Core", "cost": 25},
    "58": {"text": "Neutron Star", "cost": 26},
    "59": {"text": "Supermassive Black Hole", "cost": 35},
    "60": {"text": "Entropy", "cost": 45}
}


# Enhanced semantic relationships - what beats what
SEMANTIC_RULES = {
    # Natural elements
    "Water": ["Fire", "Flame", "Magma", "Coal"],
    "Fire": ["Paper", "Leaf", "Twig", "Feather"],
    "Rock": ["Scissors", "Glass", "Egg"],
    "Paper": ["Rock", "Stone"],
    
    # Technology/weapons
    "Shield": ["Sword", "Gun", "Laser"],
    "Gun": ["Sword", "Knife"],
    
    # Medical/science
    "Vaccine": ["Virus", "Disease", "Bacteria", "Plague"],
    "Cure": ["Disease", "Virus"],
    
    # Nature/weather
    "Storm": ["Paper", "Leaf", "Feather"],
    "Earthquake": ["Building", "Bridge"],
    "Tsunami": ["Coastal City", "Beach"],
    
    # Cosmic/abstract
    "Black Hole": ["Star", "Planet", "Light"],
    "Time": ["Sound", "Wind"],
    "Gravity": ["Flight", "Jump"],
    
    # Fallbacks for unmatched words
    "default": {
        "high_cost": ["Supermassive Black Hole", "Nuclear Bomb", "Gamma-Ray Burst"],
        "low_cost": ["Rock", "Paper", "Scissors"]
    }
}

def what_beats(sys_word):
    # First try to find a direct semantic counter
    for counter_word, beats_list in SEMANTIC_RULES.items():
        if sys_word in beats_list:
            # Find the counter word in our word list
            for word_id, word_data in player_words.items():
                if word_data["text"] == counter_word:
                    return word_id
    
    # If no direct counter found, use strategic fallbacks
    if random.random() < 0.7:  # 70% chance to pick high-cost word
        high_cost_words = [word_id for word_id, word_data in player_words.items() 
                          if word_data["cost"] >= 10]
        if high_cost_words:
            return random.choice(high_cost_words)
    
    # Default to random choice
    return random.choice(list(player_words.keys()))

def get_current_round():
    try:
        response = requests.get(get_url, timeout=5)
        if response.status_code == 200:
            return response.json()['round']
    except requests.exceptions.RequestException:
        pass
    return -1

def play_game(player_id):
    total_cost = 0
    
    for round_id in range(1, NUM_ROUNDS + 1):
        # Wait for the current round to match our round_id
        while True:
            current_round = get_current_round()
            if current_round == round_id:
                break
            sleep(1)
        
        # Get system word
        try:
            response = requests.get(get_url, timeout=5)
            if response.status_code != 200:
                print(f"Error getting word: {response.status_code}")
                return None
            
            sys_word = response.json()['word']
            print(f"\nRound {round_id}: System chose '{sys_word}'")
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return None

        # Choose counter word
        chosen_word_id = what_beats(sys_word)
        chosen_word = player_words[chosen_word_id]
        print(f"Player chose '{chosen_word['text']}' (Cost: {chosen_word['cost']})")

        # Submit word
        try:
            response = requests.post(
                post_url,
                json={"player_id": player_id, "word_id": chosen_word_id, "round_id": round_id},
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"Submission failed: {response.text}")
                return None
            
            result = response.json()
            print(f"Result: {result.get('outcome', 'unknown')}")
            
            # Update cost
            total_cost += chosen_word['cost']
            if result.get("outcome") == "fail":
                total_cost += PENALTY_COST
                print(f"Penalty applied! (+{PENALTY_COST})")
            
        except requests.exceptions.RequestException as e:
            print(f"Submission error: {e}")
            return None

        # Check game status
        try:
            status = requests.get(status_url, timeout=5).json()
            print(f"Status: P1 {status.get('p1_won', False)} | P2 {status.get('p2_won', False)}")
            
            if status.get("game_over", False):
                print("Game over!")
                break
        except requests.exceptions.RequestException:
            pass

        sleep(1)  # Be polite to the server

    print(f"\nFinal Total Cost: ${total_cost}")
    return total_cost

if __name__ == "__main__":
    player_id = "player1"  # Replace with your player ID
    play_game(player_id)