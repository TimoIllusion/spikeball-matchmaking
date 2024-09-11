import numpy as np
cimport numpy as np

def _calculate_player_interactions_c(np.ndarray[np.int32_t, ndim=3] teammates, np.ndarray[np.int32_t, ndim=4] enemies):
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
    cdef int num_sessions = teammates.shape[0]
    cdef int num_players = teammates.shape[1]
    cdef int num_rounds = teammates.shape[2]
    
    # Initialize result arrays for interactions PER session
    cdef np.ndarray[np.int32_t, ndim=2] per_player_unique_people_not_played_with_or_against = np.zeros((num_sessions, num_players), dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=2] per_player_unique_people_not_played_with = np.zeros((num_sessions, num_players), dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=2] per_player_unique_people_not_played_against = np.zeros((num_sessions, num_players), dtype=np.int32)
    
    # Loop through each session to calculate player interactions
    cdef np.ndarray[np.uint8_t, ndim=2] played_with, played_against
    cdef int session, player, round_num, teammate, enemy_1, enemy_2

    for session in range(num_sessions):
        # Reset interaction arrays for each session
        played_with = np.zeros((num_players, num_players), dtype=np.uint8)
        played_against = np.zeros((num_players, num_players), dtype=np.uint8)

        # Track teammates interactions for this session
        for player in range(num_players):
            for round_num in range(num_rounds):
                teammate = teammates[session, player, round_num]
                if teammate != -1:
                    played_with[player, teammate] = 1

        # Track enemy interactions for this session
        for player in range(num_players):
            for round_num in range(num_rounds):
                enemy_1 = enemies[session, player, round_num, 0]
                enemy_2 = enemies[session, player, round_num, 1]
                if enemy_1 != -1:
                    played_against[player, enemy_1] = 1
                if enemy_2 != -1:
                    played_against[player, enemy_2] = 1

        # Calculate people not played with or against in this session
        played_with_or_against = played_with | played_against
        total_players = num_players

        # Update result arrays per session
        per_player_unique_people_not_played_with[session] = total_players - np.sum(played_with, axis=1)
        per_player_unique_people_not_played_against[session] = total_players - np.sum(played_against, axis=1)
        per_player_unique_people_not_played_with_or_against[session] = total_players - np.sum(played_with_or_against, axis=1)
    
    return (
        per_player_unique_people_not_played_with_or_against,
        per_player_unique_people_not_played_with,
        per_player_unique_people_not_played_against
    )

def _compute_enemy_team_succession_index_c(np.ndarray[np.int32_t, ndim=4] enemies) -> np.ndarray:
    """
    Computes the enemy team succession index efficiently in Cython by calculating how often players faced the same
    enemy team in consecutive rounds, considering order-invariance (i.e., [1, 2] is the same as [2, 1]).
    Returns the sum of consecutive enemy team occurrences per player and computes
    the sum across players in each session.
    """
    cdef int num_sessions = enemies.shape[0]
    cdef int num_players = enemies.shape[1]
    cdef int num_rounds = enemies.shape[2]

    # Initialize an array to store the number of consecutive enemy team occurrences for each player
    cdef np.ndarray[np.float32_t, ndim=2] consecutive_enemies = np.zeros((num_sessions, num_players), dtype=np.float32)

    # Step 1: Iterate over sessions, players, and rounds to check for consecutive enemies
    cdef int session, player, round_num
    cdef int current_enemy1, current_enemy2, prev_enemy1, prev_enemy2

    for session in range(num_sessions):
        for player in range(num_players):
            # Compare consecutive rounds
            for round_num in range(1, num_rounds):
                # Extract enemies from current and previous rounds
                current_enemy1 = enemies[session, player, round_num, 0]
                current_enemy2 = enemies[session, player, round_num, 1]
                prev_enemy1 = enemies[session, player, round_num - 1, 0]
                prev_enemy2 = enemies[session, player, round_num - 1, 1]

                # Check if both rounds are valid (player played both rounds)
                if current_enemy1 != -1 and current_enemy2 != -1 and prev_enemy1 != -1 and prev_enemy2 != -1:
                    # Check for order-invariant equality
                    if (current_enemy1 == prev_enemy1 and current_enemy2 == prev_enemy2) or \
                       (current_enemy1 == prev_enemy2 and current_enemy2 == prev_enemy1):
                        consecutive_enemies[session, player] += 1

    # Step 2: Compute the sum of consecutive enemy team counts across all players for each session
    cdef np.ndarray[np.float32_t, ndim=1] enemy_team_succession_sum = np.zeros(num_sessions, dtype=np.float32)
    for session in range(num_sessions):
        enemy_team_succession_sum[session] = np.sum(consecutive_enemies[session])

    return enemy_team_succession_sum  # Shape: (num_sessions,)