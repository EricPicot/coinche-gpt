import React from 'react';
import PropTypes from 'prop-types';
import './BiddingSummary.css';

const BiddingSummary = ({ annonces, onStartGame }) => {
    console.log('BiddingSummary rendered with annonces:', annonces); // Log pour déboguer
    return (
        <div className="bidding-summary">
            <h2>Récapitulatif des Annonces</h2>
            <div className="annonces-grid">
                <div className="player-annonce north">
                    <h3>Nord</h3>
                    <p>{annonces["North"] || "Passe"}</p>
                </div>
                <div className="player-annonce west">
                    <h3>Ouest</h3>
                    <p>{annonces["West"] || "Passe"}</p>
                </div>
                <div className="player-annonce east">
                    <h3>Est</h3>
                    <p>{annonces["East"] || "Passe"}</p>
                </div>
                <div className="player-annonce south">
                    <h3>Sud</h3>
                    <p>{annonces["South"] || "Passe"}</p>
                </div>
            </div>
            <button className="start-game-button" onClick={onStartGame}>
                Commencer le jeu
            </button>
        </div>
    );
};

BiddingSummary.propTypes = {
    annonces: PropTypes.object.isRequired,
    onStartGame: PropTypes.func.isRequired,
};

export default BiddingSummary; 