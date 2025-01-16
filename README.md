# Coinche R.O.

Coinche is a game card.


[Here](https://ibelote.com/en/rules-coinche.php) are the rules. The coinche is played between two teams of two players using a set of 32 classic cards (8 cards of each color - tile, clover, heart and spades). La Coinche is a strategic game similar to the Bridge. In Coinche, players must evaluate their hands and estimate the number of points they think they can reach in the game. Players make contracts and the ads have a major role in the game.

A round of Coinche could be divided into two distinct parts:
- First, given their hand, players propose a contrat (number of points to do + the suit)
- Secondly, the players play heigh tricks

For non-French, here are some imilar Games:
	•	Portugal: Sueca – Trick-taking game with a trump suit and team play.
	•	England: Whist – Classic trick-taking, though simpler, without bidding; Knaves Dial – A game with a bidding phase and trump suit, more similar to Coinche.
	•	United States: Pinochle – A complex trick-taking game with trump suits, bidding, and melds, similar to Coinche and Belote.

All these games involve strategic thinking, teamwork, and the use of a trump suit, making them appealing to those who enjoy the mechanics of Coinche.

## Objectives of the project

We want to apply a Large Language Model (LLM) Agent to Coinche. **To begin, we'll focus on both phases of a round: the bidding phase (called "annonce") and after the playing phase. Players will be provided their eight cards and will participate in the bidding process to establish a contract.**

The LLM Agent will then have to learn the rules and some strategies for both phases.

One of the issues that we are facing is the possibility of the LLM Agent making an invalid move given the context. To prevent such situations, we chose to deliver as output of the LLM Agent a vector of probabilities rather than a specific action. Therefore, if the LLM Agent favors an action that can't be performed, the gym environment will mask the invalid moves and select the highest probability action favored by the LLM Agent.

We will use OpenAI Gym to create a custom environment for Coinche, ensuring that the LLM Agent can interact with the game in a structured manner. This environment will handle the game logic, enforce the rules, and provide feedback to the LLM Agent to facilitate learning and improvement.


## Installations

### Prerequisites:

At this stage of the project, you need to have an OPENAI API key. (in the future, I want to be more agnostic to the llms)

### Set up

#### Creation of a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
#### Set up of Reac

```bash
cd frontend
npm install
```

#### Set up of open-ai credentials

- create a file called `.env` at the root of the project
- add the following lines to the file:
```OPENAI_API_KEY=YOUR_API_KEY```

## Launch the project

In the first terminal, run:
```python run.py```

In a second terminal, run:

```bash
cd frontend
npm start
```

## Game
### Steps of the Game
TODO

### Performances
TODO

## License
[C.R.O.](https://fr.wikipedia.org/wiki/Coinche)

