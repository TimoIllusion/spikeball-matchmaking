from matchmaking.data import Player
from matchmaking.generator import get_most_diverse_matchups
from matchmaking.utils import export_to_excel

def main():
    NUM_ITERATIONS = 100000
    NUM_ROUNDS = 10
    NUM_FIELDS = 1

    players = [
        Player("A"),
        Player("B"),
        Player("C"),
        Player("D"),
        Player("E"),
        Player("F"),
        Player("G"),
        Player("H"),
        Player("I"),
        Player("J"),
        Player("K"),
        ]
    
    WEIGHT_METRIC_CONFIG = [
        (100000.0, "global_not_playing_players_index"),
        (10000.0, "global_played_matches_index"),
        (100.0, "global_matchup_length_index"),
        (10.0, "global_player_engagement_fairness_index"),
        (10.0, "global_teammate_succession_index"),
        (10.0, "global_enemy_team_succession_index"),
        (5.0, "global_player_engagement_index"),
        (5.0, "global_teammate_variety_index"),
        (5.0, "global_enemy_team_variety_index"),
        (5.0, "global_break_occurrence_index"), # 0.0-5.0
        (5.0, "global_break_shortness_index"), # 0.0-5.0
        ]
    
    best_matchup_config, best_score, results = get_most_diverse_matchups(players, NUM_ROUNDS, NUM_FIELDS, NUM_ITERATIONS, WEIGHT_METRIC_CONFIG)
    
    export_to_excel(best_matchup_config, players, NUM_FIELDS, f'output/matchups_with_points_and_format_pl{len(players)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_score:.3f}.xlsx')

if __name__ == "__main__":
   main()