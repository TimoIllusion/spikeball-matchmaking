from matchmaking.data import Player
from matchmaking.generator import get_most_diverse_matchups

if __name__ == "__main__":
    NUM_ROUNDS = 6
    NUM_FIELDS = 3

    players = [
        Player("1"), 
        Player("2"), 
        Player("3"), 
        Player("4"), 
        Player("5"), 
        Player("6"), 
        Player("7"), 
        Player("8"),
        Player("9"),
        Player("10"),
        Player("11"),
        Player("12"),
        ]

    NUM_ITERATIONS = 10000
    
    get_most_diverse_matchups(players, NUM_ROUNDS, NUM_FIELDS, NUM_ITERATIONS)