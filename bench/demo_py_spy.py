import math
import time

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def compute_primes(limit):
    primes = []
    for num in range(2, limit):
        if is_prime(num):
            primes.append(num)
    return primes

def heavy_sorting_task(data):
    return sorted(data, key=lambda x: math.sin(x) * math.exp(-x / 5000))

def main():
    start = time.time()

    print("Computing primes up to 20000...")
    primes = compute_primes(2000000)

    print("Sorting primes with heavy key function...")
    sorted_primes = heavy_sorting_task(primes)

    print(f"Top 10 primes: {sorted_primes[-10:]}")
    print(f"Done in {time.time() - start:.2f} seconds")

if __name__ == "__main__":
    main()
    time.sleep(5)  # <--- give py-spy time to attach
