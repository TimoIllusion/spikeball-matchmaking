"""
Python wrapper for the C++ matchmaking metrics implementation.
This provides a drop-in replacement for the original Python implementation.
"""

from typing import List, Dict, Tuple

import matchmaking_fast  # The compiled C++ module
from matchmaking.data import Matchup, Team, Player
from matchmaking.config import MetricWeightsConfig


def convert_matchups_to_cpp_format(
    matchups: List[Matchup],
) -> List[matchmaking_fast.MatchupData]:
    """Convert Python Matchup objects to C++ MatchupData format."""
    cpp_matchups = []

    for matchup in matchups:
        cpp_matchup = matchmaking_fast.MatchupData()

        # Get all player UIDs
        cpp_matchup.all_player_uids = matchup.get_all_player_uids()

        # Build teammate mapping
        cpp_matchup.player_to_teammate = {}
        cpp_matchup.player_to_enemy_team = {}
        cpp_matchup.player_to_enemy_players = {}

        for player_uid in cpp_matchup.all_player_uids:
            # Get teammate
            teammate = matchup.get_teammate(player_uid)
            if teammate is not None:
                cpp_matchup.player_to_teammate[player_uid] = (
                    teammate.get_unique_identifier()
                )

            # Get enemy team
            enemy_team = matchup.get_enemy_team(player_uid)
            if enemy_team is not None:
                cpp_matchup.player_to_enemy_team[player_uid] = (
                    enemy_team.get_unique_identifier()
                )
                cpp_matchup.player_to_enemy_players[player_uid] = (
                    enemy_team.get_all_player_uids()
                )

        cpp_matchups.append(cpp_matchup)

    return cpp_matchups


def convert_weights_config_to_cpp_format(
    weights_config: MetricWeightsConfig,
) -> Dict[str, float]:
    """Convert MetricWeightsConfig to C++ compatible format."""
    cpp_weights = {}

    for metric_type, weight in weights_config.weight_per_metric.items():
        # Convert enum to string value
        cpp_weights[metric_type.value] = float(weight)

    return cpp_weights


class PlayerStatisticsWrapper:
    """Wrapper to make C++ PlayerStatistics compatible with existing Python code."""

    def __init__(self, cpp_stats: matchmaking_fast.PlayerStatistics):
        self.cpp_stats = cpp_stats

        # Copy all attributes for compatibility
        self.num_played_matches = cpp_stats.num_played_matches
        self.break_lengths = cpp_stats.break_lengths
        self.break_lengths_avg = cpp_stats.break_lengths_avg
        self.break_lengths_stdev = cpp_stats.break_lengths_stdev
        self.teammate_hist_stdev = cpp_stats.teammate_hist_stdev
        self.enemy_teams_hist_stdev = cpp_stats.enemy_teams_hist_stdev
        self.consecutive_teammates_total = cpp_stats.consecutive_teammates_total
        self.consecutive_enemies_total = cpp_stats.consecutive_enemies_total
        self.num_unique_people_not_played_with_or_against = (
            cpp_stats.num_unique_people_not_played_with_or_against
        )
        self.num_unique_people_not_played_with = (
            cpp_stats.num_unique_people_not_played_with
        )
        self.num_unique_people_not_played_against = (
            cpp_stats.num_unique_people_not_played_against
        )

    def jsonify(self) -> dict:
        """Convert to JSON-compatible dictionary."""
        return {
            "num_played_matches": self.num_played_matches,
            "break_lengths": self.break_lengths,
            "break_lengths_avg": self.break_lengths_avg,
            "break_lengths_stdev": self.break_lengths_stdev,
            "teammate_hist_stdev": self.teammate_hist_stdev,
            "enemy_teams_hist_stdev": self.enemy_teams_hist_stdev,
            "consecutive_teammates_total": self.consecutive_teammates_total,
            "consecutive_enemies_total": self.consecutive_enemies_total,
            "num_unique_people_not_played_with_or_against": self.num_unique_people_not_played_with_or_against,
            "num_unique_people_not_played_with": self.num_unique_people_not_played_with,
            "num_unique_people_not_played_against": self.num_unique_people_not_played_against,
        }


def get_total_matchup_set_score_fast(
    matchups: List[Matchup],
    num_players: int,
    weights_and_metrics: MetricWeightsConfig,
    num_fields: int,
) -> Tuple[Dict, float]:
    """
    Fast C++ implementation of get_total_matchup_set_score.

    This is a drop-in replacement for the original Python function.
    Returns the same format: (results_dict, loss_value)
    """

    # Convert inputs to C++ format
    cpp_matchups = convert_matchups_to_cpp_format(matchups)
    cpp_weights = convert_weights_config_to_cpp_format(weights_and_metrics)

    # Call the C++ implementation
    global_results, loss = matchmaking_fast.get_total_matchup_set_score_cpp(
        cpp_matchups, num_players, cpp_weights, num_fields
    )

    # For compatibility with existing code, we need to also calculate per-player stats
    # if they're needed elsewhere
    unique_players = set()
    for matchup in matchups:
        unique_players.update(matchup.get_all_player_uids())

    results = {}

    # Calculate individual player stats if needed for compatibility
    for player_uid in unique_players:
        calculator = matchmaking_fast.PlayerMetricCalculatorCpp(
            cpp_matchups, num_players, player_uid, num_fields
        )
        cpp_player_stats = calculator.calculate_player_stats()
        results[player_uid] = PlayerStatisticsWrapper(cpp_player_stats)

    # Add global results
    results["global"] = global_results

    return results, loss
