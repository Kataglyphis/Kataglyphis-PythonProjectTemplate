from memory_profiler import profile
from kataglyphispythonpackage.fib import fib


@profile
def run():
    fib(35)


if __name__ == "__main__":
    run()
