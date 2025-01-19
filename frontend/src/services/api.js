import { API_BASE_URL } from '../config/constants';

export const gameService = {
    initialize: async () => {
        const response = await fetch(`${API_BASE_URL}/initialize`, {
            method: 'POST',
        });
        if (!response.ok) throw new Error('Failed to initialize game');
        return response.json();
    },

    fetchBiddingOptions: async (player) => {
        const response = await fetch(`${API_BASE_URL}/get_bidding_options?player=${player}`);
        if (!response.ok) throw new Error('Failed to fetch bidding options');
        return response.json();
    },

    sendBid: async (player, bid) => {
        const response = await fetch(`${API_BASE_URL}/bid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player, bid }),
        });
        if (!response.ok) throw new Error('Failed to send bid');
        return response.json();
    },

    getGameState: async () => {
        const response = await fetch(`${API_BASE_URL}/game_state`);
        if (!response.ok) throw new Error('Failed to fetch game state');
        return response.json();
    },

    playCard: async (player, card) => {
        const response = await fetch(`${API_BASE_URL}/play_card`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player, card }),
        });
        if (!response.ok) throw new Error('Failed to play card');
        return response.json();
    },

    getAnnonces: async () => {
        const response = await fetch(`${API_BASE_URL}/get_annonces`);
        if (!response.ok) throw new Error('Failed to fetch annonces');
        return response.json();
    }
}; 