import time

import numpy as np

from matchmaking.vectorized_optimizer import (
    VectorizedMatchupOptimizer,
    VectorizedStatCalculator,
)
from matchmaking.data import Player


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

    num_matches = stats_calculator.compute_played_matches(sessions_with_played_matches)
    print(num_matches.shape)

    break_lengths = stats_calculator.compute_break_lengths(sessions_with_played_matches)

    duration = time.time() - t
    print(f"Duration: {duration*1000.0} ms")


if __name__ == "__main__":
    test_vectorized_matchup_optimizer()
