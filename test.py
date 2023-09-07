from pprint import pprint

import numpy as np


from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_avg_game_distance

NUM_GAMES = 100

players = [Player("A"), Player("B"), Player("C"), Player("D"), Player("E"), Player("F"), Player("G"), Player("H")]

matchups = []
for i in range(NUM_GAMES):

    selected_players = np.random.choice(players, replace=False, size=4).tolist()

    matchups.append(Matchup.from_names(*selected_players))

results = get_avg_game_distance(matchups)
pprint(results)