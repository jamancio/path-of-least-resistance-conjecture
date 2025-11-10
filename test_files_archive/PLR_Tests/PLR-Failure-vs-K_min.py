# ==============================================================================
# PLR ANALYSIS TEST 1: PLR Failure Rate vs. PAS k_min
#
# This script analyzes the 42.16% of failures from the "v7.0 Recursive" engine.
#
# HYPOTHESIS:
# The 42.16% of "PLR Failures" are not random. They will be
# disproportionately concentrated on anchors that are "messy"
# in a specific way (e.g., true anchors where k_min = 9, 15, 25, etc.).
#
# METHODOLOGY:
# 1. Loop through all 50,000,000 p_n.
# 2. For each p_n, find its *true* anchor S_n = p_n + p_{n+1}.
# 3. Find the PAS Law I status for S_n by finding its k_min.
# 4. Run the full v7.0 Recursive PLR test (10 candidates)
#    to get the PLR Status ("Success" or "Failure").
# 5. Log the PLR status against the k_min type (e.g., "CLEAN", 9, 15, 25...).
# 6. Print a final summary table showing the PLR failure rate for each k_min.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v7.0 "Recursive") ---
# We assume the data files are in a 'data' subfolder
MOD6_ENGINE_FILE = "../data/messiness_map_v_mod6.json"
MOD210_ENGINE_FILE = "../data/messiness_map_v3_mod210.json"
# v1.0 (Mod 30) map is hard-coded as seen in your other scripts
MESSINESS_MAP_V1_MOD30 = {
    0: 9907,    1: float('inf'), 2: 654113,  3: float('inf'), 4: 431661,
    5: float('inf'), 6: 171547,  7: float('inf'), 8: 662464,  9: float('inf'),
    10: 751163, 11: float('inf'), 12: 199190, 13: float('inf'), 14: 424448,
    15: float('inf'), 16: 426340, 17: float('inf'), 18: 200139, 19: float('inf'),
    20: 749951, 21: float('inf'), 22: 661166, 23: float('inf'), 24: 171854,
    25: float('inf'), 26: 430955, 27: float('inf'), 28: 654709, 29: float('inf')
}

MESSINESS_MAP_V_MOD6 = None
MESSINESS_MAP_V3_MOD210 = None

def load_all_engine_data():
    """Loads all three messiness maps."""
    global MESSINESS_MAP_V_MOD6, MESSINESS_MAP_V1_MOD30, MESSINESS_MAP_V3_MOD210
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            data_mod6 = json.load(f)
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in data_mod6.items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
            
        print("Loaded v1.0 (Mod 30) engine data (hard-coded).")

        with open(MOD210_ENGINE_FILE, 'r') as f:
            data_mod210 = json.load(f)
            MESSINESS_MAP_V3_MOD210 = {int(k): v for k, v in data_mod210.items()}
        print(f"Loaded v3.0 (Mod 210) engine data from '{MOD210_ENGINE_FILE}'.")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        print("Please ensure 'messiness_map_v_mod6.json' and 'messiness_map_v3_mod210.json' are in a 'data' folder.")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v7_recursive(anchor_sn, gap_g_n):
    """The v7.0 "Recursive" Engine."""
    if MESSINESS_MAP_V_MOD6 is None or MESSINESS_MAP_V1_MOD30 is None or MESSINESS_MAP_V3_MOD210 is None:
        return (float('inf'), float('inf')) # Engine failed to load

    # --- This is the "Recursive" logic ---
    if gap_g_n > 210:
        # Gap is huge, use our most precise filter: Mod 210
        score = MESSINESS_MAP_V3_MOD210.get(anchor_sn % 210, float('inf'))
    elif gap_g_n > 30:
        # Gap is large, use the Mod 30 filter
        score = MESSINESS_MAP_V1_MOD30.get(anchor_sn % 30, float('inf'))
    else:
        # Gap is small, use the Mod 6 filter (our champion)
        score = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    
    # We add the gap as a "tie-breaker"
    return (score, gap_g_n)
# --- End Engine Setup ---


# --- Configuration ---
PRIME_INPUT_FILE = "../prime/primes_100m.txt"
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
        print("Please ensure 'primes_100m.txt' is in a 'prime' folder.")
        return None, None
    
    prime_set = set(prime_list)
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes and created set in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 100 # Buffer
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None, None
        
    return prime_list, prime_set

def is_prime(k_val, prime_set):
    """Helper function to check if k is prime."""
    if k_val < 2: return False
    return k_val in prime_set

