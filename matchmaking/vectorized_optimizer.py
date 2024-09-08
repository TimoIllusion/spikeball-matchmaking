from typing import List

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


@dataclass
class Session:
    mathchups: List[Matchup] = field(default_factory=list)


class VectorizedStatCalculator:

    @staticmethod
    def prepare_played_matches_tensor(
        sessions_tensor: np.ndarray, num_players: int
    ) -> np.ndarray:
        """
        Compute a representation that shows the played matches over all players in all sessions and give back a suitable tensor.
        It is assumed that the player IDs are unique and start from 0.

        Args:
            sessions_tensor (np.ndarray): Tensor of shape (num_sessions, num_rounds, num_fields, 4)

        Returns:
            np.ndarray: Tensor of shape (...)
        """

        player_ids = np.arange(num_players)  # All player IDs from 0 to num_players-1

        # check if min and max of tensor is qeual to player_ids min and max
        assert np.min(sessions_tensor) >= np.min(player_ids), "Player ID mismatch!"
        assert np.max(sessions_tensor) <= np.max(player_ids), "Player ID mismatch!"

        # Create a new axis for player IDs and compare each match entry with all player IDs at once
        # The resulting tensor has shape (100, 10, 3, 4, num_players), where it's True if player is present
        played_matches = (sessions_tensor[..., np.newaxis] == player_ids).astype(int)
        return played_matches  # Shape: (100, 10, 3, 4, num_players)

    @staticmethod
    def compute_played_matches(played_matches_tensor: np.ndarray) -> np.ndarray:
        total_played_matches_per_player = np.sum(played_matches_tensor, axis=(1, 2, 3))
        return total_played_matches_per_player  # Shape: (num_sessions, num_players)

    @staticmethod
    def compute_break_lengths(played_matches_tensor: np.ndarray) -> np.ndarray:
        """
        Computes break lengths for each player using PyTorch for convolution to detect consecutive breaks
        and Numba for post-processing.
        """
        # Move to GPU
        played_matches_tensor_torch = torch.tensor(played_matches_tensor).cuda()

        # Sum across fields (axis=2) and players in each field (axis=3)
        # Resulting shape will be (10000, 10, 13) -> (configs, rounds, players)
        player_rounds = torch.sum(
            played_matches_tensor_torch, dim=(2, 3)
        )  # Shape: (10000, 10, 13)

        # Invert the tensor to track breaks (1 for break, 0 for played)
        inverted_rounds = (player_rounds == 0).float()

        # Reshape: flatten player dimension into the batch dimension
        # Now shape is (10000 * 13, 1, 10)
        reshaped_rounds = inverted_rounds.permute(0, 2, 1).reshape(
            -1, 1, inverted_rounds.size(1)
        )

        # Create a convolution kernel to detect consecutive breaks
        kernel = torch.ones(2, device="cuda").view(
            1, 1, -1
        )  # Kernel to detect consecutive breaks

        # Apply 1D convolution along the rounds dimension
        convolved = F.conv1d(
            reshaped_rounds, kernel, padding=1
        )  # Shape (10000 * 13, 1, 10)

        # Reshape back to (10000, 13, 10) for post-processing
        convolved = convolved.view(10000, 13, -1)

        # Move the convolved data back to CPU for post-processing
        convolved = convolved.cpu().numpy()

        # Call Numba-accelerated post-processing function
        break_lengths_per_player = VectorizedStatCalculator._postprocess_break_lengths(
            convolved
        )

        return break_lengths_per_player

    @staticmethod
    @jit(nopython=True)
    def _postprocess_break_lengths(
        convolved_output: np.ndarray,
    ) -> List[List[List[int]]]:
        """
        Post-processes the convolved output to compute the lengths of consecutive breaks for each player.

        Args:
            convolved_output: A NumPy array of shape (num_sessions, num_players, num_rounds), which is the output of the convolution.

        Returns:
            A nested list where each configuration has the list of break lengths for each player.
        """
        # Initialize an empty list to store the break lengths for each configuration and player
        break_lengths_per_player = []

        # Iterate over configurations (10000)
        for config in range(convolved_output.shape[0]):
            player_breaks = []

            # Iterate over players (13)
            for player in range(convolved_output.shape[1]):
                convolved_values = convolved_output[config, player, :]

                break_lengths = []
                current_break_length = 0

                # Iterate through the convolved values for the player
                for value in convolved_values:
                    if value == 2:  # Detected two consecutive breaks
                        current_break_length += 1
                    else:
                        if current_break_length > 0:
                            break_lengths.append(current_break_length)
                        current_break_length = 0

                # Handle trailing break at the end
                if current_break_length > 0:
                    break_lengths.append(current_break_length)

                player_breaks.append(break_lengths)

            break_lengths_per_player.append(player_breaks)

        # Return the result as a Python list (more flexible for jagged data)
        return break_lengths_per_player


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
