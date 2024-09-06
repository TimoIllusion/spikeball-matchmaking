from typing import List
import os
from pathlib import Path

import pandas as pd

from matchmaking.data import Matchup, Team, Player


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
