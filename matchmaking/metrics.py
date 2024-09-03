from typing import List, Tuple, Dict
import statistics
from collections import Counter
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from matchmaking.data import Matchup, Team, Player
from matchmaking.config import MetricWeightsConfig
from matchmaking.metric_type import MetricType


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


def _get_teammate_uids(matchups: List[Matchup], player_uid: str) -> List[str]:
    teammate_uids = []

    for matchup in matchups:
        if player_uid in matchup.get_all_player_uids():
            teammate = matchup.get_teammate(player_uid)

            if teammate is not None:
                teammate_uid = teammate.get_unique_identifier()
                teammate_uids.append(teammate_uid)

    assert (
        player_uid not in teammate_uids
    ), "Player should not be in the list of teammates"

    return teammate_uids


def _count_consecutive_occurences(list_of_symbols: List[str]) -> Counter:
    temp_counter = 0
    counter = Counter()
    for i in range(len(list_of_symbols)):
        if i == 0:
            continue

        if list_of_symbols[i] == list_of_symbols[i - 1]:
            temp_counter += 1
        else:
            counter[list_of_symbols[i - 1]] += temp_counter
            temp_counter = 0

    return counter


def _get_enemy_teams(
    matchups: List[Matchup], player_uid: str
) -> Tuple[List[str], List[str]]:

    enemy_team_uids = []
    enemy_player_uids = []
    for matchup in matchups:
        enemy_team = matchup.get_enemy_team(player_uid)

        if enemy_team is not None:
            enemy_team_uid = enemy_team.get_unique_identifier()
            enemy_team_uids.append(enemy_team_uid)
            enemy_player_uids.extend(enemy_team.get_all_player_uids())

    assert (
        player_uid not in enemy_player_uids
    ), "Player should not be in the list of enemies"

    return enemy_team_uids, enemy_player_uids


@dataclass
class PlayerStatistics:
    num_played_matches: int
    break_lengths_avg: float
    break_lengths_stdev: float
    break_lengths_hist: Counter[int]
    matchup_lengths_played_between_breaks_second_length: float
    matchup_lengths: List[int]
    teammate_hist: Counter[str]
    teammate_hist_stdev: float
    enemy_teams_hist: Counter[str]
    enemy_teams_hist_stdev: float
    consecutive_teammates_hist: Counter[str]
    consecutive_enemies_hist: Counter[str]
    consecutive_teammates_total: int
    consecutive_enemies_total: int
    unique_people_played_with_or_against: int
    unique_people_not_played_with_or_against: int


