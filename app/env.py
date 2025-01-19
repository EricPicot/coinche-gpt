import logging
from .llm_agent import LLM_Agent
from .deck import Deck
from .player import HumanPlayer, LLMPlayer
from .game_constants import CARD_VALUES_NORMALIZED, CARD_ORDER  # Ajout de l'import


logging.basicConfig(level=logging.INFO)

class CoincheEnv:
    """
    Environment for the Coinche game.
    Manages the game state, bidding phase, and interactions with players.
    """

    def __init__(self):
        self.llm_agent = LLM_Agent('LLM_Agent')
        self.players = [
            HumanPlayer("South"),
            LLMPlayer("West", self.llm_agent),
            LLMPlayer("North", self.llm_agent),
            LLMPlayer("East", self.llm_agent)
        ]
        self.deck = Deck()
        self.current_contract = None
        self.current_contract_value = 70
        self.current_contract_holder = None
        self.atout_suit = None
        self.annonces = {player.name: None for player in self.players}
        self.current_player_index = 0
        self.bidding_round = 0
        self.bidding_phase_over = False
        self.played_cards = [] #cards won by each player

        # Attributs pour la phase de jeu
        self.current_trick = []  # Liste des cartes jouées dans le pli actuel
        self.trick_positions = {  # Pour savoir qui a joué quelle carte
            'North': None,
            'East': None,
            'South': None,
            'West': None
        }
        self.trick_starter = 'South'  # Le joueur qui commence le pli
        self.current_player = 'South'  # Le joueur actuel (utilise le nom au lieu de l'index)
        self.trick_winner = None  # Le gagnant du pli actuel
        self.trick_count = 0  # Nombre de plis joués
        self.team_points = {  # Points des équipes
            'NS': 0,  # North-South
            'EW': 0   # East-West
        }



    def initialize_game(self):
        """
        Initialize the game by resetting the deck, players' hands, and game state.
        """
        # Reset des attributs existants
        self.current_contract = None
        self.current_contract_value = 70
        self.current_contract_holder = None
        self.atout_suit = None
        self.annonces = {player.name: None for player in self.players}
        self.current_player_index = 0
        self.bidding_round = 0
        self.bidding_phase_over = False
        self.played_cards = [] # cards won by each player

        # Reset des nouveaux attributs de la phase de jeu
        self.current_trick = []
        self.trick_positions = {
            'North': None,
            'East': None,
            'South': None,
            'West': None
        }
        self.trick_starter = 'South'
        self.current_player = 'South'
        self.trick_winner = None
        self.trick_count = 0
        self.team_points = {
            'NS': 0,
            'EW': 0
        }

        # Distribution des cartes
        self.deck.reset()
        for player in self.players:
            player.reset_hand()
        hands = self.deck.deal(num_hands=4, num_cards_per_hand=8)
        for player, hand in zip(self.players, hands):
            player.receive_cards(hand)
            player.organize_hand()

    def handle_bidding(self, player_name, bid):
        """
        Handle the bidding process for a player.
        
        Args:
            player_name (str): The name of the player making the bid.
            bid (str): The bid made by the player.
        """
        if bid != 'pass':
            bid_value = int(bid.split()[0])
            if ((self.current_contract_value is None or bid_value > self.current_contract_value) 
                and (bid.split()[2] in ['hearts', 'spades', 'diamonds', 'clubs'])):
                self.current_contract_value = bid_value
                self.current_contract_holder = player_name
                self.current_contract = bid
                self.atout_suit = bid.split()[2]
                self.annonces[player_name] = bid
            else:
                self.annonces[player_name] = 'pass'
        else:
            self.annonces[player_name] = 'pass'
        
        logging.info(f"Annonces: {self.annonces}")
        self.advance_bidding_round()

    def advance_bidding_round(self):
        """
        Advance to the next round of bidding.
        """
        if self.bidding_phase_over:
            return

        self.current_player_index = (self.current_player_index + 1) % 4

        passes = [bid == 'pass' for bid in self.annonces.values()]
        reindexed_passes = passes[self.current_player_index:] + passes[:self.current_player_index]
        current_player = self.players[self.current_player_index]
        if all(reindexed_passes[-3:]) and all([bid is not None for bid in self.annonces.values()]):
            logging.info("Three consecutive passes detected. Bidding phase ends.")
            self.bidding_phase_over = True
            return

        if not current_player.is_llm:
            self.render_bidding_options('South')
        else:
            annonce = self.llm_agent.get_annonce(current_player.name, 
                                                 current_player.hand, 
                                                 self.current_contract,
                                                 self.current_contract_holder)
            self.handle_bidding(current_player.name, annonce)

    def render_bidding_options(self, player_name):
        """
        Render bidding options for the given player.
        
        Args:
            player_name (str): The name of the player.
        """
        options = self.get_bidding_options(player_name)
        self.send_bidding_options_to_frontend(player_name, options)

    def send_bidding_options_to_frontend(self, player_name, options):
        """
        Send bidding options to the frontend.
        
        Args:
            player_name (str): The name of the player.
            options (dict): The bidding options.
        """
        logging.info(f"Sending bidding options to {player_name}: {options}")

    def get_bidding_options(self, player_name):

        """
        Get bidding options for the given player.
        
        Args:
            player_name (str): The name of the player.
        
        Returns:
            dict: The bidding options and bidding phase status.
        """
        options = []
        if player_name == 'South':
            for suit in ['hearts', 'spades', 'diamonds', 'clubs']:
                for value in range(self.current_contract_value + 10, 170, 10):
                    options.append(f'{value} of {suit}')
        return {
            'options': options,
            'bidding_phase_over': self.bidding_phase_over
        }
    
    def calculate_trick_points(self, trick_cards):
        """Calcule les points du pli"""
        from .game_constants import CARD_POINTS
        
        total_points = 0
        for card in trick_cards:
            value, suit = card.split(' of ')
            # Convertir en minuscules pour la comparaison
            value = value.lower()
            points_table = CARD_POINTS['trump' if suit == self.atout_suit else 'normal']
            # Utiliser la version minuscule pour la recherche
            total_points += points_table[value]
            
        return total_points
    
    def play_card(self, player_name, card_str):
        """Gère le tour de jeu complet après qu'un joueur a joué"""
        
        logging.info(f"Starting play_card with player: {player_name}, card: {card_str}")
        logging.info(f"Current trick: {self.current_trick}")
        logging.info(f"Current player: {self.current_player}")
        
        try:
            # Trouver le joueur
            player = next((p for p in self.players if p.name == player_name), None)
            if not player:
                raise ValueError(f"Player {player_name} not found")

            # Vérifier si c'est le bon joueur
            if player_name != self.current_player:
                raise ValueError(f"Not your turn. Current player is {self.current_player}")

            # Si c'est un joueur humain, normaliser la carte
            if not player.is_llm:
                card_value, card_suit = card_str.split(' of ')
                if card_value in CARD_VALUES_NORMALIZED:
                    card_str = f"{CARD_VALUES_NORMALIZED[card_value]} of {card_suit}"
                else:
                    card_str = card_str.lower()
                
                logging.info(f"Normalized card: {card_str}")
                
                # Jouer la carte
                card = player.play_card(card_str, self.current_trick, self.atout_suit)
            else:
                # Pour un LLM, laisser le joueur choisir sa carte
                card = player.play_card(
                    current_trick=self.current_trick,
                    atout_suit=self.atout_suit,
                    trick_positions=self.trick_positions
                )

            # Mettre à jour l'état du jeu
            self.current_trick.append(str(card))
            self.trick_positions[player_name] = str(card)
            
            # Faire jouer les LLM jusqu'au prochain joueur humain
            next_player = self.get_next_player(player_name)
            
            while next_player != 'South' and len(self.current_trick) < 4:
                llm_player = next(p for p in self.players if p.name == next_player)
                llm_card = llm_player.play_card(
                    current_trick=self.current_trick,
                    atout_suit=self.atout_suit,
                    trick_positions=self.trick_positions
                )
                
                self.current_trick.append(str(llm_card))
                self.trick_positions[next_player] = str(llm_card)
                next_player = self.get_next_player(next_player)
            
            # Gérer la fin du pli si nécessaire
            if len(self.current_trick) == 4:
                self.trick_winner = self.determine_trick_winner()
                
                # Calculer et attribuer les points
                trick_points = self.calculate_trick_points(self.current_trick)
                if self.trick_winner in ['North', 'South']:
                    self.team_points['NS'] += trick_points
                else:
                    self.team_points['EW'] += trick_points
                
                
                # Réinitialiser pour le prochain pli
                self.current_trick = []
                self.trick_positions = {p: None for p in self.trick_positions}
                self.current_player = self.trick_winner
                self.trick_starter = self.trick_winner
            else:
                self.current_player = next_player

            return {
                'status': 'success',
                'current_trick': self.get_current_trick(),
                'trick_winner': self.trick_winner,
                'next_player': self.current_player,
                'team_points': self.team_points,
                'players_hands': {
                    p.name: [str(card) for card in p.hand] 
                    for p in self.players
                }
            }

        except Exception as e:
            logging.error(f"Error in play_card: {str(e)}")
            raise

    def get_current_trick(self):
        """
        Retourne l'état actuel du pli avec les informations sur qui a joué quoi
        """
        return {
            'cards': self.current_trick,
            'positions': self.trick_positions,
            'starter': self.trick_starter,
            'current_player': self.current_player,
            'trick_number': len(self.current_trick),
            'is_complete': len(self.current_trick) == 4,
            'atout_suit': self.atout_suit,
            'contract': {
                'value': self.current_contract_value,
                'holder': self.current_contract_holder
            }
        }

    def resolve_round(self):
        """
        Determine the winner of the round and assign the played cards to the winner.
        """
        leading_suit = self.played_cards[0][1].suit
        winning_card = self.played_cards[0][1]
        winning_player = self.played_cards[0][0]

        for player_name, card in self.played_cards[1:]:
            if card.suit == self.atout_suit and winning_card.suit != self.atout_suit:
                winning_card = card
                winning_player = player_name
            elif card.suit == winning_card.suit and card.value > winning_card.value:
                winning_card = card
                winning_player = player_name

        winning_player_obj = next(p for p in self.players if p.name == winning_player)
        winning_player_obj.won_cards.extend([card for _, card in self.played_cards])
        self.played_cards = []
        self.current_player_index = self.players.index(winning_player_obj)

    def start_playing_phase(self):
        """
        Start the playing phase after the bidding phase is over.
        """
        self.current_player_index = 0  # South starts playing
        for player in self.players:
            player.won_cards = []

    def get_current_player(self):
        """
        Get the name of the current player.
        """
        return self.players[self.current_player_index].name

    def get_game_state(self):
        """Retourne l'état actuel du jeu"""
        try:
            current_player_obj = next(p for p in self.players if p.name == self.current_player)
            playable_cards = self.get_playable_cards(self.current_player) if self.current_player == 'South' else []
            
            return {
                'current_trick': [str(card) for card in self.current_trick],
                'trick_positions': {
                    player: str(card) if card else None 
                    for player, card in self.trick_positions.items()
                },
                'trick_winner': self.trick_winner,
                'current_player': self.current_player,
                'playable_cards': playable_cards,
                'trick_starter': self.trick_starter,
                'trick_count': self.trick_count,
                'atout_suit': self.atout_suit,
                'team_points': self.team_points,
                'last_trick_points': self.last_trick_points if hasattr(self, 'last_trick_points') else 0,
                'contract': {
                    'value': self.current_contract_value,
                    'holder': self.current_contract_holder
                }
            }
        except Exception as e:
            logging.error(f"Error in get_game_state: {str(e)}")  # Correction ici
            raise

    def determine_trick_winner(self):
        """Détermine le gagnant du pli selon les règles de la coinche"""
        from .game_constants import CARD_ORDER
        
        if not self.current_trick:
            return None
            
        # Première carte jouée
        leading_card = self.current_trick[0]
        leading_suit = leading_card.split(' of ')[1]
        winning_card = leading_card
        winning_player = self.trick_starter
        
        for player, card in self.trick_positions.items():
            if card is None:
                continue
                
            card_value, card_suit = card.split(' of ')
            card_value = card_value.lower()  # Normaliser en minuscules
            
            # Si c'est de l'atout
            if card_suit == self.atout_suit:
                if winning_card.split(' of ')[1] != self.atout_suit:
                    winning_card = card
                    winning_player = player
                else:
                    # Comparer les valeurs des atouts
                    try:
                        current_rank = CARD_ORDER['trump'].index(card_value)
                        winning_value = winning_card.split(' of ')[0].lower()  # Normaliser en minuscules
                        winning_rank = CARD_ORDER['trump'].index(winning_value)
                        if current_rank < winning_rank:  # Plus petit index = plus forte carte
                            winning_card = card
                            winning_player = player
                    except ValueError as e:
                        logging.error(f"Error comparing cards: {card_value} vs {winning_value}")
                        raise ValueError(f"Invalid card value: {e}")
                        
            # Si c'est la couleur demandée (pas atout)
            elif card_suit == leading_suit and winning_card.split(' of ')[1] != self.atout_suit:
                try:
                    current_rank = CARD_ORDER['normal'].index(card_value)
                    winning_value = winning_card.split(' of ')[0].lower()  # Normaliser en minuscules
                    winning_rank = CARD_ORDER['normal'].index(winning_value)
                    if current_rank < winning_rank:
                        winning_card = card
                        winning_player = player
                except ValueError as e:
                    logging.error(f"Error comparing cards: {card_value} vs {winning_value}")
                    raise ValueError(f"Invalid card value: {e}")
                    
        return winning_player

    def get_next_player(self, current_player):
        """Retourne le joueur suivant"""
        players = ['North', 'East', 'South', 'West']
        current_index = players.index(current_player)
        return players[(current_index + 1) % 4]

    def get_playable_cards(self, player):
        """Détermine quelles cartes peuvent être jouées selon les règles de la coinche"""
        # Trouver le joueur dans la liste des joueurs
        player_obj = next((p for p in self.players if p.name == player), None)
        if not player_obj:
            logging.error(f"Player {player} not found")
            return []

        try:
            logging.info(f"1. Current trick: {self.current_trick}")
            logging.info(f"2. Player hand: {[str(card) for card in player_obj.hand]}")
            playable_cards = player_obj.get_playable_cards(self.current_trick, self.atout_suit)
            logging.info(f"3. Playable cards: {[str(card) for card in playable_cards]}")
            return [str(card).lower() for card in playable_cards]  # Assurons-nous que tout est en minuscules
        except Exception as e:
            logging.error(f"Error getting playable cards: {str(e)}")
            return []