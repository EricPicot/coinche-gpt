import { API_BASE_URL } from '../config/constants';

export const gameService = {
    initialize: async () => {
        const response = await fetch(`${API_BASE_URL}/initialize`, {
            method: 'POST',
        });
        if (!response.ok) throw new Error('Failed to initialize game');
        return response.json();
    },
    async playCard(player, card) {
        try {
            console.log('1. Card received in playCard:', card);
            const normalizedCard = card.toLowerCase();
            console.log('2. Card after normalization:', normalizedCard);
            
            const requestBody = JSON.stringify({ player, card: normalizedCard });
            console.log('3. Request body:', requestBody);
            
            const response = await fetch(`${API_BASE_URL}/play_card`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: requestBody
            });
    
            
            console.log('4. Response status:', response.status);
            const data = await response.json();
            console.log('5. Response data:', data); // Vérifions que trick_starter et atout_suit sont présents

            if (!response.ok) {
                console.log('6. Error response:', data);
                throw new Error(data.error || 'Failed to play card');
            }

            return data;
        } catch (error) {
            console.error('7. Error in playCard:', error);
            throw error;
        }
    },
    fetchBiddingOptions: async (player) => {
        const response = await fetch(`${API_BASE_URL}/get_bidding_options?player=${player}`);
        if (!response.ok) throw new Error('Failed to fetch bidding options');
        return response.json();
    },

    sendBid: async (player, bid) => {
        try {
            console.log('Sending bid request:', { player, bid });
            const response = await fetch(`${API_BASE_URL}/bid`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({ player, bid }),
            });
            
            console.log('Bid response status:', response.status);
            const data = await response.json();
            console.log('Bid response data:', data);
            
            if (!response.ok) {
                console.error('Bid error:', data);
                throw new Error(data.error || 'Failed to send bid');
            }
            
            return data;
        } catch (error) {
            console.error('Error in sendBid:', error);
            throw error;
        }
    },

    getGameState: async () => {
        const response = await fetch(`${API_BASE_URL}/game_state`);
        if (!response.ok) throw new Error('Failed to fetch game state');
        return response.json();
    },

    getAnnonces: async () => {
        const response = await fetch(`${API_BASE_URL}/get_annonces`);
        if (!response.ok) throw new Error('Failed to fetch annonces');
        return response.json();
    },

    nextTrick: async () => {
        console.log('Calling next trick API...');  // Ajout de log
        const response = await fetch(`${API_BASE_URL}/next_trick`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to start next trick');
        }
        
        return response.json();
    },

    getGameStatus: async () => {
        const response = await fetch(`${API_BASE_URL}/game_status`);
        if (!response.ok) {
            throw new Error('Failed to fetch game status');
        }
        return response.json();
    },

    resetGame: async () => {
        const response = await fetch(`${API_BASE_URL}/reset_game`, {
            method: 'POST'
        });
        if (!response.ok) {
            throw new Error('Failed to reset game');
        }
        return response.json();
    }

};