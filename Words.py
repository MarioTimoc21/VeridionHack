import random
from collections import defaultdict
import requests
from time import sleep

class WordsOfPowerAI:
    def __init__(self):
        # Initialize word data
        self.word_data = {
            i+1: {"text": word, "cost": cost} 
            for i, (word, cost) in enumerate([
                ("Feather", 1), ("Coal", 1), ("Pebble", 1), ("Leaf", 2), ("Paper", 2),
                ("Rock", 2), ("Water", 3), ("Twig", 3), ("Sword", 4), ("Shield", 4),
                ("Gun", 5), ("Flame", 5), ("Rope", 5), ("Disease", 6), ("Cure", 6),
                ("Bacteria", 6), ("Shadow", 7), ("Light", 7), ("Virus", 7), ("Sound", 8),
                ("Time", 8), ("Fate", 8), ("Earthquake", 9), ("Storm", 9), ("Vaccine", 9),
                ("Logic", 10), ("Gravity", 10), ("Robots", 10), ("Stone", 11), ("Echo", 11),
                ("Thunder", 12), ("Karma", 12), ("Wind", 13), ("Ice", 13), ("Sandstorm", 13),
                ("Laser", 14), ("Magma", 14), ("Peace", 14), ("Explosion", 15), ("War", 15),
                ("Enlightenment", 15), ("Nuclear Bomb", 16), ("Volcano", 16), ("Whale", 17),
                ("Earth", 17), ("Moon", 17), ("Star", 18), ("Tsunami", 18), ("Supernova", 19),
                ("Antimatter", 19), ("Plague", 20), ("Rebirth", 20), ("Tectonic Shift", 21),
                ("Gamma-Ray Burst", 22), ("Human Spirit", 23), ("Apocalyptic Meteor", 24),
                ("Earth's Core", 25), ("Neutron Star", 26), ("Supermassive Black Hole", 35),
                ("Entropy", 45)
            ])
        }
        
        # Create text to ID mapping
        self.text_to_id = {v['text'].lower(): k for k, v in self.word_data.items()}
        
        # Initialize learning mechanisms
        self.word_effectiveness = defaultdict(int)
        self.opponent_word_counters = defaultdict(list)
        self.consecutive_losses = 0
        self.risk_factor = 0.4  # Moderate risk initially
        
        # Game state
        self.total_cost = 0
        self.round = 0

    def choose_word(self, opponent_word):
        """Select the best response to opponent's word"""
        opponent_word = opponent_word.lower()
        
        # First check for known effective counters
        known_counters = self.opponent_word_counters.get(opponent_word, [])
        if known_counters:
            # Filter by affordable cost based on risk factor
            max_cost = 15 + (20 * self.risk_factor)
            valid_counters = [
                (self.text_to_id[word], word) 
                for word in known_counters 
                if self.word_data[self.text_to_id[word]]['cost'] <= max_cost
            ]
            if valid_counters:
                # Choose the cheapest known counter
                valid_counters.sort(key=lambda x: self.word_data[x[0]]['cost'])
                return valid_counters[0][0]

        # If no known counter, use strategic selection
        return self.strategic_selection(opponent_word)

    def strategic_selection(self, opponent_word):
        """Select word based on opponent word's estimated strength"""
        # Estimate opponent word strength
        strength = self.estimate_word_strength(opponent_word)
        
        # Determine target cost range based on strength and risk factor
        base_cost = min(max(5, strength * 0.8), 30)
        cost_min = max(1, base_cost * (1 - self.risk_factor))
        cost_max = min(45, base_cost * (1 + self.risk_factor))
        
        # Find candidate words in the cost range
        candidates = []
        for word_id, word in self.word_data.items():
            cost = word['cost']
            if cost_min <= cost <= cost_max:
                effectiveness = self.word_effectiveness.get(word['text'].lower(), 0)
                # Score favors effectiveness but penalizes high cost
                score = effectiveness - (cost * 0.05)
                candidates.append((score, word_id))
        
        # If no candidates in range, expand to all words
        if not candidates:
            candidates = [
                (self.word_effectiveness.get(w['text'].lower(), 0), wid) 
                for wid, w in self.word_data.items()
            ]
        
        # Sort candidates by score and pick from top 3
        candidates.sort(reverse=True, key=lambda x: x[0])
        top_candidates = candidates[:3]
        
        if not top_candidates:
            return random.choice(list(self.word_data.keys()))
        
        # Prefer positive scores if available
        positive = [c for c in top_candidates if c[0] > 0]
        if positive:
            return random.choice(positive)[1]
        return top_candidates[0][1]

    def estimate_word_strength(self, word):
        """Estimate how strong/dangerous an opponent word is"""
        word = word.lower()
        # Basic factors
        length_factor = len(word.split()) * 4 + len(word) * 0.5
        
        # Special terms that indicate power
        power_terms = {
            'black hole': 35, 'supernova': 30, 'meteor': 25,
            'dragon': 20, 'pandemic': 18, 'armageddon': 25,
            'quantum': 22, 'gamma': 20, 'volcanic': 18,
            'tectonic': 17, 'cosmic': 20, 'void': 15,
            'zero': 12, 'hypernova': 30, 'wrath': 15,
            'nuclear': 25, 'apocalyptic': 24, 'entropy': 30
        }
        
        # Check for power terms
        term_bonus = max(
            (value for term, value in power_terms.items() if term in word),
            default=0
        )
        
        return length_factor + term_bonus

    def update_knowledge(self, opponent_word, player_word_id, won):
        """Update AI knowledge based on round outcome"""
        self.round += 1
        player_word = self.word_data[player_word_id]['text'].lower()
        opponent_word = opponent_word.lower()
        
        # Update word effectiveness (more for wins, less for losses)
        change = 5 if won else -2
        self.word_effectiveness[player_word] += change
        
        # Record successful counters
        if won:
            self.opponent_word_counters[opponent_word].append(player_word)
        
        # Adjust risk factor based on performance
        if won:
            self.consecutive_losses = 0
            # Occasionally become more aggressive after wins
            if random.random() < 0.25:
                self.risk_factor = min(0.8, self.risk_factor + 0.1)
        else:
            self.consecutive_losses += 1
            # Become more conservative after consecutive losses
            if self.consecutive_losses >= 2:
                self.risk_factor = max(0.1, self.risk_factor - 0.15)

