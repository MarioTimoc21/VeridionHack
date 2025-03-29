import requests
from time import sleep
import random
from collections import defaultdict

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
    "57": {"text": "Earth's Core", "cost": 25},
    "58": {"text": "Neutron Star", "cost": 26},
    "59": {"text": "Supermassive Black Hole", "cost": 35},
    "60": {"text": "Entropy", "cost": 45}
}

word_text_to_id = {data["text"].lower(): word_id for word_id, data in player_words.items()}


SEMANTIC_RELATIONSHIPS = {
    "feather": {
        "beats": ["pebble", "leaf", "twig"],
        "beaten_by": ["rock", "flame", "water", "wind", "storm"]
    },
    "coal": {
        "beats": ["feather", "paper", "leaf", "twig"],
        "beaten_by": ["water", "rock", "flame"]
    },
    "pebble": {
        "beats": ["feather", "twig"],
        "beaten_by": ["rock", "water", "earthquake"]
    },
    "leaf": {
        "beats": ["pebble", "feather"],
        "beaten_by": ["flame", "wind", "storm", "sandstorm"]
    },
    "paper": {
        "beats": ["rock", "stone", "logic"],
        "beaten_by": ["flame", "water", "wind", "scissors"]
    },
    "rock": {
        "beats": ["feather", "pebble", "scissors"],
        "beaten_by": ["paper", "earthquake", "explosion", "water", "tectonic shift"]
    },
    "water": {
        "beats": ["flame", "fire", "coal", "magma", "volcano", "explosion", "nuclear bomb"],
        "beaten_by": ["ice", "gravity", "earth", "tectonic shift", "sandstorm"]
    },
    "twig": {
        "beats": ["feather", "leaf"],
        "beaten_by": ["flame", "rock", "water", "wind"]
    },

    "sword": {
        "beats": ["rope", "feather", "leaf", "twig"],
        "beaten_by": ["shield", "gun", "explosion", "laser"]
    },
    "shield": {
        "beats": ["sword", "rock", "pebble", "feather"],
        "beaten_by": ["gun", "laser", "explosion", "nuclear bomb"]
    },
    "gun": {
        "beats": ["shield", "sword", "feather", "leaf"],
        "beaten_by": ["water", "explosion", "peace", "nuclear bomb"]
    },
    "flame": {
        "beats": ["feather", "leaf", "paper", "twig", "rope"],
        "beaten_by": ["water", "sand", "rock", "explosion", "ice"]
    },
    "rope": {
        "beats": ["feather", "leaf", "twig", "pebble"],
        "beaten_by": ["sword", "flame", "laser"]
    },
    "disease": {
        "beats": ["feather", "leaf", "human spirit"],
        "beaten_by": ["cure", "vaccine", "enlightenment"]
    },
    "cure": {
        "beats": ["disease", "bacteria", "virus", "plague"],
        "beaten_by": ["time", "fate", "entropy"]
    },
    "bacteria": {
        "beats": ["rope", "leaf", "paper"],
        "beaten_by": ["cure", "vaccine", "flame"]
    },
    "shadow": {
        "beats": ["light", "feather", "twig", "leaf"],
        "beaten_by": ["light", "sun", "star", "flame"]
    },
    "light": {
        "beats": ["shadow", "darkness", "bacteria", "virus"],
        "beaten_by": ["black hole", "shadow", "supermassive black hole"]
    },
    "virus": {
        "beats": ["human spirit", "bacteria", "disease"],
        "beaten_by": ["vaccine", "cure", "light", "flame"]
    },
    "sound": {
        "beats": ["shadow", "silence", "feather", "leaf"],
        "beaten_by": ["echo", "vacuum", "black hole"]
    },
    "time": {
        "beats": ["rock", "stone", "mountain", "human constructs"],
        "beaten_by": ["black hole", "eternity", "entropy", "supermassive black hole"]
    },
    "fate": {
        "beats": ["human spirit", "choice", "free will", "time"],
        "beaten_by": ["karma", "enlightenment", "time", "entropy"]
    },

    "earthquake": {
        "beats": ["rock", "stone", "building", "structure"],
        "beaten_by": ["water", "tsunami", "tectonic shift"]
    },
    "storm": {
        "beats": ["feather", "leaf", "twig", "paper"],
        "beaten_by": ["peace", "gravity", "earth", "moon"]
    },
    "vaccine": {
        "beats": ["virus", "disease", "bacteria", "plague"],
        "beaten_by": ["time", "entropy", "fate"]
    },
    "logic": {
        "beats": ["fate", "karma", "superstition"],
        "beaten_by": ["paper", "human spirit", "enlightenment", "entropy"]
    },
    "gravity": {
        "beats": ["feather", "water", "storm", "rain"],
        "beaten_by": ["black hole", "supermassive black hole", "antimatter"]
    },
    "robots": {
        "beats": ["human labor", "time", "efficiency"],
        "beaten_by": ["water", "emp", "logic", "virus"]
    },
    "stone": {
        "beats": ["feather", "leaf", "twig", "paper"],
        "beaten_by": ["water", "earthquake", "tectonic shift"]
    },
    "echo": {
        "beats": ["sound", "silence"],
        "beaten_by": ["vacuum", "black hole", "supermassive black hole"]
    },
    "thunder": {
        "beats": ["peace", "silence", "calm", "feather"],
        "beaten_by": ["lightning rod", "ear plugs", "storm"]
    },
    "karma": {
        "beats": ["bad deeds", "human spirit", "choice"],
        "beaten_by": ["enlightenment", "fate", "rebirth", "entropy"]
    },
    "wind": {
        "beats": ["feather", "leaf", "paper", "sound"],
        "beaten_by": ["mountain", "gravity", "earth", "moon"]
    },
    "ice": {
        "beats": ["water", "flame", "fire"],
        "beaten_by": ["heat", "flame", "sun", "star", "supernova"]
    },
    "sandstorm": {
        "beats": ["feather", "leaf", "paper", "water"],
        "beaten_by": ["stone", "rock", "mountain", "water"]
    },
    "laser": {
        "beats": ["shield", "rope", "diamond", "metal"],
        "beaten_by": ["mirror", "vacuum", "light"]
    },
    "magma": {
        "beats": ["rock", "ice", "stone", "earth"],
        "beaten_by": ["water", "tsunami", "ocean", "ice"]
    },
    "peace": {
        "beats": ["war", "violence", "chaos", "storm"],
        "beaten_by": ["human nature", "fate", "karma"]
    },
    "explosion": {
        "beats": ["rock", "stone", "shield", "building"],
        "beaten_by": ["water", "vacuum", "reinforced structure"]
    },
    "war": {
        "beats": ["peace", "humanity", "civilization"],
        "beaten_by": ["peace", "enlightenment", "human spirit"]
    },
    "enlightenment": {
        "beats": ["karma", "fate", "war", "ignorance"],
        "beaten_by": ["entropy", "time", "rebirth"]
    },

    "nuclear bomb": {
        "beats": ["city", "building", "human", "shield", "army"],
        "beaten_by": ["water", "nuclear shelter", "space", "earth's core"]
    },
    "volcano": {
        "beats": ["city", "forest", "earth", "human"],
        "beaten_by": ["water", "tsunami", "ocean", "tectonic shift"]
    },
    "whale": {
        "beats": ["water", "fish", "small creatures"],
        "beaten_by": ["tsunami", "land", "gravity", "plague"]
    },
    "earth": {
        "beats": ["human", "whale", "tree", "water"],
        "beaten_by": ["earth's core", "tectonic shift", "apocalyptic meteor"]
    },
    "moon": {
        "beats": ["tide", "night", "darkness"],
        "beaten_by": ["earth", "star", "sun", "gravity"]
    },
    "star": {
        "beats": ["darkness", "cold", "moon", "planet"],
        "beaten_by": ["supernova", "black hole", "supermassive black hole"]
    },
    "tsunami": {
        "beats": ["city", "human", "earth", "whale"],
        "beaten_by": ["gravity", "moon", "earth's core"]
    },
    "supernova": {
        "beats": ["star", "planet", "moon", "light"],
        "beaten_by": ["black hole", "supermassive black hole", "gamma-ray burst"]
    },
    "antimatter": {
        "beats": ["matter", "gravity", "reality"],
        "beaten_by": ["matter", "reality", "void", "entropy"]
    },
    "plague": {
        "beats": ["human", "animal", "civilization"],
        "beaten_by": ["cure", "vaccine", "enlightenment", "rebirth"]
    },
    "rebirth": {
        "beats": ["death", "plague", "ending", "karma"],
        "beaten_by": ["entropy", "gamma-ray burst", "supermassive black hole"]
    },
    "tectonic shift": {
        "beats": ["earth", "mountain", "city", "earthquake"],
        "beaten_by": ["earth's core", "gamma-ray burst", "entropy"]
    },
    "gamma-ray burst": {
        "beats": ["earth", "star", "planet", "civilization"],
        "beaten_by": ["supermassive black hole", "neutron star", "entropy"]
    },
    "human spirit": {
        "beats": ["war", "disease", "plague", "challenge"],
        "beaten_by": ["entropy", "time", "gamma-ray burst", "apocalyptic meteor"]
    },
    "apocalyptic meteor": {
        "beats": ["earth", "civilization", "dinosaur", "peace"],
        "beaten_by": ["supermassive black hole", "neutron star", "entropy"]
    },
    "earth's core": {
        "beats": ["earth", "tectonic shift", "earthquake", "volcano"],
        "beaten_by": ["supermassive black hole", "neutron star", "entropy"]
    },
    "neutron star": {
        "beats": ["planet", "star", "gamma-ray burst", "light"],
        "beaten_by": ["supermassive black hole", "entropy"]
    },
    "supermassive black hole": {
        "beats": ["star", "planet", "neutron star", "light", "gravity"],
        "beaten_by": ["entropy"]
    },
    "entropy": {
        "beats": ["everything", "time", "universe", "supermassive black hole"],
        "beaten_by": []  
    }
}

