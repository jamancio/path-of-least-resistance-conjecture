# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 11: The "Recursive" Engine
#
# This script tests the new "v7.0 Recursive" engine.
#
# HYPOTHESIS:
# By dynamically choosing the filter (Mod 6, 30, or 210) based
# on the candidate's gap size (g_n), this engine will
# intelligently combine the signals and beat the 55.51% baseline.
# ==============================================================================

import time
import math
# Import the v7.0 engine
from pac_diagnostic_engine_v7_recursive import get_messiness_score_v7_recursive, load_all_engine_data

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
def run_PLR_recursive_test():
    
    if not load_all_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Recursive' Test (v7.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using Engine v7.0 (Recursive Mod 6/30/210 + Gap Tie-Break)")
    print(f"  - Scoring {NUM_CANDIDATES_TO_CHECK} candidates for each prime.")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        true_p_n_plus_1 = candidates[0]
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            
            # --- Call the v7.0 "Recursive" Engine ---
            messiness_score_tuple = get_messiness_score_v7_recursive(S_cand, gap_g_i)
            # ---
            
            # Store ( (primary_score, secondary_gap), prime)
            candidate_scores.append((messiness_score_tuple, q_i))
            
        # Find the Best Candidate (Hierarchical Sort)
        # 1. Sort by primorial "Messiness Score" (score[0])
        # 2. Sort by gap size 'g_n' (score[1]) as a tie-breaker
        candidate_scores.sort(key=lambda x: x[0]) 
        
        # --- Use "Tied-for-1st" logic ---
        min_score = candidate_scores[0][0] # Get the best score tuple
        winners_list = [q_i for score_tuple, q_i in candidate_scores if score_tuple == min_score]
        
        total_predictions += 1
        if true_p_n_plus_1 in winners_list:
            total_successes += 1
            
    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v7.0 'Recursive') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    baseline_v_mod6_accuracy = 55.51 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:      {random_chance_accuracy:.2f}%")
    print(f"  v_mod6 Engine (Baseline):    {baseline_v_mod6_accuracy:.2f}% (Mod 6 Only)")
    print(f"  v7.0 'Recursive' Engine (New): {accuracy:.2f}%")
    print("  ---------------------------------")
    improvement = accuracy - baseline_v_mod6_accuracy
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > baseline_v_mod6_accuracy:
        print("\n  [VERDICT: SUCCESS. v7.0 'RECURSIVE' MODEL IS SUPERIOR]")
        print("  The new 'Recursive' engine is the strongest predictor yet!")
        print(f"  This is a new accuracy record: {accuracy:.2f}%")
        print("  This proves that a dynamic, hierarchical filter is the")
        print("  correct way to model the 'Path of Least Resistance'.")
    else:
        print("\n  [VERDICT: NO IMPROVEMENT. v_mod6 REMAINS CHAMPION]")
        print(f"  The new 'Recursive' engine's accuracy ({accuracy:.2f}%) is not better than")
        print(f"  the v_mod6 baseline ({baseline_v_mod6_accuracy:.2f}%).")
        print("  This implies the pure 'Mod 6' signal is truly the only")
        print("  dominant factor, regardless of gap size.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_recursive_test()