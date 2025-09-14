import datetime

from matchmaking.data import Player
from multiprocessing import Process, Manager
from matchmaking.simple_optimizer import SimpleMatchupOptimizer
from matchmaking.export import export_to_excel, export_results_to_json
from matchmaking.visualizer import Visualizer
from config import *


def optimize_and_store_result(index, return_dict):

    players = [Player(p) for p in PLAYER_NAMES]

    optimizer = SimpleMatchupOptimizer(
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


def check_if_even_break_distribution_is_possible():
    ## validation checks
    print("Num players", len(PLAYER_NAMES))
    break_players_per_round = len(PLAYER_NAMES) % (NUM_FIELDS * 4)
    print("Break players per round", break_players_per_round)
    assert (break_players_per_round * NUM_ROUNDS) % len(PLAYER_NAMES) == 0, (
        f"Number of total break players is not divisible by the number of players. "
        f"Break players per round: {break_players_per_round}, "
        f"Total break players: {break_players_per_round * NUM_ROUNDS}, "
        f"Players: {len(PLAYER_NAMES)}. "
        f"There is no option to distribute breaks evenly!"
    )


def check_if_num_players_is_sufficient_for_num_fields():
    assert (
        len(PLAYER_NAMES) >= NUM_FIELDS * 4
    ), "Not enough players for the given number of fields!"


def main():
    manager = Manager()
    return_dict = manager.dict()

    check_if_num_players_is_sufficient_for_num_fields()
    check_if_even_break_distribution_is_possible()

    while True:
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

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = "output"
        out_file_name = f"{timestamp}_matchups_pl{len(PLAYER_NAMES)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_result['best_score']:.3f}"

        best_scores_plot_img = Visualizer.plot_best_scores(
            best_result["best_scores"],
            best_result["best_scores_iterations"],
            out_dir,
            out_file_name,
        )

        export_results_to_json(
            best_result["results"],
            f"{out_dir}/{out_file_name}.json",
        )

        export_to_excel(
            best_result["best_matchup_config"],
            [Player(p) for p in PLAYER_NAMES],
            NUM_FIELDS,
            f"{out_dir}/{out_file_name}.xlsx",
        )

        if not RETRY_IF_NOT_ALL_PLAYERS_EQUAL_NUM_MATCHES:
            break

        # stop criterium: all players play the same amount of matches
        if (
            best_result["results"]["global"][
                MetricType.GLOBAL_PLAYED_MATCHES_INDEX.value
            ]
            == 0.0
            and best_result["results"]["global"][
                MetricType.GLOBAL_NOT_PLAYED_WITH_OR_AGAINST_PLAYERS_INDEX.value
            ]
            == 0.0
        ):
            print("Requirement met: All players play the same amount of matches.")
            break
        else:
            print("Requirement not met: Repeating the optimization process...")


if __name__ == "__main__":

    print(f"Starting {WORKERS} processes for matchmaking...")

    main()

    print("Done")
