from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import cv2
import PIL

from matchmaking.data import Player
from multiprocessing import Process
from matchmaking.generator import MatchupDiversityOptimizer
from matchmaking.utils import export_to_excel
from matchmaking.visualizer import Visualizer

from config import *


def main():

    players = [Player(p) for p in PLAYER_NAMES]

    optimizer = MatchupDiversityOptimizer(
        players, NUM_ROUNDS, NUM_FIELDS, NUM_ITERATIONS, METRIC_WEIGHTS_CONFIG
    )

    best_matchup_config, best_score, results, best_scores, best_scores_iterations = (
        optimizer.get_most_diverse_matchups()
    )

    best_scores_plot_img = Visualizer.plot_best_scores(
        best_scores, best_scores_iterations
    )

    Visualizer.write_image(
        best_scores_plot_img,
        "output",
        f"best_scores_pl{len(players)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_score:.3f}",
    )

    export_to_excel(
        best_matchup_config,
        players,
        NUM_FIELDS,
        f"output/matchups_with_points_and_format_pl{len(players)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_score:.3f}.xlsx",
    )


if __name__ == "__main__":

    print(f"Starting {WORKERS} processes for matchmatking...")

    processes = []
    for i in range(WORKERS):
        p = Process(target=main)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("Done")
