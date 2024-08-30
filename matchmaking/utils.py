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

        team1_str = matchup.team_a.get_unique_identifier()
        team2_str = matchup.team_b.get_unique_identifier()
        row = [i + 1, f"Field {i%num_fields}", team1_str, "VS", team2_str]
        row += [None]  # spacer
        row += [None]  # sets team 1 result
        row += [None]  # sets team 2 result
        row += [None]  # spacer

        team1_player_uids = matchup.team_a.get_all_player_uids()
        team2_player_uids = matchup.team_b.get_all_player_uids()
        playing_status = []

        for player in [x.get_unique_identifier() for x in players]:
            if player in team1_player_uids:
                playing_status.append(-1)
            elif player in team2_player_uids:
                playing_status.append(-2)
            else:
                playing_status.append(0)

        row += playing_status

        df_list.append(row)

    column_names = [
        "Round",
        "Field",
        "Team 1",
        "VS",
        "Team 2",
        "",
        "Sets Team 1",
        "Sets Team 2",
        "",
    ] + players
    df = pd.DataFrame(df_list, columns=column_names)
    df.to_excel(out_path, index=False)
