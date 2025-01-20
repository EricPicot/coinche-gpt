import openai
import os
from dotenv import load_dotenv
import json
from .game_constants import CARD_ORDER, CARD_POINTS
import time
load_dotenv()  # Load environment variables from .env file

def extract_annonce(json_string):
    data = json.loads(json_string)
    annonce = data.get('annonce')
    return annonce

def get_partner(player_name):
    partners = {
        "South": "North",
        "North": "South",
        "East": "West",
        "West": "East"
    }
    return partners.get(player_name, "Unknown")

class LLM_Agent:
    def __init__(self, name):
        self.name = name
        self.model = 'gpt-4'
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_action(self, game_state):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a player in a game of Coinche, a French card game similar to Belote."},
                {"role": "user", "content": f"Given the game state: {game_state}, what action should the player take?"}
            ]
        )
        action = response.choices[0].message['content'].strip()
        return action

    def get_annonce(self, player_name, player_hand, current_contract, current_contract_holder):
        prompt = (
            f"You are playing a game of Coinche, a French card game similar to Belote. "
            f"The current phase is the annonce phase. "
            f"You are {player_name}, and your partner is {get_partner(player_name)}. "
            f"Your hand is: {player_hand}. "
            f"The current highest contract value is {current_contract}, "
            f"and the current contract holder is {current_contract_holder}. "
            "Your goal is to make a strategic decision about your annonce. You must give a value and a suit for your annonce. The suit is the one you would like to see as trump given the strenght of you game."
            "Your response must strictly follow the format 'value of suit', for example, '80 of hearts'. If you cannot make a higher annonce, respond with 'pass'. "
            "\n\n"
            "Key rules and considerations for your decision: "
            "1. **Card Values in Trump Suit:** Jack = 20 points, Nine = 14 points, Ace = 11 points, Ten = 10 points, King = 4 points, Queen = 3 points, others = 0 points. "
            "2. **Card Values in Non-Trump Suits:** Ace = 11 points, Ten = 10 points, King = 4 points, Queen = 3 points, Jack = 2 points, others = 0 points. "
            "3. **Your Hand:** Evaluate the points in your hand and assess its strength, especially in potential trump suits. Strong trump cards and high-ranking non-trump cards are key to success. "
            "4. **Partner Coordination:** If you have high cards (e.g., Ace or Ten), consider how they might complement your partner's hand. For example, keeping a high trump card can add value to your partner's trumps. "
            "5. **Bidding Strategy:** Only bid higher if your hand justifies it. For example: "
            "   - A trump card always beats a non-trump card. "
            "   - If your hand includes strong trump cards and high non-trump cards, bid higher. "
            "   - If your hand is weak, pass. "
            "   - Consider suits where you have many high-value cards to declare trump. "
            "   - Use your judgment to bid aggressively or conservatively based on the game state. "
            "\n\n"
            "Your decision should be rational and based on the above rules and considerations. Only provide a single response in the exact format: 'value of suit' (e.g., '80 of hearts') or 'pass'."
        )
        
        print(f"You are the great {player_name}. ")
        print(f"Your partner is {get_partner(player_name)}. ")
        print(f"Your hand is: {player_hand}. ")
        print(f"The current highest contract is {current_contract}, ")
        print(f'and the current contract holder is {current_contract_holder}. ')

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a player in a game of Coinche, a French card game similar to Belote."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        annonce = response.choices[0].message.content.strip().lower()
        annonce = annonce.replace("'", "").replace('"', "")
        time.sleep(1.5)
        print("Annonce:", annonce)
        print(50*"-")
        try:
            if int(annonce.split()[0]) > 160:
                return 'pass' # not allowed to bid greater than 160
            else:
                return annonce
        except:
            return annonce


    def get_card_to_play(self, player_name, player_hand, current_trick, trick_positions, atout_suit):
        """Détermine quelle carte jouer selon les règles de la coinche"""
        if not player_hand:
            raise ValueError("No playable cards")

        # Si on est le premier à jouer
        if not current_trick:
            return str(player_hand[0])

        # Sinon, on suit la couleur demandée
        leading_card = str(current_trick[0])
        leading_suit = leading_card.split(' of ')[1]
        
        # Détermine l'ordre des cartes à utiliser
        card_order = CARD_ORDER['trump'] if leading_suit == atout_suit else CARD_ORDER['normal']
        
        # Trie les cartes jouables par force (en capitalisant la première lettre)
        sorted_cards = sorted(
            player_hand,
            key=lambda c: card_order.index(str(c).split(' of ')[0].capitalize())
        )
        
        time.sleep(1.5)
        return str(sorted_cards[0])