CONCEPT_CATEGORIES = {
    "elemental": ["water", "flame", "fire", "ice", "wind", "stone", "rock", "earth", "magma"],
    "celestial": ["star", "moon", "sun", "supernova", "black hole", "neutron star", "supermassive black hole", "gamma-ray burst"],
    "natural_phenomena": ["earthquake", "storm", "tsunami", "volcano", "sandstorm", "tectonic shift"],
    "biological": ["virus", "bacteria", "disease", "plague", "cure", "vaccine"],
    "weapons": ["sword", "shield", "gun", "nuclear bomb", "laser"],
    "abstract": ["time", "fate", "karma", "peace", "war", "logic", "enlightenment", "human spirit", "entropy", "rebirth"],
    "materials": ["feather", "coal", "pebble", "leaf", "paper", "twig", "rope"]
}


game_state = {
    "total_cost": 0,
    "remaining_budget": 0,
    "round": 0,
    "opponent_history": [],
    "our_plays": [],
    "outcomes": [],
    "observed_beats": defaultdict(list),  
    "observed_failures": defaultdict(list) 
}

COST_TIERS = {
    "low_cost": [wid for wid, data in player_words.items() if data["cost"] <= 5],
    "mid_cost": [wid for wid, data in player_words.items() if 5 < data["cost"] <= 15],
    "high_cost": [wid for wid, data in player_words.items() if 15 < data["cost"] <= 25],
    "ultra_cost": [wid for wid, data in player_words.items() if data["cost"] > 25]
}

