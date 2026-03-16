# HW3
# MSML606
# Author: Chenhongshu Yu
# UID: 116610971

# Statement: The use of external resources is clearly cited. 
# If no citation is found for any specific part of my submission, 
# it means "No external sources were used; all ideas are my own or from course lecture slides".


# FEEL FREE TO ADD MORE FUNCTIONS AS PER YOUR NEED
# THERE IS NO UNCHANGEABLE "MAIN" FUNCTION IN THIS HW

import time
import random
import numpy as np

# Use "EMPTY" and "DELETED" to denote "never used" slots from "deleted" slots
EMPTY   = "EMPTY"
DELETED = "DELETED"

# Citation: Knuth's multiplicative hash: https://www.cs.hmc.edu/~geoff/classes/hmc.cs070.200401/homework10/hashfuncs.html
# Knuth's constant for the multiplication method: A = (sqrt(5) - 1) / 2
A = 0.6180339887

# Problem 1. Implement a hash table.

# Implement HashMap in this class
# Do not use built in dictionary
# Implement own hashing function using division/multiplication method
class HashMap:
    # Constructor to init
    def __init__(self, size=101, hash_method="multiplication"):
        # Size
        self.size = size
        # Configure hash_method parameter when creating the hashmap
        self.hash_method = hash_method
        # Number of live entries
        self.count = 0

        # Store keys and values in parallel slots in Numpy arrays
        self.keys = np.full(self.size, EMPTY, dtype=object)
        self.values = np.full(self.size, EMPTY, dtype=object)

    # Implement the hash function for both division and multiplication methods
    def _hash(self, key, method="division"):
        # Convert string keys to an integer k
        if isinstance(key, str):
            k = 0
            for ch in key:
                k = k * 31 + ord(ch)
        else:
            k = int(key)

        if method == "division":
            # Division method: h(k) = k mod m
            return k % self.size
        elif method == "multiplication":
            # Multiplication method: h(k) = floor(m * ((k * A) mod 1))
            # A = (sqrt(5) - 1) / 2 ≈ 0.6180339887  (Knuth's constant)
            frac = (k * A) % 1          # fractional part of k*A
            return int(self.size * frac)

    # Search for a key and return its value
    def search(self, key):
        # Get the value from its key 
        # Return None if not found

        # Linear probing: skip DELETED slots and stop at EMPTY slots.
        index = self._hash(key, method=self.hash_method)

        # Start probing
        for _ in range(self.size):
            # When the key is not found
            if self.keys[index] == EMPTY:
                return None
            # when the key is found and not deleted
            if self.keys[index] != DELETED and self.keys[index] == key:
                return self.values[index]
            # Continue probing
            index = (index + 1) % self.size
        return None

    # Insert a (key, value) pair
    def insert(self, key, value):
        # Insert (key, value) pair
        # Update the value if key already exists

        # Resize when necessary (if load factor exceeds 0.67) before inserting
        if self.count / self.size >= 0.67:
            self.dynamicResizing()

        index = self._hash(key, method=self.hash_method)
        # first DELETED slot during probing
        first_deleted = None

        # Start linear probing
        for _ in range(self.size):
            slot = self.keys[index]

            # When the slot is EMPTY
            if slot == EMPTY:
                # Insert at the first deleted slot if one was seen
                # else insert here
                if first_deleted is not None:
                    target = first_deleted
                else:
                    target = index

                self.keys[target] = key
                self.values[target] = value
                self.count += 1
                return

            # When the slot is DELETED
            if slot == DELETED:
                if first_deleted is None:
                    first_deleted = index
            elif slot == key:                # When the key is found
                # update existing key
                self.values[index] = value
                return

            index = (index + 1) % self.size

        # first_deleted is to be set, insert
        if first_deleted is not None:
            self.keys[first_deleted] = key
            self.values[first_deleted] = value
            self.count += 1

    # Remove a (key, value) pair
    def delete(self, key):
        # Remove a (key, value) pair, marked as "DELETED"
        # Return True if deleted
        # Return False if key is not found

        # Linear probing continues as deleted
        index = self._hash(key, method=self.hash_method)

        # Start linear probing
        for _ in range(self.size):
            # When the key is not found
            if self.keys[index] == EMPTY:
                return False
            # When the key is found and not deleted
            if self.keys[index] != DELETED and self.keys[index] == key:
                self.keys[index] = DELETED
                self.values[index] = DELETED
                self.count -= 1
                return True
            # Continue probing
            index = (index + 1) % self.size
        return False

    # Resize the hash table when load factor exceeds 0.67 (called when inserting)
    def dynamicResizing(self):
        # Double the table size and rehash entries
        old_keys = self.keys
        old_values = self.values
        old_size = self.size

        self.size = old_size * 2
        self.count = 0
        self.keys = np.full(self.size, EMPTY, dtype=object)
        self.values = np.full(self.size, EMPTY, dtype=object)

        for i in range(old_size):
            if old_keys[i] != EMPTY and old_keys[i] != DELETED:
                self.insert(old_keys[i], old_values[i])

