# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 24: v12.0 Failure Rank Distribution
#
# This is a "post-mortem" on our *new* 68.07% champion v12.0 engine.
#
# Our goal is to analyze the 31.93% of failures that *remain*.
#
# HYPOTHESIS:
# The v12.0 engine fixed the "Clean #1 vs. Messy #2" signature.
# The *new* failure distribution will be different.
#
# We will run the v12.0 engine and, when it fails, we will find
# the rank of the "true" prime ($p_{n+1}$) in the *original*
# v11.0 ranked list.
#
# This will show us the "new" failure signature. Are all the
# failures now at Rank 3? Or did our override create new,
# different failures? This is the next step to 100%.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v11.0 "Weighted Gap") ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# --- These are the "Signature" thresholds ---
CLEAN_THRESHOLD = 3.0  # (v_mod6 score < 3.0 is "Clean")
MESSY_THRESHOLD = 20.0 # (v_mod6 score > 20.0 is "Messy")

def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
        print(f"  - 'Clean' Signature Threshold: < {CLEAN_THRESHOLD}%")
        print(f"  - 'Messy' Signature Threshold: > {MESSY_THRESHOLD}%")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    """The v11.0 "Weighted Gap" Engine."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'):
        return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
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
        print("Please ensure 'primes_100m.txt' is in a 'prime' folder.")
        return None
    
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_v12_failure_rank_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR v12.0 Failure Rank Analysis for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v12.0 (Signature Override)")
    print(f"  - Analyzing the ranks of the *remaining* 31.93% of failures...")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v12 = 0
    total_failures_v12 = 0
    
    # --- Data structure for the rank distribution ---
    failure_rank_distribution = defaultdict(int)
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v12_acc = (total_successes_v12 / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Acc: {v12_acc:.2f}% | Failures: {total_failures_v12:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        # Get the v11.0 ranked list
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
            # Store (score, prime, vmod6_score)
            vmod6_rate = get_vmod6_score(S_cand)
            candidate_scores.append((score_v11, q_i, vmod6_rate))

        total_predictions += 1
        candidate_scores.sort(key=lambda x: x[0])
        
        # --- Run v12.0 "Signature" Logic ---
        winner_v11_prime = candidate_scores[0][1]
        winner_v11_vmod6 = candidate_scores[0][2]
        
        final_prediction = winner_v11_prime # Default
        
        if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean"
            if len(candidate_scores) >= 2:
                candidate_2_vmod6 = candidate_scores[1][2]
                if candidate_2_vmod6 > MESSY_THRESHOLD: # AND #2 is "Messy"
                    final_prediction = candidate_scores[1][1] # OVERRIDE

        # --- Tally v12.0 Result ---
        if final_prediction == true_p_n_plus_1:
            total_successes_v12 += 1
        else:
            # --- THIS IS A v12.0 FAILURE. ANALYZE IT. ---
            total_failures_v12 += 1
            
            true_prime_rank = -1
            # Find the rank of the true prime in the *original v11.0 list*
            for rank in range(NUM_CANDIDATES_TO_CHECK): # rank is 0-9
                if candidate_scores[rank][1] == true_p_n_plus_1:
                    true_prime_rank = rank + 1
                    break
            
            if true_prime_rank != -1:
                failure_rank_distribution[true_prime_rank] += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v12_acc = (total_successes_v12 / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Acc: {v12_acc:.2f}% | Failures: {total_failures_v12:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v12.0) FAILURE RANK REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"  - Total SUCCESSES: {total_successes_v12:,} ({v12_acc:.2f}%)")
    print(f"  - Total FAILURES:  {total_failures_v12:,} ({(100-v12_acc):.2f}%)")
    
    print("\n" + "-" * 20 + " New Distribution of True Prime's Rank (in v12.0 Failures) " + "-" * 20)
    
    print(f"\n{'Rank of True Prime':<20} | {'Failure Count':<15} | {'% of All Failures':<20}")
    print("-" * 60)
    
    sorted_ranks = sorted(failure_rank_distribution.keys())
    
    for rank in sorted_ranks:
        count = failure_rank_distribution[rank]
        perc_of_failure = (count / total_failures_v12) * 100 if total_failures_v12 > 0 else 0
        print(f"{rank:<20} | {count:<15,} | {perc_of_failure:>19.2f}%")
        
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  This table shows the 'failure signature' of our 68.07% engine.")
    
    rank_3_failures = failure_rank_distribution.get(3, 0)
    rank_3_perc = (rank_3_failures / total_failures_v12) * 100 if total_failures_v12 > 0 else 0

    if rank_3_perc > 30.0: # If Rank 3 is now the dominant failure
        print(f"\n  [VERDICT: THE NEXT SIGNATURE IS FOUND!]")
        print(f"  The new 'Rank 2' is now 'Rank 3'.")
        print(f"  A massive {rank_3_perc:.2f}% of our *new* failures")
        print("  are cases where the true prime was at Rank 3.")
        print("  This suggests the 'v14.0 Chained' logic was correct")
        print("  and we can proceed to 'fix' Rank 3.")
    else:
        print(f"\n  [VERDICT: THE TRAIL HAS GONE COLD. 68.07% IS THE LIMIT.]")
        print(f"  The failures are now distributed more evenly, with")
        print(f"  Rank 3 only accounting for {rank_3_perc:.2f}% of failures.")
        print("  This implies our 'Clean #1 vs. Messy #2' rule was the")
        print("  only reliable signature, and the remaining 31.93% of")
        print("  failures are true 'noise' that cannot be easily fixed.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v12_failure_rank_analysis()