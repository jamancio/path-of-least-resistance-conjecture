# ==============================================================================
# PRIMORIAL ANCHOR CONJECTURE (PAC) - TEST 8: Mod 210 Residue Analysis
#
# This script builds the "v3.0" engine data.
#
# It's a direct expansion of the successful Test 3 (Mod 30).
# It will analyze all 6.6 million failures
# and bin them based on their S_n % 210 residue class.
#
# The output will be a "Messiness Score" (the Failure Rate %) for
# each of the 210 residue classes, which will be the
# data for the new PLR v3.0 engine.
# ==============================================================================

import math
import time
from collections import defaultdict

# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
MAX_PRIME_PAIRS_TO_TEST = 50000000
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
    
    required_primes = MAX_PRIME_PAIRS_TO_TEST + START_INDEX + 10
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small.")
        return None, None
        
    return prime_list, prime_set

# --- Main Testing Logic ---
def run_mod210_residue_analysis():
    
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PAC Mod 210 Residue Analysis for {MAX_PRIME_PAIRS_TO_TEST:,} S_n pairs...")
    print(f"  - Binning anchors and failures by S_n % 210...")
    print("-" * 80)
    start_time = time.time()
    
    # --- Data structures for the test ---
    total_law_I_failures = 0
    
    # Dictionary: {residue: failure_count}
    failure_counts = defaultdict(int)
    
    # Dictionary: {residue: anchor_count}
    anchor_counts = defaultdict(int)

    loop_end_index = MAX_PRIME_PAIRS_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            print(f"Progress: {progress:,} / {MAX_PRIME_PAIRS_TO_TEST:,} | Law I Fails: {total_law_I_failures:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        p_n_plus_1 = prime_list[i+1]
        anchor_S_n = p_n + p_n_plus_1
        
        # --- 1. Categorize the Anchor ---
        residue = anchor_S_n % 210
        anchor_counts[residue] += 1

        # --- 2. Find the Law I k_min ---
        min_distance_k = 0
        search_dist = 1
        
        while True:
            q_lower = anchor_S_n - search_dist
            q_upper = anchor_S_n + search_dist

            if q_lower in prime_set:
                min_distance_k = search_dist
                break
            if q_upper in prime_set:
                min_distance_k = search_dist
                break
                
            search_dist += 1
            if search_dist > 2000: break 
        
        if min_distance_k == 0: continue 

        # --- 3. Check if it's a composite failure ---
        is_k_composite = (min_distance_k > 1) and (min_distance_k not in prime_set)
        
        if is_k_composite:
            total_law_I_failures += 1
            
            # --- 4. Log the failure in the map ---
            failure_counts[residue] += 1
            
    print(f"Progress: {MAX_PRIME_PAIRS_TO_TEST:,} / {MAX_PRIME_PAIRS_TO_TEST:,} | Law I Fails: {total_law_I_failures:,} | Time: {time.time() - start_time:.0f}s   ")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    # --- Final Reports ---
    print("\n" + "="*20 + " PAC-8: MOD 210 RESIDUE ANALYSIS (v3.0 Engine Data) " + "="*20)
    print(f"\nTotal S_n Anchors Analyzed: {MAX_PRIME_PAIRS_TO_TEST:,}")
    print(f"Total Law I Failures Found: {total_law_I_failures:,}")

    print("\n" + "-" * 20 + " Failure Rate by S_n % 210 Residue " + "-" * 20)
    print(f"\n{'Residue':<10} | {'Failure Count':<15} | {'Total Anchors':<15} | {'FAILURE RATE (%)':<20}")
    print("-" * 65)
    
    messiness_scores = {} # This is the new v3.0 engine data
    
    # We must sort by FAILURE RATE (messiness) to see the best/worst
    residue_data = []
    for residue in range(210):
        failures = failure_counts.get(residue, 0)
        total_anchors = anchor_counts.get(residue, 0)
        
        if total_anchors > 0:
            failure_rate = (failures / total_anchors) * 100
            messiness_scores[residue] = failure_rate
            residue_data.append((residue, failures, total_anchors, failure_rate))
    
    # Sort by failure rate, messiest first
    residue_data.sort(key=lambda x: x[3], reverse=True)
    
    print("--- Top 20 'Messiest' Residue Classes (Highest Failure Rate) ---")
    for data in residue_data[:20]:
        print(f"{data[0]:<10} | {data[1]:<15,} | {data[2]:<15,} | {data[3]:<20.4f}%")
        
    print("\n" + "..." + "\n")

    print("--- Top 20 'Cleanest' Residue Classes (Lowest Failure Rate) ---")
    for data in residue_data[-20:]:
        print(f"{data[0]:<10} | {data[1]:<15,} | {data[2]:<15,} | {data[3]:<20.4f}%")
        
    print("-" * 65)

    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  Analysis complete. This 2D map provides the true 'Messiness Score'")
    print("  (the Failure Rate) for each of the 210 residue classes.")
    print("  This data will be the engine for the PLR v3.0 test.")
    
    # You can save 'messiness_scores' dictionary to a file here
    # import json
    # with open('messiness_map_v3_mod210.json', 'w') as f:
    #     json.dump(messiness_scores, f)
    # print("\n  Messiness Score map saved to 'messiness_map_v3_mod210.json'")
    
    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_mod210_residue_analysis()