from pprint import pprint
from copy import deepcopy
from typing import List

from tqdm import tqdm
import numpy as np
from itertools import combinations, permutations, product

from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_avg_game_distance

NUM_ROUNDS = 6
NUM_FIELDS = 3

players = [
    Player("1"), 
    Player("2"), 
    Player("3"), 
    Player("4"), 
    Player("5"), 
    Player("6"), 
    Player("7"), 
    Player("8"),
    Player("9"),
    Player("10"),
    Player("11"),
    Player("12"),
    ]

NUM_ITERATIONS = 10000



best_values = []
best_value = 0
best_matchup_config = None

for i in tqdm(range(NUM_ITERATIONS)):

    matchup_history = []
    matchups: List[str] = []
    for i in range(NUM_ROUNDS):
        
        #TODO: sample from all possible 4-player matchups and check if any player is already playing in the current round
        selected_players = np.random.choice(players, replace=False, size=4*NUM_FIELDS).tolist()
        # print(selected_players)
        
        temp_matchups = []
        for j in range(NUM_FIELDS):
            four_players = selected_players[ j*4 : j*4 + 4 ]
            temp_matchups.append(Matchup.from_names(*four_players))
            
        valid = True
        for matchup in temp_matchups:
            if matchup.get_unique_identifier() in matchup_history:
                valid = False
                
        if valid == False:
            continue
            
        matchup_history += [x.get_unique_identifier() for x in temp_matchups]
        matchup_history = list(set(matchup_history))

        matchups += temp_matchups

    # print(matchups)

    results, value = get_avg_game_distance(matchups)
    # pprint(results)
    # print(value)
    
    if value > best_value:
        best_matchup_config = deepcopy(matchups)
        best_value = value
        best_values.append(best_value)


[print(f"{i} - {i%NUM_FIELDS} - {x}") for i, x in enumerate(best_matchup_config)]
print(best_values[-100:-1])
print(best_values)

print("=====================================")
results, value = get_avg_game_distance(best_matchup_config)
pprint(results)