# --- Main Testing Logic ---
def run_PLR_vs_k_min_analysis():
    
    if not load_all_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Failure vs. k_min Analysis for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using v7.0 'Recursive' Engine")
    print(f"  - Correlating PLR status with true anchor's k_min type.")
    print("-" * 80)
    start_time = time.time()
    
    # --- Data structures for the k_min breakdown ---
    total_predictions = 0
    k_min_success_counts = defaultdict(int)
    k_min_failure_counts = defaultdict(int)
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    # Ensure we don't read past the end of the list
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 1):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i+1]
        
        # --- 1. Get PLR Status (We do this first) ---
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            messiness_score_tuple = get_messiness_score_v7_recursive(S_cand, gap_g_i)
            candidate_scores.append((messiness_score_tuple, q_i))

        # Sort by score (tuple[0]), then gap (tuple[1])
        candidate_scores.sort(key=lambda x: x[0]) 
        
        min_score = candidate_scores[0][0] # Get the best score tuple
        winners_list = [q_i for score_tuple, q_i in candidate_scores if score_tuple == min_score]
        
        is_PLR_success = (true_p_n_plus_1 in winners_list)

        # --- 2. Get PAS Law I Status for the *true* anchor ---
        anchor_S_n = p_n + true_p_n_plus_1
        
        min_distance_k = 0
        search_dist = 1
        # Search for the closest prime to the true anchor
        while True:
            # Check k=search_dist
            q_lower = anchor_S_n - search_dist
            if q_lower in prime_set: 
                min_distance_k = search_dist
                break
            
            q_upper = anchor_S_n + search_dist
            if q_upper in prime_set: 
                min_distance_k = search_dist
                break
                
            search_dist += 1
            
            # Failsafe for very large gaps
            if search_dist > 2000: 
                min_distance_k = -1 # Flag as an anomaly
                break 
        
        if min_distance_k == -1: 
            continue # Skip this prime (e.g., k_min is too large)
            
        # Determine the k_min "type"
        is_PAS_clean = (min_distance_k == 1) or is_prime(min_distance_k, prime_set)
        
        if is_PAS_clean:
            k_type = "CLEAN (k=1,P)"
        else:
            k_type = min_distance_k # e.g., 9, 15, 21, 25...

        # --- 3. Tally the results ---
        total_predictions += 1
        if is_PLR_success:
            k_min_success_counts[k_type] += 1
        else:
            k_min_failure_counts[k_type] += 1
            
    # --- Final Summary ---
    progress = total_predictions
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR Failure vs. k_min Analysis Report " + "="*20)
    print(f"\nTotal Primes Analyzed (p_n): {total_predictions:,}")
    
    total_PLR_success = sum(k_min_success_counts.values())
    total_PLR_failure = sum(k_min_failure_counts.values())
    
    print(f"  - Overall PLR v7.0 Accuracy: {(total_PLR_success / total_predictions) * 100:.2f}%")
    
    print("\n" + "-" * 20 + " PLR Performance by True Anchor's k_min Type " + "-" * 20)
    print(f"\n{'k_min Type':<15} | {'PLR Success':<12} | {'PLR Failure':<12} | {'Total Events':<12} | {'PLR Failure Rate':<18}")
    print("-" * 75)
    
    all_k_types = set(k_min_success_counts.keys()) | set(k_min_failure_counts.keys())
    
    # Handle "CLEAN" row first
    k_clean = "CLEAN (k=1,P)"
    if k_clean in all_k_types:
        s = k_min_success_counts[k_clean]
        f = k_min_failure_counts[k_clean]
        total = s + f
        fail_rate = (f / total) * 100
        print(f"{k_clean:<15} | {s:<12,} | {f:<12,} | {total:<12,} | {fail_rate:>17.2f}%")
    
    # Sort and print composite k_min rows
    composite_keys = sorted([k for k in all_k_types if k != k_clean])
    
    for k in composite_keys:
        s = k_min_success_counts[k]
        f = k_min_failure_counts[k]
        total = s + f
        fail_rate = (f / total) * 100
        print(f"{k:<15} | {s:<12,} | {f:<12,} | {total:<12,} | {fail_rate:>17.2f}%")

    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  This table shows the *exact* source of the PLR engine's failures.")
    print("  By comparing the 'PLR Failure Rate' of 'CLEAN' anchors")
    print("  against the rates for composite k_min anchors (like 9, 15, 25),")
    print("  you can prove which 'messy' anchors are 'poisoning' the accuracy.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_vs_k_min_analysis()