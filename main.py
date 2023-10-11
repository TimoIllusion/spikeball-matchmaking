import streamlit as st
import numpy as np


from matchmaking.data import Player, Matchup, Team 
from matchmaking.metrics import get_avg_matchup_diversity_score

#TODO: use simpler metric based approach and offline matchup generation

def reset_matchups():
    # TODO: reset session
    st.session_state.matchup_history = []
    st.session_state.next_matchup = Matchup.create_dummy()
    st.session_state.all_matchups_played = False
    st.session_state.num_unique_matchups = 0


def init_state():

    if "players" not in st.session_state:
        st.session_state.players = []

    if "matchup_history" not in st.session_state:
        st.session_state.matchup_history = []

    if 'next_matchup' not in st.session_state:
        st.session_state.next_matchup = Matchup.create_dummy()

    if 'all_matchups_played' not in st.session_state:
        st.session_state.all_matchups_played = False

    if 'num_unique_matchups' not in st.session_state:
        st.session_state.num_unique_matchups = 0
        


def submit_add_player(player_phrase: str):
    """ Callback function during adding a new project. """
    # display a warning if the user entered an existing name
    #st.write("got something!")
    
    if "," in player_phrase:
        players = player_phrase.split(",")
    else:
        players = [player_phrase]
    
    for player_name in players:
        player = Player(player_name)
        if player.get_unique_identifier() in [x.get_unique_identifier() for x in st.session_state.players]:
            st.warning(f'The name "{player}" already exists.')
        else:
            st.session_state.players.append(player)

    # st.write(st.session_state.players)


def calculate_max_matchups(num_players):

    n = num_players

    return int(((n * n - n) / 8) * (n * n - 5 * n + 6))


def generate_all_possible_matchups():
    
    players = st.session_state.players
    
    matchups = []
    for player_self in players:
        for player_mate in players:
            for player_enemy_1 in players:
                for player_enemy_2 in players:
                    
                    unique_players = list(set([player_self, player_mate, player_enemy_1, player_enemy_2]))
                    if len(unique_players) < 4:
                        continue
                    
                    m = Matchup.from_names(player_self, player_mate, player_enemy_1, player_enemy_2)
                    
                    if m.get_unique_identifier() not in [x.get_unique_identifier() for x in matchups]:
                        matchups.append(m)
                        
    print([str(x) for x in matchups])
    print(len(matchups))                    
    
    return matchups                 
                    
        
        
        
        
        
        
    
    

def generate_random_matchup():

    selected_players = np.random.choice(st.session_state.players,
                             replace=False, size=4).tolist()

    return Matchup.from_names(*selected_players)

def calculate_player_draft_score_naive(missed_matchups, played_matchups):
    
    # the more matchups missed, the higher the score (linear or exponential)
    # the more matchups played, the lower the score
    # dont play with the same exact team mate two times in a row if possible
    # match according to skill level
    
    score_offset = 5 + missed_matchups * 1000
    
    return score_offset





def generate_matchup_with_naive_heuristic():
    
    # 1. evaluate and assign possibilities of each person to be drafted
    # 2. generate matchup
    # 3. validate matchup
    
    
    DEPTH = 5
    
    # check history 
    for player in st.session_state.players:
        
        player_uid = player.get_unique_identifier()
        player_occurences_reversed = []
        
        reversed_indices = reversed(range(len(st.session_state.matchup_history)))
        for i in reversed_indices:
            matchup = st.session_state.matchup_history[i]
            player_occured = player_uid in matchup.get_unique_identifier()
            player_occurences_reversed.append(player_occured)
        
        
        missed_matchups = 0
        for i in range(len(player_occurences_reversed)):
            if player_occurences_reversed[i]:
                break
            else:
                missed_matchups +=1
        
        if len(player_occurences_reversed) < DEPTH:
            DEPTH = len(player_occurences_reversed)
        
        played_matchups = 0
        for occurence in player_occurences_reversed[:DEPTH]:
            if occurence:
                played_matchups += 1
                
        
        # amount of games played in last X games
        # matchups since last played
        
        draft_score = calculate_player_draft_score_naive(missed_matchups, played_matchups)
        player.set_draft_probability_score(draft_score)
    
        # formulat to calculate probability based on player_matchups in DEPTH and times since last play -> also heuristic: if didn't play last time, high chance to play a game
        print("player", player, "missed", missed_matchups, "played", played_matchups)
        
    players = select_players_by_draft_score()
    return Matchup.from_names(*players)

def select_players_by_draft_score():
    
    draft_probability_scores = np.array([x.get_draft_probability_score() for x in st.session_state.players])
    
    total_score = np.sum(draft_probability_scores)
    
    draft_probabilities = draft_probability_scores / total_score
    
    print([str(x) for x in st.session_state.players])
    print(draft_probabilities)
    
    selected_players = np.random.choice(st.session_state.players,
                             replace=False, size=4, p = draft_probabilities).tolist()
    
    return selected_players

