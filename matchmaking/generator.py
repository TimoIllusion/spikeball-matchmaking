from pprint import pprint
from copy import deepcopy
from typing import List, Tuple

from tqdm import tqdm
import numpy as np

from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_avg_matchup_diversity_score

#TODO: split in subfunctions and clean up
def get_most_diverse_matchups(players: List[Player], num_rounds: int, num_fields: int, num_iterations: int, weights_and_metrics: List[Tuple[float, str]]) -> Tuple[List[Matchup], float, dict]:

    #TODO: make configurable from outside
    weights_and_metrics = [
        (100000.0, "global_not_playing_players_index"),
        (10000.0, "global_played_matches_index"),
        (10.0, "global_teammate_succession_index"),
        (10.0, "global_enemy_team_succession_index"),
        (5.0, "global_teammate_variety_index"),
        (5.0, "global_enemy_team_variety_index"),
        (0.0, "global_break_occurence_index"), # 0.0-5.0
        (0.0, "global_break_shortness_index"), # 0.0-5.0
        ]

    best_scores = []
    min_score = np.inf
    best_matchup_config = None

    for _ in tqdm(range(num_iterations)):

        matchup_history = []
        matchups: List[str] = []
        for r in range(num_rounds):
            # print("Round " + str(r + 1))
            
            invalid = True
            while invalid:
                
                # print("try")
            
                #TODO: sample from all possible 4-player matchups and check if any player is already playing in the current round
                selected_players = np.random.choice(players, replace=False, size=4*num_fields).tolist()
                # print(selected_players)
                
                temp_matchups = []
                for j in range(num_fields):
                    four_players = selected_players[ j*4 : j*4 + 4 ]
                    temp_matchups.append(Matchup.from_names(*four_players))
                    
                invalid = False
                for matchup in temp_matchups:
                    if matchup.get_unique_identifier() in matchup_history:
                        invalid = True
        
                
            matchup_history += [x.get_unique_identifier() for x in temp_matchups]
            matchup_history = list(set(matchup_history))

            matchups += temp_matchups

        # print(matchups)

        results, score = get_avg_matchup_diversity_score(matchups, len(players), weights_and_metrics)
        # pprint(results)
        # print(value)
        
        if score < min_score:
            best_matchup_config = deepcopy(matchups)
            min_score = score
            best_scores.append(min_score)
            print("Got new minimal index: ", min_score)

    results, _ = get_avg_matchup_diversity_score(best_matchup_config, len(players), weights_and_metrics)

    pprint(results)
    print(best_scores)

    print("=====================================")
    [print(f"{i} - {i%num_fields} - {x}") for i, x in enumerate(best_matchup_config)]
    print("matchup_diversity_index (lower is better):", min_score)
    
    return best_matchup_config, min_score, results