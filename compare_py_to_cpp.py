"""
Benchmark script comparing Python vs C++ implementations with realistic data.
"""

import time
import datetime
from typing import List
from matchmaking.data import Player
from matchmaking.simple_optimizer import SimpleMatchupOptimizer
from matchmaking.config import MetricWeightsConfig
from config import *

# Import both implementations for comparison
from matchmaking.metrics import get_total_matchup_set_score  # Original Python
from matchmaking_fast_wrapper import get_total_matchup_set_score_fast  # Fast C++


def create_sample_optimization():
    """Create a sample optimization to get realistic matchup data for benchmarking."""

    print("🔧 Creating sample matchup data...")

    players = [Player(p) for p in PLAYER_NAMES]

    # Use a smaller number of iterations for quick data generation
    optimizer = SimpleMatchupOptimizer(
        players, NUM_ROUNDS, NUM_FIELDS, min(100, NUM_ITERATIONS), METRIC_WEIGHTS_CONFIG
    )

    # Get some optimized matchups for testing
    best_matchup_config, best_score, results, _, _ = (
        optimizer.get_most_diverse_matchups()
    )

    print(f"   Generated {len(best_matchup_config)} matchups")
    print(f"   Using {len(players)} players, {NUM_FIELDS} fields, {NUM_ROUNDS} rounds")

    return best_matchup_config, len(players), METRIC_WEIGHTS_CONFIG, NUM_FIELDS


def speed_comparison_with_real_data(iterations: int = 5):
    """
    Speed comparison using real matchmaking data.
    """

    print("🚀 Speed Comparison: Python vs C++ (Real Data)")
    print("=" * 60)

    # Generate realistic test data
    matchups, num_players, weights_config, num_fields = create_sample_optimization()

    print(f"Benchmarking with:")
    print(f"   Matchups: {len(matchups)}")
    print(f"   Players: {num_players}")
    print(f"   Fields: {num_fields}")
    print(f"   Iterations: {iterations}")
    print()

    # Test Python implementation
    print("🐍 Testing Python implementation...")
    python_times = []

    for i in range(iterations):
        start_time = time.time()
        py_results, py_loss = get_total_matchup_set_score(
            matchups, num_players, weights_config, num_fields
        )
        elapsed = time.time() - start_time
        python_times.append(elapsed)

        if i == 0:  # Store first result for comparison
            first_py_loss = py_loss
            first_py_results = py_results

        print(f"   Run {i+1}: {elapsed:.6f}s")

    python_avg = sum(python_times) / len(python_times)
    print(f"   Average: {python_avg:.6f}s")
    print(f"   Loss: {first_py_loss:.6f}")

    # Test C++ implementation
    print("\n⚡ Testing C++ implementation...")
    cpp_times = []

    for i in range(iterations):
        start_time = time.time()
        cpp_results, cpp_loss = get_total_matchup_set_score_fast(
            matchups, num_players, weights_config, num_fields
        )
        elapsed = time.time() - start_time
        cpp_times.append(elapsed)

        if i == 0:  # Store first result for comparison
            first_cpp_loss = cpp_loss
            first_cpp_results = cpp_results

        print(f"   Run {i+1}: {elapsed:.6f}s")

    cpp_avg = sum(cpp_times) / len(cpp_times)
    print(f"   Average: {cpp_avg:.6f}s")
    print(f"   Loss: {first_cpp_loss:.6f}")

    # Calculate metrics
    speedup = python_avg / cpp_avg if cpp_avg > 0 else float("inf")
    loss_difference = abs(first_py_loss - first_cpp_loss)
    time_saved_ms = (python_avg - cpp_avg) * 1000

    print("\n📊 Performance Results:")
    print(f"   Python average: {python_avg:.6f}s")
    print(f"   C++ average:    {cpp_avg:.6f}s")
    print(f"   Speedup:        {speedup:.1f}x")
    print(f"   Time saved:     {time_saved_ms:.2f}ms per call")

    print("\n🔍 Accuracy Check:")
    print(f"   Loss difference: {loss_difference:.2e}")

    if loss_difference < 1e-10:
        print("   ✅ Perfect match!")
    elif loss_difference < 1e-6:
        print("   ✅ Excellent match (within floating-point precision)")
    elif loss_difference < 1e-3:
        print("   ⚠️  Small difference (likely precision)")
    else:
        print("   ❌ Significant difference - check implementation")

    # Compare some global metrics
    print("\n📈 Sample Global Metrics Comparison:")
    for key in list(first_py_results["global"].keys())[:5]:  # Show first 5 metrics
        py_val = first_py_results["global"][key]
        cpp_val = first_cpp_results["global"][key]
        diff = abs(py_val - cpp_val)
        print(f"   {key}: Python={py_val:.6f}, C++={cpp_val:.6f}, diff={diff:.2e}")

    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    if speedup > 50:
        print("   🔥 EXCEPTIONAL! C++ is dramatically faster.")
        print("   💡 This will significantly improve optimization times.")
    elif speedup > 10:
        print("   🚀 EXCELLENT! Major performance improvement.")
        print("   💡 Your optimization will run much faster.")
    elif speedup > 3:
        print("   👍 GOOD! Significant speedup achieved.")
        print("   💡 Noticeable improvement in optimization speed.")
    elif speedup > 1.5:
        print("   📈 MODEST improvement.")
        print("   💡 Some benefit, but consider further optimization.")
    else:
        print("   🤔 MINIMAL speedup.")
        print("   💡 Check if C++ extensions compiled with optimizations.")

    # Scaling estimate
    if speedup > 1:
        optimization_estimate = (NUM_ITERATIONS * python_avg) / speedup
        time_saved_total = (NUM_ITERATIONS * python_avg) - optimization_estimate
        print(f"\n⏱️  Optimization Time Estimate:")
        print(f"   Full optimization with Python: {NUM_ITERATIONS * python_avg:.1f}s")
        print(f"   Full optimization with C++:    {optimization_estimate:.1f}s")
        print(
            f"   Total time saved:               {time_saved_total:.1f}s ({time_saved_total/60:.1f}min)"
        )

    return {
        "python_avg": python_avg,
        "cpp_avg": cpp_avg,
        "speedup": speedup,
        "loss_difference": loss_difference,
        "matchup_count": len(matchups),
        "player_count": num_players,
    }


def quick_benchmark():
    """Quick benchmark with minimal setup."""
    print("Quick Benchmark Mode")
    print("=" * 30)

    try:
        results = speed_comparison_with_real_data(iterations=3)

        print(f"\n✅ Benchmark Complete!")
        print(f"   C++ is {results['speedup']:.1f}x faster")
        print(
            f"   Tested with {results['matchup_count']} matchups, {results['player_count']} players"
        )

    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure config.py has valid PLAYER_NAMES, NUM_ROUNDS, etc.")
        print("2. Ensure both Python and C++ implementations are available")
        print("3. Check that the matchmaking module imports work")


if __name__ == "__main__":
    print("Matchmaking Speed Benchmark")
    print("=" * 40)
    print(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    quick_benchmark()
