"""Demo script for system monitoring functionality."""

import time
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kataglyphispythonpackage.system_monitor import SystemMonitor, monitor_function
from kataglyphispythonpackage.visualize_monitor import visualize_monitoring_file
from loguru import logger


def example_heavy_computation():
    """Simulate a heavy computation that uses CPU and memory."""
    logger.info("Starting heavy computation...")

    # Allocate some memory
    data = []
    for i in range(5):
        # Allocate ~100MB each iteration
        arr = np.random.rand(10_000_000)
        data.append(arr)

        # Do some CPU-intensive work
        result = np.sum(arr**2)
        logger.info(f"Iteration {i + 1}/5: Sum = {result:.2e}")

        time.sleep(1)

    logger.info("Computation finished!")
    return data


@monitor_function
def decorated_function_example():
    """Example of using the @monitor_function decorator."""
    logger.info("Running decorated function...")
    time.sleep(2)
    result = sum(i**2 for i in range(1_000_000))
    logger.info(f"Result: {result}")
    return result


def demo_basic_monitoring():
    """Demo 1: Basic manual monitoring."""
    logger.info("=" * 60)
    logger.info("DEMO 1: Basic Manual Monitoring")
    logger.info("=" * 60)

    monitor = SystemMonitor(output_dir="output/monitoring/demo1")

    # Monitor for 10 seconds
    logger.info("Monitoring for 10 seconds...")
    for i in range(10):
        sample = monitor.sample()
        logger.info(
            f"Sample {i + 1}: CPU={sample['cpu_percent']:.1f}%, RAM={sample['ram_percent']:.1f}%"
        )
        time.sleep(1)

    # Save data
    csv_path = monitor.save_data()
    monitor.save_metadata()

    # Visualize
    logger.info("\nGenerating visualization...")
    visualize_monitoring_file(csv_path)

    logger.info("Demo 1 complete!\n")


def demo_monitoring_with_computation():
    """Demo 2: Monitor during computation."""
    logger.info("=" * 60)
    logger.info("DEMO 2: Monitoring During Computation")
    logger.info("=" * 60)

    monitor = SystemMonitor(output_dir="output/monitoring/demo2")

    # Start background monitoring in a separate thread would be ideal,
    # but for simplicity, we'll sample before, during, and after
    logger.info("Taking baseline sample...")
    monitor.sample()

    logger.info("\nStarting computation...")
    example_heavy_computation()

    logger.info("\nTaking samples during cooldown...")
    for i in range(5):
        monitor.sample()
        time.sleep(1)

    # Save and visualize
    csv_path = monitor.save_data()
    monitor.save_metadata()
    visualize_monitoring_file(csv_path)

    logger.info("Demo 2 complete!\n")


def demo_decorator_monitoring():
    """Demo 3: Using the decorator."""
    logger.info("=" * 60)
    logger.info("DEMO 3: Decorator-Based Monitoring")
    logger.info("=" * 60)

    # The decorator will automatically monitor and save
    result = decorated_function_example()

    logger.info(f"Function returned: {result}")
    logger.info("Check output/monitoring/ for the monitoring files")
    logger.info("Demo 3 complete!\n")


def demo_continuous_monitoring():
    """Demo 4: Continuous monitoring with auto-stop."""
    logger.info("=" * 60)
    logger.info("DEMO 4: Continuous Monitoring (15 seconds)")
    logger.info("=" * 60)

    monitor = SystemMonitor(output_dir="output/monitoring/demo4")

    try:
        monitor.start_monitoring(interval=0.5, duration=15)
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")

    # Save and visualize
    csv_path = monitor.save_data()
    monitor.save_metadata()
    visualize_monitoring_file(csv_path)

    logger.info("Demo 4 complete!\n")


if __name__ == "__main__":
    logger.info("System Monitoring Demo")
    logger.info("This demo will show different ways to monitor system resources\n")

    # Run all demos
    try:
        demo_basic_monitoring()
        time.sleep(2)

        demo_monitoring_with_computation()
        time.sleep(2)

        demo_decorator_monitoring()
        time.sleep(2)

        demo_continuous_monitoring()

    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")

    logger.info("\n" + "=" * 60)
    logger.info("All demos complete!")
    logger.info("Check the output/monitoring/ directory for results")
    logger.info("=" * 60)
