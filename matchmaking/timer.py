import time
from typing import Optional


class Timer:
    def __init__(self):
        self.start_time = None

    def start(self, name: str = ""):
        """Starts the timer for a specific metric."""
        self.name = name
        self.start_time = time.time()

    def stop(self, iterations: int = 0) -> Optional[float]:
        """Stops the timer and prints the elapsed time."""
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            print(f"{self.name} took {elapsed_time:.4f} seconds.")

            if iterations > 0:
                print(f"Throughput: {iterations / elapsed_time:.4f} it/s.")

            self.start_time = None
            return elapsed_time
        else:
            print("Timer was not started.")
            return None
