from matchmaking.data import Player
from matchmaking.generator import get_most_diverse_matchups


def test_matchup_generation():

    # TODO: fix random seed of numpy and random python module

    players = [
        Player("A"),
        Player("B"),
        Player("C"),
        Player("D"),
        Player("E"),
        Player("F"),
    ]

    num_rounds = 10
    num_fields = 1
    num_iterations = 100

    metric_config = [
        (100000.0, "global_not_playing_players_index"),
        (10000.0, "global_played_matches_index"),
        (100.0, "global_matchup_length_index"),
        (10.0, "global_player_engagement_fairness_index"),
        (10.0, "global_teammate_succession_index"),
        (10.0, "global_enemy_team_succession_index"),
        (5.0, "global_player_engagement_index"),
        (5.0, "global_teammate_variety_index"),
        (5.0, "global_enemy_team_variety_index"),
        (5.0, "global_break_occurrence_index"),  # 0.0-5.0
        (5.0, "global_break_shortness_index"),  # 0.0-5.0
    ]

    best_matchup_config, best_score, results = get_most_diverse_matchups(
        players, num_rounds, num_fields, num_iterations, metric_config
    )

    assert len(best_matchup_config) > 0
