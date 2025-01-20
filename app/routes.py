from flask import Blueprint, request, jsonify
from flask_cors import CORS
import logging
from .env import CoincheEnv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)
CORS(main)  # Enable CORS for the blueprint
env = CoincheEnv()

@main.route('/initialize', methods=['POST'])
def initialize():
    """
    Initialize the game and return the initial state including players' hands and bidding options.
    """
    env.initialize_game()
    
    # Création du state initial
    initial_state = {
        'players_hands': {player.name: [str(card) for card in player.hand] for player in env.players},
        'bidding_options': env.get_bidding_options('South')['options'],
        'bidding_phase_over': env.bidding_phase_over,
        'annonces': env.annonces,
        # Ajout des informations de la phase de jeu
        'game_state': {
            'current_trick': env.current_trick,
            'trick_positions': env.trick_positions,
            'current_player': env.current_player,
            'trick_starter': env.trick_starter,
            'trick_count': env.trick_count,
            'team_points': env.team_points
        }
    }

    # Logging
    for player in env.players:
        logger.info(f"{player.name}: {player.hand}")
    logger.info("Bidding options Initialization: %s", initial_state['bidding_options'])
    logger.info("Initial game state: %s", initial_state['game_state'])

    return jsonify(initial_state) 


@main.route('/bid', methods=['POST'])
def bid():
    """
    Handle a bid from a player.
    """
    try:
        data = request.json
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        player = data.get('player')
        bid = data.get('bid')
        
        logger.info(f"Received bid request - Player: {player}, Bid: {bid}")
        
        if not player or not bid:
            logger.error(f"Missing data - Player: {player}, Bid: {bid}")
            return jsonify({'error': 'Player and bid are required'}), 400

        env.handle_bidding(player, bid)
        
        logger.info(f"Bid processed successfully - Current contract: {env.current_contract}")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error in bid endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main.route('/get_bidding_options', methods=['GET'])
def get_bidding_options():
    """
    Get the bidding options for a specific player.
    """
    player = request.args.get('player')
    logger.info("Getting bidding options for player: %s", player)
    options = env.get_bidding_options(player)
    logger.info("Options: %s", options)
    return jsonify({
        'options': options['options'],
        'bidding_phase_over': options['bidding_phase_over'],
        'annonces': env.annonces
    })


@main.route('/game_state', methods=['GET'])
def get_game_state():
    try:
        game_state = env.get_game_state()
        logger.info(f"Game state fetched: {game_state}")
        return jsonify(game_state)
    except Exception as e:
        logger.error(f"Error fetching game state: {str(e)}")
        return jsonify({'error': str(e)}), 400

