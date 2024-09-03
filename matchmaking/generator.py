from pprint import pprint
from copy import deepcopy
from typing import List, Tuple

from tqdm import tqdm
import numpy as np

from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_avg_matchup_diversity_score
from matchmaking.config import MetricWeightsConfig


class MatchupDiversityOptimizer:

    def __init__(
        self,
        players: List[Player],
        num_rounds: int,
        num_fields: int,
        num_iterations: int,
        weights_and_metrics: MetricWeightsConfig,
    ):
        self.players = players
        self.num_rounds = num_rounds
        self.num_fields = num_fields
        self.num_iterations = num_iterations
        self.weights_and_metrics = weights_and_metrics

        self.best_scores = []
        self.best_scores_iterations = []
        self.min_score = np.inf
        self.best_matchup_config = None

    def get_most_diverse_matchups(
        self,
    ) -> Tuple[List[Matchup], float, dict, List[float], List[int]]:
        for iter in tqdm(range(self.num_iterations)):
            matchup_history = set()
            matchups: List[Matchup] = []

            for _ in range(self.num_rounds):
                temp_matchups = self.sample_matchups()
                matchup_history.update(
                    [x.get_unique_identifier() for x in temp_matchups]
                )
                matchups.extend(temp_matchups)

            self.best_matchup_config, self.min_score = self.update_best_score(
                matchups, self.min_score, self.best_matchup_config, iter
            )

        results, _ = get_avg_matchup_diversity_score(
            self.best_matchup_config, len(self.players), self.weights_and_metrics
        )

        return (
            self.best_matchup_config,
            self.min_score,
            results,
            self.best_scores,
            self.best_scores_iterations,
        )

    def sample_matchups(self) -> List[Matchup]:
        """
        Sample matchups from the player pool ensuring no player is repeated in the current round.
        """
        while True:
            selected_players = np.random.choice(
                self.players, replace=False, size=4 * self.num_fields
            ).tolist()
            temp_matchups = [
                Matchup.from_names(*selected_players[j * 4 : j * 4 + 4])
                for j in range(self.num_fields)
            ]

            if not self.has_duplicate_matchups(temp_matchups):
                return temp_matchups

    def has_duplicate_matchups(self, matchups: List[Matchup]) -> bool:
        """
        Check if any matchup has been repeated.
        """
        unique_identifiers = set()
        for matchup in matchups:
            identifier = matchup.get_unique_identifier()
            if identifier in unique_identifiers:
                return True
            unique_identifiers.add(identifier)
        return False

    def update_best_score(
        self,
        matchups: List[Matchup],
        min_score: float,
        best_matchup_set: List[Matchup],
        iter: int,
    ) -> Tuple[List[Matchup], float]:
        """
        Update the best score and configuration if the current score is lower than the minimum score.
        """
        results, score = get_avg_matchup_diversity_score(
            matchups, len(self.players), self.weights_and_metrics
        )

        if score < min_score:
            best_matchup_set = deepcopy(matchups)
            min_score = score
            self.best_scores.append(min_score)
            self.best_scores_iterations.append(iter)
            print("Got new minimal index: ", min_score)

        return best_matchup_set, min_score
