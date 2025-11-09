# ==============================================================================
# PRIMORIAL ANCHOR CONJECTURE (PAC) - TEST 7: 2D Messiness Map (v2.1)
#
# This script builds the "v2.1" engine by creating a 2D lookup table of
# "Messiness Scores". It replaces the flawed v2.0 "Gap Factor" logic.
#
# GOAL:
# We will analyze all 6.6 million failures and bin
# them based on TWO features:
# 1. The S_n % 30 residue class (from Test 3)
# 2. The g_n gap category (Small, Medium, Large) (from Test 6)
#
# The output is a precise 2D map of failure counts (e.g., Score[residue][gap_category]),
# which will become the basis for the PLR v2.1 engine.
# ==============================================================================

import math
import time
from collections import defaultdict

# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
MAX_PRIME_PAIRS_TO_TEST = 50000000
START_INDEX = 10 

# --- Gap Categorization (from test-6-result.txt) ---
# Overall average gap g_n from 50M pair test
OVERALL_AVG_GAP = 19.6490 #
# Let's define simple, clean bins around the average
GAP_BIN_SMALL = 18.0  # Gaps < 18 are "Small"
GAP_BIN_LARGE = 22.0  # Gaps >= 22 are "Large"
                      # Gaps between 18 and 22 are "Medium"

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
def run_2D_messiness_map_analysis():
    
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PAC 2D Messiness Map Analysis for {MAX_PRIME_PAIRS_TO_TEST:,} S_n pairs...")
    print(f"  - Binning {MAX_PRIME_PAIRS_TO_TEST:,} anchors by (S_n % 30) AND (Gap Category)...")
    print(f"  - Gap Bins: Small (<{GAP_BIN_SMALL}), Medium, Large (>{GAP_BIN_LARGE})")
    print("-" * 80)
    start_time = time.time()
    
    # --- Data structures for the test ---
    total_law_I_failures = 0
    
    # 2D Dictionary: {residue: {gap_category: failure_count}}
    failure_map = {res: defaultdict(int) for res in range(30)}
    
    # We also count total anchors in each bin to find the *failure rate*
    # {residue: {gap_category: anchor_count}}
    anchor_map = {res: defaultdict(int) for res in range(30)}

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
        residue = anchor_S_n % 30
        gap_category = categorize_gap(gap_g_n)
        
        # Increment the count for this type of anchor
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
            
            # --- 4. Log the failure in 2D map ---
            failure_map[residue][gap_category] += 1
            
    print(f"Progress: {MAX_PRIME_PAIRS_TO_TEST:,} / {MAX_PRIME_PAIRS_TO_TEST:,} | Law I Fails: {total_law_I_failures:,} | Time: {time.time() - start_time:.0f}s   ")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    # --- Final Reports ---
    print("\n" + "="*20 + " PAC-7: 2D MESSINESS MAP (v2.1 Engine Data) " + "="*20)
    print(f"\nTotal S_n Anchors Analyzed: {MAX_PRIME_PAIRS_TO_TEST:,}")
    print(f"Total Law I Failures Found: {total_law_I_failures:,}")

    print("\n" + "-" * 20 + " Failure Rate by (S_n % 30 Residue) AND (Gap Category) " + "-" * 20)
    print(f"\n{'Residue':<10} | {'Gap Cat.':<10} | {'Failure Count':<15} | {'Total Anchors':<15} | {'FAILURE RATE (%)':<20}")
    print("-" * 75)
    
    messiness_scores = {} # This is new v2.1 engine data

    for residue in range(30):
        if not anchor_map[residue]: continue # Skip empty residues
            
        for category in ["Small", "Medium", "Large"]:
            failures = failure_map[residue].get(category, 0)
            total_anchors = anchor_map[residue].get(category, 0)
            
            if total_anchors > 0:
                failure_rate = (failures / total_anchors) * 100
                
                # New "Messiness Score" is this failure rate.
                # A 15% failure rate is "messier" than a 10% rate.
                messiness_scores[(residue, category)] = failure_rate
                
                print(f"{residue:<10} | {category:<10} | {failures:<15,} | {total_anchors:<15,} | {failure_rate:<20.4f}%")
        print("-" * 75)
        
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  Analysis complete. This 2D map provides the true 'Messiness Score'")
    print("  (the Failure Rate) for each anchor combination.")
    print("\n  This data is the new, more accurate v2.1 engine.")
    print("  We can now build a PLR v2.1 test using this 'Failure Rate' as the")
    print("  score to predict the Path of Least Resistance.")

    # Optional: Save the messiness_scores to a file (e.g., pickle or json)
    # for the v2.1 test script to load directly.
    
    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_2D_messiness_map_analysis()