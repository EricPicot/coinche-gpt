import React, { useState, useEffect } from 'react';
import CardTable from './CardTable';
import BiddingOptions from './BiddingOptions';
import BiddingSummary from './BiddingSummary';
import PlayingPhase from './PlayingPhase';
import { gameService } from '../services/api';
import { POLLING_INTERVAL } from '../config/constants';
import GameOverScreen from './GameOverScreen';


const InitializeGame = () => {
    const [gameState, setGameState] = useState({
        playersHands: null,
        biddingOptions: [],
        biddingPhaseOver: false,
        annonces: {},
        playedCard: null,
        isInitialized: false,
        playingPhaseStarted: false
    });
    const [gameOver, setGameOver] = useState(false);


    const handleInitialize = async () => {
        try {
            const data = await gameService.initialize();
            console.log('Initialize response:', data); // Debug log
            setGameState(prevState => ({
                ...prevState,
                playersHands: data.players_hands,
                biddingOptions: data.bidding_options,
                isInitialized: true
            }));
        } catch (error) {
            console.error('Error initializing game:', error);
        }
    };

    const updateAnnonces = (newAnnonces, biddingOver) => {
        console.log('Updating annonces:', newAnnonces, 'bidding over:', biddingOver); // Debug log
        setGameState(prevState => ({
            ...prevState,
            annonces: newAnnonces,
            biddingPhaseOver: biddingOver
        }));
    };

    const handleStartGame = () => {
        console.log('Starting game phase'); // Debug log
        setGameState(prevState => ({
            ...prevState,
            playingPhaseStarted: true
        }));
    };
    const handleReset = async () => {
        try {
            await gameService.resetGame(); // Appel au backend pour réinitialiser
            setGameOver(false); // Réinitialise l'état de fin de partie
            setGameState({ // Réinitialise l'état du jeu
                playersHands: null,
                biddingOptions: [],
                biddingPhaseOver: false,
                annonces: {},
                playedCard: null,
                isInitialized: false,
                playingPhaseStarted: false
            });
            handleInitialize(); // Réinitialise le jeu
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    };
    useEffect(() => {
        if (gameState.isInitialized && !gameState.playingPhaseStarted) {
            const fetchGameState = async () => {
                try {
                    const biddingOptions = await gameService.fetchBiddingOptions('South');
                    console.log('Fetched bidding options:', biddingOptions); // Debug log
                    
                    setGameState(prevState => ({
                        ...prevState,
                        biddingOptions: biddingOptions.options,
                        biddingPhaseOver: biddingOptions.bidding_phase_over,
                        annonces: biddingOptions.annonces
                    }));
                } catch (error) {
                    console.error('Error fetching game state:', error);
                }
            };

            fetchGameState();
            const interval = setInterval(fetchGameState, POLLING_INTERVAL);
            return () => clearInterval(interval);
        }
    }, [gameState.isInitialized, gameState.playingPhaseStarted]);

    console.log('Current game state:', gameState); // Debug log

        // Nouveau useEffect pour vérifier la fin de partie
        useEffect(() => {
            if (gameState.playingPhaseStarted) {
                const checkGameStatus = async () => {
                    try {
                        const status = await gameService.getGameStatus();
                        console.log('Game status received:', status); // Debug log
                        if (status && status.game_over) {
                            setGameOver(true);
                        }
                    } catch (error) {
                        console.error('Error checking game status:', error);
                        // Optionnel : arrêter le polling en cas d'erreur
                        // clearInterval(interval);
                    }
                };
        
                // Faire une première vérification immédiate
                checkGameStatus();
                
                const interval = setInterval(checkGameStatus, POLLING_INTERVAL);
                return () => clearInterval(interval);
            }
        }, [gameState.playingPhaseStarted]);

        return (
            <div>
                <h1>Initialize Game</h1>
                {gameOver ? (
                    <GameOverScreen onReset={handleReset} />
                ) : (
                    <>
                        {!gameState.isInitialized && (
                            <button onClick={handleInitialize}>Initialize Game</button>
                        )}
                        
                        {gameState.isInitialized && (
                            <div>
                                {!gameState.playingPhaseStarted && (
                                    <CardTable 
                                        playersHands={gameState.playersHands} 
                                        annonces={gameState.annonces} 
                                        biddingPhaseOver={gameState.biddingPhaseOver}
                                    />
                                )}
                                
                                {gameState.biddingPhaseOver && !gameState.playingPhaseStarted && (
                                    <BiddingSummary 
                                        annonces={gameState.annonces}
                                        onStartGame={handleStartGame}
                                    />
                                )}
                                
                                {!gameState.biddingPhaseOver && !gameState.playingPhaseStarted && (
                                    <BiddingOptions 
                                        player="South" 
                                        options={gameState.biddingOptions}
                                        updateAnnonces={updateAnnonces}
                                    />
                                )}
        
                                {gameState.playingPhaseStarted && (
                                    <PlayingPhase 
                                        playersHands={gameState.playersHands}
                                        currentPlayer="South"
                                    />
                                )}
                            </div>
                        )}
                    </>
                )}
            </div>
        );
    };

export default InitializeGame;