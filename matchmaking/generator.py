from pprint import pprint
from copy import deepcopy
from typing import List, Tuple

from tqdm import tqdm
import numpy as np
from itertools import combinations, permutations, product

from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_avg_matchup_diversity_score

def get_most_diverse_matchups(players: List[Player], num_rounds: int, num_fields: int, num_iterations: int) -> Tuple[List[Matchup], float, dict]:

    best_scores = []
    best_score = 0
    best_matchup_config = None

    for _ in tqdm(range(num_iterations)):

        matchup_history = []
        matchups: List[str] = []
        for _ in range(num_rounds):
            
            #TODO: sample from all possible 4-player matchups and check if any player is already playing in the current round
            selected_players = np.random.choice(players, replace=False, size=4*num_fields).tolist()
            # print(selected_players)
            
            temp_matchups = []
            for j in range(num_fields):
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

        results, score = get_avg_matchup_diversity_score(matchups)
        # pprint(results)
        # print(value)
        
        if score > best_score:
            best_matchup_config = deepcopy(matchups)
            best_score = score
            best_scores.append(best_score)

    results, _ = get_avg_matchup_diversity_score(best_matchup_config)

    pprint(results)
    print(best_scores[-100:-1])

    print("=====================================")
    [print(f"{i} - {i%num_fields} - {x}") for i, x in enumerate(best_matchup_config)]
    print("matchup_diversity_score:", best_score)
    
    return best_matchup_config, best_score, results