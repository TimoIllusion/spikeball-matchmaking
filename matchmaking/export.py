from typing import List
import os
from pathlib import Path
import json
from copy import deepcopy

import pandas as pd
import numpy as np

from matchmaking.data import Matchup, Team, Player
from matchmaking.metrics import PlayerStatistics


def export_results_to_json(results: dict, out_path: str):
    out_dir = Path(out_path).parent
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    results_jsonified = {}

    results_jsonified["global"] = deepcopy(results["global"])
    results_jsonified["global"] = (
        convert_npint64_and_npfloat64_to_int_and_float_in_dict(
            results_jsonified["global"]
        )
    )

    for key in results.keys():
        if key == "global":
            continue
        else:
            results_jsonified[key] = deepcopy(results[key]).jsonify()

    # Write the results to a JSON file
    with open(out_path, "w") as f:
        json.dump(results_jsonified, f, indent=4)


def convert_npint64_and_npfloat64_to_int_and_float_in_dict(data: dict) -> dict:
    for key, value in data.items():
        if isinstance(value, np.int64):
            data[key] = int(value)

        elif isinstance(value, np.float64):
            data[key] = float(value)

    return data


# TODO: add point differences to excel sheet and respective formula (not just points that someone has made on their team side!)
def export_to_excel(
    matchups: List[Matchup], players: List[Player], num_fields: int, out_path: str
):

    out_dir = Path(out_path).parent
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Create a DataFrame and write it to an Excel file

    df_list = []
    for i, matchup in enumerate(matchups):

        team1_player_1_str = matchup.team_a.player_1.get_unique_identifier()
        team1_player_2_str = matchup.team_a.player_2.get_unique_identifier()
        team2_player_1_str = matchup.team_b.player_1.get_unique_identifier()
        team2_player_2_str = matchup.team_b.player_2.get_unique_identifier()
        row = [
            i // num_fields,
            f"Field {i%num_fields}",
            team1_player_1_str,
            team1_player_2_str,
            "vs.",
            team2_player_1_str,
            team2_player_2_str,
        ]
        row += [None]  # spacer
        row += [None]  # sets team 1 result
        row += [None]  # sets team 2 result
        row += [None]  # spacer

        for player_id, _ in enumerate(players):
            if i == 0 and player_id == 0:
                row += [
                    "'=IF(OR($C2=L$1; $D2=L$1); IF($I2>$J2; 3; IF($I2=$J2; 1; 0)); IF(OR($F2=L$1; $G2=L$1); IF($J2>$I2; 3; IF($I2=$J2; 1; 0)); 0))"
                ]
            else:
                row += [
                    None
                ]  # empty cells for each player, later used for result points

        df_list.append(row)

    df_list.append([None] * 10 + ["Summe"] + [f"=SUM(L2:L{len(matchups)+1})"])  # spacer

    column_names = [
        "Round",
        "Field",
        "Team 1",
        "Team 1",
        "VS",
        "Team 2",
        "Team 2",
        "",
        "Points Team 1",
        "Points Team 2",
        "",
    ] + players
    df = pd.DataFrame(df_list, columns=column_names)
    df.to_excel(out_path, index=False)
