from typing import List
import statistics
from collections import Counter


from matchmaking.data import Matchup, Team, Player

def find_consecutive_zeros(arr):
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

def get_avg_game_distance(matchups: List[Matchup]) -> int:
    
    # get unique player identifiers
    players = []
    for matchup in matchups:
        players += matchup.get_all_player_uids()
        
    unique_players = list(set(players))
    print(unique_players)
    
    # search for distances between games for each player, basically calculating the average distance between games for each player
    
    results = {}
    for player_uid in unique_players:
        played_matches = [player_uid in x.get_all_player_uids() for x in matchups]

        break_lengths = find_consecutive_zeros(played_matches)
        
        print(break_lengths)
        
        results[player_uid] = {
            "num_played_matches": sum(played_matches),
            "break_lengths_avg": statistics.mean(break_lengths), 
            "break_lengths_stdev": statistics.stdev(break_lengths), 
            "break_lengths_hist": Counter(break_lengths)
            }
               
    # calculate std dev of results (shows how fair the playtime distribution is)
    results["global"] = {
        "num_played_matches_stdev": statistics.stdev([results[x]["num_played_matches"] for x in results.keys()])
        }
    
    # TODO: calculate entropy, energy or something similar to quantify how good the variety of matchups played is
    
    return results
        