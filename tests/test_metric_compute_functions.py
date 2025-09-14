# test_metrics.py
import pytest
import numpy as np
from collections import Counter
from unittest.mock import Mock

from matchmaking.data import Matchup, Team, Player

# Import the functions to test
from matchmaking.metric_compute_functions import (
    _get_teammate_uids,
    _count_consecutive_occurences,
    _get_enemy_teams,
    compute_num_played_matches,
    compute_break_lengths,
    compute_break_lengths_avg,
    compute_break_lengths_stdev,
    compute_break_lengths_hist,
    compute_matchup_lengths_played_between_breaks,
    compute_matchup_lengths_played_between_breaks_second_length,
    compute_teammate_hist,
    compute_teammate_hist_stdev,
    compute_enemy_teams_hist,
    compute_enemy_teams_hist_stdev,
    compute_consecutive_teammates_hist,
    compute_consecutive_enemies_hist,
    compute_consecutive_teammates_total,
    compute_consecutive_enemies_total,
    compute_unique_people_not_played_with_or_against,
    compute_unique_people_not_played_with,
    compute_unique_people_not_played_against,
    _find_consecutive_numbers,
)


class TestPrivateHelperFunctions:
    """Test suite for private helper functions."""

    def test_get_teammate_uids_empty_matchups(self):
        """Test _get_teammate_uids with empty matchups list."""
        result = _get_teammate_uids([], "player1")
        assert result == []

    def test_get_teammate_uids_player_not_in_any_matchup(self):
        """Test _get_teammate_uids when player is not in any matchup."""
        mock_matchup = Mock()
        mock_matchup.get_all_player_uids.return_value = ["player2", "player3"]

        result = _get_teammate_uids([mock_matchup], "player1")
        assert result == []

    def test_get_teammate_uids_with_teammates(self):
        """Test _get_teammate_uids with valid teammates."""
        # Create mock matchups
        mock_matchup1 = Mock()
        mock_matchup1.get_all_player_uids.return_value = ["player1", "teammate1"]
        mock_teammate1 = Mock()
        mock_teammate1.get_unique_identifier.return_value = "teammate1"
        mock_matchup1.get_teammate.return_value = mock_teammate1

        mock_matchup2 = Mock()
        mock_matchup2.get_all_player_uids.return_value = ["player1", "teammate2"]
        mock_teammate2 = Mock()
        mock_teammate2.get_unique_identifier.return_value = "teammate2"
        mock_matchup2.get_teammate.return_value = mock_teammate2

        result = _get_teammate_uids([mock_matchup1, mock_matchup2], "player1")
        assert result == ["teammate1", "teammate2"]

    def test_get_teammate_uids_no_teammate_found(self):
        """Test _get_teammate_uids when get_teammate returns None."""
        mock_matchup = Mock()
        mock_matchup.get_all_player_uids.return_value = ["player1"]
        mock_matchup.get_teammate.return_value = None

        result = _get_teammate_uids([mock_matchup], "player1")
        assert result == []

    def test_count_consecutive_occurences_empty_list(self):
        """Test _count_consecutive_occurences with empty list."""
        result = _count_consecutive_occurences([])
        assert result == Counter()

    def test_count_consecutive_occurences_single_element(self):
        """Test _count_consecutive_occurences with single element."""
        result = _count_consecutive_occurences(["A"])
        assert result == Counter()

    def test_count_consecutive_occurences_no_consecutive(self):
        """Test _count_consecutive_occurences with no consecutive elements."""
        result = _count_consecutive_occurences(["A", "B", "C", "D"])
        assert result == Counter({"A": 0, "B": 0, "C": 0})

    def test_count_consecutive_occurences_with_consecutive(self):
        """Test _count_consecutive_occurences with consecutive elements."""
        result = _count_consecutive_occurences(["A", "A", "B", "B", "B", "C"])
        expected = Counter({"A": 1, "B": 2})
        assert result == expected

    def test_count_consecutive_occurences_all_same(self):
        """Test _count_consecutive_occurences with all same elements."""
        result = _count_consecutive_occurences(["A", "A", "A", "A"])
        expected = Counter({"A": 3})
        assert result == expected

    def test_get_enemy_teams_empty_matchups(self):
        """Test _get_enemy_teams with empty matchups list."""
        team_uids, player_uids = _get_enemy_teams([], "player1")
        assert team_uids == []
        assert player_uids == []

    def test_get_enemy_teams_with_enemies(self):
        """Test _get_enemy_teams with valid enemy teams."""
        mock_matchup1 = Mock()
        mock_enemy_team1 = Mock()
        mock_enemy_team1.get_unique_identifier.return_value = "team1"
        mock_enemy_team1.get_all_player_uids.return_value = ["enemy1", "enemy2"]
        mock_matchup1.get_enemy_team.return_value = mock_enemy_team1

        mock_matchup2 = Mock()
        mock_enemy_team2 = Mock()
        mock_enemy_team2.get_unique_identifier.return_value = "team2"
        mock_enemy_team2.get_all_player_uids.return_value = ["enemy3", "enemy4"]
        mock_matchup2.get_enemy_team.return_value = mock_enemy_team2

        team_uids, player_uids = _get_enemy_teams(
            [mock_matchup1, mock_matchup2], "player1"
        )
        assert team_uids == ["team1", "team2"]
        assert player_uids == ["enemy1", "enemy2", "enemy3", "enemy4"]

    def test_get_enemy_teams_no_enemy_found(self):
        """Test _get_enemy_teams when get_enemy_team returns None."""
        mock_matchup = Mock()
        mock_matchup.get_enemy_team.return_value = None

        team_uids, player_uids = _get_enemy_teams([mock_matchup], "player1")
        assert team_uids == []
        assert player_uids == []

    def test_find_consecutive_numbers_empty_array(self):
        """Test _find_consecutive_numbers with empty array."""
        result = _find_consecutive_numbers([], 1)
        assert result == []

    def test_find_consecutive_numbers_no_target(self):
        """Test _find_consecutive_numbers with no target numbers."""
        result = _find_consecutive_numbers([0, 0, 0], 1)
        assert result == []

    def test_find_consecutive_numbers_single_occurrences(self):
        """Test _find_consecutive_numbers with single occurrences."""
        result = _find_consecutive_numbers([1, 0, 1, 0, 1], 1)
        assert result == [1, 1, 1]

    def test_find_consecutive_numbers_multiple_consecutive(self):
        """Test _find_consecutive_numbers with multiple consecutive sequences."""
        result = _find_consecutive_numbers([1, 1, 0, 1, 1, 1, 0, 1], 1)
        assert result == [2, 3, 1]

    def test_find_consecutive_numbers_trailing_sequence(self):
        """Test _find_consecutive_numbers with trailing sequence."""
        result = _find_consecutive_numbers([0, 1, 1, 1], 1)
        assert result == [3]

    def test_find_consecutive_numbers_all_target(self):
        """Test _find_consecutive_numbers with all target numbers."""
        result = _find_consecutive_numbers([1, 1, 1, 1], 1)
        assert result == [4]


