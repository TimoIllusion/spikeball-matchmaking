from typing import List, Tuple

from dataclasses import dataclass, field

import torch
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm
from numba import jit

from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_total_matchup_set_score
from matchmaking.config import MetricWeightsConfig
from matchmaking.optimizer import MatchupOptimizer

from matchmaking.vectorized_stat_calculator import VectorizedStatCalculator


@dataclass
class Session:
    mathchups: List[Matchup] = field(default_factory=list)


class VectorizedMatchupOptimizer(MatchupOptimizer):

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

        self.player_ids = [player.unique_numeric_identifier for player in players]

    def get_most_diverse_matchups():
        pass

        # generate N random session matchup configs (N = num_iterations)
        # calculate score for each config in parallel
        # find best scoring config

    def generate_n_matchup_configs(self, num_configs: int) -> List[List[np.ndarray]]:
        sessions = []
        for _ in tqdm(range(num_configs)):
            session = self.sample_one_session(
                self.num_rounds, self.num_fields, self.player_ids
            )
            sessions.append(session)

        return sessions

    def convert_nested_matchup_config_list_to_tensor(
        self, sessions_np_lists: List[List[np.ndarray]]
    ) -> np.ndarray:

        sessions_np_reshaped = np.array(sessions_np_lists)

        # reshape to num_samples_sessions x num_rounds x num_fields x 4 (because 4 players per field)
        sessions_np_reshaped = np.reshape(
            sessions_np_reshaped,
            (len(sessions_np_lists), self.num_rounds, self.num_fields, 4),
        )

        return sessions_np_reshaped

    @staticmethod
    def sample_one_session(
        num_rounds: int, num_fields: int, player_ids: List[int]
    ) -> List[np.ndarray]:

        matchups_for_one_session = []
        for _ in range(num_rounds):
            one_matchup = np.random.choice(
                player_ids, replace=False, size=4 * num_fields
            )
            matchups_for_one_session.append(one_matchup)

        return matchups_for_one_session
