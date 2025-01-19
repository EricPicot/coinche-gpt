import React from 'react';
import PropTypes from 'prop-types';
import './CardTable.css';

const CardTable = ({ playersHands, annonces = {}, biddingPhaseOver }) => {
    const getCardImage = (card) => {
        const [value, suit] = card.split(' of ');
        return `/cards/${value}_of_${suit}.png`;
    };
    console.log('biddingPhaseOver:', `${biddingPhaseOver}`);

    return (
        <div className="card-table">
            {playersHands && (
                <>
                    <div className="player north">
                        {!biddingPhaseOver && annonces["North"] && (
                            <div className="annonce">{annonces["North"]}</div>
                        )}
                        {playersHands["North"] && playersHands["North"].map((card, index) => (
                            <div key={index} className="card">
                                <img 
                                    src={getCardImage(card)}
                                    alt={card}
                                    className="card-image rotated"
                                />
                            </div>
                        ))}
                    </div>

                    <div className="player west">
                        {!biddingPhaseOver && annonces["West"] && (
                            <div className="annonce">{annonces["West"]}</div>
                        )}
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

                    <div className="player east">
                        {!biddingPhaseOver && annonces["East"] && (
                            <div className="annonce">{annonces["East"]}</div>
                        )}
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

                    <div className="player south">
                        {!biddingPhaseOver && annonces["South"] && (
                            <div className="annonce">{annonces["South"]}</div>
                        )}
                        {playersHands["South"] && playersHands["South"].map((card, index) => (
                            <div key={index} className="card">
                                <img 
                                    src={getCardImage(card)}
                                    alt={card}
                                    className="card-image"
                                />
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
};

CardTable.propTypes = {
    playersHands: PropTypes.object,
    annonces: PropTypes.object,
    biddingPhaseOver: PropTypes.bool,
};

CardTable.defaultProps = {
    annonces: {},
    biddingPhaseOver: false,
};

export default CardTable;