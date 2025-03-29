import random
from collections import defaultdict
import requests
from time import sleep
from requests.exceptions import RequestException

class WordsOfPowerAI:
    def __init__(self):
        # Initialize with the provided word data
        self.word_data = {
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
        
        # Create text to ID mapping
        self.text_to_id = {v['text'].lower(): k for k, v in self.word_data.items()}
        
        # Learning mechanisms
        self.word_effectiveness = defaultdict(int)
        self.opponent_word_counters = defaultdict(list)
        self.cost_effectiveness = defaultdict(list)
        
        # Game state
        self.total_cost = 0
        self.round = 0
        self.consecutive_losses = 0
        self.risk_factor = 0.4  # Initial moderate risk
        
        # Predefined counters for common opponent words
        self.hardcoded_counters = {
            'dragon': ['human spirit', 'nuclear bomb', 'laser', 'gun'],
            'pandemic': ['vaccine', 'cure', 'human spirit'],
            'black hole': ['entropy', 'human spirit', 'neutron star'],
            'lightning': ['shield', 'earth', 'stone'],
            'supernova': ['black hole', 'entropy', 'human spirit'],
            'volcanic': ['ice', 'water', 'earth'],
            'meteor': ['shield', 'earth', 'moon'],
            'gamma': ['shield', 'earth'],
            'wrath': ['peace', 'human spirit', 'enlightenment'],
            'flood': ['drought', 'sandstorm', 'earth'],
            'hammer': ['shield', 'rock', 'stone'],
            'tornado': ['earth', 'stone', 'mountain'],
            'fire': ['water', 'ice', 'sandstorm'],
            'chaos': ['logic', 'order', 'enlightenment'],
            'death': ['rebirth', 'life', 'human spirit']
        }

    def choose_word(self, opponent_word):
        """Select the best response to opponent's word"""
        opponent_word_lower = opponent_word.lower()
        
        # First check hardcoded counters
        for pattern, counters in self.hardcoded_counters.items():
            if pattern in opponent_word_lower:
                # Find available counters within cost limit
                max_cost = 15 + (20 * self.risk_factor)
                valid_counters = []
                for counter in counters:
                    if counter in self.text_to_id:
                        word_id = self.text_to_id[counter]
                        cost = self.word_data[word_id]['cost']
                        if cost <= max_cost:
                            valid_counters.append((cost, word_id))
                
                if valid_counters:
                    # Choose the cheapest valid counter
                    valid_counters.sort()
                    return valid_counters[0][1]
        
        # Then check learned counters
        known_counters = self.opponent_word_counters.get(opponent_word_lower, [])
        if known_counters:
            max_cost = 10 + (15 * self.risk_factor)
            valid_counters = []
            for word in known_counters:
                if word in self.text_to_id:
                    word_id = self.text_to_id[word]
                    cost = self.word_data[word_id]['cost']
                    if cost <= max_cost:
                        valid_counters.append((cost, word_id))
            
            if valid_counters:
                valid_counters.sort()
                return valid_counters[0][1]
        
        # If no known counters, use strategic selection
        return self.strategic_selection(opponent_word_lower)

    def strategic_selection(self, opponent_word):
        """Select word based on opponent word's estimated strength"""
        strength = self.estimate_word_strength(opponent_word)
        
        # Determine target cost range based on strength and risk factor
        base_cost = min(max(5, strength * 0.7), 30)
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
        
        # If no candidates in range, expand search
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
        # Basic factors
        length_factor = len(word.split()) * 4 + len(word) * 0.5
        
        # Special terms that indicate power
        power_terms = {
            'black hole': 35, 'supernova': 30, 'meteor': 25,
            'dragon': 20, 'pandemic': 18, 'armageddon': 25,
            'quantum': 22, 'gamma': 20, 'volcanic': 18,
            'tectonic': 17, 'cosmic': 20, 'void': 15,
            'zero': 12, 'hypernova': 30, 'wrath': 15,
            'nuclear': 25, 'apocalyptic': 24, 'entropy': 30,
            'supermassive': 30, 'neutron': 25, 'plague': 20,
            'tsunami': 18, 'earthquake': 16, 'storm': 15
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
        
        # Update word effectiveness
        change = 5 if won else -2
        self.word_effectiveness[player_word] += change
        
        # Record successful counters
        if won:
            if player_word not in self.opponent_word_counters[opponent_word]:
                self.opponent_word_counters[opponent_word].append(player_word)
        
        # Track cost effectiveness
        cost = self.word_data[player_word_id]['cost']
        self.cost_effectiveness[cost].append(won)
        
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

def play_game(player_id, host, max_retries=5, retry_delay=2):
    """Main game loop with improved error handling"""
    ai = WordsOfPowerAI()
    post_url = f"http://{host}/submit-word"
    get_url = f"http://{host}/get-word"
    status_url = f"http://{host}/status"
    
    # Configure session with timeout
    session = requests.Session()
    session.timeout = 10  # 10 second timeout
    
    for round_num in range(1, 6):
        print(f"\n=== Round {round_num} ===")
        
        # Get system word with retry logic
        sys_word = None
        for attempt in range(max_retries):
            try:
                response = session.get(get_url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('round') == round_num:
                        sys_word = data['word']
                        break
                    else:
                        print(f"Waiting for round {round_num} data...")
                else:
                    print(f"Server returned status {response.status_code}")
            except RequestException as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                    continue
        
        if not sys_word:
            print("Failed to get system word after multiple attempts. Using fallback.")
            sys_word = random.choice(["Dragon", "Pandemic", "Black Hole", "Lightning", "Supernova"])
        
        print(f"System word: {sys_word}")
        
        # AI chooses word
        chosen_id = ai.choose_word(sys_word)
        chosen_word = ai.word_data[chosen_id]['text']
        chosen_cost = ai.word_data[chosen_id]['cost']
        print(f"AI choosing: {chosen_word} (ID: {chosen_id}, Cost: ${chosen_cost})")
        
        # Submit choice with retry logic
        for attempt in range(max_retries):
            try:
                response = session.post(
                    post_url,
                    json={
                        "player_id": player_id,
                        "word_id": chosen_id,
                        "round_id": round_num
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    print("Submission successful")
                    break
                else:
                    print(f"Submission failed with status {response.status_code}")
            except RequestException as e:
                print(f"Submission attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                    continue
        
        # Get result (simulate if API not responding)
        outcome = None
        for attempt in range(max_retries):
            try:
                status = session.get(status_url, timeout=10)
                if status.status_code == 200:
                    status_data = status.json()
                    # Parse outcome from status response if available
                    # This depends on the actual API response format
                    outcome = True  # Temporary placeholder
                    break
            except RequestException as e:
                print(f"Status check attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                    continue
        
        if outcome is None:
            print("Could not get result from server. Simulating outcome.")
            outcome = determine_outcome(sys_word, chosen_word, ai.word_data)
        
        # Update AI knowledge
        ai.update_knowledge(sys_word, chosen_id, outcome)
        
        # Calculate cost
        cost = chosen_cost
        if not outcome:
            cost += 30  # Penalty
            print("Result: LOSE (Penalty applied)")
        else:
            print("Result: WIN")
        
        ai.total_cost += cost
        print(f"Total cost: ${ai.total_cost}")
        print(f"Current risk factor: {ai.risk_factor:.2f}")
    
    print(f"\n=== Game Over ===")
    print(f"Final total cost: ${ai.total_cost}")

def determine_outcome(opponent_word, player_word, word_data):
    """Determine if player word beats system word (simulation)"""
    # Convert to lowercase for case-insensitive comparison
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
        'wrath': ['peace', 'human spirit', 'enlightenment'],
        'flood': ['drought', 'sandstorm', 'earth'],
        'hammer': ['shield', 'rock', 'stone'],
        'tornado': ['earth', 'stone', 'mountain'],
        'fire': ['water', 'ice', 'sandstorm'],
        'chaos': ['logic', 'order', 'enlightenment'],
        'death': ['rebirth', 'life', 'human spirit']
    }
    
    # Check if player word is a known counter
    for pattern, counters in specific_counters.items():
        if pattern in opponent_word and any(c in player_word for c in counters):
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

if __name__ == "__main__":
    HOST = "http://172.18.4.158:8000"  # Your server address
    PLAYER_ID = "your_player_id"  # Your player ID
    
    try:
        play_game(PLAYER_ID, HOST)
    except Exception as e:
        print(f"Fatal error: {str(e)}")