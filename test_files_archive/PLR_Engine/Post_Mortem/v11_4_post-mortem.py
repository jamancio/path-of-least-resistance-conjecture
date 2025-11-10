# ==============================================================================
# PLR ANALYSIS - TEST 28: Structural Factor (k_min) Composition
#
# This script analyzes the remaining predictability by classifying the
# structural type (the k_min) of every composite failure.
#
# Our goal is to identify which odd prime factors (5, 7, 11...) are
# creating the final, unpredictable failures.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v11.0 "Weighted Gap" Core) ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False

def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    """The v11.0 "Weighted Gap" Engine."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'):
        return float('inf')
    return (score_mod6 + 1.0) * gap_g_n
# --- End Engine Setup ---

# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
PRIMES_TO_TEST = 50000000 
NUM_CANDIDATES_TO_CHECK = 10 
START_INDEX = 10 

# --- Function to load primes from a file ---
def load_primes_from_file(filename):
    """Loads ALL primes from the text file."""
    print(f"Loading ALL primes from {filename}...")
    start_time = time.time()
    try:
        with open(filename, 'r') as f:
            prime_list = [int(line.strip()) for line in f]
    except FileNotFoundError:
        print(f"FATAL ERROR: The prime file '{filename}' was not found.")
        return None, None
    
    prime_set = set(prime_list)
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes and created set in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None, None
        
    return prime_list, prime_set

def is_prime(k_val, prime_set):
    """Helper function to check if k is prime."""
    if k_val < 2: return False
    return k_val in prime_set

# --- Main Testing Logic ---
def run_PLR_k_min_composition_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR k_min Composition Analysis for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Analyzing composite k_min for v11.0 Failures (the structural root).")
    print("-" * 80)
    start_time = time.time()
    
    total_v11_failures_analyzed = 0
    # Dictionary: {k_min_value: failure_count}
    k_min_failure_counts = defaultdict(int) 
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Failures Analyzed: {total_v11_failures_analyzed:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        # 1. Run the v11.0 Engine to check for a FAILURE
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
            candidate_scores.append((score_v11, q_i))

        candidate_scores.sort(key=lambda x: x[0])
        winner_v11 = candidate_scores[0][1]

        if winner_v11 != true_p_n_plus_1:
            # --- THIS IS A v11.0 FAILURE. NOW ANALYZE THE TRUE ANCHOR'S STRUCTURE. ---
            
            # 2. Find the true anchor's k_min (structural factor)
            anchor_S_n = p_n + true_p_n_plus_1
            min_distance_k = 0
            search_dist = 1
            
            while True:
                q_lower = anchor_S_n - search_dist
                q_upper = anchor_S_n + search_dist
                if q_lower in prime_set: min_distance_k = search_dist; break
                if q_upper in prime_set: min_distance_k = search_dist; break
                search_dist += 1
                if search_dist > 2000: break # Failsafe
            
            if min_distance_k > 0:
                is_k_composite = (min_distance_k > 1) and not is_prime(min_distance_k, prime_set)
                
                if is_k_composite:
                    total_v11_failures_analyzed += 1
                    k_min_failure_counts[min_distance_k] += 1
            
    # --- Final Summary ---
    print(f"Progress: {PRIMES_TO_TEST:,} / {PRIMES_TO_TEST:,} | Failures Analyzed: {total_v11_failures_analyzed:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " k_min COMPOSITION OF PLR FAILURES " + "="*20)
    print(f"\nTotal v11.0 Failures Analyzed (k_min Composite): {total_v11_failures_analyzed:,}")
    
    # Process and sort data
    k_min_data = []
    for k, count in k_min_failure_counts.items():
        k_min_data.append((k, count))
    
    # Sort by count (descending)
    k_min_data.sort(key=lambda x: x[1], reverse=True)
    
    print("\n" + "-" * 20 + " Top 10 Structural Failure Factors " + "-" * 20)
    print(f"\n{'k_min Value':<12} | {'Failure Count':<15} | {'% of Total Failures':<25} | {'Dominant Factor':<15}")
    print("-" * 75)
    
    total_sum = sum(k_min_failure_counts.values())
    
    # Find the dominant prime factor for context
    def get_dominant_prime_factor(k):
        if k % 3 == 0: return "Factor of 3"
        if k % 5 == 0: return "Factor of 5"
        if k % 7 == 0: return "Factor of 7"
        if k == 25: return "5*5"
        if k == 49: return "7*7"
        if k == 91: return "7*13"
        return "Other"

    for k, count in k_min_data[:10]:
        percentage = (count / total_sum) * 100
        factor = get_dominant_prime_factor(k)
        print(f"{k:<12} | {count:<15,} | {percentage:>24.2f}% | {factor:<15}")

    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  This analysis shows the structural weakness of the true anchor.")
    print("  We are looking for a concentration of factors other than 3.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_k_min_composition_analysis()