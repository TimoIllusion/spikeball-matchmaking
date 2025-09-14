# Compute functions for metrics
from typing import List, Tuple
from collections import Counter
from itertools import groupby
from matchmaking.data import Matchup

import numpy as np


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
    counter = Counter()

    for symbol, group in groupby(list_of_symbols):
        length = len(list(group))
        if length > 1:  # Only count consecutive (length > 1)
            counter[symbol] += length - 1

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


def compute_num_played_matches(played_matches: np.ndarray) -> int:
    return np.sum(played_matches)


def compute_break_lengths(played_matches: np.ndarray) -> List[int]:
    return _find_consecutive_numbers(played_matches, 0)


def compute_break_lengths_avg(break_lengths: List[int]) -> float:
    return np.mean(break_lengths) if len(break_lengths) > 0 else 0.0


def compute_break_lengths_stdev(break_lengths: List[int]) -> float:
    return np.std(break_lengths) if len(break_lengths) > 0 else 0.0


def compute_break_lengths_hist(break_lengths: List[int]) -> Counter:
    return Counter(break_lengths)


def compute_matchup_lengths_played_between_breaks(
    played_matches: np.ndarray,
) -> List[int]:
    return _find_consecutive_numbers(played_matches, 1)


def compute_matchup_lengths_played_between_breaks_second_length(
    matchup_lengths: List[int],
) -> float:
    return matchup_lengths[1] if len(matchup_lengths) > 1 else 10.0


def compute_teammate_hist(teammate_uids: List[str]) -> Counter:
    return Counter(teammate_uids)


def compute_teammate_hist_stdev(teammate_hist: Counter) -> float:
    teammate_hist_values = list(teammate_hist.values())
    return np.std(teammate_hist_values)


def compute_enemy_teams_hist(enemy_team_uids: List[str]) -> Counter:
    return Counter(enemy_team_uids)


def compute_enemy_teams_hist_stdev(enemy_teams_hist: Counter) -> float:
    enemy_teams_hist_values = list(enemy_teams_hist.values())
    return np.std(enemy_teams_hist_values)


def compute_consecutive_teammates_hist(teammate_uids: List[str]) -> Counter:
    return _count_consecutive_occurences(teammate_uids)


def compute_consecutive_enemies_hist(enemy_team_uids: List[str]) -> Counter:
    return _count_consecutive_occurences(enemy_team_uids)


def compute_consecutive_teammates_total(consecutive_teammates_hist: Counter) -> int:
    consecutive_teammates_hist_values = list(consecutive_teammates_hist.values())
    return np.sum(consecutive_teammates_hist_values)


def compute_consecutive_enemies_total(consecutive_enemies_hist: Counter) -> int:
    consecutive_enemies_hist_values = list(consecutive_enemies_hist.values())
    return np.sum(consecutive_enemies_hist_values)


def compute_unique_people_not_played_with_or_against(
    num_players: int, enemy_player_uids: List[str], teammate_uids: List[str]
) -> int:
    return (num_players - 1) - len(set(enemy_player_uids + teammate_uids))


def compute_unique_people_not_played_with(
    num_players: int, teammate_uids: List[str]
) -> int:
    return (num_players - 1) - len(set(teammate_uids))


def compute_unique_people_not_played_against(
    num_players: int, enemy_player_uids: List[str]
) -> int:
    return (num_players - 1) - len(set(enemy_player_uids))


def _find_consecutive_numbers(arr, target_number: int):
    return [len(list(group)) for key, group in groupby(arr) if key == target_number]


# def _find_consecutive_numbers(arr, target_number: int):
#     lengths = []
#     length = 0

#     for num in arr:
#         if num == target_number:
#             length += 1
#         else:
#             if length > 0:
#                 lengths.append(length)
#             length = 0

#     # Account for a trailing sequence of target_number
#     if length > 0:
#         lengths.append(length)

#     return lengths
