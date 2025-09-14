from typing import List, Tuple, Dict
import statistics
from collections import Counter
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from matchmaking.data import Matchup, Team, Player
from matchmaking.config import MetricWeightsConfig
from matchmaking.metric_type import MetricType

from matchmaking.metric_compute_functions import (
    compute_num_played_matches,
    compute_break_lengths,
    compute_break_lengths_avg,
    compute_break_lengths_stdev,
    compute_break_lengths_hist,
    compute_matchup_lengths_played_between_breaks,
    compute_matchup_lengths_played_between_breaks_second_length,
    compute_teammate_hist,
    compute_teammate_hist_stdev,
    compute_enemy_teams_hist,
    compute_enemy_teams_hist_stdev,
    compute_consecutive_teammates_hist,
    compute_consecutive_enemies_hist,
    compute_consecutive_teammates_total,
    compute_consecutive_enemies_total,
    compute_unique_people_not_played_with_or_against,
    compute_unique_people_not_played_with,
    compute_unique_people_not_played_against,
    _find_consecutive_numbers,
    _get_teammate_uids,
    _get_enemy_teams,
    _count_consecutive_occurences,
)


@dataclass
class PlayerStatistics:
    num_played_matches: int
    break_lengths: List[int]
    break_lengths_avg: float
    break_lengths_stdev: float
    break_lengths_hist: Counter[int]
    matchup_lengths_played_between_breaks_second_session_only: float
    matchup_lengths_played_between_breaks: List[int]
    teammate_hist: Counter[str]
    teammate_hist_stdev: float
    enemy_teams_hist: Counter[str]
    enemy_teams_hist_stdev: float
    consecutive_teammates_hist: Counter[str]
    consecutive_enemies_hist: Counter[str]
    consecutive_teammates_total: int
    consecutive_enemies_total: int
    num_unique_people_not_played_with_or_against: int
    num_unique_people_not_played_with: int
    num_unique_people_not_played_against: int

    def jsonify(self) -> dict:
        # convert arrays and counters to lists
        attributes = {}
        for key, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                attributes[key] = value.tolist()
            elif isinstance(value, Counter):
                attributes[key] = dict(value)
            else:
                attributes[key] = value

        # convert np float/int to native python types
        for key, value in attributes.items():
            if isinstance(value, np.int64):
                attributes[key] = int(value)
            elif isinstance(value, np.float64):
                attributes[key] = float(value)

        return attributes


class PlayerMetricCalculator:

    def __init__(
        self,
        matchups: List[Matchup],
        num_players: int,
        num_fields: int,
        player_uid: str,
    ):
        self.matchups = matchups
        self.num_players = num_players
        self.player_uid = player_uid
        self.num_fields = num_fields

        self.calculate_base_statistics()

    # TODO: add check for consecutive enemy players (not just team composition)
    # TODO: maybe get actual histo of all players instead of just hist of the played players, at least for specific metrics (not for consecutive teammate hist)

    def calculate_base_statistics(self):

        self.played_matches = self.get_played_matches()

        self.break_lengths = _find_consecutive_numbers(self.played_matches, 0)

        self.matchup_lengths_played_between_breaks = _find_consecutive_numbers(
            self.played_matches, 1
        )

        self.teammate_uids = _get_teammate_uids(self.matchups, self.player_uid)
        self.teammate_hist = Counter(self.teammate_uids)
        # TODO: fix this! (and also for enemies)
        self.consecutive_teammates_hist = _count_consecutive_occurences(
            self.teammate_uids
        )

        self.enemy_team_uids, self.enemy_player_uids = _get_enemy_teams(
            self.matchups, self.player_uid
        )
        self.enemy_teams_hist = Counter(self.enemy_team_uids)

        self.consecutive_enemies_hist = _count_consecutive_occurences(
            self.enemy_team_uids
        )

    def get_played_matches(self) -> np.ndarray:
        # Get a list of all player UIDs for each matchup and convert it into a boolean array
        played_matches = np.array(
            [self.player_uid in x.get_all_player_uids() for x in self.matchups]
        )

        # Reshape the array into rounds with num_fields columns
        played_matches = played_matches.reshape(-1, self.num_fields)

        # Check if the player played on ANY field for each round (axis=1)
        played_matches_per_round = np.any(played_matches, axis=1)

        return played_matches_per_round

    def calculate_player_stats(self) -> PlayerStatistics:
        return PlayerStatistics(
            num_played_matches=compute_num_played_matches(self.played_matches),
            break_lengths=compute_break_lengths(self.played_matches),
            break_lengths_avg=compute_break_lengths_avg(self.break_lengths),
            break_lengths_stdev=compute_break_lengths_stdev(self.break_lengths),
            break_lengths_hist=compute_break_lengths_hist(self.break_lengths),
            matchup_lengths_played_between_breaks_second_session_only=compute_matchup_lengths_played_between_breaks_second_length(
                self.matchup_lengths_played_between_breaks
            ),  # optimized for short sessions
            matchup_lengths_played_between_breaks=compute_matchup_lengths_played_between_breaks(
                self.matchup_lengths_played_between_breaks
            ),
            teammate_hist=compute_teammate_hist(self.teammate_uids),
            teammate_hist_stdev=compute_teammate_hist_stdev(self.teammate_hist),
            enemy_teams_hist=compute_enemy_teams_hist(self.enemy_team_uids),
            enemy_teams_hist_stdev=compute_enemy_teams_hist_stdev(
                self.enemy_teams_hist
            ),
            consecutive_teammates_hist=compute_consecutive_teammates_hist(
                self.teammate_uids
            ),
            consecutive_enemies_hist=compute_consecutive_enemies_hist(
                self.enemy_team_uids
            ),
            consecutive_teammates_total=compute_consecutive_teammates_total(
                self.consecutive_teammates_hist
            ),
            consecutive_enemies_total=compute_consecutive_enemies_total(
                self.consecutive_enemies_hist
            ),
            num_unique_people_not_played_with_or_against=compute_unique_people_not_played_with_or_against(
                self.num_players, self.enemy_player_uids, self.teammate_uids
            ),
            num_unique_people_not_played_with=compute_unique_people_not_played_with(
                self.num_players, self.teammate_uids
            ),
            num_unique_people_not_played_against=compute_unique_people_not_played_against(
                self.num_players, self.enemy_player_uids
            ),
        )


