import random
import logging

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.won_cards = []

    def receive_cards(self, cards):
        self.hand.extend(cards)

    def reset_hand(self):
        self.hand = []
        self.won_cards = []
    
    def organize_hand(self):
        self.hand.sort(key=lambda card: (card.suit, card.value))
    
    def get_playable_cards(self, current_trick, atout_suit):
        """Détermine les cartes jouables selon les règles de la coinche"""
        # Si c'est la première carte du pli, toutes les cartes sont jouables
        if not current_trick:
            return self.hand

        # Première carte du pli - s'assurer qu'elle est en string
        first_card = current_trick[0]
        leading_suit = str(first_card).split(' of ')[1]

        # Cartes de la même couleur que la première carte
        same_suit_cards = [
            card for card in self.hand 
            if str(card).split(' of ')[1] == leading_suit
        ]
        
        # Si on a des cartes de la même couleur, on doit les jouer
        if same_suit_cards:
            return same_suit_cards
            
        # Si on n'a pas de carte de la même couleur
        # Atouts si possible
        atout_cards = [
            card for card in self.hand 
            if str(card).split(' of ')[1] == atout_suit
        ]
        if atout_cards and leading_suit != atout_suit:
            return atout_cards
            
        # Si on ne peut ni fournir ni couper, toutes les cartes sont jouables
        return self.hand

    def play_card(self, card_str, current_trick, atout_suit):
        """Joue une carte de la main"""
        # Trouver la carte dans la main
        card_to_play = None
        for card in self.hand:
            if str(card).lower() == card_str.lower():
                card_to_play = card
                break

        if not card_to_play:
            raise ValueError(f"Card {card_str} not in hand")

        # Vérifier si la carte est jouable
        playable_cards = self.get_playable_cards(current_trick, atout_suit)
        if card_to_play not in playable_cards:
            raise ValueError(f"Card {card_str} is not playable")

        # Retirer la carte de la main
        self.hand.remove(card_to_play)
        return str(card_to_play)  # Retourner la carte en string

class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.is_llm = False
        
    def play_card(self, card_str, current_trick, atout_suit, trick_positions=None):
        """Joue la carte choisie par le joueur humain"""
        playable_cards = self.get_playable_cards(current_trick, atout_suit)
        
        # Convertir toutes les cartes jouables en string pour la comparaison
        playable_cards_str = [str(c) for c in playable_cards]
        if card_str not in playable_cards_str:
            raise ValueError(f"Cette carte ne peut pas être jouée. Cartes jouables: {playable_cards_str}")
            
        # Trouver la carte dans la main
        card_to_play = next(c for c in self.hand if str(c) == card_str)
        self.hand.remove(card_to_play)
        return str(card_to_play)


class LLMPlayer(Player):
    def __init__(self, name, llm_agent):
        super().__init__(name)
        self.is_llm = True
        self.llm_agent = llm_agent
        
    def play_card(self, current_trick=None, atout_suit=None, trick_positions=None):
        # Obtenir les cartes jouables
        playable_cards = self.get_playable_cards(current_trick, atout_suit)
        logging.info(f"LLMPlayer {self.name} - Playable cards: {playable_cards}")
        
        # Choisir une carte (pour l'instant, la première carte jouable)
        chosen_card = str(playable_cards[0]).lower()  # Forcer en minuscules
        
        # Retirer la carte de la main
        card_to_remove = next(card for card in self.hand if str(card).lower() == chosen_card)
        self.hand.remove(card_to_remove)
        
        return chosen_card