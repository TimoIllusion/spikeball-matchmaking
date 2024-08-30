import psutil
from matchmaking.metric_type import MetricType
from matchmaking.config import MetricWeightsConfig

NUM_ITERATIONS = 10000
NUM_ROUNDS = 10
NUM_FIELDS = 1

PLAYER_NAMES = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
]


METRIC_WEIGHTS_CONFIG = MetricWeightsConfig()


WORKERS = psutil.cpu_count()