def _calculate_all_player_statistics(
    unique_players: List[str],
    matchups: List[Matchup],
    num_players: int,
    num_fields: int,
) -> dict:

    results = {}
    for player_uid in unique_players:

        metric_calculator = PlayerMetricCalculator(
            matchups, num_players, num_fields, player_uid
        )

        results[player_uid] = metric_calculator.calculate_player_stats()

    return results


# TODO: combine compute of per player metrics and global metrics into one class
class GlobalMetricCalculator:
    def __init__(self, player_stats: Dict[str, PlayerStatistics], num_players: int):
        self.player_stats = player_stats
        self.num_players = num_players

    def compute_not_playing_players_index(self) -> int:
        unique_players = len(self.player_stats)
        return self.num_players - unique_players

    def compute_played_matches_index(self) -> float:
        global_num_played_matches = [
            stat.num_played_matches for stat in self.player_stats.values()
        ]
        return np.std(global_num_played_matches)

    # def compute_break_even_occurrence_index(self) -> float:
    #     global_break_lengths_stdev = [
    #         stat.break_lengths_stdev for stat in self.player_stats.values()
    #     ]
    #     return np.sum(global_break_lengths_stdev)

    def compute_break_shortness_index(self) -> float:
        """This metric computes, the summed squared break lengths above length of 1 for all players, to penalize longer breaks."""

        global_player_break_lengths = []
        for stat in self.player_stats.values():
            global_player_break_lengths.extend(stat.break_lengths)

        # filter out breaks of length 1
        global_player_break_lengths_filtered = np.array(
            [x for x in global_player_break_lengths if x > 1]
        )

        return np.sum(global_player_break_lengths_filtered**2)

    def compute_second_continous_matchup_length_focused_on_short_sessions_index(
        self,
    ) -> float:
        per_player_matchup_length_second_element = [
            stat.matchup_lengths_played_between_breaks_second_session_only
            for stat in self.player_stats.values()
        ]
        return np.std(per_player_matchup_length_second_element)

    def compute_teammate_variety_index(self) -> float:  # TODO: correct?
        per_player_teammate_hist_stdev = [
            stat.teammate_hist_stdev for stat in self.player_stats.values()
        ]
        return np.sum(per_player_teammate_hist_stdev)

    def compute_enemy_team_variety_index(self) -> float:  # TODO: correct?
        per_player_enemy_teams_hist_stdev = [
            stat.enemy_teams_hist_stdev for stat in self.player_stats.values()
        ]
        return np.sum(per_player_enemy_teams_hist_stdev)

    def compute_teammate_succession_index(self) -> float:
        per_player_consecutive_teammates_amount = [
            stat.consecutive_teammates_total for stat in self.player_stats.values()
        ]
        return np.sum(per_player_consecutive_teammates_amount)

    def compute_enemy_team_succession_index(self) -> float:
        per_player_consecutive_enemies_amount = [
            stat.consecutive_enemies_total for stat in self.player_stats.values()
        ]
        return np.sum(per_player_consecutive_enemies_amount)

    def compute_player_engagement_fairness_index(self) -> float:
        per_player_unique_people_not_played_with_or_against = [
            stat.num_unique_people_not_played_with_or_against
            for stat in self.player_stats.values()
        ]
        return np.std(per_player_unique_people_not_played_with_or_against)

    def compute_not_played_with_or_against_players_index(self) -> float:
        per_player_unique_people_not_played_with_or_against = [
            stat.num_unique_people_not_played_with_or_against
            for stat in self.player_stats.values()
        ]
        return np.sum(per_player_unique_people_not_played_with_or_against)

    def compute_not_played_with_players_index(self) -> float:
        per_player_unique_people_not_played_with = [
            stat.num_unique_people_not_played_with
            for stat in self.player_stats.values()
        ]
        return np.sum(per_player_unique_people_not_played_with)

    def compute_not_played_against_players_index(self) -> float:
        per_player_unique_people_not_played_against = [
            stat.num_unique_people_not_played_against
            for stat in self.player_stats.values()
        ]
        return np.sum(per_player_unique_people_not_played_against)

    def calculate_global_stats(self) -> Dict[str, float]:
        stats = {
            MetricType.GLOBAL_NOT_PLAYING_PLAYERS_INDEX.value: self.compute_not_playing_players_index(),
            MetricType.GLOBAL_PLAYED_MATCHES_INDEX.value: self.compute_played_matches_index(),
            MetricType.GLOBAL_MATCHUP_SESSION_LENGTH_BETWEEN_BREAKS_INDEX.value: self.compute_second_continous_matchup_length_focused_on_short_sessions_index(),
            # MetricType.GLOBAL_BREAK_OCCURRENCE_INDEX.value: self.compute_break_even_occurrence_index(),
            MetricType.GLOBAL_BREAK_SHORTNESS_INDEX.value: self.compute_break_shortness_index(),
            MetricType.GLOBAL_TEAMMATE_VARIETY_INDEX.value: self.compute_teammate_variety_index(),
            MetricType.GLOBAL_ENEMY_TEAM_VARIETY_INDEX.value: self.compute_enemy_team_variety_index(),
            MetricType.GLOBAL_TEAMMATE_SUCCESSION_INDEX.value: self.compute_teammate_succession_index(),
            MetricType.GLOBAL_ENEMY_TEAM_SUCCESSION_INDEX.value: self.compute_enemy_team_succession_index(),
            MetricType.GLOBAL_PLAYER_ENGAGEMENT_FAIRNESS_INDEX.value: self.compute_player_engagement_fairness_index(),
            MetricType.GLOBAL_NOT_PLAYED_WITH_OR_AGAINST_PLAYERS_INDEX.value: self.compute_not_played_with_or_against_players_index(),
            MetricType.GLOBAL_NOT_PLAYED_WITH_PLAYERS_INDEX.value: self.compute_not_played_with_players_index(),
            MetricType.GLOBAL_NOT_PLAYED_AGAINST_PLAYERS_INDEX.value: self.compute_not_played_against_players_index(),
        }
        return stats


# TODO: fix break calculation for multiple fields
# TODO: find a way to incorporate time between breaks as metric (matchup_lengths_played_between_breaks)
# TODO: optimize for 5 and 6 players (most common normal player counts for single net)
def get_total_matchup_set_score(
    matchups: List[Matchup],
    num_players: int,
    weights_and_metrics: MetricWeightsConfig,
    num_fields: int,
) -> int:

    # Get unique player identifiers
    players = []
    for matchup in matchups:
        players += matchup.get_all_player_uids()

    unique_players = list(set(players))

    # Calculate all player statistics
    results: Dict[str, PlayerStatistics] = _calculate_all_player_statistics(
        unique_players, matchups, num_players, num_fields
    )

    # TODO: calculate entropy, energy or something similar to quantify how good the variety of matchups played is
    global_metric_calculator = GlobalMetricCalculator(results, num_players)

    global_results = global_metric_calculator.calculate_global_stats()

    results["global"] = global_results

    loss = 0.0

    for metric_type, metric_weight in weights_and_metrics.weight_per_metric.items():
        loss += metric_weight * global_results[metric_type.value]

    return results, loss
