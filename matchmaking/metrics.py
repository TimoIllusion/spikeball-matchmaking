from typing import List
import statistics
from collections import Counter

from matchmaking.data import Matchup, Team, Player

def _find_consecutive_zeros(arr):
    lengths = []
    length = 0
    
    for num in arr:
        if num == 0:
            length += 1
        else:
            if length > 0:
                lengths.append(length)
            length = 0
            
    # Account for a trailing sequence of zeros
    if length > 0:
        lengths.append(length)
        
    return lengths

def _get_teammates(matchups: List[Matchup], player_uid: str) -> List[str]:
    teammates = []
    
    for matchup in matchups:
        if player_uid in matchup.get_all_player_uids():
            teammate = matchup.get_teammate(player_uid)
            
            if teammate is not None:
                teammate_uid = teammate.get_unique_identifier()
                teammates.append(teammate_uid)
            
    return teammates

def _count_consecutive_occurences(list_of_symbols: List[str]) -> Counter:
    temp_counter = 0
    counter = Counter()
    for i in range(len(list_of_symbols)):
        if i == 0:
            continue
        
        if list_of_symbols[i] == list_of_symbols[i-1]:
            temp_counter += 1
        else:
            counter[list_of_symbols[i-1]] += temp_counter
            temp_counter = 0
            
    return counter
            

def _get_enemy_teams(matchups: List[Matchup], player_uid: str) -> List[str]:
    
    enemy_team_uids = []
    for matchup in matchups:
        enemy_team = matchup.get_enemy_team(player_uid)
        
        if enemy_team is not None:
            enemy_team_uid = enemy_team.get_unique_identifier()
            enemy_team_uids.append(enemy_team_uid)

    return enemy_team_uids


def get_avg_matchup_diversity_score(matchups: List[Matchup]) -> int:
    
    # get unique player identifiers
    players = []
    for matchup in matchups:
        players += matchup.get_all_player_uids()
        
    unique_players = list(set(players))
    # print(unique_players)
    
    # search for distances between games for each player, basically calculating the average distance between games for each player
    
    results = {}
    for player_uid in unique_players:
        played_matches = [player_uid in x.get_all_player_uids() for x in matchups]
        break_lengths = _find_consecutive_zeros(played_matches)
        
        teammates = _get_teammates(matchups, player_uid)
        consecutive_teammates = _count_consecutive_occurences(teammates)
        
        enemies = _get_enemy_teams(matchups, player_uid)
        consecutive_enemies = _count_consecutive_occurences(enemies)
        # print(break_lengths)
        
        results[player_uid] = {
            "num_played_matches": sum(played_matches),
            "break_lengths_avg": statistics.mean(break_lengths), 
            "break_lengths_stdev": statistics.stdev(break_lengths), 
            "break_lengths_hist": Counter(break_lengths),
            "teammate_hist": Counter(teammates),
            "enemy_teams_hist": Counter(enemies),
            "consectuve_teammates_hist": consecutive_teammates,
            "consecutive_enemies_hist": consecutive_enemies,
            }
               
    # calculate std dev of results (shows how fair the playtime distribution is)
    
    global_results = {}
    
    global_results["num_played_matches_stdev"] = statistics.stdev([results[x]["num_played_matches"] for x in results.keys()])
    
    global_results["acc_break_lengths_stdev"] = sum([results[x]["break_lengths_stdev"] for x in results.keys()])
    
    global_results["per_player_squared_break_lengths_avg"] = sum([results[x]["break_lengths_avg"] ** 2 for x in results.keys()])
    
    global_results["acc_teammate_hist_stdev"] = sum([statistics.stdev(list(results[x]["teammate_hist"].values())) for x in results.keys() if len(results[x]["teammate_hist"].values()) > 1])
    
    global_results["acc_enemy_teams_hist_stdev"] = sum([statistics.stdev(list(results[x]["enemy_teams_hist"].values())) for x in results.keys() if len(results[x]["enemy_teams_hist"].values()) > 1])
    
    global_results["acc_consecutive_teammates_amount"] = sum([sum(list(results[x]["consectuve_teammates_hist"].values())) for x in results.keys()])
    
    global_results["acc_consecutive_enemies_amount"] = sum([sum(list(results[x]["consecutive_enemies_hist"].values())) for x in results.keys()])
        
    # TODO: calculate entropy, energy or something similar to quantify how good the variety of matchups played is
    
    weights_and_metrics = [
        (10.0, "num_played_matches_stdev"),
        (0.0, "acc_break_lengths_stdev"),
        (0.0, "per_player_squared_break_lengths_avg"),
        (5.0, "acc_teammate_hist_stdev"),
        (5.0, "acc_enemy_teams_hist_stdev"),
        (10.0, "acc_consecutive_teammates_amount"),
        (10.0, "acc_consecutive_enemies_amount"),
        ]

    loss = 0.0
    
    for weight, attribute_key in weights_and_metrics:
        loss += weight * global_results[attribute_key]
    
    results["global"] = global_results
    
    return results, loss
        
