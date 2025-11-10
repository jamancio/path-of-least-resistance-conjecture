# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 20: Failure Rank Distribution
#
# This is a "post-mortem" on our 60.49% champion v11.0 engine.
#
# Our goal is to find out, *when the engine fails*, where does
# the "true" prime ($p_{n+1}$) end up in the ranked list?
#
# Does it "just barely" lose, consistently ranking 2nd?
# Or does it get buried at 8th, 9th, or 10th place?
#
# This will tell us if the "messy" true prime still carries a
# strong, usable signal even when it loses.
#
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v11.0 "Weighted Gap") ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

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
    """
    The v11.0 "Weighted Gap" Engine.
    Final_Score = (v_mod6_rate + 1.0) * (gap_g_n)
    """
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')

    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    
    if score_mod6 == float('inf'):
        return float('inf')
        
    final_weighted_score = (score_mod6 + 1.0) * gap_g_n
    return final_weighted_score
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
def run_PLR_v11_failure_rank_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR v11.0 Failure Rank Analysis for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v11.0 (v_mod6_rate * gap_g_n)")
    print(f"  - Analyzing the rank of the true prime in all failures...")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes = 0
    total_failures = 0
    
    # --- Data structure for the rank distribution ---
    # Stores {rank: count}, e.g., {2: 50000, 3: 20000, ...}
    failure_rank_distribution = defaultdict(int)
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v11_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Acc: {v11_acc:.2f}% | Failures: {total_failures:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            
            score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
            # Store (score, prime)
            candidate_scores.append((score_v11, q_i))

        # --- Tally Winners ---
        total_predictions += 1
        
        # Sort the list by score
        candidate_scores.sort(key=lambda x: x[0])
        
        # Get the winner
        winner = candidate_scores[0][1]

        if winner == true_p_n_plus_1:
            total_successes += 1
        else:
            # --- THIS IS A FAILURE. FIND THE TRUE PRIME'S RANK. ---
            total_failures += 1
            
            true_prime_rank = -1
            for rank in range(NUM_CANDIDATES_TO_CHECK): # rank is 0-9
                if candidate_scores[rank][1] == true_p_n_plus_1:
                    # Ranks are 1-based, so add 1
                    true_prime_rank = rank + 1
                    break
            
            if true_prime_rank != -1:
                failure_rank_distribution[true_prime_rank] += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v11_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Acc: {v11_acc:.2f}% | Failures: {total_failures:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v11.0) FAILURE RANK REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"  - Total SUCCESSES: {total_successes:,} ({v11_acc:.2f}%)")
    print(f"  - Total FAILURES:  {total_failures:,} ({(100-v11_acc):.2f}%)")
    
    print("\n" + "-" * 20 + " Distribution of True Prime's Rank (in Failures) " + "-" * 20)
    
    print(f"\n{'Rank of True Prime':<20} | {'Failure Count':<15} | {'% of All Failures':<20}")
    print("-" * 60)
    
    sorted_ranks = sorted(failure_rank_distribution.keys())
    
    for rank in sorted_ranks:
        count = failure_rank_distribution[rank]
        perc_of_failure = (count / total_failures) * 100 if total_failures > 0 else 0
        print(f"{rank:<20} | {count:<15,} | {perc_of_failure:>19.2f}%")
        
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  This table shows the *full distribution* of failures.")
    
    rank_2_failures = failure_rank_distribution.get(2, 0)
    rank_2_perc = (rank_2_failures / total_failures) * 100 if total_failures > 0 else 0

    if rank_2_perc > 50.0:
        print(f"\n  [VERDICT: A NEW 'SECOND-PLACE' SIGNAL IS DISCOVERED!]")
        print(f"  An incredible {rank_2_perc:.2f}% of all failures")
        print("  are 'Scenario B' failures where the true prime *came in 2nd*.")
        print("  This proves the 'messy-but-true' prime still carries")
        print("  a powerful, predictable signal. This is solvable.")
    else:
        print(f"\n  [VERDICT: 'PATH OF LEAST RESISTANCE' IS THE TRUE LIMIT]")
        print(f"  The failures are distributed across all ranks, with only")
        print(f"  {rank_2_perc:.2f}% of failures coming from 2nd place.")
        print("  This suggests the 39.51% of failures are truly 'noise',")
        print("  where the true prime is not the 'Path of Least Resistance'")
        print("  and is often indistinguishable from other candidates.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v11_failure_rank_analysis()