# Problem 2: Performance Analysis

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Generate keys for different distributions
def generate_keys(distribution, n, key_range=10000000):
    # Return a list of n integer keys from the distribution
    
    # Uniform: keys drawn uniformly at random from [0, key_range)
    # Skewed: 80 % of keys come from only one percent of the range (hot zone)
    # Sequential: keys are 0, 1, 2, …, n-1
    
    # Uniform
    if distribution == "uniform":
        keys = []
        
        for _ in range(n):
            keys.append(random.randint(0, key_range - 1))
            
        return keys
    # Skewed
    elif distribution == "skewed":
        # 80 % of draws come from the bottom one percent of the range
        hot_limit = max(1, key_range // 100)
        keys = []
        
        for _ in range(n):
            if random.random() < 0.80:
                keys.append(random.randint(0, hot_limit - 1))
            else:
                keys.append(random.randint(0, key_range - 1))
                
        return keys
    # Sequential
    elif distribution == "sequential":
        return list(range(n))
    # Other (error handler)
    else:
        raise ValueError(f"Unknown distribution: '{distribution}'")

# Measure the average search time for a list of keys
def measure_search_time(hashmap, keys):
    # Measure the average time in seconds to search for each key in keys
    # Use timer (time.perf_counter()) to measure average search time for a randomly selected key
    # Return the average search time per key

    # Timer - time.perf_counter()
    start = time.perf_counter()

    for k in keys:
        hashmap.search(k)
        
    end = time.perf_counter()
    
    return (end - start) / len(keys)

# Helper function: measure average probe lengths for open addressing
def measure_probe_lengths(table_size, keys):
    # Count probe lengths by iterating the backing arrays directly

    # avg_insert: average number of slots examined per insertion
    # avg_search: average number of slots examined per successful search
    # avg_fail: average number of slots examined per unsuccessful search

    hm = HashMap(size=table_size, hash_method="multiplication")

    # Insert keys into the hash map
    for k in keys:
        hm.insert(k, k)

    # Count unique keys (deduplicated)
    unique_keys = list(dict.fromkeys(keys))

    # Helper function: count search probes for a given key
    def count_search_probes(key):
        # Replicate linear-probe walk and count steps
        index = hm._hash(key, method=hm.hash_method)
        probes = 0

        # Linear probe search
        for _ in range(hm.size):
            probes += 1
            # When the key is not found
            if hm.keys[index] == EMPTY:
                break
            # When the key is found and not deleted
            if hm.keys[index] != DELETED and hm.keys[index] == key:
                break
            # Continue probing
            index = (index + 1) % hm.size
        return probes

    # Successful search probes
    hit_probes = [count_search_probes(k) for k in unique_keys]

    # Unsuccessful search probes (keys guaranteed absent)
    miss_keys = [k + 10000000 for k in unique_keys[:200]]
    miss_probes = [count_search_probes(k) for k in miss_keys]

    # Insert probes: rebuild the table from scratch, counting per insert
    hm2 = HashMap(size=table_size, hash_method="multiplication")
    insert_probes = []

    # Count insert probes for each key
    for k in keys:
        index = hm2._hash(k, method=hm2.hash_method)
        probes = 0

        # Count probes for each insert
        for _ in range(hm2.size):
            probes += 1
            slot = hm2.keys[index]

            # When the slot is empty or the key is found
            if slot == EMPTY or slot == k:
                break
            index = (index + 1) % hm2.size
        insert_probes.append(probes)
        # Insert the key
        hm2.insert(k, k)

    avg_insert = sum(insert_probes) / len(insert_probes)
    avg_search = sum(hit_probes) / len(hit_probes)
    avg_fail = sum(miss_probes) / len(miss_probes)

    return avg_insert, avg_search, avg_fail

# Experiment 1: Load factor vs. lookup time (fix 2-3 table sizes)
def experiment_load_factor_vs_search_time():
    # Fix 3 table sizes [101, 499, 4999]
    # Vary load factor from 0.1 to 0.65
    # Record average successful and unsuccessful search times.

    # Three fixed table sizes
    table_sizes = [101, 499, 4999]
    # Vary load factor from 0.1 to 0.65
    load_factors = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.65]
    # Number of queries per measurement
    n_queries = 500

    # results[size] = (lf_list, hit_times, miss_times)
    results = {}

    # Measure search times for each table size
    for size in table_sizes:
        lf_list = []
        hit_times = []
        miss_times = []

        # Measure search times for each load factor
        for lf in load_factors:
            n_keys = int(size * lf)
            if n_keys == 0:
                continue

            # Build table
            keys = random.sample(range(0, size * 20), n_keys)
            # Initialize hash map with multiplication method
            hm = HashMap(size=size, hash_method="multiplication")
            for k in keys:
                hm.insert(k, k)

            # Successful searches, randomly sampled
            hit_sample = random.choices(keys, k=n_queries)
            # Unsuccessful searches, not in the keys
            miss_sample = []
            for k in random.choices(keys, k=n_queries):
                miss_sample.append(k + size * 20 + 1)

            # Measure search times
            lf_list.append(lf)
            hit_times.append(measure_search_time(hm, hit_sample))
            miss_times.append(measure_search_time(hm, miss_sample))

        results[size] = (lf_list, hit_times, miss_times)

    # Citation: Used AI tools for better visualization
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Experiment 1: Load Factor vs. Average Search Time", fontsize=13)

    for size, (lf_list, hit_times, miss_times) in results.items():
        # convert to microseconds for readability
        hit_us = [t * 1e6 for t in hit_times]
        miss_us = [t * 1e6 for t in miss_times]
        axes[0].plot(lf_list, hit_us, marker="o", label=f"size={size}")
        axes[1].plot(lf_list, miss_us, marker="s", label=f"size={size}")

    for ax, title in zip(axes, ["Successful Search", "Unsuccessful Search"]):
        ax.set_xlabel("Load Factor")
        ax.set_ylabel("Avg Search Time (µs)")
        ax.set_title(title)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("exp1_load_factor_vs_search_time.png", dpi=150)
    plt.show()

