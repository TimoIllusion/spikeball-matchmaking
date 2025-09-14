from typing import List
import os
from pathlib import Path
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import cv2

from matchmaking.data import Matchup, Player
from matchmaking.metric_type import MetricType
from matchmaking.metrics import PlayerStatistics


class Visualizer:

    @staticmethod
    def plot_best_scores(
        best_scores: List[float],
        best_scores_iterations: List[float],
        out_dir: str,
        file_name: str,
    ) -> None:
        """
        Plot best scores over iterations and save directly to file.

        Args:
            best_scores: List of best score values
            best_scores_iterations: List of iteration numbers corresponding to best scores
            out_dir: Directory to save plot
            file_name: File name without extension
        """
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(10, 6))
        plt.plot(
            best_scores_iterations,
            best_scores,
            "b-",
            linewidth=2,
            marker="o",
            markersize=4,
        )
        plt.title("Best Scores Over Iterations", fontsize=14, fontweight="bold")
        plt.xlabel("Iteration", fontsize=12)
        plt.ylabel("Score (lower is better)", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(out_path / f"{file_name}.png", dpi=150)
        plt.close()

    @staticmethod
    def print_results_to_console(
        best_matchup_set: List[Matchup],
        num_fields: int,
        num_rounds: int,
        min_score: float,
        results: dict,
        players: List[Player],
    ) -> None:

        pprint(results)

        print("====== MATCHUPS ======")
        print()

        for i in range(num_rounds):
            # create a fixed distance (similar to tabs) between the reound and field text
            print("Round", i + 1, end=" | ")
            temp_playing_players_uids = []
            for j in range(num_fields):
                matchup = best_matchup_set[i * num_fields + j]

                print(
                    f"Field {j}:",
                    matchup.get_unique_identifier(),
                    end=" | ",
                )

                temp_playing_players_uids += matchup.get_all_player_uids()

            not_playing_players = []
            for player in players:
                if player.get_unique_identifier() not in temp_playing_players_uids:
                    not_playing_players.append(player)

            print("Break Field:", not_playing_players)

        print()
        print("====== STATS ======")
        print()

        global_results = results["global"]

        print(
            MetricType.GLOBAL_PLAYED_MATCHES_INDEX.name,
            global_results[MetricType.GLOBAL_PLAYED_MATCHES_INDEX.value],
        )
        print()

        for player in players:
            player_uid = player.get_unique_identifier()

            player_stats: PlayerStatistics = results[player_uid]

            print(
                f"Player {player_uid} - Unique players not played with or against: {player_stats.num_unique_people_not_played_with_or_against}"
            )

        print()

        for player in players:
            player_uid = player.get_unique_identifier()

            player_stats: PlayerStatistics = results[player_uid]

            print(
                f"Player {player_uid} - Consecutive teammates: {player_stats.consecutive_teammates_total}"
            )

            print(
                f"Player {player_uid} - Unique poeple not played with: {player_stats.num_unique_people_not_played_with}"
            )

            print(
                f"Player {player_uid} - Unique people not played against: {player_stats.num_unique_people_not_played_against}"
            )

        print()
        print("====== OVERALL ======")
        print()
        print("Total rating (lower is better):", min_score)
