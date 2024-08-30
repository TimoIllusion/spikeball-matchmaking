from matchmaking.data import Player
from multiprocessing import Process
from matchmaking.generator import get_most_diverse_matchups
from matchmaking.utils import export_to_excel
from config import *


def main():

    players = [Player(p) for p in PLAYER_NAMES]

    best_matchup_config, best_score, results = get_most_diverse_matchups(
        players, NUM_ROUNDS, NUM_FIELDS, NUM_ITERATIONS, WEIGHT_METRIC_CONFIG
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
