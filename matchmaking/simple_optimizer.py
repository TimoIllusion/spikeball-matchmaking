from pprint import pprint
from copy import deepcopy
from typing import List, Tuple, Optional

from tqdm import tqdm
import numpy as np

from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_total_matchup_set_score
from matchmaking.config import MetricWeightsConfig
from matchmaking.optimizer import MatchupOptimizer


class SimpleMatchupOptimizer(MatchupOptimizer):

    def __init__(
        self,
        players: List[Player],
        num_rounds: int,
        num_fields: int,
        num_iterations: int,
        weights_and_metrics: MetricWeightsConfig,
    ):
        super().__init__(
            players, num_rounds, num_fields, num_iterations, weights_and_metrics
        )

        self.best_scores: List[float] = []
        self.best_scores_iterations: List[int] = []
        self.min_score: float = np.inf
        self.best_matchup_config: Optional[List[Matchup]] = None

    def get_most_diverse_matchups(
        self,
    ) -> Tuple[List[Matchup], float, dict, List[float], List[int]]:

        for iter in tqdm(range(self.num_iterations)):
            matchup_history = set()
            matchups: List[Matchup] = []

            for _ in range(self.num_rounds):
                temp_matchups = self.sample_matchups(matchup_history)
                matchup_history.update(m.get_unique_identifier() for m in temp_matchups)
                matchups.extend(temp_matchups)

            self.best_matchup_config, self.min_score = self.update_best_score(
                matchups, self.min_score, self.best_matchup_config, iter
            )

        results, _ = get_total_matchup_set_score(
            self.best_matchup_config,
            len(self.players),
            self.weights_and_metrics,
            self.num_fields,
        )

        return (
            self.best_matchup_config,
            self.min_score,
            results,
            self.best_scores,
            self.best_scores_iterations,
        )

    def sample_matchups(self, matchup_history: set) -> List[Matchup]:
        """
        Sample matchups ensuring no player is repeated in the current round,
        and that no matchup has appeared in previous rounds.
        """
        player_names = [player.name for player in self.players]

        while True:
            selected_players = np.random.choice(
                player_names, replace=False, size=4 * self.num_fields
            ).tolist()

            temp_matchups = [
                Matchup.from_names(*selected_players[j * 4 : j * 4 + 4])
                for j in range(self.num_fields)
            ]

            ids = [m.get_unique_identifier() for m in temp_matchups]

            # Must be unique in current round and across history
            if len(ids) == len(set(ids)) and not any(i in matchup_history for i in ids):
                return temp_matchups

    def has_duplicate_matchups(self, matchups: List[Matchup]) -> bool:
        """
        Check if any matchup list contains duplicates.
        """
        seen = set()
        for m in matchups:
            if m.get_unique_identifier() in seen:
                return True
            seen.add(m.get_unique_identifier())
        return False

    def update_best_score(
        self,
        matchups: List[Matchup],
        min_score: float,
        best_matchup_set: Optional[List[Matchup]],
        iter: int,
    ) -> Tuple[List[Matchup], float]:
        """
        Update the best score and configuration if the current score is lower than the minimum score.
        """
        results, score = get_total_matchup_set_score(
            matchups, len(self.players), self.weights_and_metrics, self.num_fields
        )

        if score < min_score:
            best_matchup_set = deepcopy(matchups)
            min_score = score
            self.best_scores.append(min_score)
            self.best_scores_iterations.append(iter)
            print("Got new minimal score:", min_score)

        return best_matchup_set, min_score
