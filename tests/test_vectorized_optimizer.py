import time
from pprint import pprint

import numpy as np

from matchmaking.vectorized_optimizer import VectorizedMatchupOptimizer
from matchmaking.vectorized_stat_calculator import VectorizedStatCalculator
from matchmaking.data import Player
from matchmaking.vectorized_metric_calculator import VectorizedMetricCalculator
from matchmaking.timer import Timer


def calc_memory_footprint(arr: np.ndarray) -> float:
    memory_footprint = arr.nbytes / 1024**2
    print(f"Memory footprint: {memory_footprint} MB")
    return memory_footprint


def test_vectorized_matchup_optimizer():
    timer = Timer()
    timer_total = Timer()
    timer_total.start("Total time")

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

    # Optimizer initialization
    timer.start("Optimizer initialization")
    optimizer = VectorizedMatchupOptimizer(
        players=players,
        num_rounds=10,
        num_fields=3,
        num_iterations=NUM_GENERATED_SESSIONS,
        weights_and_metrics=None,
    )
    timer.stop()

    # Generate sessions
    timer.start("Session generation")
    sessions = optimizer.generate_n_matchup_configs(NUM_GENERATED_SESSIONS)
    timer.stop()

    # Convert sessions to tensor
    timer.start("Session tensor conversion")
    sessions = optimizer.convert_nested_matchup_config_list_to_tensor(sessions)
    timer.stop()

    print(sessions.shape)
    calc_memory_footprint(sessions)

    # Validate shape of sessions
    assert sessions.shape == (
        NUM_GENERATED_SESSIONS,
        10,
        3,
        4,
    ), "Shape of sessions tensor is wrong!"

    # Initialize the stats calculator
    stats_calculator = VectorizedStatCalculator()

    # Prepare played matches tensor
    timer.start("Played matches tensor preparation")
    sessions_with_played_matches = stats_calculator.prepare_played_matches_tensor(
        sessions, len(players)
    )
    timer.stop()

    calc_memory_footprint(sessions_with_played_matches)

    # Compute played matches
    timer.start("Played matches computation")
    played_matches = stats_calculator.compute_played_matches(
        sessions_with_played_matches
    )
    timer.stop()

    print(played_matches.shape)

    # Compute break lengths and match lengths per player
    timer.start("Break lengths and match lengths computation")
    break_lengths, match_lengths_per_player = (
        stats_calculator.compute_break_lengths_and_match_lengths(
            sessions_with_played_matches
        )
    )
    timer.stop()

    # Compute teammates and enemies
    timer.start("Teammates and enemies computation")
    teammates, enemies = stats_calculator.compute_teammates_and_enemies(
        sessions, len(players)
    )
    timer.stop()

    # Calculate player interactions
    timer.start("Player interactions computation")
    (
        per_player_unique_people_not_played_with_or_against,
        per_player_unique_people_not_played_with,
        per_player_unique_people_not_played_against,
    ) = stats_calculator.calculate_player_interactions(teammates, enemies)
    timer.stop()

    # Metric calculator initialization
    metric_calculator = VectorizedMetricCalculator(
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

    # Calculate total loss for all sessions
    timer.start("Loss calculation")
    losses = metric_calculator.calculate_total_loss()
    timer.stop()

    best_session_idx = np.argmin(losses)

    loss = losses[best_session_idx]
    best_session = sessions[best_session_idx]

    pprint(best_session)
    print("Best session index:", best_session_idx)
    print("Loss:", loss)

    timer_total.stop(NUM_GENERATED_SESSIONS)


if __name__ == "__main__":
    test_vectorized_matchup_optimizer()
