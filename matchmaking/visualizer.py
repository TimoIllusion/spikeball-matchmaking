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
        best_scores: List[float], best_scores_iterations: List[float]
    ) -> np.ndarray:

        plt.plot(best_scores_iterations, best_scores)
        plt.title("Best Scores")

        plt.draw()
        canvas = plt.gca().figure.canvas
        canvas.draw()

        image = np.frombuffer(canvas.buffer_rgba(), dtype="uint8")
        image = image.reshape(canvas.get_width_height()[::-1] + (4,))

        plt.close()

        return image

    @staticmethod
    def write_image(image: np.ndarray, out_dir: str, file_name: str) -> None:

        out_dir = Path(out_dir)

        os.makedirs(out_dir, exist_ok=True)

        out_path = out_dir / (file_name + ".png")

        cv2.imwrite(out_path, image)

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
