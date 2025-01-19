import React from 'react';
import { gameService } from '../services/api';

const GameOverScreen = ({ onReset }) => {
    const [gameStatus, setGameStatus] = React.useState(null);

    React.useEffect(() => {
        const fetchGameStatus = async () => {
            try {
                const status = await gameService.getGameStatus();
                setGameStatus(status);
            } catch (error) {
                console.error('Error fetching game status:', error);
            }
        };

        fetchGameStatus();
    }, []);

    if (!gameStatus) return null;

    return (
        <div className="game-over-screen">
            <h2>Partie terminée !</h2>
            
            <div className="scores">
                <div className="team">
                    <h3>Équipe Nord-Sud</h3>
                    <p>{gameStatus.final_score.NS} points</p>
                </div>
                
                <div className="team">
                    <h3>Équipe Est-Ouest</h3>
                    <p>{gameStatus.final_score.EW} points</p>
                </div>
            </div>
            
            <div className="contract-result">
                <p>
                    Contrat de {gameStatus.contract.value} à {gameStatus.contract.suit}
                    par {gameStatus.contract.holder}:
                    <span className={gameStatus.contract_made ? 'success' : 'failure'}>
                        {gameStatus.contract_made ? ' Réussi' : ' Chuté'}
                    </span>
                </p>
            </div>
            
            <button onClick={onReset} className="reset-button">
                Nouvelle partie
            </button>
        </div>
    );
};

export default GameOverScreen; 