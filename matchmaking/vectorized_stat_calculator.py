from typing import List, Tuple
import time

import numpy as np
import torch
import torch.nn.functional as F
from numba import jit

from matchmaking.interaction_calculator import calculate_player_interactions_c


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
    def compute_break_lengths_and_match_lengths(
        played_matches_tensor: np.ndarray,
    ) -> Tuple[List[List[List[int]]], List[List[List[int]]]]:
        """
        Computes break lengths and match lengths for each player using PyTorch for convolution to detect consecutive breaks
        and Numba for post-processing.

        Args:
            played_matches_tensor (np.ndarray): Input tensor of shape (num_sessions, num_rounds, num_fields, num_players_per_field, num_players)

        Returns:
            Tuple: Two lists (break lengths per player and match lengths per player), each of shape (num_sessions, num_players, dynamic_lengths)
        """
        # Move the played_matches_tensor to GPU
        played_matches_tensor_torch = torch.tensor(played_matches_tensor).cuda()

        # Get the dynamic dimensions from the input tensor
        num_sessions, num_rounds, num_fields, num_players_per_field, num_players = (
            played_matches_tensor_torch.shape
        )

        # Sum across fields (axis=2) and players in each field (axis=3)
        player_rounds = torch.sum(
            played_matches_tensor_torch, dim=(2, 3)
        )  # Shape: (num_sessions, num_rounds, num_players)

        # Invert the tensor to track breaks (1 for break, 0 for played)
        inverted_rounds = (player_rounds == 0).float()

        # Reshape: flatten player dimension into the batch dimension
        reshaped_rounds = inverted_rounds.permute(0, 2, 1).reshape(
            -1, 1, inverted_rounds.size(1)
        )  # Shape: (num_sessions * num_players, 1, num_rounds)

        # Create a convolution kernel to detect consecutive breaks
        kernel = torch.ones(2, device="cuda").view(
            1, 1, -1
        )  # Kernel to detect consecutive breaks

        # Apply 1D convolution along the rounds dimension
        convolved = F.conv1d(
            reshaped_rounds, kernel, padding=1
        )  # Shape: (num_sessions * num_players, 1, num_rounds)

        # Reshape back to (num_sessions, num_players, num_rounds) for post-processing
        convolved = convolved.view(num_sessions, num_players, -1)

        # Move the convolved data back to CPU for post-processing
        convolved = convolved.cpu().numpy()

        # Call Numba-accelerated post-processing function
        break_lengths_per_player, match_lengths_per_player = (
            VectorizedStatCalculator._postprocess_break_and_match_lengths(convolved)
        )

        return break_lengths_per_player, match_lengths_per_player

    @staticmethod
    @jit(nopython=True)
    def _postprocess_break_and_match_lengths(
        convolved_output: np.ndarray,
    ) -> Tuple[List[List[List[int]]], List[List[List[int]]]]:
        """
        Post-processes the convolved output to compute the lengths of consecutive breaks and the matches played between breaks for each player.

        Args:
            convolved_output: A NumPy array of shape (num_sessions, num_players, num_rounds), which is the output of the convolution.

        Returns:
            A tuple of nested lists where each configuration has the list of break lengths and the list of match lengths for each player.
        """
        # Initialize empty lists to store break lengths and match lengths for each configuration and player
        break_lengths_per_player = []
        match_lengths_per_player = []

        # Iterate over configurations (10000)
        for config in range(convolved_output.shape[0]):
            player_breaks = []
            player_matches = []

            # Iterate over players (13)
            for player in range(convolved_output.shape[1]):
                convolved_values = convolved_output[config, player, :]

                break_lengths = []
                match_lengths = []
                current_break_length = 0
                current_match_length = 0

                # Iterate through the convolved values for the player
                for value in convolved_values:
                    if value == 2:  # Detected a break (two consecutive breaks)
                        if current_match_length > 0:
                            match_lengths.append(current_match_length)
                            current_match_length = 0
                        current_break_length += 1
                    else:  # Detected a match
                        if current_break_length > 0:
                            break_lengths.append(current_break_length)
                            current_break_length = 0
                        current_match_length += 1

                # Handle trailing breaks or matches at the end
                if current_break_length > 0:
                    break_lengths.append(current_break_length)
                if current_match_length > 0:
                    match_lengths.append(current_match_length)

                player_breaks.append(break_lengths)
                player_matches.append(match_lengths)

            break_lengths_per_player.append(player_breaks)
            match_lengths_per_player.append(player_matches)

        return break_lengths_per_player, match_lengths_per_player

    @staticmethod
    @jit(nopython=True)
    # TODO: maybe use cpython for this instead of numba
    def compute_teammates_and_enemies(
        sessions_tensor: np.ndarray, num_players: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the teammates and enemies for each player across all rounds and sessions. For each player,
        return a vector of length `num_rounds`, where:
          - [..., 0] contains the teammate ID,
          - [..., 1:3] contains the IDs of the two enemies.
        If the player had a break, the values will be [-1, -1, -1].

        Args:
            sessions_tensor (np.ndarray): Tensor of shape (num_sessions, num_rounds, num_fields, 4)
                                          where each entry represents player IDs.
            num_players (int): Total number of unique players.

        Returns:
            np.ndarray: Two NumPy arrays, one of shape (num_sessions, num_players, num_rounds) and
                        one of shape (num_sessions, num_players, num_rounds, 2).
        """

        num_sessions, num_rounds, num_fields, _ = sessions_tensor.shape

        # Initialize the output array with -1 to represent breaks
        result_array = -1 * np.ones(
            (num_sessions, num_players, num_rounds, 3), dtype=np.int32
        )

        # Iterate over all sessions, rounds, and fields to find teammates and enemies
        for session in range(num_sessions):
            for round_num in range(num_rounds):
                for field in range(num_fields):
                    # Get the four players in this field
                    players_in_field = sessions_tensor[session, round_num, field]

                    # Team 1: Players in positions 0 and 1 are teammates, enemies are players 2 and 3
                    player_0, player_1, player_2, player_3 = players_in_field

                    # Assign teammate and enemies for player_0
                    result_array[session, player_0, round_num, 0] = player_1  # Teammate
                    result_array[session, player_0, round_num, 1] = (
                        player_2  # First enemy
                    )
                    result_array[session, player_0, round_num, 2] = (
                        player_3  # Second enemy
                    )

                    # Assign teammate and enemies for player_1
                    result_array[session, player_1, round_num, 0] = player_0  # Teammate
                    result_array[session, player_1, round_num, 1] = (
                        player_2  # First enemy
                    )
                    result_array[session, player_1, round_num, 2] = (
                        player_3  # Second enemy
                    )

                    # Assign teammate and enemies for player_2
                    result_array[session, player_2, round_num, 0] = player_3  # Teammate
                    result_array[session, player_2, round_num, 1] = (
                        player_0  # First enemy
                    )
                    result_array[session, player_2, round_num, 2] = (
                        player_1  # Second enemy
                    )

                    # Assign teammate and enemies for player_3
                    result_array[session, player_3, round_num, 0] = player_2  # Teammate
                    result_array[session, player_3, round_num, 1] = (
                        player_0  # First enemy
                    )
                    result_array[session, player_3, round_num, 2] = (
                        player_1  # Second enemy
                    )

        # split up tensor by last axis to get teammates and enemies
        teammates = result_array[:, :, :, 0]
        enemies = result_array[:, :, :, 1:]

        return (
            teammates,  # Shape: (num_sessions, num_players, num_rounds)
            enemies,  # Shape: (num_sessions, num_players, num_rounds, 2)
        )

    @staticmethod
    @jit(nopython=True)
    def calculate_player_interactions_numba(
        teammates: np.ndarray, enemies: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes three datasets PER SESSION:
        1. per_player_unique_people_not_played_with_or_against: Unique people each player has not played with or against.
        2. per_player_unique_people_not_played_with: Unique people each player has not played with as teammates.
        3. per_player_unique_people_not_played_against: Unique people each player has not played against.

        Args:
            teammates (np.ndarray): A NumPy array of shape (num_sessions, num_players, num_rounds), where each entry
                                    contains the ID of the teammate in that round, or -1 if no teammate was present.
            enemies (np.ndarray): A NumPy array of shape (num_sessions, num_players, num_rounds, 2), where each entry
                                  contains the IDs of the enemies in that round, or -1 if no enemies were present.

        Returns:
            Tuple containing three NumPy arrays, each of shape (num_sessions, num_players):
                - per_player_unique_people_not_played_with_or_against
                - per_player_unique_people_not_played_with
                - per_player_unique_people_not_played_against
        """

        num_sessions, num_players, num_rounds = teammates.shape

        # Initialize result matrices for interactions PER session
        per_player_unique_people_not_played_with_or_against = np.zeros(
            (num_sessions, num_players), dtype=np.int32
        )
        per_player_unique_people_not_played_with = np.zeros(
            (num_sessions, num_players), dtype=np.int32
        )
        per_player_unique_people_not_played_against = np.zeros(
            (num_sessions, num_players), dtype=np.int32
        )

        # Step 1: Loop through each session to calculate player interactions
        for session in range(num_sessions):
            played_with = np.zeros((num_players, num_players), dtype=np.bool_)
            played_against = np.zeros((num_players, num_players), dtype=np.bool_)

            # Track teammates interactions for this session
            for player in range(num_players):
                for round_num in range(num_rounds):
                    teammate = teammates[session, player, round_num]
                    if teammate != -1:
                        played_with[player, teammate] = True

            # Track enemy interactions for this session
            for player in range(num_players):
                for round_num in range(num_rounds):
                    enemy_1, enemy_2 = enemies[session, player, round_num]
                    if enemy_1 != -1:
                        played_against[player, enemy_1] = True
                    if enemy_2 != -1:
                        played_against[player, enemy_2] = True

            # Step 2: Calculate the number of people each player has not played with or against in this session
            played_with_or_against = played_with | played_against

            total_players = num_players
            per_player_unique_people_not_played_with[session] = total_players - np.sum(
                played_with, axis=1
            )
            per_player_unique_people_not_played_against[session] = (
                total_players - np.sum(played_against, axis=1)
            )
            per_player_unique_people_not_played_with_or_against[session] = (
                total_players - np.sum(played_with_or_against, axis=1)
            )

        return (
            per_player_unique_people_not_played_with_or_against,
            per_player_unique_people_not_played_with,
            per_player_unique_people_not_played_against,
        )

    # Cython implementation
    @staticmethod
    def calculate_player_interactions(
        teammates: np.ndarray, enemies: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes three datasets:
        1. per_player_unique_people_not_played_with_or_against: Unique people each player has not played with or against.
        2. per_player_unique_people_not_played_with: Unique people each player has not played with as teammates.
        3. per_player_unique_people_not_played_against: Unique people each player has not played against.

        Args:
            teammates (np.ndarray): A NumPy array of shape (num_sessions, num_players, num_rounds), where each entry
                                    contains the ID of the teammate in that round, or -1 if no teammate was present.
            enemies (np.ndarray): A NumPy array of shape (num_sessions, num_players, num_rounds, 2), where each entry
                                  contains the IDs of the enemies in that round, or -1 if no enemies were present.

        Returns:
            Tuple containing three NumPy arrays, each of shape (num_players,):
                - per_player_unique_people_not_played_with_or_against
                - per_player_unique_people_not_played_with
                - per_player_unique_people_not_played_against
        """
        teammates = teammates.astype(np.int32)
        enemies = enemies.astype(np.int32)

        result = calculate_player_interactions_c(teammates, enemies)

        return result
