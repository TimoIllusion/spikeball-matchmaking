import pandas as pd
from collections import Counter
import sys


def normalize_matchup(matchup_str):
    """Normalize a matchup string to detect duplicates regardless of team order."""
    # Split by "vs."
    parts = matchup_str.split(" vs. ")
    if len(parts) != 2:
        return matchup_str  # Return as-is if format is unexpected

    team1 = sorted(parts[0].split())
    team2 = sorted(parts[1].split())

    # Sort teams lexicographically
    teams = sorted([team1, team2])
    return f"{' '.join(teams[0])} vs. {' '.join(teams[1])}"


def extract_players(matchup_str):
    """Extract all player names from a matchup string."""
    return matchup_str.replace(" vs. ", " ").split()


def check_tournament_excel(file_path):
    """Check Excel tournament file for duplicates and fair play."""
    print(f"Analyzing tournament file: {file_path}")
    print("=" * 60)

    # Read Excel file
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    print("Available columns:", list(df.columns))

    # Look for team columns - there are 4 columns for 4 players
    team1_cols = []
    team2_cols = []

    # Find all columns that contain team data
    for col in df.columns:
        col_str = str(col)
        if col_str == "Team 1" or col_str.startswith("Team 1"):
            team1_cols.append(col)
        elif col_str == "Team 2" or col_str.startswith("Team 2"):
            team2_cols.append(col)

    print(f"Found Team 1 columns: {team1_cols}")
    print(f"Found Team 2 columns: {team2_cols}")

    if len(team1_cols) < 2 or len(team2_cols) < 2:
        print("❌ Expected at least 2 columns for Team 1 and 2 columns for Team 2")
        print("Your Excel should have 4 player columns (2 per team)")
        return

    # Take first 2 columns for each team
    team1_col1, team1_col2 = team1_cols[0], team1_cols[1]
    team2_col1, team2_col2 = team2_cols[0], team2_cols[1]

    print(f"Using columns: {team1_col1}, {team1_col2} vs {team2_col1}, {team2_col2}")

    # Combine the 4 player columns to create matchups
    matchups = []
    for idx, row in df.iterrows():
        # Get all 4 players
        p1 = str(row[team1_col1]).strip() if pd.notna(row[team1_col1]) else ""
        p2 = str(row[team1_col2]).strip() if pd.notna(row[team1_col2]) else ""
        p3 = str(row[team2_col1]).strip() if pd.notna(row[team2_col1]) else ""
        p4 = str(row[team2_col2]).strip() if pd.notna(row[team2_col2]) else ""

        # Only create matchup if all 4 players are present
        if all([p1, p2, p3, p4]) and all([p != "nan" for p in [p1, p2, p3, p4]]):
            team1_str = f"{p1} {p2}"
            team2_str = f"{p3} {p4}"
            matchup = f"{team1_str} vs. {team2_str}"
            matchups.append(matchup)

    print(f"Total matchups found: {len(matchups)}")

    if not matchups:
        print("No matchups found to analyze")
        return

    # Display first few matchups for verification
    print("\nFirst few matchups:")
    for i, matchup in enumerate(matchups[:3]):
        print(f"  {i}: {matchup}")

    # Show sample of raw data for verification
    print(f"\nSample raw data from first few rows:")
    for i in range(min(3, len(df))):
        p1 = df.iloc[i][team1_col1] if pd.notna(df.iloc[i][team1_col1]) else "NaN"
        p2 = df.iloc[i][team1_col2] if pd.notna(df.iloc[i][team1_col2]) else "NaN"
        p3 = df.iloc[i][team2_col1] if pd.notna(df.iloc[i][team2_col1]) else "NaN"
        p4 = df.iloc[i][team2_col2] if pd.notna(df.iloc[i][team2_col2]) else "NaN"
        print(f"  Row {i}: [{p1} {p2}] vs [{p3} {p4}]")

    # Check for duplicates
    print("\n1. CHECKING FOR DUPLICATE MATCHES:")
    print("-" * 40)

    normalized_matchups = [normalize_matchup(m) for m in matchups]
    matchup_counts = Counter(normalized_matchups)
    duplicates = {k: v for k, v in matchup_counts.items() if v > 1}

    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate match(es):")
        for matchup, count in duplicates.items():
            print(f"  '{matchup}' appears {count} times")
    else:
        print("✅ No duplicate matches found!")

    # Check player game counts
    print("\n2. CHECKING PLAYER GAME DISTRIBUTION:")
    print("-" * 40)

    player_counts = Counter()
    for matchup in matchups:
        players = extract_players(matchup)
        for player in players:
            player_counts[player] += 1

    if not player_counts:
        print("No players found in matchups")
        return

    # Display player counts
    print("Games per player:")
    for player, count in sorted(player_counts.items()):
        print(f"  {player}: {count} games")

    # Check if distribution is fair
    game_counts = list(player_counts.values())
    min_games = min(game_counts)
    max_games = max(game_counts)

    if min_games == max_games:
        print(f"✅ Fair distribution: All players play {min_games} games")
    else:
        print(f"❌ Unfair distribution: Games range from {min_games} to {max_games}")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Total players: {len(player_counts)}")
    print(f"  Total matches: {len(matchups)}")
    print(f"  Duplicates: {'Yes' if duplicates else 'No'}")
    print(f"  Fair play: {'Yes' if min_games == max_games else 'No'}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tournament_checker.py <excel_file_path>")
        print("Example: python tournament_checker.py tournament.xlsx")
    else:
        check_tournament_excel(sys.argv[1])
