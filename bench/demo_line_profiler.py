from kataglyphispythonpackage.fib import fib


@profile
def benchmark_with_lineprofiler():
    fib(35)


if __name__ == "__main__":
    benchmark_with_lineprofiler()
