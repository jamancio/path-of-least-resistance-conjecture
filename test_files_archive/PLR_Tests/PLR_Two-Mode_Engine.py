# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 9: The "Two-Mode" Engine
#
# This script tests the "v6.0 Two-Mode" engine.
#
# HYPOTHESIS:
# By using the v_mod6 (Mod 6) engine for small gaps and the
# v1.0 (Mod 30) engine for large gaps, we can "fix" the 44.49% of
# failures and achieve an accuracy *higher* than 55.51%.
# ==============================================================================

import time
import math
# Import the v6.0 engine
from pac_diagnostic_engine_v6_two_mode import get_messiness_score_v6_two_mode, load_all_engine_data

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
def run_PLR_two_mode_test():
    
    if not load_all_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Two-Mode' Test (v6.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using Engine v6.0 (Mod 6 for Small Gaps, Mod 30 for Large Gaps)")
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
            q_i = prime_list[i + j]
            candidates.append(q_i)
        
        true_p_n_plus_1 = candidates[0]
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            
            # --- Call the v6.0 "Two-Mode" Engine ---
            messiness_score = get_messiness_score_v6_two_mode(S_cand, gap_g_i)
            # ---
            
            candidate_scores.append((messiness_score, q_i))
            
        # Find the Best Candidate (lowest score / lowest failure rate)
        candidate_scores.sort(key=lambda x: x[0])
        
        # --- Use "Tied-for-1st" logic ---
        min_score = candidate_scores[0][0]
        winners_list = [q_i for score, q_i in candidate_scores if score == min_score]
        
        total_predictions += 1
        if true_p_n_plus_1 in winners_list:
            total_successes += 1
            
    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v6.0 'Two-Mode') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    baseline_v_mod6_accuracy = 55.51 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:      {random_chance_accuracy:.2f}%")
    print(f"  v_mod6 Engine (Baseline):    {baseline_v_mod6_accuracy:.2f}% (Small Gaps)")
    print(f"  v6.0 'Two-Mode' Engine:    {accuracy:.2f}% (Small + Large Gaps)")
    print("  ---------------------------------")
    improvement = accuracy - baseline_v_mod6_accuracy
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > baseline_v_mod6_accuracy:
        print("\n  [VERDICT: SUCCESS. 'HIDDEN VARIABLE' SOLVED]")
        print("  The new 'Two-Mode' engine is a stronger predictor!")
        print(f"  This is a new accuracy record: {accuracy:.2f}%")
        print("  This proves the 44.49% of failures were caused by a 'mode switch'")
        print("  to a Mod 30 signal, which this engine correctly models.")
    else:
        print("\n  [VERDICT: NO IMPROVEMENT. v_mod6 REMAINS CHAMPION]")
        print(f"  The new 'Two-Mode' engine's accuracy ({accuracy:.2f}%) is not better than")
        print(f"  the v_m" + "od6 baseline (55.51%).")
        print("  This implies the Mod 30 signal is *also* noise in the 'Large-Gap' mode,")
        print("  and the 44.49% of failures are caused by a different, unknown factor.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_two_mode_test()