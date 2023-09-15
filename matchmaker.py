# Matchmake people for 2v2 games. Permutes through all possible combinations of players and returns the best match with some guidelines:
# 1. Players should not play with the same person twice in a row (but may)
# 2. Players should not play against the same team twice in a row (but may)
# 3. If more or less people than amount of fields, then some people will have to sit out -> but try to minimize this OR completely neutralize it (will increase rounds sometimes)

from itertools import combinations
from collections import deque, Counter
from random import shuffle
import pandas as pd

NUM_PLAYERS = 10 #14
PLAYERS = ['Player' + str(i) for i in range(1, NUM_PLAYERS + 1)]
MAX_ROUNDS = 15
FIELDS = 2

APPROX_TIME_PER_ROUND_MINUTES = 10
TIME_FOR_BREAKS_AFTER_EACH_ROUND_MINUTES = 5


def calculate_amount_of_unique_matchups(players):
    # Generate all combinations of 2 players to form a team
    all_teams = list(combinations(players, 2))

    unique_matchups_set = set()

    for team1 in all_teams:
        remaining_players = [p for p in players if p not in team1]
        
        # Generate combinations of 2 players for the second team from the remaining players
        opponent_teams = list(combinations(remaining_players, 2))

        for team2 in opponent_teams:
            # Sort the teams to avoid duplicate matchups (Team A vs Team B == Team B vs Team A)
            matchup = tuple(sorted([team1, team2]))
            
            unique_matchups_set.add(matchup)

    return unique_matchups_set





def generate_matchups(players, fields, max_rounds):
    all_teams = list(combinations(players, 2))
    shuffle(all_teams)
    
    rounds = []
    breaks = Counter({player: 0 for player in players})
    break_queue = deque(players)

    for rnd in range(1, max_rounds + 1):
        # Determine who should take a break this round
        num_players = len(players)
        num_playing = fields * 4
        num_breaks = num_players - num_playing

        break_players = [break_queue.popleft() for _ in range(num_breaks)]
        for player in break_players:
            break_queue.append(player)
            breaks[player] += 1

        # Check if all breaks are equal
        if len(set(breaks.values())) == 1 and list(breaks.values())[0] != 0:
            print(f"Warning: All breaks are equal after Round {rnd}")

        # Form teams for this round
        available_players = [p for p in players if p not in break_players]
        shuffle(available_players)
        round_teams = []

        for _ in range(fields):
            field_teams = []
            for team in list(all_teams):
                if all(player in available_players for player in team):
                    field_teams.append(team)
                    for player in team:
                        available_players.remove(player)
                    all_teams.remove(team)
                if len(field_teams) == 2:
                    break
            if len(field_teams) == 2:
                round_teams.append(field_teams)
        rounds.append(round_teams)
        
        # Add the used teams back for future rounds
        all_teams.extend([team for field in round_teams for team in field])
        
    return rounds


def main():
    players = PLAYERS 
    fields = FIELDS  # 3 fields
    max_rounds = MAX_ROUNDS  # 10 rounds
    
    print("Number of players:", len(players))
    
    result = calculate_amount_of_unique_matchups(players)

    # Output the number of unique matchups
    print("Number of unique matchups:", len(result))
    # print("Unique matchups:", result)

    # Fair mode
    rounds = generate_matchups(players, fields, max_rounds)
    for i, rnd in enumerate(rounds):
        print(f"Round {i+1}: {rnd}")

    total_duration = len(rounds) * (APPROX_TIME_PER_ROUND_MINUTES + TIME_FOR_BREAKS_AFTER_EACH_ROUND_MINUTES)
    hours = total_duration // 60
    minutes = total_duration % 60
    duration_str = f"{hours}h{minutes}min"
    print(f"Total approx. time: {hours} h {minutes} min")
    
    
    # Create a DataFrame and write it to an Excel file        
    df_list = []
    for i, rnd in enumerate(rounds):
        for j, field in enumerate(rnd):
            team1_str = f"{field[0][0]} & {field[0][1]}"
            team2_str = f"{field[1][0]} & {field[1][1]}"
            row = [i+1, f"Field {j+1}", team1_str, "VS", team2_str]
            row += [None]  # For the spacer column
            
            team1_players = set(field[0])
            team2_players = set(field[1])
            playing_status = []
            
            for player in players:
                if player in team1_players:
                    playing_status.append(-1)
                elif player in team2_players:
                    playing_status.append(-2)
                else:
                    playing_status.append(0)
            
            row += playing_status
            
            df_list.append(row)

    column_names = ['Round', 'Field', 'Team 1', 'VS', 'Team 2', ''] + players
    df = pd.DataFrame(df_list, columns=column_names)
    df.to_excel(f'matchups_with_points_and_format_{NUM_PLAYERS}pl_{duration_str}.xlsx', index=False)
        
    
if __name__ == '__main__':
    main()