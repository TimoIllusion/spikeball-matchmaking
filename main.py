import streamlit as st

from matchmaking.data import Player
from matchmaking.generator import get_most_diverse_matchups
from matchmaking.metric_type import MetricType
from matchmaking.config import MetricWeightsConfig


def init_state() -> None:

    if "players" not in st.session_state:
        st.session_state.players = []

    if "matchups" not in st.session_state:
        st.session_state.matchups = []

    if "matchup_gen_score" not in st.session_state:
        st.session_state.matchup_gen_score = 0.0

    if "results" not in st.session_state:
        st.session_state.results = {}

    if "NUM_ITERATIONS" not in st.session_state:
        st.session_state.NUM_ITERATIONS = 10000

    if "NUM_ROUNDS" not in st.session_state:
        st.session_state.NUM_ROUNDS = 10

    if "NUM_FIELDS" not in st.session_state:
        st.session_state.NUM_FIELDS = 1

    if "WEIGHT_METRIC_CONFIG" not in st.session_state:
        st.session_state.WEIGHT_METRIC_CONFIG = MetricWeightsConfig()


def _get_default_num_rounds() -> int:

    if st.session_state.max_matchups > 0:
        return st.session_state.max_matchups
    else:
        return 10


def matchup_generation() -> None:

    st.write("## Matchup generation")

    _show_max_matchups()

    st.button(
        "Generate matchups [may take a while...]",
        key="button_gen_10_matchup",
        on_click=_gen_matchup_batch,
    )

    st.write(st.session_state.matchups)

    st.write("Score (lower is better):", st.session_state.matchup_gen_score)


def _show_max_matchups() -> None:

    st.session_state.max_matchups = _calculate_max_matchups(
        len(st.session_state.players)
    )
    st.write("Max possible amount of unique matchups:", st.session_state.max_matchups)


def _calculate_max_matchups(num_players) -> int:

    n = num_players

    return int(((n * n - n) / 8) * (n * n - 5 * n + 6))


def _gen_matchup_batch() -> None:

    if len(st.session_state.players) < 4:
        st.warning(
            f"Not enough players to generate matchups: {len(st.session_state.players)}. Four players are needed at least."
        )
        return

    print(st.session_state.WEIGHT_METRIC_CONFIG.weight_per_metric)

    best_matchup_config, best_score, results, _, _ = get_most_diverse_matchups(
        st.session_state.players,
        st.session_state.NUM_ROUNDS,
        st.session_state.NUM_FIELDS,
        st.session_state.NUM_ITERATIONS,
        st.session_state.WEIGHT_METRIC_CONFIG,
    )

    st.session_state.matchups = best_matchup_config
    st.session_state.matchup_gen_score = best_score
    st.session_state.results = results


def configure():
    st.write("## Configuration")

    _input_new_players()

    st.write("#### Game Params")
    st.session_state.NUM_ROUNDS = st.slider(
        "Number of Rounds:", min_value=1, max_value=100, value=_get_default_num_rounds()
    )
    st.session_state.NUM_FIELDS = st.slider(
        "Number of Fields:", min_value=1, max_value=10, value=1
    )

    st.write("#### Optimization Params")
    st.session_state.NUM_ITERATIONS = st.slider(
        "Number of Optimization Iterations:",
        min_value=1000,
        max_value=100000,
        value=10000,
    )

    st.write("#### Metric Weights")

    value = st.slider("Weight for Global Matchup Length Index:", 0.0, 100.0, 10000.0)
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_MATCHUP_LENGTH_INDEX, value
    )

    value = st.slider(
        "Weight for Global Player Engagement Fairness Index:", 0.0, 100.0, 10.0
    )
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_PLAYER_ENGAGEMENT_FAIRNESS_INDEX, value
    )

    value = st.slider("Weight for Global Teammate Succession Index:", 0.0, 100.0, 10.0)
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_TEAMMATE_SUCCESSION_INDEX, value
    )

    value = st.slider(
        "Weight for Global Enemy Team Succession Index:", 0.0, 100.0, 10.0
    )
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_ENEMY_TEAM_SUCCESSION_INDEX, value
    )

    value = st.slider("Weight for Global Player Engagement Index:", 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_PLAYER_ENGAGEMENT_INDEX, value
    )

    value = st.slider("Weight for Global Teammate Variety Index:", 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_TEAMMATE_VARIETY_INDEX, value
    )

    value = st.slider("Weight for Global Enemy Team Variety Index:", 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_ENEMY_TEAM_VARIETY_INDEX, value
    )

    value = st.slider("Weight for Global Break Occurrence Index:", 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_BREAK_OCCURRENCE_INDEX, value
    )

    value = st.slider("Weight for Global Break Shortness Index:", 0.0, 100.0, 5.0)
    st.session_state.WEIGHT_METRIC_CONFIG.update_weight(
        MetricType.GLOBAL_BREAK_SHORTNESS_INDEX, value
    )

    st.write(
        f"Weight for Global Not Playing Players Index [CONSTANT]:",
        st.session_state.WEIGHT_METRIC_CONFIG.weight_per_metric[
            MetricType.GLOBAL_NOT_PLAYING_PLAYERS_INDEX
        ],
    )
    st.write(
        f"Weight for Global Played Matches Index [CONSTANT]:",
        st.session_state.WEIGHT_METRIC_CONFIG.weight_per_metric[
            MetricType.GLOBAL_PLAYED_MATCHES_INDEX
        ],
    )


def _input_new_players() -> None:

    st.write("#### Player selection")
    new_player = st.text_input(
        "New player name (or list of players seperated by comma):",
        key="input_new_player_name",
        placeholder="Name OR Name1,Name2,Name3,Name4,...",
    )

    st.button(
        "Add player",
        key="button_add_player",
        on_click=_submit_add_player,
        args=(new_player,),
    )

    st.write("Current players:")
    st.write([str(x) for x in st.session_state.players])


def _submit_add_player(player_phrase: str) -> None:

    if player_phrase == "":
        st.warning(f"Please insert a player name or a comma separated list of names.")
        return

    if "," in player_phrase:
        players = player_phrase.split(",")
    else:
        players = [player_phrase]

    for player_name in players:
        player = Player(player_name)
        if player.get_unique_identifier() in [
            x.get_unique_identifier() for x in st.session_state.players
        ]:
            st.warning(f'The name "{player}" already exists.')
        else:
            st.session_state.players.append(player)


def additional_info() -> None:
    st.write("#### Additional Result Info")
    st.write("Matchup Statistics:", st.session_state.results)


def main() -> None:

    init_state()

    st.write(
        """
    # Spikeball WebApp
    Generate optimal matchups.
    """
    )

    matchup_generation()
    configure()
    additional_info()


if __name__ == "__main__":
    main()
