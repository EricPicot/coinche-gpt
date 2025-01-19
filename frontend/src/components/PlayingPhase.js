import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { gameService } from '../services/api';
import { POLLING_INTERVAL } from '../config/constants';
import './PlayingPhase.css';

const PlayingPhase = ({ playersHands, currentPlayer }) => {
    const [gameState, setGameState] = useState({
        currentTrick: [],
        trickWinner: null,
        isPlayerTurn: false,
        playableCards: [],
    });



    
        const getCardImage = (card) => {
            const [value, suit] = card.split(' of ');
            return `/cards/${value}_of_${suit}.png`;
        };

        const fetchGameState = async () => {
        try {
            const data = await gameService.getGameState();
            setGameState(prevState => ({
                ...prevState,
                currentTrick: data.current_trick,
                trickWinner: data.trick_winner,
                isPlayerTurn: data.current_player === 'South',
                playableCards: data.playable_cards || [],
            }));
        } catch (error) {
            console.error("Error fetching game state:", error);
        }
    };

    const handleCardPlay = async (card) => {
        if (!gameState.isPlayerTurn) return;
        
        try {
            const response = await gameService.playCard('South', card);
            if (response.status === 'success') {
                await fetchGameState();
            }
        } catch (error) {
            console.error("Error playing card:", error);
        }
    };

    useEffect(() => {
        fetchGameState();
        const interval = setInterval(fetchGameState, POLLING_INTERVAL);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="playing-phase">
            {/* Main du joueur Nord */}
            <div className="player north">
                {playersHands["North"] && playersHands["North"].map((card, index) => (
                    <div key={index} className="card rotated">
                        <img 
                            src={getCardImage(card)}
                            alt={card}
                            className="card-image"
                        />
                    </div>
                ))}
            </div>

            {/* Mains des joueurs Est et Ouest */}
            <div className="horizontal-players">
                <div className="player west">
                    {playersHands["West"] && playersHands["West"].map((card, index) => (
                        <div key={index} className="card rotated-left">
                            <img 
                                src={getCardImage(card)}
                                alt={card}
                                className="card-image"
                            />
                        </div>
                    ))}
                </div>

                {/* Pli actuel au centre */}
                <div className="current-trick">
                    {gameState.currentTrick.map((card, index) => (
                        <div key={index} className={`played-card position-${index}`}>
                            <img 
                                src={getCardImage(card)}
                                alt={card}
                                className="card-image"
                            />
                        </div>
                    ))}
                </div>

                <div className="player east">
                    {playersHands["East"] && playersHands["East"].map((card, index) => (
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

            {/* Main du joueur Sud (joueur humain) */}
            <div className="player south">
                {playersHands["South"] && playersHands["South"].map((card, index) => (
                    <button
                        key={index}
                        onClick={() => handleCardPlay(card)}
                        disabled={!gameState.playableCards.includes(card)}
                        className="card-button"
                    >
                        <img 
                            src={getCardImage(card)}
                            alt={card}
                            className="card-image hoverable"
                        />
                    </button>
                ))}
            </div>

            {gameState.trickWinner && (
                <div className="trick-winner">
                    Pli gagné par : {gameState.trickWinner}
                </div>
            )}
        </div>
    );
};

PlayingPhase.propTypes = {
    playersHands: PropTypes.object.isRequired,
    currentPlayer: PropTypes.string,
};

export default PlayingPhase;