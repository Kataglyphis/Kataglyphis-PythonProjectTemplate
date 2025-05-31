import time
from kataglyphispythonpackage.dummy import SimpleMLPreprocessor


def main():
    SimpleMLPreprocessor(10000).run_pipeline()


if __name__ == "__main__":
    main()
    time.sleep(30)  # <--- give py-spy time to attach
