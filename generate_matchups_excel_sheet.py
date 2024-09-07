from matchmaking.data import Player
from multiprocessing import Process, Manager
from matchmaking.generator import MatchupDiversityOptimizer
from matchmaking.export import export_to_excel, export_results_to_json
from matchmaking.visualizer import Visualizer
from config import *


def optimize_and_store_result(index, return_dict):
    players = [Player(p) for p in PLAYER_NAMES]

    optimizer = MatchupDiversityOptimizer(
        players, NUM_ROUNDS, NUM_FIELDS, NUM_ITERATIONS, METRIC_WEIGHTS_CONFIG
    )

    best_matchup_config, best_score, results, best_scores, best_scores_iterations = (
        optimizer.get_most_diverse_matchups()
    )

    return_dict[index] = {
        "best_matchup_config": best_matchup_config,
        "best_score": best_score,
        "results": results,
        "best_scores": best_scores,
        "best_scores_iterations": best_scores_iterations,
    }


def main():
    manager = Manager()
    return_dict = manager.dict()

    processes = []
    for i in range(WORKERS):
        p = Process(target=optimize_and_store_result, args=(i, return_dict))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    # Find the best result across all processes
    best_result = min(return_dict.values(), key=lambda x: x["best_score"])

    # Visualize and export the best result
    Visualizer.print_results_to_console(
        best_result["best_matchup_config"],
        NUM_FIELDS,
        NUM_ROUNDS,
        best_result["best_score"],
        best_result["results"],
        [Player(p) for p in PLAYER_NAMES],
    )

    best_scores_plot_img = Visualizer.plot_best_scores(
        best_result["best_scores"], best_result["best_scores_iterations"]
    )

    Visualizer.write_image(
        best_scores_plot_img,
        "output",
        f"best_scores_pl{len(PLAYER_NAMES)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_result['best_score']:.3f}",
    )

    export_results_to_json(
        best_result["results"],
        f"output/results_pl{len(PLAYER_NAMES)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_result['best_score']:.3f}.json",
    )

    export_to_excel(
        best_result["best_matchup_config"],
        [Player(p) for p in PLAYER_NAMES],
        NUM_FIELDS,
        f"output/matchups_with_points_and_format_pl{len(PLAYER_NAMES)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_result['best_score']:.3f}.xlsx",
    )


if __name__ == "__main__":

    print(f"Starting {WORKERS} processes for matchmaking...")

    main()

    print("Done")
