from matchmaking.data import Player
from matchmaking.generator import get_most_diverse_matchups
from matchmaking.config import MetricWeightsConfig

# fix random seeds
import random

random.seed(42)

import numpy as np

np.random.seed(42)


def test_matchup_generation():

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

    metric_config = MetricWeightsConfig()

    best_matchup_config, best_score, results = get_most_diverse_matchups(
        players, num_rounds, num_fields, num_iterations, metric_config
    )

    print(best_matchup_config)

    assert (
        best_score == 5404.723502208126
    ), "Unexpected score result. Did the metrics change?"


if __name__ == "__main__":
    test_matchup_generation()
