# ==============================================================================
# PRIMORIAL ANCHOR CONJECTURE (PAC) - TEST 10: Mod 6 Gap Analysis
#
# This script builds the "v_mod6_gap" engine data.
#
# It creates a 2D "Messiness Map" by binning all 50M anchors
# and their failures based on TWO features:
# 1. The S_n % 6 residue class (our 55.51% signal)
# 2. The g_n gap category (Small, Medium, Large)
#
# The output is a precise 2D map of "Failure Rates (%)", which will be
# the new engine for our next PLR test.
# ==============================================================================

import math
import time
from collections import defaultdict
import json

# --- Configuration ---
PRIME_INPUT_FILE = "../prime/primes_100m.txt"
MAX_PRIME_PAIRS_TO_TEST = 50000000
START_INDEX = 10 
OUTPUT_JSON_FILE = "messiness_map_v_mod6_gap.json" # Our new engine file

# --- Gap Categorization (from test-6-result.txt) ---
OVERALL_AVG_GAP = 19.6490 #
GAP_BIN_SMALL = 18.0
GAP_BIN_LARGE = 22.0

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

def categorize_gap(gap_g_n):
    """Categorizes the gap g_n into Small, Medium, or Large."""
    if gap_g_n < GAP_BIN_SMALL:
        return "Small"
    elif gap_g_n >= GAP_BIN_LARGE:
        return "Large"
    else:
        return "Medium"

# --- Main Testing Logic ---
def run_mod6_gap_analysis():
    
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PAC Mod 6 + Gap 2D Analysis for {MAX_PRIME_PAIRS_TO_TEST:,} S_n pairs...")
    print(f"  - Binning anchors and failures by (S_n % 6) AND (Gap Category)...")
    print(f"  - Saving results to {OUTPUT_JSON_FILE}")
    print("-" * 80)
    start_time = time.time()
    
    total_law_I_failures = 0
    
    # 2D Dictionary: {residue: {gap_category: failure_count}}
    failure_map = {res: defaultdict(int) for res in range(6)}
    
    # {residue: {gap_category: anchor_count}}
    anchor_map = {res: defaultdict(int) for res in range(6)}

    loop_end_index = MAX_PRIME_PAIRS_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            print(f"Progress: {progress:,} / {MAX_PRIME_PAIRS_TO_TEST:,} | Law I Fails: {total_law_I_failures:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        p_n_plus_1 = prime_list[i+1]
        anchor_S_n = p_n + p_n_plus_1
        gap_g_n = p_n_plus_1 - p_n
        
        # --- 1. Categorize the Anchor ---
        residue = anchor_S_n % 6
        gap_category = categorize_gap(gap_g_n)
        
        anchor_map[residue][gap_category] += 1

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
            failure_map[residue][gap_category] += 1
            
    print(f"Progress: {MAX_PRIME_PAIRS_TO_TEST:,} / {MAX_PRIME_PAIRS_TO_TEST:,} | Law I Fails: {total_law_I_failures:,} | Time: {time.time() - start_time:.0f}s   ")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    # --- Final Reports ---
    print("\n" + "="*20 + " PAC-10: MOD 6 + GAP ANALYSIS (v_mod6_gap Engine Data) " + "="*20)
    print(f"\nTotal S_n Anchors Analyzed: {MAX_PRIME_PAIRS_TO_TEST:,}")
    print(f"Total Law I Failures Found: {total_law_I_failures:,}")

    print("\n" + "-" * 20 + " Failure Rate by (S_n % 6 Residue) AND (Gap Category) " + "-" * 20)
    print(f"\n{'Residue':<10} | {'Gap Cat.':<10} | {'Failure Count':<15} | {'Total Anchors':<15} | {'FAILURE RATE (%)':<20}")
    print("-" * 75)
    
    messiness_scores_v_mod6_gap = {} 

    for residue in range(6):
        # S_n = p_n + p_{n+1}. For n>0, p_n, p_{n+1} are odd, so S_n is even.
        # Residues 1, 3, 5 are not expected (except for S_0=2+3=5)
        if residue % 2 != 0: continue 
            
        for category in ["Small", "Medium", "Large"]:
            failures = failure_map[residue].get(category, 0)
            total_anchors = anchor_map[residue].get(category, 0)
            
            if total_anchors > 0:
                failure_rate = (failures / total_anchors) * 100
                messiness_scores_v_mod6_gap[(residue, category)] = failure_rate
                print(f"{residue:<10} | {category:<10} | {failures:<15,} | {total_anchors:<15,} | {failure_rate:<20.4f}%")
            else:
                # If this bin never appeared, it's impossible. Infinitely messy.
                messiness_scores_v_mod6_gap[(residue, category)] = float('inf')
        print("-" * 75)
        
    # --- *** SAVE THE ENGINE DATA TO A FILE *** ---
    try:
        # We need to convert the tuple keys to strings for JSON
        string_key_map = {f"{k[0]},{k[1]}": v for k, v in messiness_scores_v_mod6_gap.items()}
        with open(OUTPUT_JSON_FILE, 'w') as f:
            json.dump(string_key_map, f, indent=2)
        print(f"\n  [SUCCESS] Messiness Score map saved to '{OUTPUT_JSON_FILE}'")
    except Exception as e:
        print(f"\n  [FAILURE] Could not save JSON file: {e}")
    
    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_mod6_gap_analysis()