def determine_direct_counter(system_word):
    """Find words that directly counter the system word based on semantic rules."""
    system_word_lower = system_word.lower()
    

    potential_counters = []
    
    if system_word_lower in SEMANTIC_RELATIONSHIPS:
        beaten_by = SEMANTIC_RELATIONSHIPS[system_word_lower].get("beaten_by", [])
        for counter in beaten_by:
            if counter in word_text_to_id:
                word_id = word_text_to_id[counter]
                cost = player_words[word_id]["cost"]
                
                potential_counters.append((word_id, 0.9, cost))
    
    # Check for words that beat similar concepts
    for concept, words in CONCEPT_CATEGORIES.items():
        if system_word_lower in words:
            # Look for words that beat other words in this category
            for word in words:
                if word != system_word_lower and word in SEMANTIC_RELATIONSHIPS:
                    beaten_by = SEMANTIC_RELATIONSHIPS[word].get("beaten_by", [])
                    for counter in beaten_by:
                        if counter in word_text_to_id:
                            word_id = word_text_to_id[counter]
                            cost = player_words[word_id]["cost"]
                            # Lower confidence for category-based relationships
                            potential_counters.append((word_id, 0.7, cost))
    
    return potential_counters

def check_observed_counters(system_word):
    """Check previously observed successful counterplays."""
    system_word_lower = system_word.lower()
    counters = []
    
    # Look for words we've successfully used to beat similar words
    for observed_word, winners in game_state["observed_beats"].items():
        if observed_word.lower() == system_word_lower:
            # Direct match - high confidence
            for winner_id in winners:
                cost = player_words[winner_id]["cost"]
                counters.append((winner_id, 0.95, cost))
        elif fuzzy_match_concepts(observed_word, system_word):
            # Similar concept - medium confidence
            for winner_id in winners:
                cost = player_words[winner_id]["cost"]
                counters.append((winner_id, 0.8, cost))
    
    # Also check words to avoid based on past failures
    failures = game_state["observed_failures"].get(system_word_lower, [])
    
    return counters, failures

