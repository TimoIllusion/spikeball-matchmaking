from matchmaking.metric_type import MetricType


class MetricWeightsConfig:

    def __init__(self):

        self.weight_per_metric = dict()

        self.weight_per_metric[MetricType.GLOBAL_NOT_PLAYING_PLAYERS_INDEX] = (
            100000000.0
        )
        self.weight_per_metric[MetricType.GLOBAL_PLAYED_MATCHES_INDEX] = 100000.0
        self.weight_per_metric[
            MetricType.GLOBAL_NOT_PLAYED_WITH_OR_AGAINST_PLAYERS_INDEX
        ] = 10000.0
        self.weight_per_metric[
            MetricType.GLOBAL_MATCHUP_SESSION_LENGTH_BETWEEN_BREAKS_INDEX
        ] = 100.0
        self.weight_per_metric[MetricType.GLOBAL_PLAYER_ENGAGEMENT_FAIRNESS_INDEX] = (
            10.0
        )
        self.weight_per_metric[MetricType.GLOBAL_TEAMMATE_SUCCESSION_INDEX] = 100.0
        self.weight_per_metric[MetricType.GLOBAL_ENEMY_TEAM_SUCCESSION_INDEX] = 10.0
        self.weight_per_metric[MetricType.GLOBAL_TEAMMATE_VARIETY_INDEX] = 100.0
        self.weight_per_metric[MetricType.GLOBAL_ENEMY_TEAM_VARIETY_INDEX] = 10.0
        # self.weight_per_metric[MetricType.GLOBAL_BREAK_OCCURRENCE_INDEX] = 10.0
        self.weight_per_metric[MetricType.GLOBAL_BREAK_SHORTNESS_INDEX] = 10.0
        self.weight_per_metric[MetricType.GLOBAL_NOT_PLAYED_WITH_PLAYERS_INDEX] = 100.0
        self.weight_per_metric[MetricType.GLOBAL_NOT_PLAYED_AGAINST_PLAYERS_INDEX] = (
            10.0
        )

    #         GLOBAL_NOT_PLAYED_WITH_PLAYERS_INDEX = "global_not_played_with_players_index"
    # GLOBAL_NOT_PLAYED_AGAINST_PLAYERS_INDEX = "global_not_played_against_players_index"

    def update_weight(self, metric: MetricType, new_value: float):
        self.weight_per_metric[metric] = new_value
