from typing import List, Tuple
import statistics
from collections import Counter

import numpy as np

from matchmaking.data import Matchup, Team, Player

def _find_consecutive_numbers(arr, target_number: int):
    lengths = []
    length = 0
    
    for num in arr:
        if num == target_number:
            length += 1
        else:
            if length > 0:
                lengths.append(length)
            length = 0
            
    # Account for a trailing sequence of target_number
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
    enemy_player_uids = []
    for matchup in matchups:
        enemy_team = matchup.get_enemy_team(player_uid)
        
        if enemy_team is not None:
            enemy_team_uid = enemy_team.get_unique_identifier()
            enemy_team_uids.append(enemy_team_uid)
            enemy_player_uids.extend(enemy_team.get_all_player_uids())

    return enemy_team_uids, enemy_player_uids

#TODO: fix break calculation for multiple fields
#TODO: find a way to incorporate time between breaks as metric (matchup_lengths_played_between_breaks)
#TODO: optimize for 5 and 6 players (most common normal player counts for single net)
def get_avg_matchup_diversity_score(matchups: List[Matchup], num_players: int, weights_and_metrics: List[Tuple[float, str]]) -> int:
    
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
        break_lengths = _find_consecutive_numbers(played_matches, 0)
        matchup_lengths_played_between_breaks = _find_consecutive_numbers(played_matches, 1)
        
        teammates = _get_teammates(matchups, player_uid)
        consecutive_teammates_hist = _count_consecutive_occurences(teammates)
        
        enemies, enemy_players = _get_enemy_teams(matchups, player_uid)
        consecutive_enemies_hist = _count_consecutive_occurences(enemies)
        # print(break_lengths)
        
        unique_people_played_with_or_against = list(set(enemy_players + teammates))
        
        break_lengths_stdev = statistics.stdev(break_lengths) if len(break_lengths) > 1 else 0.0
        
        # only take second length if available, otherwise set to 10.0
        matchup_lengths_played_between_breaks_second_length = matchup_lengths_played_between_breaks[1] if len(matchup_lengths_played_between_breaks) > 1 else 10.0
        
        teammate_hist = Counter(teammates)
        
        teammate_hist_stdev = statistics.stdev(list(teammate_hist.values())) if len(teammate_hist) > 1 else 0.0
        
        enemy_teams_hist = Counter(enemies)
        
        enemy_teams_hist_stdev = statistics.stdev(list(enemy_teams_hist.values())) if len(enemy_teams_hist) > 1 else 0.0
        
        results[player_uid] = {
            "num_played_matches": sum(played_matches),
            "break_lengths_avg": np.mean(break_lengths), 
            "break_lengths_stdev": break_lengths_stdev, 
            "break_lengths_hist": Counter(break_lengths),
            "matchup_lengths_played_between_breaks_second_length": matchup_lengths_played_between_breaks_second_length, # optimized for short sessions
            "matchup_lengths": matchup_lengths_played_between_breaks,
            "teammate_hist": teammate_hist,
            "teammate_hist_stdev": teammate_hist_stdev,
            "enemy_teams_hist": enemy_teams_hist,
            "enemy_teams_hist_stdev": enemy_teams_hist_stdev,
            "consectuve_teammates_hist": consecutive_teammates_hist,
            "consecutive_enemies_hist": consecutive_enemies_hist,
            "consecutive_teammates_total": sum(list(consecutive_teammates_hist.values())),
            "consecutive_enemies_total": sum(list(consecutive_enemies_hist.values())),
            "unique_people_played_with_or_against": len(unique_people_played_with_or_against),
            "unique_people_not_played_with_or_against": (num_players - 1) - len(unique_people_played_with_or_against),
            }
               
    # calculate std dev of results (shows how fair the playtime distribution is)
    
    global_not_playing_players_index = num_players - len(unique_players)
    
    global_num_played_matches = [results[x]["num_played_matches"] for x in results.keys()]
    global_played_matches_index = statistics.stdev(global_num_played_matches)
    
    global_break_lengths_stdev = [results[x]["break_lengths_stdev"] for x in results.keys()]
    global_break_occurrence_index = sum(global_break_lengths_stdev)
    
    global_per_player_break_lengths_avg = [results[x]["break_lengths_avg"] for x in results.keys()]
    global_per_player_break_lengths_avg_squared = [x**2 for x in global_per_player_break_lengths_avg]
    global_break_shortness_index = sum(global_per_player_break_lengths_avg_squared)
    
    per_player_matchup_length_second_element = [results[x]["matchup_lengths_played_between_breaks_second_length"] for x in results.keys()]
    global_matchup_length_index = statistics.stdev(per_player_matchup_length_second_element)
    
    per_player_teammate_hist_stdev = [results[x]["teammate_hist_stdev"] for x in results.keys()]
    global_teammate_variety_index = sum(per_player_teammate_hist_stdev)
    
    per_player_enemy_teams_hist_stdev = [results[x]["enemy_teams_hist_stdev"] for x in results.keys()]
    global_enemy_team_variety_index = sum(per_player_enemy_teams_hist_stdev)
    
    per_player_consecutive_teammates_amount = [results[x]["consecutive_teammates_total"] for x in results.keys()]
    global_teammate_succession_index = sum(per_player_consecutive_teammates_amount)
    
    per_player_consecutive_enemies_amount = [results[x]["consecutive_enemies_total"] for x in results.keys()]
    global_enemy_team_succession_index = sum(per_player_consecutive_enemies_amount)
    
    per_player_unique_people_not_played_with_or_against = [results[x]["unique_people_not_played_with_or_against"] for x in results.keys()]
    global_player_engagement_index = sum(per_player_unique_people_not_played_with_or_against)
    global_player_engagement_fairness_index = statistics.stdev(per_player_unique_people_not_played_with_or_against)
        
    # TODO: calculate entropy, energy or something similar to quantify how good the variety of matchups played is
    
    global_results = {
        "global_not_playing_players_index": global_not_playing_players_index,
        "global_played_matches_index": global_played_matches_index,
        "global_matchup_length_index": global_matchup_length_index,
        "global_break_occurrence_index": global_break_occurrence_index,
        "global_break_shortness_index": global_break_shortness_index,
        "global_teammate_variety_index": global_teammate_variety_index,
        "global_enemy_team_variety_index": global_enemy_team_variety_index,
        "global_teammate_succession_index": global_teammate_succession_index,
        "global_enemy_team_succession_index": global_enemy_team_succession_index,
        "global_player_engagement_index": global_player_engagement_index,
        "global_player_engagement_fairness_index": global_player_engagement_fairness_index,
        }

    loss = 0.0
    
    for weight, attribute_key in weights_and_metrics:
        loss += weight * global_results[attribute_key]
    
    results["global"] = global_results
    
    return results, loss
        