def fuzzy_match_concepts(word1, word2):
    """Check if two words belong to similar conceptual categories."""
    word1_lower = word1.lower()
    word2_lower = word2.lower()
    
    # Check if they're in the same category
    for category, words in CONCEPT_CATEGORIES.items():
        if word1_lower in words and word2_lower in words:
            return True
    
    # Check for substring matches
    if word1_lower in word2_lower or word2_lower in word1_lower:
        return True
    
    return False

def infer_abstract_relationship(system_word):
    """Infer relationships for abstract concepts not explicitly defined."""
    system_word_lower = system_word.lower()
    
    # Abstract concepts that often have special relationships
    abstract_counters = {
        # Natural opposites
        "darkness": ["light", "star", "sun"],
        "light": ["shadow", "darkness", "black hole"],
        "heat": ["ice", "water", "cold"],
        "cold": ["heat", "flame", "fire"],
        "chaos": ["order", "peace", "logic"],
        "order": ["chaos", "entropy", "randomness"],
        
        # Philosophical concepts
        "reality": ["dream", "illusion", "imagination"],
        "dream": ["reality", "awakening", "logic"],
        "evil": ["good", "light", "human spirit"],
        "good": ["evil", "temptation", "corruption"],
        
        # Emotional states
        "fear": ["courage", "hope", "enlightenment"],
        "courage": ["fear", "terror", "intimidation"],
        "hate": ["love", "peace", "enlightenment"],
        "love": ["hate", "indifference", "logic"],
        
        # Cosmic concepts
        "void": ["matter", "energy", "creation"],
        "matter": ["antimatter", "void", "black hole"],
        "energy": ["void", "black hole", "entropy"],
        "creation": ["destruction", "entropy", "void"]
    }
    
    counters = []
    
    # Check if the system word might have abstract relationships
    for concept, countering_concepts in abstract_counters.items():
        if concept in system_word_lower or fuzzy_match_concepts(concept, system_word):
            for counter_concept in countering_concepts:
                # Find words related to the counter concept
                for word_id, data in player_words.items():
                    word_text = data["text"].lower()
                    if counter_concept in word_text or fuzzy_match_concepts(counter_concept, word_text):
                        cost = data["cost"]
                        counters.append((word_id, 0.6, cost))  # Lower confidence for inferred relationships
    
    return counters

def select_word_strategically(counters, failures, remaining_rounds):
    """Select the most strategic word considering cost, effectiveness and game state."""
    if not counters:
        return None
    
    # Remove words we've observed failing against this type of word
    filtered_counters = [(wid, conf, cost) for wid, conf, cost in counters 
                       if wid not in failures]
    
    if not filtered_counters:
        filtered_counters = counters  # Use original if all have failed before
    
    # Calculate budget per remaining round
    remaining_budget = game_state["remaining_budget"] - game_state["total_cost"]
    avg_budget_per_round = remaining_budget / max(remaining_rounds, 1)
    
    # Calculate cost-effectiveness scores (effectiveness vs cost)
    scored_counters = []
    for word_id, confidence, cost in filtered_counters:
        # Consider both confidence and affordability
        # Higher confidence and lower cost = better
        score = confidence * 100 - (cost / avg_budget_per_round * 10)
        scored_counters.append((word_id, score, cost))
    
    # Sort by score descending
    scored_counters.sort(key=lambda x: x[1], reverse=True)
    
    # Adjust strategy based on game state
    current_round = game_state["round"]
    
    if current_round == 1:
        # First round strategy - prefer reliable low-mid cost options
        affordable = [c for c in scored_counters if c[2] <= avg_budget_per_round * 1.2]
        if affordable:
            return affordable[0][0]
    elif current_round >= NUM_ROUNDS - 1:
        # Final rounds - can spend more if needed
        affordable = [c for c in scored_counters if c[2] <= remaining_budget]
        if affordable:
            return affordable[0][0]
    else:
        # Middle rounds - balance effectiveness and cost
        affordable = [c for c in scored_counters if c[2] <= avg_budget_per_round * 1.5]
        if affordable:
            # Choose from top options with some randomization
            top_options = affordable[:min(3, len(affordable))]
            return random.choice(top_options)[0]
    
    # If no affordable option found, pick the best we can afford
    for option in scored_counters:
        if option[2] <= remaining_budget:
            return option[0]
    
    # Last resort - pick cheapest
    cheapest = min(player_words.items(), key=lambda x: x[1]["cost"])
    return cheapest[0]

