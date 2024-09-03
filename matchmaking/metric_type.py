from enum import Enum


class MetricType(Enum):
    GLOBAL_NOT_PLAYING_PLAYERS_INDEX = "global_not_playing_players_index"
    GLOBAL_PLAYED_MATCHES_INDEX = "global_played_matches_index"
    GLOBAL_MATCHUP_LENGTH_INDEX = "global_matchup_length_index"
    GLOBAL_PLAYER_ENGAGEMENT_FAIRNESS_INDEX = "global_player_engagement_fairness_index"
    GLOBAL_TEAMMATE_SUCCESSION_INDEX = "global_teammate_succession_index"
    GLOBAL_ENEMY_TEAM_SUCCESSION_INDEX = "global_enemy_team_succession_index"
    GLOBAL_PLAYER_ENGAGEMENT_INDEX = "global_player_engagement_index"
    GLOBAL_TEAMMATE_VARIETY_INDEX = "global_teammate_variety_index"
    GLOBAL_ENEMY_TEAM_VARIETY_INDEX = "global_enemy_team_variety_index"
    GLOBAL_BREAK_OCCURRENCE_INDEX = "global_break_occurrence_index"
    GLOBAL_BREAK_SHORTNESS_INDEX = "global_break_shortness_index"