class PlayerMetricCalculator:

    def __init__(self, matchups: List[Matchup], num_players: int, player_uid: str):
        self.matchups = matchups
        self.num_players = num_players
        self.player_uid = player_uid

        self.calculate_base_statistics()

    def calculate_base_statistics(self):

        self.played_matches = [
            self.player_uid in x.get_all_player_uids() for x in self.matchups
        ]

        self.break_lengths = _find_consecutive_numbers(self.played_matches, 0)

        self.matchup_lengths_played_between_breaks = _find_consecutive_numbers(
            self.played_matches, 1
        )

        self.teammate_uids = _get_teammate_uids(self.matchups, self.player_uid)
        self.teammate_hist = Counter(self.teammate_uids)
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

    def compute_num_played_matches(self):
        return sum(self.played_matches)

    def compute_break_lengths_avg(self):
        return np.mean(self.break_lengths)

    def compute_break_lengths_stdev(self):
        return (
            statistics.stdev(self.break_lengths) if len(self.break_lengths) > 1 else 0.0
        )

    def compute_break_lengths_hist(self):
        return Counter(self.break_lengths)

    def compute_matchup_lengths_played_between_breaks(self):
        return self.matchup_lengths_played_between_breaks

    def compute_matchup_lengths_played_between_breaks_second_length(self):
        return (
            self.matchup_lengths_played_between_breaks[1]
            if len(self.matchup_lengths_played_between_breaks) > 1
            else 10.0
        )

    def compute_teammate_hist(self):
        return self.teammate_hist

    def compute_teammate_hist_stdev(self):
        return (
            statistics.stdev(list(self.teammate_hist.values()))
            if len(self.teammate_hist) > 1
            else 0.0
        )

    def compute_enemy_teams_hist(self):
        return self.enemy_teams_hist

    def compute_enemy_teams_hist_stdev(self):
        return (
            statistics.stdev(list(self.enemy_teams_hist.values()))
            if len(self.enemy_teams_hist) > 1
            else 0.0
        )

    def compute_consecutive_teammates_hist(self):
        return self.consecutive_teammates_hist

    def compute_consecutive_enemies_hist(self):
        return self.consecutive_enemies_hist

    def compute_consecutive_teammates_total(self):
        return sum(list(self.consecutive_teammates_hist.values()))

    def compute_consecutive_enemies_total(self):
        return sum(list(self.consecutive_enemies_hist.values()))

    def compute_unique_people_played_with_or_against(self):
        return len(set(self.enemy_player_uids + self.teammate_uids))

    def compute_unique_people_not_played_with_or_against(self):
        return (self.num_players - 1) - len(
            set(self.enemy_player_uids + self.teammate_uids)
        )

    def calculate_player_stats(self) -> PlayerStatistics:
        return PlayerStatistics(
            num_played_matches=self.compute_num_played_matches(),
            break_lengths_avg=self.compute_break_lengths_avg(),
            break_lengths_stdev=self.compute_break_lengths_stdev(),
            break_lengths_hist=self.compute_break_lengths_hist(),
            matchup_lengths_played_between_breaks_second_length=self.compute_matchup_lengths_played_between_breaks_second_length(),  # optimized for short sessions
            matchup_lengths=self.compute_matchup_lengths_played_between_breaks(),
            teammate_hist=self.compute_teammate_hist(),
            teammate_hist_stdev=self.compute_teammate_hist_stdev(),
            enemy_teams_hist=self.compute_enemy_teams_hist(),
            enemy_teams_hist_stdev=self.compute_enemy_teams_hist_stdev(),
            consecutive_teammates_hist=self.compute_consecutive_teammates_hist(),
            consecutive_enemies_hist=self.compute_consecutive_enemies_hist(),
            consecutive_teammates_total=self.compute_consecutive_teammates_total(),
            consecutive_enemies_total=self.compute_consecutive_enemies_total(),
            unique_people_played_with_or_against=self.compute_unique_people_played_with_or_against(),
            unique_people_not_played_with_or_against=self.compute_unique_people_not_played_with_or_against(),
        )


