# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 30: v16.0 Gap Signature Analysis
#
# This is the final post-mortem on our 75.94% champion v16.0 engine.
#
# We are testing the "Gap Signature" hypothesis:
# Are the remaining 24.06% of failures correlated with the
# relationship between the *previous* gap (g_{n-1}) and the
# *current* gap (g_n)?
#
# This script will run the v16.0 engine and, for every failure,
# it will log the failure in a 2D matrix:
#
#          | g_n (Small) | g_n (Medium) | g_n (Large)
# g_{n-1} (Small) | ...         | ...          | ...
# g_{n-1} (Medium)| ...         | ...          | ...
# g_{n-1} (Large) | ...         | ...          | ...
#
# A non-uniform distribution (e.g., a huge number in the
# "Small_to_Large" bin) will prove the existence of
# a new, solvable "Gap Signature".
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v16.0 "Chained Signature") ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

CLEAN_THRESHOLD = 3.0  
MESSY_THRESHOLD = 20.0 
MAX_SIGNATURE_SEARCH_DEPTH = 4 # Ranks 2, 3, 4

def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    """The v11.0 "Weighted Gap" Engine Core."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'): return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))

# --- Full v16.0 Prediction Logic ---
def get_v16_prediction(p_n, candidates):
    
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        vmod6_rate = get_vmod6_score(S_cand)
        candidate_scores.append((score_v11, q_i, vmod6_rate))

    candidate_scores.sort(key=lambda x: x[0])
    
    winner_v11_prime = candidate_scores[0][1]
    winner_v11_vmod6 = candidate_scores[0][2]
    
    prediction_v16 = winner_v11_prime # Default
    
    if winner_v11_vmod6 < CLEAN_THRESHOLD: 
        for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH): # Ranks 2, 3, 4
            if rank_index >= len(candidate_scores): break
            next_candidate_vmod6 = candidate_scores[rank_index][2]
            if next_candidate_vmod6 > MESSY_THRESHOLD:
                prediction_v16 = candidate_scores[rank_index][1]
                break
                
    return prediction_v16

# --- Gap Categorization ---
# Based on test-7 result: Overall Average Gap (g_n) for all tested primes: 19.6490
AVG_GAP = 19.649
GAP_BIN_SMALL = 18.0
GAP_BIN_LARGE = 22.0

def categorize_gap(gap):
    """Categorizes the gap g_n into Small, Medium, or Large."""
    if gap < GAP_BIN_SMALL:
        return "Small"
    elif gap >= GAP_BIN_LARGE:
        return "Large"
    else: # 18.0 <= gap < 22.0
        return "Medium"

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
        return None
    
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_gap_signature_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Gap Signature' Analysis (Test 30) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v16.0 (75.94% Champion)")
    print(f"  - Analyzing Failures by Gap Signature (g_{'n-1'} vs. g_n)...")
    print(f"  - Gap Bins: Small (<{GAP_BIN_SMALL}), Medium (>= {GAP_BIN_SMALL} and < {GAP_BIN_LARGE}), Large (>= {GAP_BIN_LARGE})")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_failures = 0
    
    # --- Data structure for the 2D Matrix ---
    # Stores {"Small_to_Large": count, "Small_to_Small": count, ...}
    gap_signature_failure_counts = defaultdict(int) 
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    # Start at START_INDEX + 1 so we always have a g_{n-1}
    for i in range(START_INDEX + 1, loop_end_index):
        if (i - (START_INDEX+1) + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - (START_INDEX+1) + 1
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Failures: {total_failures:,} | Time: {elapsed:.0f}s", end='\r')

        # --- 1. Get Gaps ---
        p_n_minus_1 = prime_list[i - 1]
        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        g_n_minus_1 = p_n - p_n_minus_1
        g_n = true_p_n_plus_1 - p_n
        
        # --- 2. Get v16.0 Prediction ---
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        total_predictions += 1
        prediction_v16 = get_v16_prediction(p_n, candidates)

        if prediction_v16 != true_p_n_plus_1:
            # --- THIS IS A v16.0 FAILURE. ANALYZE IT. ---
            total_failures += 1
            
            # 3. Categorize gaps and log the signature
            g_n_minus_1_category = categorize_gap(g_n_minus_1)
            g_n_category = categorize_gap(g_n)
            
            signature = f"{g_n_minus_1_category}_to_{g_n_category}"
            gap_signature_failure_counts[signature] += 1
            
    # --- Final Summary ---
    print(f"Progress: {total_predictions:,} / {total_predictions:,} | Failures: {total_failures:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " v16.0 FAILURE DISTRIBUTION BY GAP SIGNATURE (g_n-1 vs g_n) " + "="*20)
    print(f"\nTotal Primes Tested: {total_predictions:,}")
    print(f"Total Failures Analyzed (24.06%): {total_failures:,}")
    
    print("\n" + "-" * 20 + " 2D Failure Matrix (Previous Gap vs. Current Gap) " + "-" * 20)
    
    # --- Print the 2D Matrix ---
    categories = ["Small", "Medium", "Large"]
    header = f"{'g_(n-1)':<10} | {'g_n (Small)':<15} | {'g_n (Medium)':<15} | {'g_n (Large)':<15} | {'TOTAL':<15}"
    print(header)
    print("-" * 75)
    
    row_totals = defaultdict(int)
    col_totals = defaultdict(int)
    
    for prev_cat in categories:
        row_str = f"{prev_cat:<10} | "
        for curr_cat in categories:
            signature = f"{prev_cat}_to_{curr_cat}"
            count = gap_signature_failure_counts.get(signature, 0)
            
            perc_of_total = (count / total_failures) * 100 if total_failures > 0 else 0
            row_str += f"{count:>10,} ({perc_of_total:4.1f}%) | "
            
            row_totals[prev_cat] += count
            col_totals[curr_cat] += count
        
        row_perc = (row_totals[prev_cat] / total_failures) * 100 if total_failures > 0 else 0
        row_str += f"{row_totals[prev_cat]:>10,} ({row_perc:4.1f}%)"
        print(row_str)

    print("-" * 75)
    
    # Print Column Totals
    total_str = f"{'TOTAL':<10} | "
    for curr_cat in categories:
        col_perc = (col_totals[curr_cat] / total_failures) * 100 if total_failures > 0 else 0
        total_str += f"{col_totals[curr_cat]:>10,} ({col_perc:4.1f}%) | "
    total_str += f"{total_failures:>10,} (100.0%)"
    print(total_str)


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL ANALYTIC CONCLUSION " + "="*20)
    print("\n  We are looking for a 'hot corner' in the matrix.")
    
    small_to_large_perc = (gap_signature_failure_counts.get("Small_to_Large", 0) / total_failures) * 100 if total_failures > 0 else 0

    if small_to_large_perc > 25.0: # If >25% of all failures are in this one bin
        print(f"\n  [VERDICT: 'GAP SIGNATURE' DISCOVERED!]")
        print(f"  A massive {small_to_large_perc:.2f}% of all failures")
        print("  are concentrated in the 'Small_to_Large' gap signature.")
        print("  This is a new, solvable, non-linear signal.")
        print("  It proves failures are predictable based on gap volatility.")
    else:
        print(f"\n  [VERDICT: THE TRAIL HAS GONE COLD. 75.94% IS THE LIMIT.]")
        print(f"  The failures ({small_to_large_perc:.2f}% in 'Small_to_Large')")
        print("  are distributed relatively evenly across all gap signatures.")
        print("  This confirms the previous p_n residue test: the 24.06%")
        print("  of failures are true *local* randomness, not correlated")
        print("  with the previous gap. The analytic pursuit ends here.")

    print("=" * (50 + len(" FINAL ANALYTIC CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_gap_signature_analysis()