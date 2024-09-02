import psutil

NUM_ITERATIONS = 10000
NUM_ROUNDS = 10
NUM_FIELDS = 3

PLAYER_NAMES = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
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
    (5.0, "global_break_occurrence_index"),  # 0.0-5.0
    (5.0, "global_break_shortness_index"),  # 0.0-5.0
]

WORKERS = psutil.cpu_count()
