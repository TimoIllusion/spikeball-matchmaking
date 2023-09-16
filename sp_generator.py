from matchmaking.data import Player
from matchmaking.generator import get_most_diverse_matchups
from matchmaking.utils import export_to_excel

def main():
    NUM_ITERATIONS = 20000

    NUM_ROUNDS = 6
    NUM_FIELDS = 2

    players = [
        Player("Diana"), 
        Player("Marco"), 
        Player("Peggy"), 
        Player("Freddy"), 
        Player("Frederik"), 
        Player("Manuel"), 
        Player("Melike"), 
        Player("Dascha"),
        Player("Corasti"),
        Player("Ben"),
        Player("Julius"),
        # Player("Timo"),
        ]
    
    best_matchup_config, best_score, results = get_most_diverse_matchups(players, NUM_ROUNDS, NUM_FIELDS, NUM_ITERATIONS)
    
    export_to_excel(best_matchup_config, players, NUM_FIELDS, f'output/matchups_with_points_and_format_pl{len(players)}_flds{NUM_FIELDS}_rds{NUM_ROUNDS}_opt{best_score:.3f}.xlsx')

if __name__ == "__main__":
   main()