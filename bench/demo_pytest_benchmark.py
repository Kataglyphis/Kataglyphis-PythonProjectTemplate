# test_fib.py
from kataglyphispythonpackage.fib import fib


def test_fib_benchmark(benchmark):
    result = benchmark(fib, 35)
    assert result == 9227465
