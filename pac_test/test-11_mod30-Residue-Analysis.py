# ==============================================================================
# PRIMORIAL ANCHOR CONJECTURE (PAC) - TEST 15: Mod 30 Residue Analysis
#
# This script builds the *CORRECTED* "v1.0" (Mod 30) engine data.
#
# It bins all anchors and failures by their S_n % 30 residue class
# and calculates the FAILURE RATE (%) for each class.
#
# This will replace the old, hard-coded "raw count" data
# with a normalized "failure rate" map, allowing for a true
# "apples-to-apples" comparison against the v_mod6 engine.
# ==============================================================================

import math
import time
from collections import defaultdict
import json

# --- Configuration ---
PRIME_INPUT_FILE = "../prime/primes_100m.txt"
MAX_PRIME_PAIRS_TO_TEST = 50000000
START_INDEX = 10 
OUTPUT_JSON_FILE = "messiness_map_v1_mod30.json" # Our new, corrected engine file

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
    
    required_primes = MAX_PRIME_PAIRS_TO_TEST + START_INDEX + 10
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small.")
        return None, None
        
    return prime_list, prime_set

# --- Main Testing Logic ---
def run_mod30_residue_analysis():
    
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PAC Mod 30 Residue Analysis for {MAX_PRIME_PAIRS_TO_TEST:,} S_n pairs...")
    print(f"  - Binning anchors and failures by S_n % 30...")
    print(f"  - Saving results to {OUTPUT_JSON_FILE}")
    print("-" * 80)
    start_time = time.time()
    
    total_law_I_failures = 0
    failure_counts = defaultdict(int)
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
        
        # --- THIS IS THE ONLY CHANGE ---
        residue = anchor_S_n % 30
        # ---
        anchor_counts[residue] += 1

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

        is_k_composite = (min_distance_k > 1) and (min_distance_k not in prime_set)
        
        if is_k_composite:
            total_law_I_failures += 1
            failure_counts[residue] += 1
            
    print(f"Progress: {MAX_PRIME_PAIRS_TO_TEST:,} / {MAX_PRIME_PAIRS_TO_TEST:,} | Law I Fails: {total_law_I_failures:,} | Time: {time.time() - start_time:.0f}s   ")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    # --- Process and Save Data ---
    print("\n" + "="*20 + " PAC-15: MOD 30 RESIDUE ANALYSIS (Corrected v1.0 Data) " + "="*20)
    print(f"\nTotal S_n Anchors Analyzed: {MAX_PRIME_PAIRS_TO_TEST:,}")
    print(f"Total Law I Failures Found: {total_law_I_failures:,}")
    
    messiness_scores_v1_mod30 = {}
    
    print(f"\n{'Residue':<10} | {'Failure Count':<15} | {'Total Anchors':<15} | {'FAILURE RATE (%)':<20}")
    print("-" * 65)

    for residue in range(30):
        failures = failure_counts.get(residue, 0)
        total_anchors = anchor_counts.get(residue, 0)
        
        if total_anchors > 0:
            failure_rate = (failures / total_anchors) * 100
            messiness_scores_v1_mod30[residue] = failure_rate
            print(f"{residue:<10} | {failures:<15,} | {total_anchors:<15,} | {failure_rate:<20.4f}%")
        else:
            # Mark impossible residues (odd numbers, etc.) as 'inf'
            messiness_scores_v1_mod30[residue] = float('inf')
            
    print("-" * 65)

    # --- *** SAVE THE ENGINE DATA TO A FILE *** ---
    try:
        with open(OUTPUT_JSON_FILE, 'w') as f:
            json.dump(messiness_scores_v1_mod30, f, indent=2)
        print(f"\n  [SUCCESS] Corrected messiness map saved to '{OUTPUT_JSON_FILE}'")
    except Exception as e:
        print(f"\n  [FAILURE] Could not save JSON file: {e}")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_mod30_residue_analysis()