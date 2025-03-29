import random
import json
from collections import defaultdict
from time import sleep

class AdaptiveAI:
    def __init__(self, word_data):
        self.word_data = word_data
        self.text_to_id = {v['text'].lower(): k for k, v in word_data.items()}
        
        # Load saved knowledge if exists
        self.load_knowledge()

        # Learning mechanisms
        self.learned_opponent_words = set()

        # Strategy parameters
        self.risk_factor = 0.4
        self.consecutive_losses = 0
        self.conservative_threshold = 3
        
        # Game state
        self.total_cost = 0
        self.round = 0

    def load_knowledge(self):
        """Load previously saved knowledge from a file."""
        try:
            with open('ai_knowledge.json', 'r') as file:
                data = json.load(file)
                self.word_effectiveness = defaultdict(int, data.get('word_effectiveness', {}))
                self.opponent_word_power = defaultdict(int, data.get('opponent_word_power', {}))
                self.category_strategy = defaultdict(list, data.get('category_strategy', {}))
                self.learned_opponent_words = set(data.get('learned_opponent_words', []))
        except FileNotFoundError:
            print("No previous knowledge found, starting fresh.")
            self.word_effectiveness = defaultdict(int)
            self.opponent_word_power = defaultdict(int)
            self.category_strategy = defaultdict(list)

    def save_knowledge(self):
        """Save the current knowledge to a file."""
        data = {
            'word_effectiveness': dict(self.word_effectiveness),
            'opponent_word_power': dict(self.opponent_word_power),
            'category_strategy': dict(self.category_strategy),
            'learned_opponent_words': list(self.learned_opponent_words),
        }
        with open('ai_knowledge.json', 'w') as file:
            json.dump(data, file)

    def update_knowledge(self, opponent_word, player_word_id, won):
        """Learn from each round's outcome"""
        self.round += 1
        player_word = self.word_data[player_word_id]['text'].lower()
        opponent_word = opponent_word.lower()
        self.learned_opponent_words.add(opponent_word)
        
        # Update effectiveness tracking
        change = 2 if won else -1
        self.word_effectiveness[player_word] += change
        
        # Update opponent word power estimation
        opponent_power_change = -3 if won else 2
        self.opponent_word_power[opponent_word] += opponent_power_change
        
        # Update category relationships
        opponent_category = self.categorize_word(opponent_word)
        player_category = self.categorize_word(player_word)
        if opponent_category and player_category:
            if won:
                self.category_strategy[opponent_category].append(player_category)
            else:
                if player_category in self.category_strategy[opponent_category]:
                    self.category_strategy[opponent_category].remove(player_category)
        
        # Adjust strategy based on performance
        if won:
            self.consecutive_losses = 0
            if self.risk_factor < 0.7:
                self.risk_factor += 0.05
        else:
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.conservative_threshold:
                self.risk_factor = max(0.1, self.risk_factor - 0.15)

    def categorize_word(self, word):
        """Categorize words for strategic matching"""
        word = word.lower()
        categories = {
            'natural': ['storm', 'earthquake', 'tornado', 'flood', 'lightning'],
            'physical': ['sword', 'hammer', 'gun', 'shield', 'laser'],
            'living': ['dragon', 'whale', 'virus', 'bacteria', 'human'],
            'abstract': ['time', 'fate', 'infinity', 'logic', 'entropy'],
            'cosmic': ['black hole', 'supernova', 'star', 'galaxy', 'singularity']
        }
        for category, words in categories.items():
            if any(w in word for w in words):
                return category
        return None

    def estimate_opponent_strength(self, word):
        """Estimate how strong an opponent word is"""
        word = word.lower()
        # Base estimation
        length_factor = len(word.split()) * 3 + len(word) * 0.7
        complexity = sum(1 for c in word if c.isupper()) * 2
        
        # Learned power adjustment
        observed_power = self.opponent_word_power.get(word, 0)
        
        # Category bonus
        category_bonus = 5 if self.categorize_word(word) in ['cosmic', 'abstract'] else 0
        
        return length_factor + complexity + observed_power + category_bonus

    def calculate_word_value(self, word_id):
        """Score each word based on effectiveness and cost"""
        word = self.word_data[word_id]
        text = word['text'].lower()
        cost = word['cost']
        
        # Base effectiveness
        base_power = min(cost * 1.3, 25)  # Cap base power
        
        # Learned effectiveness
        learned = self.word_effectiveness.get(text, 0)
        
        # Usage penalty (avoid overusing same word)
        usage = sum(1 for k in self.learned_opponent_words if text in self.word_effectiveness)
        
        # Value formula (higher is better)
        return (base_power + learned) / (cost * (1 + usage*0.1))

    def choose_word(self, opponent_word):
        """Select the best response using adaptive strategy"""
        opponent_word = opponent_word.lower()
        opponent_power = self.estimate_opponent_strength(opponent_word)
        
        # Get opponent category for strategic response
        opponent_category = self.categorize_word(opponent_word)
        
        # Score all available words
        scored_words = []
        for word_id, word in self.word_data.items():
            score = self.calculate_word_value(word_id)
            
            # Bonus for category advantage
            player_category = self.categorize_word(word['text'])
            if opponent_category and player_category:
                if player_category in self.category_strategy.get(opponent_category, []):
                    score *= 1.5
            
            scored_words.append((score, word['cost'], word_id, word['text']))
        
        # Sort by best value (score/cost ratio)
        scored_words.sort(key=lambda x: x[0]/x[1], reverse=True)
        
        # Risk-based selection
        if random.random() < self.risk_factor:
            # Risky play - try low-cost words that might counter
            cheap_options = [x for x in scored_words if x[1] <= 4]
            if cheap_options:
                chosen = random.choice(cheap_options[:3])
                return chosen[2]  # Return word_id
        
        # Default strategy - pick from top 3 value options
        top_options = [x[2] for x in scored_words[:3]]
        return random.choice(top_options) if top_options else random.choice(list(self.word_data.keys()))

    def record_result(self, opponent_word, player_word_id, won):
        """Update game state after each round"""
        cost = self.word_data[player_word_id]['cost']
        if won:
            self.total_cost += cost
        else:
            self.total_cost += cost + 30  # Include penalty
        self.update_knowledge(opponent_word, player_word_id, won)

