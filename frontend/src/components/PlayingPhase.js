import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { gameService } from '../services/api';
import { POLLING_INTERVAL } from '../config/constants';
import './PlayingPhase.css';

const PlayingPhase = ({ playersHands: initialPlayersHands, currentPlayer }) => {
    const [gameState, setGameState] = useState({
        currentTrick: [],
        trickWinner: null,
        isPlayerTurn: false,
        playableCards: [],
        trick_positions: {},
        team_points: { NS: 0, EW: 0 },
    });

    const [showTrickSummary, setShowTrickSummary] = useState(false);
    const [trickPoints, setTrickPoints] = useState(0);
    const [playersHands, setPlayersHands] = useState(initialPlayersHands);

    const getCardImage = (card) => {
        const [value, suit] = card.toLowerCase().split(' of ');
        return `/cards/${value}_of_${suit}.png`;
    };

    const handleCardPlay = async (card) => {
        try {
            console.log('Card before any processing:', card);  // NEW LOG

            // Vérifier si c'est bien notre tour
            if (!gameState.isPlayerTurn) {
                alert("Ce n'est pas votre tour !");
                return;
            }
    
            // Vérifier si la carte est jouable (insensible à la casse)
            const isPlayable = gameState.playableCards.some(
                playableCard => playableCard.toLowerCase() === card.toLowerCase()
            );
            if (!isPlayable) {
                alert("Cette carte n'est pas jouable !");
                return;
            }
    
            console.log('Attempting to play card:', card);
            // ... reste du code ...
            console.log('Current game state:', gameState);
            
            const response = await gameService.playCard(currentPlayer, card);
            console.log('Play card response:', response);
            
            if (response.status === 'success') {
                if (response.players_hands) {
                    setPlayersHands(response.players_hands);
                }
                
                // Mettre à jour l'état du jeu
                setGameState(prevState => ({
                    ...prevState,
                    currentTrick: response.current_trick,
                    trickWinner: response.trick_winner,
                    isPlayerTurn: response.next_player === currentPlayer,
                    trick_positions: response.trick_positions || {},
                    team_points: response.team_points || prevState.team_points,
                }));
            }
        } catch (error) {
            console.error('Error playing card bastard:', error);
            const errorMessage = error.response?.data?.error || error.message || 'Erreur inconnue';
            // alert(`Erreur lors du jeu de la carte : ${errorMessage}`);
        }
    };

    useEffect(() => {
        const fetchGameState = async () => {
            try {
                const gameStateResponse = await gameService.getGameState();
                console.log('Fetched game state:', gameStateResponse);
                
                // Si un nouveau pli vient de se terminer
                if (gameStateResponse.trick_winner && !showTrickSummary) {
                    setTrickPoints(gameStateResponse.last_trick_points || 0);
                    setShowTrickSummary(true);
                }
                
                setGameState(prevState => ({
                    ...prevState,
                    currentTrick: gameStateResponse.current_trick || [],
                    trickWinner: gameStateResponse.trick_winner,
                    isPlayerTurn: gameStateResponse.current_player === currentPlayer,
                    playableCards: gameStateResponse.playable_cards || [],
                    trick_positions: gameStateResponse.trick_positions || {},
                    team_points: gameStateResponse.team_points || { NS: 0, EW: 0 },
                }));

                if (gameStateResponse.players_hands) {
                    setPlayersHands(gameStateResponse.players_hands);
                }
            } catch (error) {
                console.error('Error fetching game state:', error);
            }
        };

        fetchGameState();
        const interval = setInterval(fetchGameState, POLLING_INTERVAL);
        return () => clearInterval(interval);
    }, [currentPlayer, showTrickSummary]);

    const handleNextTrick = async () => {
        try {
            console.log('Starting next trick...');  // Ajout de log
            const response = await gameService.nextTrick();
            console.log('Next trick response:', response);  // Ajout de log
            
            if (response.status === 'success') {
                setShowTrickSummary(false);
                // Mettre à jour l'état du jeu avec les nouvelles données
                setGameState(prevState => ({
                    ...prevState,
                    currentTrick: [],
                    trickWinner: null,
                    isPlayerTurn: response.next_player === currentPlayer,
                    trick_positions: {},
                    team_points: response.team_points || prevState.team_points,
                }));
            }
        } catch (error) {
            console.error('Error starting next trick:', error);
        }
    };

    return (
        <div className="playing-phase">
            {/* Cartes des autres joueurs */}
            <div className="player north">
                {playersHands["North"]?.map((card, index) => (
                    <div key={index} className="card">
                        <img 
                            src={getCardImage(card)}
                            alt={card}
                            className="card-image rotated"
                        />
                    </div>
                ))}
            </div>

            <div className="horizontal-players">
                <div className="player west">
                    {playersHands["West"]?.map((card, index) => (
                        <div key={index} className="card rotated-left">
                            <img 
                                src={getCardImage(card)}
                                alt={card}
                                className="card-image"
                            />
                        </div>
                    ))}
                </div>
                {/* Affichage des points */}
                <div className="team-points">
                    <div>NS: {gameState.team_points.NS}</div>
                    <div>EW: {gameState.team_points.EW}</div>
                </div>
                {/* Zone centrale pour les cartes jouées */}
            <div className="current-trick">
                {gameState.trick_positions && Object.entries(gameState.trick_positions)
                    .filter(([_, card]) => card !== null)
                    .map(([player, card], index) => (
                        <div 
                            key={player} 
                            className={`played-card position-${player.toLowerCase()}`}
                        >
                            <img 
                                src={getCardImage(card)}
                                alt={card}
                                className="card-image"
                            />
                        </div>
                    ))}
            </div>
                <div className="player east">
                    {playersHands["East"]?.map((card, index) => (
                        <div key={index} className="card rotated-right">
                            <img 
                                src={getCardImage(card)}
                                alt={card}
                                className="card-image"
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Cartes du joueur Sud (joueur actuel) */}
            <div className="player south">
                {playersHands["South"]?.map((card, index) => (
                    <button
                        key={index}
                        className="card-button"
                        onClick={() => handleCardPlay(card)}
                        disabled={!gameState.isPlayerTurn || !gameState.playableCards.includes(card)}
                    >
                        <img 
                            src={getCardImage(card)}
                            alt={card}
                            className="card-image"
                        />
                    </button>
                ))}
            </div>

            {/* Message du gagnant du pli */}
            {gameState.trickWinner && (
                <div className="trick-winner">
                    Pli gagné par : {gameState.trickWinner} 
                    {gameState.trickWinner === currentPlayer && " - C'est à vous de jouer !"}
                </div>
            )}
        {showTrickSummary && (
                <div className="trick-summary-modal">
                    <div className="trick-summary-content">
                        <h2>Résumé du pli</h2>
                        <div className="trick-cards-summary">
                            {Object.entries(gameState.trick_positions)
                                .filter(([_, card]) => card !== null)
                                .map(([player, card]) => (
                                    <div key={player} className="trick-card-entry">
                                        <span>{player}: </span>
                                        <img 
                                            src={getCardImage(card)}
                                            alt={card}
                                            className="small-card-image"
                                        />
                                    </div>
                                ))
                            }
                        </div>
                        <p>Gagnant : {gameState.trickWinner}</p>
                        <p>Points marqués : {trickPoints}</p>
                        <p>Score total :</p>
                        <p>NS: {gameState.team_points.NS} points</p>
                        <p>EW: {gameState.team_points.EW} points</p>
                        <button 
                            className="next-trick-button"
                            onClick={handleNextTrick}
                        >
                            Pli suivant
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

PlayingPhase.propTypes = {
    playersHands: PropTypes.object.isRequired,
    currentPlayer: PropTypes.string.isRequired,
};

export default PlayingPhase;