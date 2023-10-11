import streamlit as st

from matchmaking.data import Player
from matchmaking.generator import get_most_diverse_matchups


def init_state():

    if "players" not in st.session_state:
        st.session_state.players = []

    if 'matchups' not in st.session_state:
        st.session_state.matchups = []
        
    if 'matchup_gen_score' not in st.session_state:
        st.session_state.matchup_gen_score = 0.0
        
    if 'results' not in st.session_state:
        st.session_state.results = {}

    if 'NUM_ITERATIONS' not in st.session_state:
        st.session_state.NUM_ITERATIONS = 10000

    if 'NUM_ROUNDS' not in st.session_state:
        st.session_state.NUM_ROUNDS = 10

    if 'NUM_FIELDS' not in st.session_state:
        st.session_state.NUM_FIELDS = 1

    if 'WEIGHT_METRIC_CONFIG' not in st.session_state:
        st.session_state.WEIGHT_METRIC_CONFIG = {}
        


def input_new_players():
    st.write("#### Player selection")
    new_player = st.text_input('New player name (or list of players seperated by comma):', key='input_new_player_name', placeholder="Name OR Name1,Name2,Name3,Name4,...")

    st.button('Add player', key='button_add_player',
              on_click=_submit_add_player, args=(new_player, ))

    st.write("Current players:")
    st.write([str(x) for x in st.session_state.players])
    
def _submit_add_player(player_phrase: str):
    
    if player_phrase == "":
        st.warning(f"Please insert a player name or a comma separated list of names.")
        return
    
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
    
def show_max_matchups():
    st.session_state.max_matchups = _calculate_max_matchups(len(st.session_state.players))
    st.write("Max possible amount of unique matchups:", st.session_state.max_matchups)

def _calculate_max_matchups(num_players) -> int:

    n = num_players

    return int(((n * n - n) / 8) * (n * n - 5 * n + 6))


def configure():
    st.write("## Configuration")
    
    input_new_players()
    
    st.write("#### Game Params")
    st.session_state.NUM_ROUNDS = st.slider('Number of Rounds:', min_value=1, max_value=100, value=_get_default_num_rounds())
    st.session_state.NUM_FIELDS = st.slider('Number of Fields:', min_value=1, max_value=10, value=1)
    
    st.write("#### Optimization Params")
    st.session_state.NUM_ITERATIONS = st.slider('Number of Optimization Iterations:', min_value=1000, max_value=100000, value=10000)
    
    st.write("#### Metric Weights")
    st.session_state.WEIGHT_METRIC_CONFIG["global_not_playing_players_index"] = 100000.0
    st.session_state.WEIGHT_METRIC_CONFIG["global_played_matches_index"] = 10000.0
    st.session_state.WEIGHT_METRIC_CONFIG["global_player_engagement_fairness_index"] = st.slider('Weight for Global Player Engagement Fairness Index:', 0.0, 100.0, 10.0)
    st.session_state.WEIGHT_METRIC_CONFIG["global_teammate_succession_index"] = st.slider('Weight for Global Teammate Succession Index:', 0.0, 100.0, 10.0)
    st.session_state.WEIGHT_METRIC_CONFIG["global_enemy_team_succession_index"] = st.slider('Weight for Global Enemy Team Succession Index:', 0.0, 100.0, 10.0)
    st.session_state.WEIGHT_METRIC_CONFIG["global_player_engagement_index"] = st.slider('Weight for Global Player Engagement Index:', 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG["global_teammate_variety_index"] = st.slider('Weight for Global Teammate Variety Index:', 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG["global_enemy_team_variety_index"] = st.slider('Weight for Global Enemy Team Variety Index:', 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG["global_break_occurrence_index"] = st.slider('Weight for Global Break Occurrence Index:', 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG["global_break_shortness_index"] = st.slider('Weight for Global Break Shortness Index:', 0.0, 100.0, 5.0)
    st.write(f"Weight for Global Not Playing Players Index [CONSTANT]:", st.session_state.WEIGHT_METRIC_CONFIG["global_not_playing_players_index"])
    st.write(f"Weight for Global Played Matches Index [CONSTANT]:", st.session_state.WEIGHT_METRIC_CONFIG["global_played_matches_index"])

def _get_default_num_rounds() -> int:
    if st.session_state.max_matchups > 0:
        return st.session_state.max_matchups
    else:
        return 10

def matchup_generation():
    st.write("## Matchup generation")
    
    show_max_matchups()

    st.button('Generate matchups [may take a while...]', key='button_gen_10_matchup',
              on_click=_gen_matchup_batch)
    
    st.write(st.session_state.matchups)
    
    st.write("Score (lower is better):", st.session_state.matchup_gen_score)
    
def _gen_matchup_batch():
    
    if len(st.session_state.players) < 4:
        st.warning(f"Not enough players to generate matchups: {len(st.session_state.players)}. Four players are needed at least.")
        return
    
    weight_metric_config = [ (value, key) for key, value in st.session_state.WEIGHT_METRIC_CONFIG.items()]
    
    print(weight_metric_config)
    
    best_matchup_config, best_score, results = get_most_diverse_matchups(
        st.session_state.players, 
        st.session_state.NUM_ROUNDS, 
        st.session_state.NUM_FIELDS, 
        st.session_state.NUM_ITERATIONS, 
        weight_metric_config
    )
    
    st.session_state.matchups = best_matchup_config
    st.session_state.matchup_gen_score = best_score
    st.session_state.results = results

def additional_info():
    st.write("#### Additional Result Info")
    st.write("Matchup Statistics:", st.session_state.results)

def main():

    init_state()

    st.write("""
    # Spikeball WebApp
    Generate optimal matchups.
    """)
    
    matchup_generation()
    configure()
    additional_info()


if __name__ == "__main__":

    main()