class Opponent:
    def __init__(self):
        self.word_pool = [
            "Dragon", "Supernova", "Black Hole", "Pandemic", "Armageddon",
            "Lightning Storm", "Divine Wrath", "Quantum Entanglement",
            "Gamma Ray Burst", "Volcanic Eruption", "Tectonic Collapse",
            "Cosmic Horror", "Infinite Void", "Absolute Zero", "Hypernova"
        ]
        self.used_words = set()
    
    def choose_word(self):
        """Select a word, preferring unused ones"""
        available = [w for w in self.word_pool if w not in self.used_words]
        if not available:
            available = self.word_pool
            self.used_words = set()
        
        chosen = random.choice(available)
        self.used_words.add(chosen)
        return chosen

def determine_outcome(opponent_word, player_word):
    """Determine if player word beats opponent word"""
    opp = opponent_word.lower()
    ply = player_word.lower()
    
    # Specific hard-coded counters
    specific_counters = {
        'dragon': ['nuclear bomb', 'human spirit', 'laser'],
        'pandemic': ['vaccine', 'cure', 'human spirit'],
        'black hole': ['entropy', 'human spirit', 'neutron star'],
        'lightning': ['shield', 'earth', 'lightning rod'],
        'divine': ['human spirit', 'logic', 'enlightenment']
    }
    
    # Check if player word is a known counter
    for target, counters in specific_counters.items():
        if target in opp and any(c in ply for c in counters):
            return True
    
    # Category-based advantages
    category_matrix = {
        'natural': {'physical': 0.6, 'living': 0.4, 'abstract': 0.3},
        'physical': {'living': 0.7, 'natural': 0.5, 'abstract': 0.2},
        'living': {'abstract': 0.8, 'cosmic': 0.3, 'natural': 0.6},
        'abstract': {'cosmic': 0.7, 'natural': 0.9, 'physical': 0.5},
        'cosmic': {'abstract': 0.6, 'living': 0.3, 'natural': 0.2}
    }
    
    # Get categories
    def get_category(word):
        categories = {
            'natural': ['storm', 'earthquake', 'lightning', 'volcanic', 'tectonic'],
            'physical': ['sword', 'hammer', 'shield', 'laser', 'nuclear'],
            'living': ['dragon', 'human', 'whale', 'virus', 'bacteria'],
            'abstract': ['spirit', 'logic', 'entropy', 'infinity', 'divine'],
            'cosmic': ['black hole', 'supernova', 'quantum', 'cosmic', 'void']
        }
        for cat, terms in categories.items():
            if any(t in word for t in terms):
                return cat
        return None
    
    opp_cat = get_category(opp)
    ply_cat = get_category(ply)
    
    if opp_cat and ply_cat:
        win_prob = category_matrix.get(opp_cat, {}).get(ply_cat, 0.5)
        return random.random() < win_prob
    
    # Fallback: cost-based comparison
    player_cost = next(v['cost'] for k,v in WORD_DATA.items() if v['text'].lower() == ply)
    cost_map = {
        'weak': (1, 5), 'medium': (6, 15), 'strong': (16, 25), 'ultimate': (26, 45)
    }
    return random.random() > 0.4 + (player_cost - 20)/100