def get_cost_tier_recommendations(remaining_budget, remaining_rounds):
    """Get recommendations based on cost tiers and budget."""
    recommendations = []
    
    # Calculate how much we can spend on average per round
    avg_budget = remaining_budget / max(remaining_rounds, 1)
    
    # Select appropriate tiers based on budget
    if avg_budget <= 5:
        # Very tight budget - stick to low cost
        tier = "low_cost"
        options = COST_TIERS["low_cost"]
    elif avg_budget <= 12:
        # Moderate budget - low to mid cost
        tier = "mid_cost"
        options = COST_TIERS["low_cost"] + COST_TIERS["mid_cost"][:5]
    elif avg_budget <= 20:
        # Good budget - mid cost with occasional high
        tier = "mid_cost"
        options = COST_TIERS["mid_cost"] + COST_TIERS["high_cost"][:2]
    else:
        # Excellent budget - mid to high cost
        tier = "high_cost"
        options = COST_TIERS["mid_cost"] + COST_TIERS["high_cost"]
    
    # Filter to make sure all are affordable
    affordable = [wid for wid in options 
                 if player_words[wid]["cost"] <= remaining_budget]
    
    if affordable:
        return affordable
    
    # If nothing is affordable, return the cheapest option
    return [min(player_words.items(), key=lambda x: x[1]["cost"])[0]]

def what_beats(sys_word, round_id):
    """Advanced strategy to select the best word to beat the system word."""
    # Update game state
    game_state["round"] = round_id
    game_state["opponent_history"].append(sys_word)
    remaining_rounds = NUM_ROUNDS - round_id + 1
    
    # Get potential counters from different sources
    direct_counters = determine_direct_counter(sys_word)
    observed_counters, observed_failures = check_observed_counters(sys_word)
    abstract_counters = infer_abstract_relationship(sys_word)
    
    # Combine all potential counters
    all_counters = direct_counters + observed_counters + abstract_counters
    
    # If we have counters, select strategically
    if all_counters:
        best_word_id = select_word_strategically(all_counters, observed_failures, remaining_rounds)
        if best_word_id:
            return best_word_id
    
    # Fallback strategy based on cost tiers
    remaining_budget = game_state["remaining_budget"] - game_state["total_cost"]
    recommendations = get_cost_tier_recommendations(remaining_budget, remaining_rounds)
    
    # Select randomly from recommendations for unpredictability
    if recommendations:
        return random.choice(recommendations)
    
    # Absolute last resort - select a random affordable word
    affordable = [wid for wid, data in player_words.items() 
                if data["cost"] <= remaining_budget]
    
    if affordable:
        return random.choice(affordable)
    
    # If nothing else works, use the cheapest word
    return min(player_words.items(), key=lambda x: x[1]["cost"])[0]

def update_knowledge_base(sys_word, our_word_id, outcome):
    """Update our knowledge base based on the outcome."""
    sys_word_lower = sys_word.lower()
    
    if outcome == "success":
        # Remember this word beats the system word
        game_state["observed_beats"][sys_word_lower].append(our_word_id)
    elif outcome == "fail":
        # Remember this word fails against the system word
        game_state["observed_failures"][sys_word_lower].append(our_word_id)
    
    # Track our play history
    game_state["our_plays"].append(our_word_id)
    game_state["outcomes"].append(outcome)

def get_current_round():
    try:
        response = requests.get(get_url, timeout=5)
        if response.status_code == 200:
            return response.json()['round']
    except requests.exceptions.RequestException:
        pass
    return -1

def play_game(player_id):
    # Calculate total available budget
    game_state["remaining_budget"] = sum(word["cost"] for word in player_words.values())
    game_state["total_cost"] = 0
    game_history = []
    
    print(f"\n===== NEW GAME STARTING (Player ID: {player_id}) =====")
    print(f"Total budget available: {game_state['remaining_budget']}")
    
    
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

        # Choose counter word with optimized strategy
        chosen_word_id = what_beats(sys_word, round_id)
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
            outcome = result.get('outcome', 'unknown')
            print(f"Result: {outcome}")
            
            # Update cost and history
            game_state["total_cost"] += chosen_word['cost']
            game_history.append({
                "round": round_id,
                "opponent_word": sys_word,
                "our_word": chosen_word['text'],
                "cost": chosen_word['cost'],
                "outcome": outcome
            })
            
            if outcome == "fail":
                game_state["total_cost"] += PENALTY_COST
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

    print("\nGame History:")
    for move in game_history:
        print(f"Round {move['round']}: Opponent '{move['opponent_word']}' vs Our '{move['our_word']}' "
              f"(Cost: {move['cost']}, Result: {move['outcome']})")
    
    print(f"\nFinal Total Cost: ${game_state['total_cost']}")
    return game_state['total_cost']

if __name__ == "__main__":
    player_id = "player1"  # Replace with your player ID
    play_game(player_id)