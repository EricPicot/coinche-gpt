from flask import Blueprint, request, jsonify
from flask_cors import CORS
import logging
from .env import CoincheEnv

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
    data = request.json
    player = data['player']
    bid = data['bid']
    logger.info("Player: %s", player)
    logger.info("Bid: %s", bid)
    env.handle_bidding(player, bid)
    return jsonify({'status': 'success'})


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
        player = data.get('player')
        card = data.get('card')
        
        if not player or not card:
            raise ValueError("Player and card are required")

        result = env.play_card(player, card)
        logger.info(f"Card played: {card} by {player}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error playing card: {str(e)}")
        return jsonify({'error': str(e)}), 400


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