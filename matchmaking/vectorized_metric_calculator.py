from typing import List

import numpy as np
from numba import jit

from matchmaking.timer import Timer
from matchmaking.metric_type import MetricType


class VectorizedMetricCalculator:
    def __init__(
        self,
        sessions,
        played_matches,
        break_lengths,
        match_lengths,
        teammates,
        enemies,
        per_player_unique_people_not_played_with_or_against,
        per_player_unique_people_not_played_with,
        per_player_unique_people_not_played_against,
    ):
        self.sessions = sessions
        self.played_matches = played_matches  # NumPy array: (num_sessions, num_players)
        self.break_lengths = break_lengths  # Nested list: num_sessions x num_players x dynamic (number of break sessions)
        self.match_lengths = match_lengths  # Nested list: num_sessions x num_players x dynamic (number of match sessions)
        self.teammates = (
            teammates  # NumPy array: (num_sessions, num_players, num_rounds)
        )
        self.enemies = (
            enemies  # NumPy array: (num_sessions, num_players, num_rounds, 2)
        )

        self.per_player_unique_people_not_played_with_or_against = (
            per_player_unique_people_not_played_with_or_against
        )
        self.per_player_unique_people_not_played_with = (
            per_player_unique_people_not_played_with
        )
        self.per_player_unique_people_not_played_against = (
            per_player_unique_people_not_played_against
        )

        self.num_sessions, self.num_rounds, self.num_fields, _ = sessions.shape

        # Weights per metric (hardcoded as per your request)
        self.weights = {
            MetricType.GLOBAL_NOT_PLAYING_PLAYERS_INDEX: 123456789.0,
            MetricType.GLOBAL_PLAYED_MATCHES_INDEX: 12345678.0,
            MetricType.GLOBAL_NOT_PLAYED_WITH_OR_AGAINST_PLAYERS_INDEX: 12345.0,
            MetricType.GLOBAL_MATCHUP_SESSION_LENGTH_BETWEEN_BREAKS_INDEX: 123.0,
            MetricType.GLOBAL_NOT_PLAYED_WITH_PLAYERS_INDEX: 123.0,
            MetricType.GLOBAL_TEAMMATE_VARIETY_INDEX: 123.0,
            MetricType.GLOBAL_TEAMMATE_SUCCESSION_INDEX: 123.0,
            MetricType.GLOBAL_PLAYER_ENGAGEMENT_FAIRNESS_INDEX: 12.0,
            MetricType.GLOBAL_ENEMY_TEAM_SUCCESSION_INDEX: 12.0,
            MetricType.GLOBAL_ENEMY_TEAM_VARIETY_INDEX: 12.0,
            MetricType.GLOBAL_BREAK_SHORTNESS_INDEX: 12.0,
            MetricType.GLOBAL_NOT_PLAYED_AGAINST_PLAYERS_INDEX: 12.0,
        }

    def compute_not_playing_players_index(self) -> np.ndarray:
        # check if anyone has not played in a session

        not_playing = self.played_matches == 0

        not_playing_index = np.sum(not_playing, axis=1)

        return not_playing_index  # Shape: (num_sessions,)

    def compute_played_matches_index(self) -> np.ndarray:
        """
        Computes the index by calculating the max possible matches minus the number of played matches for each player per session.
        The index per session is the standard deviation of these differences across all players.
        """

        # The maximum possible matches per player is equal to the number of rounds
        max_possible_matches = self.num_rounds

        # Calculate the difference between the max possible matches and the played matches
        difference = max_possible_matches - self.played_matches

        # Compute the standard deviation of the differences for each session (shape: num_sessions)
        played_matches_index_per_session = np.std(difference, axis=1)

        return played_matches_index_per_session  # Shape: (num_sessions,)

    def compute_break_shortness_index(self) -> np.ndarray:
        """
        Computes the break shortness index by calculating the sum of the squared break lengths of all players per session.
        """
        # Step 1: Find the maximum number of breaks any player had across all sessions
        max_breaks = max(
            len(player_breaks)
            for session in self.break_lengths
            for player_breaks in session
        )

        # Step 2: Pad each player's break lengths to match the max number of breaks
        # Create a 3D NumPy array where breaks are padded with zeros to make all arrays the same length
        padded_break_lengths = np.array(
            [
                [
                    np.pad(player_breaks, (0, max_breaks - len(player_breaks)))
                    for player_breaks in session
                ]
                for session in self.break_lengths
            ]
        )

        # Step 3: Compute the sum of squared break lengths per session
        # First, square all the padded break lengths, then sum across players and breaks
        break_lengths_squared = np.sum(np.square(padded_break_lengths), axis=(1, 2))

        # Return the resulting sum of squared break lengths for each session
        return break_lengths_squared  # Shape: (num_sessions,)

    def compute_teammate_variety_index(self) -> np.ndarray:
        """
        Computes the teammate variety index for each session by calculating the number of unique teammates each player had,
        and then computes the standard deviation of the variety across all players.
        """
        # self.teammates is assumed to be a NumPy array of shape (num_sessions, num_players, num_rounds)
        num_sessions, num_players, num_rounds = self.teammates.shape

        # Step 1: Reshape the teammates array to group rounds per player and session
        # This reshapes it to (num_sessions * num_players, num_rounds)
        teammates_flat = self.teammates.reshape(num_sessions * num_players, num_rounds)

        # Step 2: Mask out the rounds where the player did not play (represented by -1)
        valid_teammates = teammates_flat != -1

        # Step 3: Use np.apply_along_axis to compute the unique teammate count for each player in each session
        # For each row (player across rounds), apply np.unique to count unique teammates
        unique_teammates_count = np.array(
            [
                len(np.unique(teammates_flat[i, valid_teammates[i]]))
                for i in range(teammates_flat.shape[0])
            ]
        )

        # Step 4: Reshape the result back to (num_sessions, num_players)
        unique_teammates_count = unique_teammates_count.reshape(
            num_sessions, num_players
        )

        # Step 5: Compute the standard deviation of unique teammate counts for each session
        teammate_variety_std = np.std(unique_teammates_count, axis=1)

        return teammate_variety_std  # Shape: (num_sessions,)

    def compute_enemy_team_variety_index(self) -> np.ndarray:
        """
        Computes the enemy team variety index for each session by calculating the number of unique enemy teams each player faced.
        Then computes the standard deviation of the variety across all players per session.
        """
        # Assuming self.enemies is of shape (num_sessions, num_players, num_rounds, 2)
        num_sessions, num_players, num_rounds, _ = self.enemies.shape

        # Step 1: Flatten the enemy team data to (num_sessions * num_players, num_rounds, 2)
        enemies_flat = self.enemies.reshape(num_sessions * num_players, num_rounds, 2)

        # Step 2: Mask out rounds where the player did not play (marked by -1)
        valid_enemies_mask = enemies_flat != -1

        # Step 3: Create a unique identifier for each pair of enemies by using a tuple or hashing
        # Combine enemy pairs for each round into a single unique identifier (hash or tuple)
        enemy_pairs_flat = enemies_flat[:, :, 0] * num_players + enemies_flat[:, :, 1]

        # Step 4: Use np.apply_along_axis to count the unique enemy pairs per player, ignoring invalid rounds
        unique_enemy_teams_count = np.array(
            [
                len(
                    np.unique(
                        enemy_pairs_flat[
                            i, valid_enemies_mask[i][:, 0] & valid_enemies_mask[i][:, 1]
                        ]
                    )
                )
                for i in range(enemies_flat.shape[0])
            ]
        )

        # Step 5: Reshape the result back to (num_sessions, num_players)
        unique_enemy_teams_count = unique_enemy_teams_count.reshape(
            num_sessions, num_players
        )

        # Step 6: Compute the standard deviation of enemy team variety for each session
        enemy_team_variety_std = np.std(unique_enemy_teams_count, axis=1)

        return enemy_team_variety_std  # Shape: (num_sessions,)

    def compute_teammate_succession_index(self) -> np.ndarray:
        return self._compute_teammate_succession_index(self.teammates)

    @staticmethod
    @jit(nopython=True)
    def _compute_teammate_succession_index(teammates: np.ndarray) -> np.ndarray:
        """
        Computes the teammate succession index efficiently using Numba by calculating how often players had the same teammate
        in consecutive rounds. Returns the sum of consecutive teammate occurrences per player and then computes the standard
        deviation across players in each session.
        """
        num_sessions, num_players, num_rounds = teammates.shape

        # Initialize an array to store the number of consecutive teammate occurrences for each player
        consecutive_teammates = np.zeros((num_sessions, num_players), dtype=np.float32)

        # Step 1: Iterate over sessions, players, and rounds to check for consecutive teammates
        for session in range(num_sessions):
            for player in range(num_players):
                # Compare consecutive rounds
                for round_num in range(1, num_rounds):
                    if (
                        teammates[session, player, round_num] != -1
                        and teammates[session, player, round_num - 1] != -1
                    ):
                        if (
                            teammates[session, player, round_num]
                            == teammates[session, player, round_num - 1]
                        ):
                            consecutive_teammates[session, player] += 1

        # Step 2: Compute the sum of consecutive teammate counts across all players for each session
        teammate_succession_sum = np.zeros(num_sessions, dtype=np.float32)
        for session in range(num_sessions):
            teammate_succession_sum[session] = np.sum(consecutive_teammates[session])

        return teammate_succession_sum  # Shape: (num_sessions,)

    def compute_enemy_team_succession_index(self) -> np.ndarray:
        return self._compute_enemy_team_succession_index(self.enemies)

    @staticmethod
    @jit(nopython=True)
    def _compute_enemy_team_succession_index(enemies: np.ndarray) -> np.ndarray:
        """
        Computes the enemy team succession index efficiently using Numba by calculating how often players faced the same
        enemy team in consecutive rounds, considering order-invariance (i.e., [1, 2] is the same as [2, 1]).
        Returns the sum of consecutive enemy team occurrences per player and then computes
        the standard deviation across players in each session.
        """
        num_sessions, num_players, num_rounds, _ = enemies.shape

        # Initialize an array to store the number of consecutive enemy team occurrences for each player
        consecutive_enemies = np.zeros((num_sessions, num_players), dtype=np.float32)

        # Step 1: Iterate over sessions, players, and rounds to check for consecutive enemies
        for session in range(num_sessions):
            for player in range(num_players):
                # Compare consecutive rounds
                for round_num in range(1, num_rounds):
                    # Check if the player played both rounds
                    if (
                        enemies[session, player, round_num, 0] != -1
                        and enemies[session, player, round_num - 1, 0] != -1
                        and enemies[session, player, round_num, 1] != -1
                        and enemies[session, player, round_num - 1, 1] != -1
                    ):

                        # Sort both rounds' enemy pairs to account for order invariance
                        current_round = np.sort(enemies[session, player, round_num])
                        previous_round = np.sort(
                            enemies[session, player, round_num - 1]
                        )

                        # If the sorted pairs are the same, increment the counter
                        if np.array_equal(current_round, previous_round):
                            consecutive_enemies[session, player] += 1

        # Step 2: Compute the sum of consecutive enemy team counts across all players for each session
        enemy_team_succession_sum = np.zeros(num_sessions, dtype=np.float32)
        for session in range(num_sessions):
            enemy_team_succession_sum[session] = np.sum(consecutive_enemies[session])

        return enemy_team_succession_sum  # Shape: (num_sessions,)

    def compute_player_engagement_fairness_index(self) -> np.ndarray:
        """
        Computes the standard deviation of the number of people each player has not played with or against.
        """
        return np.std(
            self.per_player_unique_people_not_played_with_or_against, axis=1
        )  # Shape: (num_sessions,)

    def compute_not_played_with_or_against_players_index(self) -> np.ndarray:
        """
        Computes the sum of people each player has not played with or against.
        """
        return np.sum(
            self.per_player_unique_people_not_played_with_or_against, axis=1
        )  # Shape: (num_sessions,)

    def compute_not_played_with_players_index(self) -> np.ndarray:
        """
        Computes the sum of people each player has not played with.
        """
        return np.sum(
            self.per_player_unique_people_not_played_with, axis=1
        )  # Shape: (num_sessions,)

    def compute_not_played_against_players_index(self) -> np.ndarray:
        """
        Computes the sum of people each player has not played against.
        """
        return np.sum(
            self.per_player_unique_people_not_played_against, axis=1
        )  # Shape: (num_sessions,)

    def calculate_total_loss(self) -> np.ndarray:
        """Calculate the total loss for all sessions based on the weighted sum of metrics."""

        # Instantiate the Timer object
        timer = Timer()
        losses = np.zeros((self.num_sessions, 1))

        # Compute all metrics with timing
        timer.start("Not playing players index")
        losses += self.weights[
            MetricType.GLOBAL_NOT_PLAYING_PLAYERS_INDEX
        ] * self.compute_not_playing_players_index().reshape(-1, 1)
        timer.stop()

        timer.start("Played matches index")
        losses += self.weights[
            MetricType.GLOBAL_PLAYED_MATCHES_INDEX
        ] * self.compute_played_matches_index().reshape(-1, 1)
        timer.stop()

        timer.start("Not played with or against players index")
        losses += self.weights[
            MetricType.GLOBAL_NOT_PLAYED_WITH_OR_AGAINST_PLAYERS_INDEX
        ] * self.compute_not_played_with_or_against_players_index().reshape(-1, 1)
        timer.stop()

        timer.start("Not played with players index")
        losses += self.weights[
            MetricType.GLOBAL_NOT_PLAYED_WITH_PLAYERS_INDEX
        ] * self.compute_not_played_with_players_index().reshape(-1, 1)
        timer.stop()

        timer.start("Teammate variety index")
        losses += self.weights[
            MetricType.GLOBAL_TEAMMATE_VARIETY_INDEX
        ] * self.compute_teammate_variety_index().reshape(-1, 1)
        timer.stop()

        timer.start("Teammate succession index")
        losses += self.weights[
            MetricType.GLOBAL_TEAMMATE_SUCCESSION_INDEX
        ] * self.compute_teammate_succession_index().reshape(-1, 1)
        timer.stop()

        timer.start("Player engagement fairness index")
        losses += self.weights[
            MetricType.GLOBAL_PLAYER_ENGAGEMENT_FAIRNESS_INDEX
        ] * self.compute_player_engagement_fairness_index().reshape(-1, 1)
        timer.stop()

        timer.start("Enemy team succession index")
        losses += self.weights[
            MetricType.GLOBAL_ENEMY_TEAM_SUCCESSION_INDEX
        ] * self.compute_enemy_team_succession_index().reshape(-1, 1)
        timer.stop()

        timer.start("Enemy team variety index")
        losses += self.weights[
            MetricType.GLOBAL_ENEMY_TEAM_VARIETY_INDEX
        ] * self.compute_enemy_team_variety_index().reshape(-1, 1)
        timer.stop()

        timer.start("Break shortness index")
        losses += self.weights[
            MetricType.GLOBAL_BREAK_SHORTNESS_INDEX
        ] * self.compute_break_shortness_index().reshape(-1, 1)
        timer.stop()

        timer.start("Not played against players index")
        losses += self.weights[
            MetricType.GLOBAL_NOT_PLAYED_AGAINST_PLAYERS_INDEX
        ] * self.compute_not_played_against_players_index().reshape(-1, 1)
        timer.stop()

        return losses  # Shape: (10000, 1)
