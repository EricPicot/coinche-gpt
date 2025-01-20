import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { gameService } from '../services/api';
import './BiddingOptions.css';

const BiddingOptions = ({ player, options, updateAnnonces }) => {
    const [selectedValue, setSelectedValue] = useState(null);
    const [selectedSuit, setSelectedSuit] = useState(null);
    const [biddingPhaseOver, setBiddingPhaseOver] = useState(false);
    const [currentAnnonces, setCurrentAnnonces] = useState({});  // Ajout

    // Extraire les valeurs uniques des options
    const values = [...new Set(options.map(opt => opt.split(' ')[0]))];

    // Fonction pour obtenir les annonces actuelles
    const fetchCurrentAnnonces = async () => {
        try {
            const response = await gameService.getAnnonces();
            setCurrentAnnonces(response.annonces);
        } catch (error) {
            console.error('Error fetching annonces:', error);
        }
    };

    // Afficher les annonces dans l'ordre des joueurs
    const renderAnnonces = () => {
        const players = ['South', 'West', 'North', 'East'];
        return (
            <div className="current-annonces">
                <h4>Annonces en cours :</h4>
                <div className="annonces-list">
                    {players.map(playerName => (
                        <div key={playerName} className="annonce-entry">
                            <span className="player-name">{playerName}: </span>
                            <span className="player-bid">
                                {currentAnnonces[playerName] || '-'}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    const handleValueSelect = (value) => {
        setSelectedValue(value);
    };

    const handleSuitSelect = (suit) => {
        setSelectedSuit(suit);
    };

    const handleBidSubmit = async () => {
        if (!selectedValue || !selectedSuit) {
            return;
        }

        try {
            const bid = `${selectedValue} of ${selectedSuit}`;
            console.log('Sending bid:', { player, bid });
            const response = await gameService.sendBid(player, bid);
            console.log('Received response:', response);
            setSelectedValue(null);
            setSelectedSuit(null);
            setBiddingPhaseOver(response.bidding_phase_over);
            updateAnnonces(response.annonces, response.bidding_phase_over);
            await fetchCurrentAnnonces();  // Mettre à jour les annonces après l'envoi
        } catch (error) {
            console.error('Error placing bid:', error);
            setSelectedValue(null);
            setSelectedSuit(null);
        }
    };

    const handlePass = async () => {
        try {
            const response = await gameService.sendBid(player, 'pass');
            if (response.status === 'success') {
                setBiddingPhaseOver(response.bidding_phase_over);
                updateAnnonces(response.annonces, response.bidding_phase_over);
                await fetchCurrentAnnonces();  // Mettre à jour les annonces après le pass
            }
        } catch (error) {
            console.error('Error in handlePass:', error);
        }
    };

    return (
        <div className="bidding-options">
            {renderAnnonces()}  {/* Ajout de l'affichage des annonces */}
            
            <h3>Faites votre annonce</h3>
            
            <div className="bidding-container">
                <div className="values-section">
                    <h4>Valeur</h4>
                    <div className="bidding-buttons">
                        {values.map((value) => (
                            <button
                                key={value}
                                className={`bid-button ${selectedValue === value ? 'selected' : ''}`}
                                onClick={() => handleValueSelect(value)}
                            >
                                {value}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="suits-section">
                    <h4>Couleur</h4>
                    <div className="suit-buttons">
                        <button 
                            className={`suit-button hearts ${selectedSuit === 'hearts' ? 'selected' : ''}`}
                            onClick={() => handleSuitSelect('hearts')}
                        >
                            ♥
                        </button>
                        <button 
                            className={`suit-button diamonds ${selectedSuit === 'diamonds' ? 'selected' : ''}`}
                            onClick={() => handleSuitSelect('diamonds')}
                        >
                            ♦
                        </button>
                        <button 
                            className={`suit-button clubs ${selectedSuit === 'clubs' ? 'selected' : ''}`}
                            onClick={() => handleSuitSelect('clubs')}
                        >
                            ♣
                        </button>
                        <button 
                            className={`suit-button spades ${selectedSuit === 'spades' ? 'selected' : ''}`}
                            onClick={() => handleSuitSelect('spades')}
                        >
                            ♠
                        </button>
                    </div>
                </div>
            </div>

            <div className="action-buttons">
                <button 
                    className="submit-button"
                    onClick={handleBidSubmit}
                    disabled={!selectedValue || !selectedSuit}
                >
                    Annoncer
                </button>
                <button 
                    className="pass-button"
                    onClick={handlePass}
                >
                    Passer
                </button>
            </div>

            {selectedValue && selectedSuit && (
                <div className="current-selection">
                    Annonce sélectionnée : {selectedValue} of {selectedSuit}
                </div>
            )}
        </div>
    );
};

BiddingOptions.propTypes = {
    player: PropTypes.string.isRequired,
    options: PropTypes.arrayOf(PropTypes.string),
    updateAnnonces: PropTypes.func.isRequired,
};

export default BiddingOptions;