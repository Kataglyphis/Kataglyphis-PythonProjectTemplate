import timeit
import sys
import os

from kataglyphispythonpackage.core import DummyOperations


def benchmark_package():
    """Performance test suite for the package"""
    test_cases = [
        ("Small Dataset", 100),
        ("Medium Dataset", 10_000),
        ("Large Dataset", 100_000),
    ]

    for name, size in test_cases:
        timer = timeit.Timer(
            stmt="obj.process_data()",
            setup=f"from kataglyphispythonpackage.core import DummyOperations; obj = DummyOperations({size})",
        )

        # Run 3 trials with 5 repetitions each
        results = timer.repeat(repeat=3, number=5)
        avg_time = sum(results) / len(results)

        print(f"{name} ({size} rows):")
        print(f"  Average time: {avg_time:.4f} sec")
        print(f"  Best run: {min(results):.4f} sec")
        print(f"  Performance variance: {max(results) - min(results):.4f} sec\n")


if __name__ == "__main__":
    benchmark_package()