def _calculate_all_player_statistics(
    unique_players: List[str], matchups: List[Matchup], num_players: int
) -> dict:

    results = {}
    for player_uid in unique_players:

        metric_calculator = PlayerMetricCalculator(matchups, num_players, player_uid)

        results[player_uid] = metric_calculator.calculate_player_stats()

    return results


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
        return statistics.stdev(global_num_played_matches)

    def compute_break_occurrence_index(self) -> float:
        global_break_lengths_stdev = [
            stat.break_lengths_stdev for stat in self.player_stats.values()
        ]
        return sum(global_break_lengths_stdev)

    def compute_break_shortness_index(self) -> float:
        global_per_player_break_lengths_avg = [
            stat.break_lengths_avg for stat in self.player_stats.values()
        ]
        global_per_player_break_lengths_avg_squared = [
            x**2 for x in global_per_player_break_lengths_avg
        ]
        return sum(global_per_player_break_lengths_avg_squared)

    def compute_matchup_length_index(self) -> float:
        per_player_matchup_length_second_element = [
            stat.matchup_lengths_played_between_breaks_second_length
            for stat in self.player_stats.values()
        ]
        return statistics.stdev(per_player_matchup_length_second_element)

    def compute_teammate_variety_index(self) -> float:
        per_player_teammate_hist_stdev = [
            stat.teammate_hist_stdev for stat in self.player_stats.values()
        ]
        return sum(per_player_teammate_hist_stdev)

    def compute_enemy_team_variety_index(self) -> float:
        per_player_enemy_teams_hist_stdev = [
            stat.enemy_teams_hist_stdev for stat in self.player_stats.values()
        ]
        return sum(per_player_enemy_teams_hist_stdev)

    def compute_teammate_succession_index(self) -> float:
        per_player_consecutive_teammates_amount = [
            stat.consecutive_teammates_total for stat in self.player_stats.values()
        ]
        return sum(per_player_consecutive_teammates_amount)

    def compute_enemy_team_succession_index(self) -> float:
        per_player_consecutive_enemies_amount = [
            stat.consecutive_enemies_total for stat in self.player_stats.values()
        ]
        return sum(per_player_consecutive_enemies_amount)

    def compute_player_engagement_index(self) -> float:
        per_player_unique_people_not_played_with_or_against = [
            stat.unique_people_not_played_with_or_against
            for stat in self.player_stats.values()
        ]
        return sum(per_player_unique_people_not_played_with_or_against)

    def compute_player_engagement_fairness_index(self) -> float:
        per_player_unique_people_not_played_with_or_against = [
            stat.unique_people_not_played_with_or_against
            for stat in self.player_stats.values()
        ]
        return statistics.stdev(per_player_unique_people_not_played_with_or_against)

    def calculate_global_stats(self) -> Dict[str, float]:
        stats = {
            MetricType.GLOBAL_NOT_PLAYING_PLAYERS_INDEX.value: self.compute_not_playing_players_index(),
            MetricType.GLOBAL_PLAYED_MATCHES_INDEX.value: self.compute_played_matches_index(),
            MetricType.GLOBAL_MATCHUP_LENGTH_INDEX.value: self.compute_matchup_length_index(),
            MetricType.GLOBAL_BREAK_OCCURRENCE_INDEX.value: self.compute_break_occurrence_index(),
            MetricType.GLOBAL_BREAK_SHORTNESS_INDEX.value: self.compute_break_shortness_index(),
            MetricType.GLOBAL_TEAMMATE_VARIETY_INDEX.value: self.compute_teammate_variety_index(),
            MetricType.GLOBAL_ENEMY_TEAM_VARIETY_INDEX.value: self.compute_enemy_team_variety_index(),
            MetricType.GLOBAL_TEAMMATE_SUCCESSION_INDEX.value: self.compute_teammate_succession_index(),
            MetricType.GLOBAL_ENEMY_TEAM_SUCCESSION_INDEX.value: self.compute_enemy_team_succession_index(),
            MetricType.GLOBAL_PLAYER_ENGAGEMENT_INDEX.value: self.compute_player_engagement_index(),
            MetricType.GLOBAL_PLAYER_ENGAGEMENT_FAIRNESS_INDEX.value: self.compute_player_engagement_fairness_index(),
        }
        return stats


# TODO: fix break calculation for multiple fields
# TODO: find a way to incorporate time between breaks as metric (matchup_lengths_played_between_breaks)
# TODO: optimize for 5 and 6 players (most common normal player counts for single net)
def get_avg_matchup_diversity_score(
    matchups: List[Matchup],
    num_players: int,
    weights_and_metrics: MetricWeightsConfig,
) -> int:

    # Get unique player identifiers
    players = []
    for matchup in matchups:
        players += matchup.get_all_player_uids()

    unique_players = list(set(players))

    # Calculate all player statistics
    results: Dict[str, PlayerStatistics] = _calculate_all_player_statistics(
        unique_players, matchups, num_players
    )

    # TODO: calculate entropy, energy or something similar to quantify how good the variety of matchups played is
    global_metric_calculator = GlobalMetricCalculator(results, num_players)

    global_results = global_metric_calculator.calculate_global_stats()

    results["global"] = global_results

    loss = 0.0

    for metric_type, metric_weight in weights_and_metrics.weight_per_metric.items():
        loss += metric_weight * global_results[metric_type.value]

    return results, loss
