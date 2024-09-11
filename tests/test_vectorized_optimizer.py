import time
from pprint import pprint

import numpy as np

from matchmaking.vectorized_optimizer import VectorizedMatchupOptimizer
from matchmaking.vectorized_stat_calculator import VectorizedStatCalculator
from matchmaking.data import Player
from matchmaking.vectorized_metric_calculator import VectorizedMetricCalculator


def calc_memory_footprint(arr: np.ndarray) -> float:
    memory_footprint = arr.nbytes / 1024**2
    print(f"Memory footprint: {memory_footprint} MB")
    return memory_footprint


def test_vectorized_matchup_optimizer():

    player_names = [
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
        "M",
    ]

    players = [Player(name) for name in player_names]

    NUM_GENERATED_SESSIONS = 10000

    optimizer = VectorizedMatchupOptimizer(
        players=players,
        num_rounds=10,
        num_fields=3,
        num_iterations=NUM_GENERATED_SESSIONS,
        weights_and_metrics=None,
    )

    t = time.time()

    sessions = optimizer.generate_n_matchup_configs(NUM_GENERATED_SESSIONS)
    sessions = optimizer.convert_nested_matchup_config_list_to_tensor(sessions)
    print(sessions.shape)

    calc_memory_footprint(sessions)

    assert sessions.shape == (
        NUM_GENERATED_SESSIONS,
        10,
        3,
        4,
    ), "Shape of sessions tensor is wrong!"

    stats_calculator = VectorizedStatCalculator()
    sessions_with_played_matches = stats_calculator.prepare_played_matches_tensor(
        sessions, len(players)
    )

    calc_memory_footprint(sessions_with_played_matches)

    played_matches = stats_calculator.compute_played_matches(
        sessions_with_played_matches
    )
    print(played_matches.shape)

    break_lengths, match_lengths_per_player = (
        stats_calculator.compute_break_lengths_and_match_lengths(
            sessions_with_played_matches
        )
    )

    # TODO: maybe use this to directly compute breaks as well (via -1 entries)
    teammates, enemies = stats_calculator.compute_teammates_and_enemies(
        sessions, len(players)
    )

    (
        per_player_unique_people_not_played_with_or_against,
        per_player_unique_people_not_played_with,
        per_player_unique_people_not_played_against,
    ) = stats_calculator.calculate_player_interactions(teammates, enemies)

    metric_calculatur = VectorizedMetricCalculator(
        sessions,
        played_matches,
        break_lengths,
        match_lengths_per_player,
        teammates,
        enemies,
        per_player_unique_people_not_played_with_or_against,
        per_player_unique_people_not_played_with,
        per_player_unique_people_not_played_against,
    )

    losses = metric_calculatur.calculate_total_loss()

    best_session_idx = np.argmin(losses)
    loss = losses[best_session_idx]
    best_session = sessions[best_session_idx]
    pprint(best_session)
    print("Loss:", loss)

    duration = time.time() - t
    print(f"Total Duration: {duration*1000.0} ms")
    iters_per_second = NUM_GENERATED_SESSIONS / duration
    print(f"Iterations per second: {iters_per_second}")


if __name__ == "__main__":
    test_vectorized_matchup_optimizer()
