import time
import timeit

from kataglyphispythonpackage.fib import fib


def benchmark_fib():
    start = time.time()
    print(f"fib(35) = {fib(35)}")
    end = time.time()
    print(f"Execution time: {end - start:.4f} seconds")


def benchmark_package():
    """Performance test suite for the package"""
    benchmark_fib()
    execution_time = timeit.timeit(
        "fib(35)", setup="from kataglyphispythonpackage.fib import fib", number=10
    )
    print(f"Average execution time over 10 runs: {execution_time:.6f} seconds")


@profile
def benchmark_with_lineprofiler():
    fib(35)


if __name__ == "__main__":
    benchmark_package()
    benchmark_with_lineprofiler()
