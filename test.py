import random
from collections import defaultdict
from time import sleep

class AdaptiveAI:
    def __init__(self, player_words):
        # Player word database (initially unknown power)
        self.player_words = {w['text'].lower(): w for w in player_words}
        
        # Knowledge tracking
        self.word_effectiveness = defaultdict(int)  # +1 for wins, -1 for losses
        self.word_usage = defaultdict(int)
        self.system_word_strength = defaultdict(int)
        self.matchup_history = defaultdict(list)  # (system_word, player_word): [results]
        
        # Strategy parameters
        self.risk_factor = 0.2  # Initial risk appetite (0-1)
        self.conservative_threshold = 3  # Become conservative after this many losses
        self.learning_rate = 0.4
        
        # Game state
        self.total_score = 0
        self.consecutive_losses = 0
        
    def update_knowledge(self, system_word, player_word, won):
        """Learn from each round's outcome"""
        sys_word = system_word.lower()
        ply_word = player_word.lower()
        
        # Update matchup history
        self.matchup_history[(sys_word, ply_word)].append(won)
        
        # Update word effectiveness
        if won:
            self.word_effectiveness[ply_word] += 1
            self.system_word_strength[sys_word] -= 1
            self.consecutive_losses = 0
        else:
            self.word_effectiveness[ply_word] -= 1
            self.system_word_strength[sys_word] += 1
            self.consecutive_losses += 1
        
        # Update usage stats
        self.word_usage[ply_word] += 1
        
        # Adjust strategy based on performance
        self._adjust_strategy()
    
    def _adjust_strategy(self):
        """Dynamically modify strategy parameters"""
        # Become more conservative after consecutive losses
        if self.consecutive_losses >= self.conservative_threshold:
            self.risk_factor = max(0.1, self.risk_factor - 0.15)
        
        # Calculate win rate
        total_rounds = sum(self.word_usage.values())
        if total_rounds > 0:
            win_rate = sum(1 for k,v in self.word_effectiveness.items() if v > 0) / total_rounds
            # Adjust risk based on overall performance
            self.risk_factor = min(0.7, max(0.2, win_rate))
    
    def estimate_system_strength(self, word):
        """Estimate how strong a system word is"""
        word = word.lower()
        # Base strength on word characteristics
        length_factor = len(word) * 2
        complexity = sum(1 for c in word if c.isupper()) + word.count(' ')
        # Combine with observed strength
        observed = self.system_word_strength.get(word, 0)
        return length_factor + complexity * 3 + observed
    
    def get_word_score(self, player_word):
        """Calculate effectiveness score for a player word"""
        word = player_word['text'].lower()
        cost = player_word['cost']
        
        # Base power estimation
        base_power = len(word) * 2 + (10 if any(c.isupper() for c in word) else 0)
        
        # Incorporate learned effectiveness
        effectiveness = self.word_effectiveness.get(word, 0)
        usage = max(1, self.word_usage.get(word, 1))  # Avoid division by zero
        
        # Calculate score (balance power and cost)
        return (base_power + effectiveness/usage) / (cost ** 0.8)
    
    def choose_word(self, system_word):
        """Select the best word based on current knowledge"""
        system_power = self.estimate_system_strength(system_word)
        candidates = []
        
        # Evaluate all available words
        for word_data in self.player_words.values():
            score = self.get_word_score(word_data)
            candidates.append((score, word_data['cost'], word_data))
        
        # Sort by best value (score/cost ratio)
        candidates.sort(reverse=True, key=lambda x: x[0]/x[1])
        
        # Risk-based selection
        if random.random() < self.risk_factor:
            # Risky strategy - try cheaper words
            cheap_options = [w for s,c,w in candidates if c < 8]
            if cheap_options:
                chosen = random.choice(cheap_options[:3])
                return chosen['text']
        
        # Default strategy - pick from top 3 options
        top_options = [w for s,c,w in candidates[:3]]
        if top_options:
            return random.choice(top_options)['text']
        
        # Fallback - random selection
        return random.choice(list(self.player_words.values()))['text']

def simulate_round(ai, system_word):
    """Simulate a complete game round"""
    print(f"\nSystem plays: {system_word}")
    
    # AI selects word
    chosen_text = ai.choose_word(system_word)
    chosen_word = ai.player_words[chosen_text.lower()]
    cost = chosen_word['cost']
    print(f"AI chooses: {chosen_text} (Cost: ${cost})")
    
    # Simulate outcome (in real game this would come from game logic)
    # Here we use a weighted random based on estimated strength
    system_power = ai.estimate_system_strength(system_word)
    player_power = ai.get_word_score(chosen_word) * 10  # Scale to similar range
    
    win_prob = player_power / (player_power + system_power)
    won = random.random() < win_prob
    
    # Update score and knowledge
    if won:
        ai.total_score += cost
        print(f"Success! (Total: ${ai.total_score})")
    else:
        ai.total_score += cost + 30
        print(f"Failed! (Total: ${ai.total_score} = {cost} + $30 penalty)")
    
    ai.update_knowledge(system_word, chosen_text, won)
    
    # Display learned knowledge
    print("\nAI Knowledge:")
    print(f"Risk Factor: {ai.risk_factor:.2f}")
    print("Top effective words:")
    sorted_words = sorted(ai.player_words.values(), 
                         key=lambda w: ai.word_effectiveness.get(w['text'].lower(), 0), 
                         reverse=True)
    for word in sorted_words[:3]:
        eff = ai.word_effectiveness.get(word['text'].lower(), 0)
        print(f"{word['text']}: Effectiveness {eff}")

def main():
    # Player word list (with costs but initially unknown power)
    player_words = [
        {"text": "Quantum", "cost": 12},
        {"text": "Nanobot", "cost": 6},
        {"text": "Psionics", "cost": 9},
        {"text": "Gravity", "cost": 10},
        {"text": "Aether", "cost": 8},
        {"text": "Plasma", "cost": 7},
        {"text": "Neutrino", "cost": 11},
        {"text": "DarkEnergy", "cost": 15}
    ]
    
    # System word list (unknown to player)
    system_words = [
        "Singularity", "Nova", "Paradox", 
        "Armageddon", "Infinity", "EventHorizon",
        "Superstring", "Omniscience"
    ]
    
    # Initialize AI
    ai = AdaptiveAI(player_words)
    
    print("Starting Adaptive Word Battle Game!\n")
    print("AI is learning as it plays...\n")
    
    # Play 5 rounds
    for round_num in range(1, 6):
        print(f"\n=== Round {round_num} ===")
        system_word = random.choice(system_words)
        simulate_round(ai, system_word)
        sleep(1)
    
    # Final results
    print("\n=== Game Over ===")
    print(f"Final Score: ${ai.total_score}")
    if ai.total_score < 100:
        print("Excellent performance! AI learned well.")
    elif ai.total_score < 150:
        print("Good effort! Strategy improved during game.")
    else:
        print("Needs improvement. Try adjusting learning parameters.")

if __name__ == "__main__":
    main()