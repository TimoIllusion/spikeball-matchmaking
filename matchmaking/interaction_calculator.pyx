import numpy as np
cimport numpy as np

def calculate_player_interactions_c(np.ndarray[np.int32_t, ndim=3] teammates, np.ndarray[np.int32_t, ndim=4] enemies):
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
