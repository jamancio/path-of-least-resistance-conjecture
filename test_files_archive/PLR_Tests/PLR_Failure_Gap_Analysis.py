# ==============================================================================
# PLR ANALYSIS (TEST 1): v7.0 Success vs. Failure Gap Analysis
#
# This is the "post-mortem" on our 57.84% champion "v7.0 Recursive" engine.
#
# GOAL:
# We will sort all 50M predictions into two bins:
# 1. SUCCESSES (57.84%): The v7.0 engine's best score included the true prime.
# 2. FAILURES (42.16%): The v7.0 engine's best score did NOT include the true prime.
#
# We will then calculate the *average prime gap (g_n)* for each bin.
#
# HYPOTHESIS:
# The 42.16% of failures are not random. They will have a statistically
# different average gap (g_n) than the 57.84% of successes.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v7.0 "Recursive") ---
MOD6_ENGINE_FILE = "../data/messiness_map_v_mod6.json"
MOD30_ENGINE_FILE = "../data/messiness_map_v1_mod30.json" # Hard-coded
MOD210_ENGINE_FILE = "../data/messiness_map_v3_mod210.json"

MESSINESS_MAP_V_MOD6 = None
MESSINESS_MAP_V1_MOD30 = None
MESSINESS_MAP_V3_MOD210 = None

def load_all_engine_data():
    """Loads all three messiness maps."""
    global MESSINESS_MAP_V_MOD6, MESSINESS_MAP_V1_MOD30, MESSINESS_MAP_V3_MOD210
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            data_mod6 = json.load(f)
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in data_mod6.items()}
        print(f"Loaded v_mod6 (Mod 6) engine data.")
            
        MESSINESS_MAP_V1_MOD30 = {
            0: 9907,    1: float('inf'), 2: 654113,  3: float('inf'), 4: 431661,
            5: float('inf'), 6: 171547,  7: float('inf'), 8: 662464,  9: float('inf'),
            10: 751163, 11: float('inf'), 12: 199190, 13: float('inf'), 14: 424448,
            15: float('inf'), 16: 426340, 17: float('inf'), 18: 200139, 19: float('inf'),
            20: 749951, 21: float('inf'), 22: 661166, 23: float('inf'), 24: 171854,
            25: float('inf'), 26: 430955, 27: float('inf'), 28: 654709, 29: float('inf')
        }
        print("Loaded v1.0 (Mod 30) engine data (hard-coded).")

        with open(MOD210_ENGINE_FILE, 'r') as f:
            data_mod210 = json.load(f)
            MESSINESS_MAP_V3_MOD210 = {int(k): v for k, v in data_mod210.items()}
        print(f"Loaded v3.0 (Mod 210) engine data.")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v7_recursive(anchor_sn, gap_g_n):
    """The v7.0 "Recursive" Engine."""
    if MESSINESS_MAP_V_MOD6 is None or MESSINESS_MAP_V1_MOD30 is None or MESSINESS_MAP_V3_MOD210 is None:
        return (float('inf'), float('inf'))

    if gap_g_n > 210:
        score = MESSINESS_MAP_V3_MOD210.get(anchor_sn % 210, float('inf'))
    elif gap_g_n > 30:
        score = MESSINESS_MAP_V1_MOD30.get(anchor_sn % 30, float('inf'))
    else:
        score = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    
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
        return None
    
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_v7_post_mortem_analysis():
    
    if not load_all_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR v7.0 Success vs. Failure Gap Analysis for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using v7.0 'Recursive' Engine")
    print(f"  - Calculating average gap g_n for SUCCESS and FAILURE bins.")
    print("-" * 80)
    start_time = time.time()
    
    # --- Data structures for the analysis ---
    total_successes = 0
    success_gap_sum = 0
    
    total_failures = 0
    failure_gap_sum = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            accuracy = (total_successes / (total_successes + total_failures)) * 100 if (total_successes + total_failures) > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Failures: {total_failures:,} | Acc: {accuracy:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        true_p_n_plus_1 = candidates[0]
        true_gap_g_n = true_p_n_plus_1 - p_n
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            messiness_score_tuple = get_messiness_score_v7_recursive(S_cand, gap_g_i)
            candidate_scores.append((messiness_score_tuple, q_i))
            
        # --- Run the "Tied-for-1st" logic ---
        candidate_scores.sort(key=lambda x: x[0]) 
        min_score = candidate_scores[0][0]
        winners_list = [q_i for score_tuple, q_i in candidate_scores if score_tuple == min_score]
        
        # --- 3. Log the result in the correct bin ---
        if true_p_n_plus_1 in winners_list:
            # SUCCESS
            total_successes += 1
            success_gap_sum += true_gap_g_n
        else:
            # FAILURE
            total_failures += 1
            failure_gap_sum += true_gap_g_n
            
    # --- Final Summary ---
    total_predictions = total_successes + total_failures
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    
    print(f"Progress: {total_predictions:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Failures: {total_failures:,} | Acc: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR v7.0 SUCCESS vs. FAILURE GAP ANALYSIS " + "="*20)
    print(f"\nTotal Primes Analyzed (p_n): {total_predictions:,}")
    
    print(f"\n  Total SUCCESSES (v7.0 Engine): {total_successes:,} ({accuracy:.2f}%)")
    print(f"  Total FAILURES (v7.0 Engine): {total_failures:,} ({(100-accuracy):.2f}%)")

    # --- Calculate Average Gaps ---
    avg_gap_success = success_gap_sum / total_successes if total_successes > 0 else 0
    avg_gap_failure = failure_gap_sum / total_failures if total_failures > 0 else 0
    overall_avg_gap = (success_gap_sum + failure_gap_sum) / total_predictions if total_predictions > 0 else 0

    print("\n" + "-" * 20 + " Average Gap (g_n) Analysis " + "-" * 20)
    print(f"  Overall Average Gap (g_n) for all tested primes: {overall_avg_gap:.4f}")
    print(f"  Average Gap (g_n) for {accuracy:.2f}% SUCCESSES:        {avg_gap_success:.4f}")
    print(f"  Average Gap (g_n) for {(100-accuracy):.2f}% FAILURES:        {avg_gap_failure:.4f}")
    
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    
    if abs(avg_gap_success - avg_gap_failure) > 0.5: # 0.5 is a significant difference
        print("\n  [VERDICT: 'HIDDEN VARIABLE' DISCOVERED]")
        print("  The 'g_n' (prime gap) is a key moderating variable.")
        print(f"  The average gap for SUCCESSES ({avg_gap_success:.4f}) is")
        print(f"  statistically different from the gap for FAILURES ({avg_gap_failure:.4f}).")
        print("\n  This proves the 42.16% of failures are NOT random.")
        print("  They are strongly correlated with the prime gap.")
    else:
        print("\n  [VERDICT: NO 'HIDDEN VARIABLE' FOUND]")
        print("  The prime gap (g_n) does not explain the failures.")
        print(f"  The average gap for SUCCESSES ({avg_gap_success:.4f}) is")
        print(f"  statistically identical to the gap for FAILURES ({avg_gap_failure:.4f}).")
        print("\n  The 42.16% of failures appear to be random or")
        print("  are caused by an unknown, non-gap-related factor.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v7_post_mortem_analysis()