@main.route('/play_card', methods=['POST'])
def play_card():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        player = data.get('player')
        card = data.get('card')
        
        if not player or not card:
            return jsonify({'error': 'Player and card are required'}), 400

        logger.info(f"Received play_card request - Player: {player}, Card: {card}")
        logger.info(f"Current trick before play: {env.current_trick}")
        logger.info(f"Current trick positions before play: {env.trick_positions}")
        logger.info(f"Current atout suit: {env.atout_suit}")

        # Vérifier les cartes jouables avant de jouer
        playable_cards = env.get_playable_cards(player)
        logger.info(f"Playable cards for {player}: {playable_cards}")

        # Passer les trick_positions actuelles
        result = env.play_card(
            player_name=player,
            card_str=card.lower()  # Convertir en minuscules ici
        )
        
        logger.info(f"Card played successfully: {card} by {player}")
        logger.info(f"Current trick after play: {env.current_trick}")
        logger.info(f"Current trick positions after play: {env.trick_positions}")
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Validation error in play_card: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in play_card: {str(e)}, type: {type(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main.route('/get_annonces', methods=['GET'])
def get_annonces():
    """
    Get the updated annonces and bidding phase status.
    """
    annonces = env.annonces
    bidding_phase_over = env.bidding_phase_over
    return jsonify({'annonces': annonces, 'bidding_phase_over': bidding_phase_over})

@main.route('/current_trick', methods=['GET'])
def get_current_trick():
    try:
        current_trick = env.get_current_trick()
        logger.info(f"Current trick fetched: {current_trick}")
        return jsonify(current_trick)
    except Exception as e:
        logger.error(f"Error fetching current trick: {str(e)}")
        return jsonify({'error': str(e)}), 400

@main.route('/next_trick', methods=['POST'])
def next_trick():
    try:
        logger.info("Starting next trick...")
        
        # Si trick_winner est None, utiliser trick_starter
        if env.trick_winner is None:
            logger.info(f"No trick winner defined, using trick_starter: {env.trick_starter}")
            env.trick_winner = env.trick_starter
        
        logger.info(f"Previous trick winner: {env.trick_winner}")
        
        # Reset du pli actuel
        env.current_trick = []
        env.trick_positions = {
            'North': None,
            'East': None,
            'South': None,
            'West': None
        }
        
        # Mettre à jour le joueur qui commence
        env.trick_starter = env.trick_winner
        env.current_player = env.trick_winner
        env.trick_winner = None
        
        # Incrémenter le compteur de plis
        env.trick_count += 1
        
        # Si c'est au tour d'un LLM, le faire jouer automatiquement
        if env.current_player != 'South':  # Si ce n'est pas le joueur humain
            logger.info(f"LLM {env.current_player} is playing...")
            # Obtenir les cartes jouables
            playable_cards = env.get_playable_cards(env.current_player)
            if playable_cards:
                # Jouer la première carte disponible
                result = env.play_card(env.current_player, playable_cards[0])
                return jsonify(result)
        
        return jsonify({
            'status': 'success',
            'next_player': env.current_player,
            'team_points': env.team_points
        })
        
    except Exception as e:
        logger.error(f"Error in next_trick: {str(e)}")
        return jsonify({'error': str(e)}), 400
@main.route('/game_status', methods=['GET'])
def get_game_status():
    """
    Vérifie si la partie est terminée et retourne le score final
    """
    try:
        # Une partie se termine après 8 plis
        game_over = env.trick_count >= 8
        
        status = {
            'game_over': game_over,
            'team_points': env.team_points,
            'trick_count': env.trick_count,
            'contract': {
                'value': env.current_contract_value,
                'holder': env.current_contract_holder,
                'suit': env.atout_suit
            }
        }
        
        if game_over:
            # Calculer qui a gagné
            contract_team = 'NS' if env.current_contract_holder in ['North', 'South'] else 'EW'
            contract_made = env.team_points[contract_team] >= env.current_contract_value
            
            status.update({
                'contract_team': contract_team,
                'contract_made': contract_made,
                'final_score': {
                    'NS': env.team_points['NS'],
                    'EW': env.team_points['EW']
                }
            })
            
        logger.info(f"Game status: {status}")
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting game status: {str(e)}")
        return jsonify({'error': str(e)}), 400

@main.route('/reset_game', methods=['POST'])
def reset_game():
    """
    Réinitialise complètement la partie
    """
    try:
        env.initialize_game()
        
        initial_state = {
            'players_hands': {player.name: [str(card) for card in player.hand] for player in env.players},
            'bidding_options': env.get_bidding_options('South')['options'],
            'bidding_phase_over': env.bidding_phase_over,
            'annonces': env.annonces,
            'game_state': {
                'current_trick': env.current_trick,
                'trick_positions': env.trick_positions,
                'current_player': env.current_player,
                'trick_starter': env.trick_starter,
                'trick_count': env.trick_count,
                'team_points': env.team_points
            }
        }
        
        logger.info("Game reset successfully")
        return jsonify(initial_state)
        
    except Exception as e:
        logger.error(f"Error resetting game: {str(e)}")
        return jsonify({'error': str(e)}), 400