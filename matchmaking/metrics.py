from typing import List


from matchmaking.data import Matchup, Team, Player


def get_avg_game_distance(matchups: List[Matchup]) -> int:
    
    
    players = []
    for matchup in matchups:
        
        team_a, team_b = matchup.get_teams()
        
        players.append(team_a.player_1)
        players.append(team_a.player_2)
        players.append(team_b.player_1)
        players.append(team_b.player_2)
        
    players = list(set(players))
    print(players)