def play_game(player_id, host):
    """Main game loop"""
    ai = WordsOfPowerAI()
    post_url = f"{host}/submit-word"
    get_url = f"{host}/get-word"
    status_url = f"{host}/status"
    
    for round_num in range(1, 6):
        # Get system word
        response = requests.get(get_url)
        while response.json().get('round') != round_num:
            sleep(1)
            response = requests.get(get_url)
        
        sys_word = response.json()['word']
        
        # AI chooses word
        chosen_id = ai.choose_word(sys_word)
        chosen_word = ai.word_data[chosen_id]['text']
        
        # Submit choice
        data = {
            "player_id": player_id,
            "word_id": chosen_id,
            "round_id": round_num
        }
        response = requests.post(post_url, json=data)
        
        # Get result (assuming API returns outcome)
        # In a real implementation, we'd parse the response
        # For now, we'll simulate determination
        outcome = determine_outcome(sys_word, chosen_word, ai.word_data)
        
        # Update AI knowledge
        ai.update_knowledge(sys_word, chosen_id, outcome)
        
        # Calculate cost
        cost = ai.word_data[chosen_id]['cost']
        if not outcome:
            cost += 30  # Penalty
        
        ai.total_cost += cost
        
        # Print round summary (for debugging)
        print(f"Round {round_num}:")
        print(f"System word: {sys_word}")
        print(f"AI chose: {chosen_word} (${ai.word_data[chosen_id]['cost']})")
        print(f"Outcome: {'WIN' if outcome else 'LOSE'} | Total cost: ${ai.total_cost}")
        print(f"Risk factor: {ai.risk_factor:.2f}\n")
    
    print(f"Game over! Final cost: ${ai.total_cost}")

def determine_outcome(opponent_word, player_word, word_data):
    """Determine if player word beats system word (simplified version)"""
    # This would be replaced with actual game logic
    # For now, we'll use a simple probabilistic model
    
    player_word = player_word.lower()
    opponent_word = opponent_word.lower()
    
    # Specific hard-coded counters
    specific_counters = {
        'dragon': ['human spirit', 'nuclear bomb', 'laser', 'gun'],
        'pandemic': ['vaccine', 'cure', 'human spirit'],
        'black hole': ['entropy', 'human spirit', 'neutron star'],
        'lightning': ['shield', 'earth', 'stone'],
        'supernova': ['black hole', 'entropy', 'human spirit'],
        'volcanic': ['ice', 'water', 'earth'],
        'meteor': ['shield', 'earth', 'moon'],
        'gamma': ['shield', 'earth'],
        'wrath': ['peace', 'human spirit', 'enlightenment']
    }
    
    # Check if player word is a known counter
    for target, counters in specific_counters.items():
        if target in opponent_word and any(c in player_word for c in counters):
            return True
    
    # Fallback: cost-based comparison with some randomness
    player_cost = next(
        v['cost'] for k, v in word_data.items() 
        if v['text'].lower() == player_word
    )
    
    # Estimate opponent word cost (not perfect, but works for simulation)
    opp_strength = len(opponent_word) + sum(1 for c in opponent_word if c.isupper()) * 2
    threshold = 0.5 + (player_cost - opp_strength/3)/100
    
    return random.random() < threshold

# Example usage
if __name__ == "__main__":
    HOST = "http://172.18.4.158:8000"  # Replace with actual API endpoint
    PLAYER_ID = "your_player_id"     # Replace with your player ID
    
    play_game(PLAYER_ID, HOST)