def play_game():
    # Initialize game components
    ai = AdaptiveAI(WORD_DATA)
    opponent = Opponent()
    
    print("Starting Word Battle: AI vs Hidden Opponent\n")
    print("AI will learn opponent's words through gameplay\n")
    
    for round_num in range(1, 6):
        print(f"\n=== Round {round_num} ===")
        
        # Opponent selects word
        opponent_word = opponent.choose_word()
        print(f"Opponent plays: {opponent_word}")
        
        # AI selects response
        chosen_id = ai.choose_word(opponent_word)
        chosen_word = WORD_DATA[chosen_id]
        print(f"AI chooses: {chosen_word['text']} (Cost: ${chosen_word['cost']})")
        
        # Determine outcome
        outcome = determine_outcome(opponent_word, chosen_word['text'])
        
        # Update AI knowledge
        ai.record_result(opponent_word, chosen_id, outcome)
        
        print(f"Result: {'WIN' if outcome else 'LOSE'} | Total Cost: ${ai.total_cost}")
        print(f"AI Risk Factor: {ai.risk_factor:.2f}")
        
        # Display learning progress
        if round_num % 2 == 0:
            print("\nAI's Discovered Knowledge:")
            print(f"Learned Opponent Words: {len(ai.learned_opponent_words)}")
            top_words = sorted(WORD_DATA.keys(),
                             key=lambda x: ai.word_effectiveness.get(WORD_DATA[x]['text'].lower(), 0),
                             reverse=True)[:3]
            for word_id in top_words:
                word = WORD_DATA[word_id]
                eff = ai.word_effectiveness.get(word['text'].lower(), 0)
                print(f"{word['text']}: Effectiveness {eff}")
        
        sleep(1)
    
    print("\n=== Game Over ===")
    print(f"Final Total Cost: ${ai.total_cost}")
    if ai.total_cost < 100:
        print("AI Performance: Excellent!")
    elif ai.total_cost < 150:
        print("AI Performance: Good")
    else:
        print("AI Performance: Needs Improvement")

# Word data (same as previously provided)
WORD_DATA = {
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

if __name__ == "__main__":
    play_game()