def check_all_matchups_played():
    unique_mtchp_history = set([x.get_unique_identifier() for x in st.session_state.matchup_history])
    
    st.session_state.num_unique_matchups = len(unique_mtchp_history)

    st.session_state.all_matchups_played = st.session_state.num_unique_matchups == st.session_state.max_matchups


def gen_matchup_callback():

    if not st.session_state.all_matchups_played:

        while True:
            mtchp = generate_random_matchup()
            #mtchp = generate_matchup_with_naive_heuristic()

            # check if already exists in history
            if mtchp.get_unique_identifier() in [x.get_unique_identifier() for x in st.session_state.matchup_history]:
                continue
            else:
                break

        st.session_state.next_matchup = mtchp

    else:

        # TODO: warning popup
        pass

def gen_10_matchups_callback():
    
    matchups = []
    for i in range(10):
        
        while True:
            mtchp = generate_random_matchup()
            #mtchp = generate_matchup_with_naive_heuristic()

            if mtchp.get_unique_identifier() in [x.get_unique_identifier() for x in st.session_state.matchup_history]:
                continue
            else:
                break
        
        matchups.append(mtchp)
        
    st.write("Planned matchups:")
    st.write(matchups)
    results = get_avg_matchup_diversity_score(matchups)
    st.write(results)
        


def gen_matchup_callback_heuristic():
    
    if not st.session_state.all_matchups_played:
        
        MAX_TRIES = 5
        try_counter = 0
        while True:
            
            mtchp_generated = generate_matchup_with_naive_heuristic()
            
            if st.session_state.matchup_history:
                # mtchp = generate_random_matchup()
                
                teams_generated = mtchp_generated.get_teams()
                
                mtchp_recent = st.session_state.matchup_history[-1]
                teams_recent = mtchp_recent.get_teams()
                teams_recent_uids = [x.get_unique_identifier() for x in teams_recent]
                
                # check if team already played together in the last matchup
                if teams_generated[0].get_unique_identifier() in teams_recent_uids or teams_generated[1].get_unique_identifier() in teams_recent_uids:
                    try_counter += 1
                    if try_counter <= MAX_TRIES:
                        continue
                    else:
                        pass
                else:
                    pass                
            
            # check if already exists in history
            if mtchp_generated.get_unique_identifier() in [x.get_unique_identifier() for x in st.session_state.matchup_history]:
                continue
            else:
                break

        st.session_state.next_matchup = mtchp_generated

    else:

        # TODO: warning popup
        pass
    
    

def finished_matchup_callback(mtchp):
    
    st.session_state.matchup_history.append(mtchp)
    check_all_matchups_played()

def export_data_callback():
    pass
    

def main():

    init_state()

    st.write("""
    # Spikeball WebApp
    Generate matchups and track scores.
    """)
    
    # left, middle, right = st.columns(3)

    # # set variables in session state
    # st.write("## Mode")

    # st.session_state.modes = [
    # 'Normal mode', 'Tournament'
    # ]
    # st.session_state.current_mode = st.radio(
    # 'Select a mode:',
    # st.session_state.modes,
    # )
    
    # get new players
    st.write("## Player selection")
    new_player = st.text_input('New player name (or list of players seperated by comma):',
                               key='input_new_player_name', placeholder="Player Name")

    st.button('Add player', key='button_add_player',
              on_click=submit_add_player, args=(new_player, ))

    st.write("Current players:")
    st.write([str(x) for x in st.session_state.players])

    # calculate all possible matchups
    st.session_state.max_matchups = calculate_max_matchups(
        len(st.session_state.players))

    st.write("Max amount of matchups:", st.session_state.max_matchups)

    # matchup history
    st.write("## Matchup history")  # TODO: an rechte column

    for matchup in st.session_state.matchup_history:
        st.write(matchup)

    st.write("Total played matchups: ", len(st.session_state.matchup_history))
    st.write("Played unique matchups: ", st.session_state.num_unique_matchups)

    # get random matchup
    st.write("## Matchup generation")

    st.button('Get next matchup randomly', key='button_gen_matchup',
              on_click=gen_matchup_callback)
    
    st.button('Get next matchup intelligently', key='button_gen_matchup_intelligently',
              on_click=gen_matchup_callback_heuristic)
    
    st.button('Get 10 matchups randomly', key='button_gen_10_matchup',
              on_click=gen_10_matchups_callback)
    
    #st.button('Calc all matchups', key='all_matchups',
    #          on_click=generate_all_possible_matchups)

    st.write(st.session_state.next_matchup)

    st.button('Finished current matchup', key='button_finished_matchup',
              on_click=finished_matchup_callback, args=(st.session_state.next_matchup, ))

    if st.session_state.all_matchups_played:
        st.write("ALL MATCHUPS PLAYED. Reset matchup history?")
        st.button("RESET", on_click=reset_matchups)
        
        
    st.button('Export data', key='export',
              on_click=export_data_callback)


if __name__ == "__main__":

    main()