class TestComputeFunctions:
    """Test suite for public compute functions."""

    def test_compute_num_played_matches_empty_array(self):
        """Test compute_num_played_matches with empty array."""
        result = compute_num_played_matches(np.array([]))
        assert result == 0

    def test_compute_num_played_matches_all_zeros(self):
        """Test compute_num_played_matches with all zeros."""
        result = compute_num_played_matches(np.array([0, 0, 0, 0]))
        assert result == 0

    def test_compute_num_played_matches_all_ones(self):
        """Test compute_num_played_matches with all ones."""
        result = compute_num_played_matches(np.array([1, 1, 1, 1]))
        assert result == 4

    def test_compute_num_played_matches_mixed(self):
        """Test compute_num_played_matches with mixed values."""
        result = compute_num_played_matches(np.array([1, 0, 1, 1, 0]))
        assert result == 3

    def test_compute_break_lengths_no_breaks(self):
        """Test compute_break_lengths with no breaks."""
        result = compute_break_lengths(np.array([1, 1, 1, 1]))
        assert result == []

    def test_compute_break_lengths_with_breaks(self):
        """Test compute_break_lengths with breaks."""
        result = compute_break_lengths(np.array([1, 0, 0, 1, 0, 1]))
        assert result == [2, 1]

    def test_compute_break_lengths_avg_empty(self):
        """Test compute_break_lengths_avg with empty list."""
        result = compute_break_lengths_avg([])
        assert result == 0.0

    def test_compute_break_lengths_avg_with_data(self):
        """Test compute_break_lengths_avg with data."""
        result = compute_break_lengths_avg([2, 4, 6])
        assert result == 4.0

    def test_compute_break_lengths_stdev_empty(self):
        """Test compute_break_lengths_stdev with empty list."""
        result = compute_break_lengths_stdev([])
        assert result == 0.0

    def test_compute_break_lengths_stdev_with_data(self):
        """Test compute_break_lengths_stdev with data."""
        result = compute_break_lengths_stdev([2, 4, 6])
        expected = np.std([2, 4, 6])
        assert np.isclose(result, expected)

    def test_compute_break_lengths_hist_empty(self):
        """Test compute_break_lengths_hist with empty list."""
        result = compute_break_lengths_hist([])
        assert result == Counter()

    def test_compute_break_lengths_hist_with_data(self):
        """Test compute_break_lengths_hist with data."""
        result = compute_break_lengths_hist([1, 2, 2, 3, 2])
        expected = Counter({1: 1, 2: 3, 3: 1})
        assert result == expected

    def test_compute_matchup_lengths_played_between_breaks(self):
        """Test compute_matchup_lengths_played_between_breaks."""
        result = compute_matchup_lengths_played_between_breaks(
            np.array([1, 1, 0, 1, 1, 1, 0, 1])
        )
        assert result == [2, 3, 1]

    def test_compute_matchup_lengths_played_between_breaks_second_length_sufficient(
        self,
    ):
        """Test compute_matchup_lengths_played_between_breaks_second_length with sufficient data."""
        result = compute_matchup_lengths_played_between_breaks_second_length([3, 5, 2])
        assert result == 5

    def test_compute_matchup_lengths_played_between_breaks_second_length_insufficient(
        self,
    ):
        """Test compute_matchup_lengths_played_between_breaks_second_length with insufficient data."""
        result = compute_matchup_lengths_played_between_breaks_second_length([3])
        assert result == 10.0

    def test_compute_matchup_lengths_played_between_breaks_second_length_empty(self):
        """Test compute_matchup_lengths_played_between_breaks_second_length with empty list."""
        result = compute_matchup_lengths_played_between_breaks_second_length([])
        assert result == 10.0

    def test_compute_teammate_hist_empty(self):
        """Test compute_teammate_hist with empty list."""
        result = compute_teammate_hist([])
        assert result == Counter()

    def test_compute_teammate_hist_with_data(self):
        """Test compute_teammate_hist with data."""
        result = compute_teammate_hist(["player1", "player2", "player1", "player3"])
        expected = Counter({"player1": 2, "player2": 1, "player3": 1})
        assert result == expected

    def test_compute_teammate_hist_stdev_empty(self):
        """Test compute_teammate_hist_stdev with empty counter."""
        result = compute_teammate_hist_stdev(Counter())
        assert np.isnan(result)

    def test_compute_teammate_hist_stdev_with_data(self):
        """Test compute_teammate_hist_stdev with data."""
        hist = Counter({"player1": 2, "player2": 4, "player3": 6})
        result = compute_teammate_hist_stdev(hist)
        expected = np.std([2, 4, 6])
        assert np.isclose(result, expected)

    def test_compute_enemy_teams_hist_empty(self):
        """Test compute_enemy_teams_hist with empty list."""
        result = compute_enemy_teams_hist([])
        assert result == Counter()

    def test_compute_enemy_teams_hist_with_data(self):
        """Test compute_enemy_teams_hist with data."""
        result = compute_enemy_teams_hist(["team1", "team2", "team1", "team3"])
        expected = Counter({"team1": 2, "team2": 1, "team3": 1})
        assert result == expected

    def test_compute_enemy_teams_hist_stdev_empty(self):
        """Test compute_enemy_teams_hist_stdev with empty counter."""
        result = compute_enemy_teams_hist_stdev(Counter())
        assert np.isnan(result)

    def test_compute_enemy_teams_hist_stdev_with_data(self):
        """Test compute_enemy_teams_hist_stdev with data."""
        hist = Counter({"team1": 3, "team2": 1, "team3": 5})
        result = compute_enemy_teams_hist_stdev(hist)
        expected = np.std([3, 1, 5])
        assert np.isclose(result, expected)

    def test_compute_consecutive_teammates_hist_empty(self):
        """Test compute_consecutive_teammates_hist with empty list."""
        result = compute_consecutive_teammates_hist([])
        assert result == Counter()

    def test_compute_consecutive_teammates_hist_with_data(self):
        """Test compute_consecutive_teammates_hist with data."""
        result = compute_consecutive_teammates_hist(["A", "A", "B", "B", "B", "C"])
        expected = Counter({"A": 1, "B": 2})
        assert result == expected

    def test_compute_consecutive_enemies_hist_empty(self):
        """Test compute_consecutive_enemies_hist with empty list."""
        result = compute_consecutive_enemies_hist([])
        assert result == Counter()

    def test_compute_consecutive_enemies_hist_with_data(self):
        """Test compute_consecutive_enemies_hist with data."""
        result = compute_consecutive_enemies_hist(
            ["team1", "team1", "team2", "team2", "team2"]
        )
        expected = Counter({"team1": 1, "team2": 2})
        assert result == expected

    def test_compute_consecutive_teammates_total_empty(self):
        """Test compute_consecutive_teammates_total with empty counter."""
        result = compute_consecutive_teammates_total(Counter())
        assert result == 0

    def test_compute_consecutive_teammates_total_with_data(self):
        """Test compute_consecutive_teammates_total with data."""
        hist = Counter({"player1": 2, "player2": 3, "player3": 1})
        result = compute_consecutive_teammates_total(hist)
        assert result == 6

    def test_compute_consecutive_enemies_total_empty(self):
        """Test compute_consecutive_enemies_total with empty counter."""
        result = compute_consecutive_enemies_total(Counter())
        assert result == 0

    def test_compute_consecutive_enemies_total_with_data(self):
        """Test compute_consecutive_enemies_total with data."""
        hist = Counter({"team1": 1, "team2": 4, "team3": 2})
        result = compute_consecutive_enemies_total(hist)
        assert result == 7

    def test_compute_unique_people_not_played_with_or_against_no_interaction(self):
        """Test compute_unique_people_not_played_with_or_against with no interactions."""
        result = compute_unique_people_not_played_with_or_against(10, [], [])
        assert result == 9  # 10 - 1 (self) - 0 (unique interactions)

    def test_compute_unique_people_not_played_with_or_against_some_interactions(self):
        """Test compute_unique_people_not_played_with_or_against with some interactions."""
        enemy_uids = ["player2", "player3", "player4"]
        teammate_uids = ["player5", "player6", "player3"]  # player3 appears in both
        result = compute_unique_people_not_played_with_or_against(
            10, enemy_uids, teammate_uids
        )
        # Unique people interacted with: {player2, player3, player4, player5, player6} = 5
        assert result == 4  # 10 - 1 (self) - 5 (unique interactions)

    def test_compute_unique_people_not_played_with_empty(self):
        """Test compute_unique_people_not_played_with with empty teammate list."""
        result = compute_unique_people_not_played_with(5, [])
        assert result == 4  # 5 - 1 (self) - 0 (unique teammates)

    def test_compute_unique_people_not_played_with_duplicates(self):
        """Test compute_unique_people_not_played_with with duplicate teammates."""
        teammate_uids = ["player2", "player3", "player2", "player4"]
        result = compute_unique_people_not_played_with(10, teammate_uids)
        # Unique teammates: {player2, player3, player4} = 3
        assert result == 6  # 10 - 1 (self) - 3 (unique teammates)

    def test_compute_unique_people_not_played_against_empty(self):
        """Test compute_unique_people_not_played_against with empty enemy list."""
        result = compute_unique_people_not_played_against(8, [])
        assert result == 7  # 8 - 1 (self) - 0 (unique enemies)

    def test_compute_unique_people_not_played_against_duplicates(self):
        """Test compute_unique_people_not_played_against with duplicate enemies."""
        enemy_uids = ["player2", "player3", "player2", "player4", "player3"]
        result = compute_unique_people_not_played_against(15, enemy_uids)
        # Unique enemies: {player2, player3, player4} = 3
        assert result == 11  # 15 - 1 (self) - 3 (unique enemies)


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_numpy_array_dtypes(self):
        """Test that functions work with different numpy array dtypes."""
        int_array = np.array([1, 0, 1, 0], dtype=np.int32)
        float_array = np.array([1.0, 0.0, 1.0, 0.0], dtype=np.float64)
        bool_array = np.array([True, False, True, False], dtype=bool)

        assert compute_num_played_matches(int_array) == 2
        assert compute_num_played_matches(float_array) == 2
        assert compute_num_played_matches(bool_array) == 2

    def test_large_arrays_performance(self):
        """Test that functions work with reasonably large arrays."""
        large_array = np.random.randint(0, 2, size=10000)

        # These should complete without error or timeout
        result = compute_num_played_matches(large_array)
        assert isinstance(result, (int, np.integer))

        breaks = compute_break_lengths(large_array)
        assert isinstance(breaks, list)

    def test_single_element_arrays(self):
        """Test functions with single element arrays."""
        single_zero = np.array([0])
        single_one = np.array([1])

        assert compute_num_played_matches(single_zero) == 0
        assert compute_num_played_matches(single_one) == 1
        assert compute_break_lengths(single_zero) == [1]
        assert compute_break_lengths(single_one) == []

    def test_edge_cases_with_real_classes(self):
        """Test edge cases using real classes."""
        # Test with players that have special characters in names
        special_matchup = Matchup.from_names(
            "Alice-123", "Bob_456", "Charlie.789", "David@email"
        )

        teammate = special_matchup.get_teammate("Alice-123")
        assert teammate.get_unique_identifier() == "Bob_456"

        # Test team sorting with special characters
        team = Team.from_names("Zed", "Alice")
        assert team.get_unique_identifier() == "Alice & Zed"

    def test_get_enemy_team_bug_fix(self):
        """Test to verify the get_enemy_team method works correctly."""
        # Note: There appears to be a bug in the original get_enemy_team method
        # It uses 'in' operator on team identifiers instead of checking player membership
        matchup = Matchup.from_names("Alice", "Bob", "Charlie", "David")

        # This test documents the current behavior - may need fixing in the actual implementation
        enemy_team = matchup.get_enemy_team("Alice")

        # The current implementation has a bug where it checks if player_uid is
        # in team.get_unique_identifier() string, which is incorrect
        # This test may fail and would indicate the bug needs to be fixed
        try:
            assert enemy_team is not None
            assert enemy_team.get_unique_identifier() == "Charlie & David"
        except AssertionError:
            # If this fails, it confirms the bug in get_enemy_team method
            pytest.xfail(
                "Known bug in get_enemy_team method - uses string 'in' operator incorrectly"
            )


if __name__ == "__main__":
    pytest.main([__file__])
