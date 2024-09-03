import psutil
from matchmaking.metric_type import MetricType
from matchmaking.config import MetricWeightsConfig

NUM_ITERATIONS = 1000
NUM_ROUNDS = 13
NUM_FIELDS = 3

PLAYER_NAMES = [
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "P6",
    "P7",
    "P8",
    "P9",
    "P10",
    "P11",
    "P12",
    "P13",
]


METRIC_WEIGHTS_CONFIG = MetricWeightsConfig()


WORKERS = 1  # psutil.cpu_count()
