from abc import ABC, abstractmethod
from typing import List

import numpy as np

from matchmaking.data import Player, Matchup, Team
from matchmaking.metrics import get_total_matchup_set_score
from matchmaking.config import MetricWeightsConfig


class MatchupOptimizer(ABC):

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

        for i, player in enumerate(self.players):
            player.assign_numeric_identifier(i)

        assert (
            self.player_uids_are_unique()
        ), "Player UIDs are not unique! Maybe some names are part of other names? (e.g. 'John' and 'Johnny')"

    def player_uids_are_unique(self) -> bool:
        player_uids = [player.get_unique_identifier() for player in self.players]

        for i in range(len(player_uids)):

            reference_player_uid = player_uids[i]

            for j in range(len(player_uids)):
                if i == j:
                    continue

                if reference_player_uid in player_uids[j]:
                    return False

        return True

    @abstractmethod
    def get_most_diverse_matchups():
        pass
