import time
from kataglyphispythonpackage.dummy import SimpleMLPreprocessor


def main():
    preprocessor = SimpleMLPreprocessor(n_samples=1_000_000)
    result = preprocessor.run_pipeline()
    time.sleep(1000)

if __name__ == "__main__":
    main()
    # time.sleep(100)  # <--- give py-spy time to attach
