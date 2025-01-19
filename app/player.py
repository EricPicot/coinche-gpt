import random

class Player:
    def __init__(self, name, is_llm=False):
        self.name = name
        self.hand = []
        self.is_llm = is_llm
        self.won_cards = []

    def receive_cards(self, cards):
        self.hand.extend(cards)

    def reset_hand(self):
        self.hand = []
        self.won_cards = []
    
    def organize_hand(self):
        self.hand.sort(key=lambda card: (card.suit, card.value))
    
    def play_card(self):
            if not self.hand:
                return None
            card = random.choice(self.hand)
            self.hand.remove(card)
            print('card played:', card)
            return card