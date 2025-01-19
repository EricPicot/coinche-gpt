import React, { useState, useEffect } from 'react';
import CardTable from './CardTable';
import BiddingOptions from './BiddingOptions';
import BiddingSummary from './BiddingSummary';
import PlayingPhase from './PlayingPhase';
import { gameService } from '../services/api';
import { POLLING_INTERVAL } from '../config/constants';

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

    return (
        <div>
            <h1>Initialize Game</h1>
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
        </div>
    );
};

export default InitializeGame;