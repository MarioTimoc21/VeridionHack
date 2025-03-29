import json
import random
from time import sleep
from collections import defaultdict

# Load wordlist and optimize data structures
with open('wordlist.json', 'r') as file:
    words_data = json.load(file)
    words_dict = {k: v for k, v in words_data.items()}

word_lookup = {v['text'].lower(): (k, v) for k, v in words_dict.items()}
cost_sorted_words = sorted(words_dict.items(), key=lambda x: x[1]['cost'])

# Load semantic relationships
with open('semantic_relationships.json', 'r') as file:
    semantic_relationships = json.load(file)

# Load wordtest data
with open('wordtest.json', 'r') as file:
    wordtest_data = json.load(file)
    wordtest_list = [v['text'] for v in wordtest_data.values()]


class SemanticAnalyzer:
    def __init__(self):
        self.semantic_relationships = semantic_relationships
        self.cost_effectiveness = cost_sorted_words
        self.cache = {}
        self.word_scores = {}

    def _calculate_word_score(self, word, enemy_word):
        score = 0
        word_lower = word.lower()
        enemy_lower = enemy_word.lower()

        # Verifică relații explicite din JSON
        if enemy_lower in self.semantic_relationships:
            relationships = self.semantic_relationships[enemy_lower]
            if word_lower in relationships.get('beaten_by', []):
                score += 3
            if word_lower in relationships.get('beats', []):
                score -= 1

        # Reguli implicite între cuvinte din wordtest.json și wordlist.json
        else:
            # Exemple extinse de logici universale
            if word_lower == "water" and enemy_lower in ["fire", "flame"]:
                score += 3
            elif word_lower == "ice" and enemy_lower in ["dragon", "lava"]:
                score += 3
            elif word_lower == "shield" and enemy_lower in ["sword", "spear"]:
                score += 3
            elif word_lower == "logic" and enemy_lower in ["ghost", "illusion"]:
                score += 3

        return score

    def find_counter_word(self, enemy_word):
        enemy_lower = enemy_word.lower()
        if enemy_lower in self.cache:
            return self.cache[enemy_lower]

        best_word = None
        best_score = -float('inf')
        best_cost = float('inf')

        for word_id, word_data in words_dict.items():
            word = word_data['text'].lower()
            cost = word_data['cost']
            score = self._calculate_word_score(word, enemy_lower)

            # Euristică îmbunătățită pentru cuvinte necunoscute
            if enemy_lower not in self.semantic_relationships:
                if 3 <= cost <= 7:  # Prioritate pentru cost mediu
                    score += 2 - (cost * 0.1)
                else:
                    score += 1 - (cost * 0.2)  # Penalizează costurile extreme
            else:
                score = score * 5 - cost * 0.2  # Scorul semantic are prioritate

            if score > best_score or (score == best_score and cost < best_cost):
                best_score = score
                best_cost = cost
                best_word = (word_id, word_data)

        # Fallback diversificat
        if best_word is None:
            balanced_words = [w for w in words_dict.values() if 2 <= w['cost'] <= 8]
            best_word = random.choice(balanced_words) if balanced_words else random.choice(list(words_dict.values()))

        self.cache[enemy_lower] = best_word
        return best_word

analyzer = SemanticAnalyzer()

def choose_word(enemy_word):
    return analyzer.find_counter_word(enemy_word)

def play_game_with_wordtest():
    total_cost = 0
    num_rounds = 10  # Numărul de runde de testare
    for round_id in range(1, num_rounds + 1):
        # Selectăm un cuvânt random din wordtest.json
        enemy_word = random.choice(wordtest_list)
        
        # Selectăm cuvântul optim
        word_id, word_data = choose_word(enemy_word)
        chosen_word = word_data['text']
        cost = word_data['cost']
        total_cost += cost
        
        print(f"\nRound {round_id} - Enemy: {enemy_word}")
        print(f"Chosen: {chosen_word} (Cost: {cost}, Total: {total_cost})")
        
    print(f"\nGame Over! Total Cost: {total_cost}")

if __name__ == "__main__":
    play_game_with_wordtest()