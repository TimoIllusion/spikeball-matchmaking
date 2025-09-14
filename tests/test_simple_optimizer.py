import unittest

from matchmaking.data import Player, Matchup, Team
from matchmaking.config import MetricWeightsConfig
from matchmaking.simple_optimizer import SimpleMatchupOptimizer


class TestSimpleMatchupOptimizer(unittest.TestCase):
    def setUp(self):
        self.players = [
            Player(name) for name in ["Jannik", "Timo", "Dascha", "Marc", "Ben"]
        ]
        self.weights = MetricWeightsConfig()
        self.optimizer = SimpleMatchupOptimizer(
            players=self.players,
            num_rounds=5,
            num_fields=1,
            num_iterations=50,
            weights_and_metrics=self.weights,
        )

    def test_sample_matchups_unique_in_round(self):
        matchup_history = set()
        matchups = self.optimizer.sample_matchups(matchup_history)
        ids = [m.get_unique_identifier() for m in matchups]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate matchup in one round")

    def test_no_repeat_across_rounds(self):
        matchup_history = set()
        all_ids = []
        for _ in range(5):
            matchups = self.optimizer.sample_matchups(matchup_history)
            ids = [m.get_unique_identifier() for m in matchups]
            for i in ids:
                self.assertNotIn(i, matchup_history, "Matchup repeated across rounds")
            matchup_history.update(ids)
            all_ids.extend(ids)
        self.assertEqual(
            len(all_ids), len(set(all_ids)), "Duplicate matchups across rounds"
        )

    def test_enemy_team_lookup(self):
        matchup = Matchup.from_names("Jannik", "Timo", "Marc", "Ben")
        enemy_team = matchup.get_enemy_team("Jannik")
        self.assertIsNotNone(enemy_team)
        self.assertIn("Marc", enemy_team.get_all_player_uids())
        self.assertIn("Ben", enemy_team.get_all_player_uids())


if __name__ == "__main__":
    unittest.main()
