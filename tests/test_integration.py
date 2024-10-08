from matchmaking.data import Player
from matchmaking.simple_optimizer import SimpleMatchupOptimizer
from matchmaking.config import MetricWeightsConfig

# fix random seeds
import random

random.seed(42)

import numpy as np

np.random.seed(42)


def test_matchup_generation():

    players = [
        Player("P01"),
        Player("P2"),
        Player("P3"),
        Player("P4"),
        Player("P5"),
        Player("P6"),
        Player("P7"),
        Player("P8"),
        Player("P9"),
        Player("P10"),
        Player("P11"),
        Player("P12"),
        Player("P13"),
    ]

    num_rounds = 10
    num_fields = 3
    num_iterations = 100

    metric_config = MetricWeightsConfig()

    optimizer = SimpleMatchupOptimizer(
        players, num_rounds, num_fields, num_iterations, metric_config
    )

    best_matchup_config, best_score, results, _, _ = (
        optimizer.get_most_diverse_matchups()
    )

    print(best_matchup_config)


if __name__ == "__main__":
    test_matchup_generation()