# Experiment 2: Key distribution comparison
def experiment_key_distribution():
    # Fixed table size and load factor
    # Part I: Compare search time across uniform, skewed, and sequential distributions
    # Part II: Measure average probe lengths for both search and insertion per distribution (open addressing: linear probing)

    # Fixed table size
    table_size = 101
    # Fixed load factor
    load_factor = 0.67
    # Number of keys
    n_keys = int(table_size * load_factor)
    # Number of queries
    n_queries = 500
    # Key distributions: uniform, skewed, and sequential
    distributions = ["uniform", "skewed", "sequential"]

    # Initialize result lists
    search_hit_times = []
    search_miss_times = []
    avg_ins_probes = []
    avg_hit_probes = []
    avg_miss_probes = []

    # Measure search times and probe lengths
    for dist in distributions:
        keys = generate_keys(dist, n_keys)

        # Build table
        hm = HashMap(size=table_size, hash_method="multiplication")
        for k in keys:
            hm.insert(k, k)

        unique_keys = list(dict.fromkeys(keys))

        # Successful searches, randomly sampled
        hit_sample = random.choices(unique_keys, k=n_queries)
        # Unsuccessful searches, not in the keys
        miss_sample = []
        for k in random.choices(unique_keys, k=n_queries):
            miss_sample.append(k + 10000000)

        # Measure search times
        search_hit_times.append(measure_search_time(hm, hit_sample) * 1e6)
        search_miss_times.append(measure_search_time(hm, miss_sample) * 1e6)

        # Probe length measurements
        ai, ah, af = measure_probe_lengths(table_size, keys)
        avg_ins_probes.append(ai)
        avg_hit_probes.append(ah)
        avg_miss_probes.append(af)

    # Citation: Used AI tools for better visualization

    # Plot 1: Search time by distributions
    x = range(len(distributions))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([i - width/2 for i in x], search_hit_times, width, label="Successful search", color="steelblue")
    ax.bar([i + width/2 for i in x], search_miss_times, width, label="Unsuccessful search", color="coral")
    ax.set_xticks(list(x))
    ax.set_xticklabels(distributions)
    ax.set_ylabel("Avg Search Time (µs)")
    ax.set_title(f"Experiment 2a: Search Time by Key Distribution\n"
                 f"(table_size={table_size}, load_factor={load_factor})")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("exp2a_distribution_search_time.png", dpi=150)
    plt.show()
    print("Experiment 2a done → exp2a_distribution_search_time.png")

    # Plot 2: Probe lengths by distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    w = 0.25
    ax.bar([i - w for i in x], avg_ins_probes, w, label="Insert probes", color="mediumseagreen")
    ax.bar([i for i in x], avg_hit_probes, w, label="Search probes (hit)", color="steelblue")
    ax.bar([i + w for i in x], avg_miss_probes, w, label="Search probes (miss)", color="coral")
    ax.set_xticks(list(x))
    ax.set_xticklabels(distributions)
    ax.set_ylabel("Avg Probe Length")
    ax.set_title(f"Experiment 2b: Avg Probe Length by Key Distribution\n"
                 f"(table_size={table_size}, load_factor={load_factor})")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("exp2b_distribution_probe_length.png", dpi=150)
    plt.show()
    print("Experiment 2b done → exp2b_distribution_probe_length.png")

    # Print summary table
    print(f"\n{'Distribution':<12} {'Hit(µs)':>10} {'Miss(µs)':>10} "
          f"{'Ins probes':>12} {'Hit probes':>12} {'Miss probes':>12}")
    print("-" * 70)
    for i, dist in enumerate(distributions):
        print(f"{dist:<12} {search_hit_times[i]:>10.4f} {search_miss_times[i]:>10.4f} "
              f"{avg_ins_probes[i]:>12.2f} {avg_hit_probes[i]:>12.2f} "
              f"{avg_miss_probes[i]:>12.2f}")

# Test across different table sizes and load factors
def run_experiments():
        # Set random seed for reproducibility
        random.seed(123)

        # Experiment 1: Load Factor vs. Search Time
        print("Running Experiment 1: Load Factor vs. Search Time")
        experiment_load_factor_vs_search_time()

        # Experiment 2: Key Distribution Comparison
        print("Running Experiment 2: Key Distribution Comparison")
        experiment_key_distribution()

# Main function: Run the experiments
if __name__ == "__main__":
    run_experiments()