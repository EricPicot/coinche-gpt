<template>
  <div v-if="gameOver" class="game-over-screen">
    <h2>Partie terminée !</h2>
    
    <div class="scores">
      <div class="team">
        <h3>Équipe Nord-Sud</h3>
        <p>{{ finalScore.NS }} points</p>
      </div>
      
      <div class="team">
        <h3>Équipe Est-Ouest</h3>
        <p>{{ finalScore.EW }} points</p>
      </div>
    </div>
    
    <div class="contract-result">
      <p>
        Contrat de {{ contract.value }} à {{ contract.suit }} 
         par {{ contract.holder }}:
        <span :class="{ 'success': contractMade, 'failure': !contractMade }">
          {{ contractMade ? ' Réussi' : ' Chuté' }}
        </span>
      </p>
    </div>
    
    <button @click="resetGame" class="reset-button">
      Nouvelle partie
    </button>
  </div>
</template>

<script>
export default {
  name: 'GameOverScreen',
  
  data() {
    return {
      gameOver: false,
      finalScore: { NS: 0, EW: 0 },
      contract: {
        value: 0,
        holder: '',
        suit: ''
      },
      contractMade: false
    }
  },
  
  methods: {
    async checkGameStatus() {
      try {
        const response = await fetch('/api/game_status')
        const data = await response.json()
        
        this.gameOver = data.game_over
        if (this.gameOver) {
          this.finalScore = data.final_score
          this.contract = data.contract
          this.contractMade = data.contract_made
        }
      } catch (error) {
        console.error('Error checking game status:', error)
      }
    },
    
    async resetGame() {
      try {
        await fetch('/api/reset_game', { method: 'POST' })
        this.$emit('game-reset')
      } catch (error) {
        console.error('Error resetting game:', error)
      }
    }
  },
  
  mounted() {
    this.checkGameStatus()
  }
}
</script>

<style scoped>
.game-over-screen {
  text-align: center;
  padding: 2rem;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 2rem auto;
  max-width: 600px;
}

.scores {
  display: flex;
  justify-content: space-around;
  margin: 2rem 0;
}

.team {
  padding: 1rem;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.contract-result {
  margin: 2rem 0;
}

.success {
  color: green;
  font-weight: bold;
}

.failure {
  color: red;
  font-weight: bold;
}

.reset-button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: background 0.3s;
}

.reset-button:hover {
  background: #45a049;
}
</style> 