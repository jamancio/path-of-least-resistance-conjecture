# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) CONJECTURE - TEST 4 (v4.0 HYBRID)
#
# This script tests the "v4.0 Hybrid Tie-Breaker" engine.
#
# HYPOTHESIS:
# By sorting candidates *first* by their Mod 6 score, and *then*
# by their Mod 210 score (as a tie-breaker), this v4.0 engine
# will achieve an accuracy *higher* than the 55.51% v_mod6 baseline.
# ==============================================================================

import time
import math
# Import the v4.0 engine
from pac_diagnostic_engine_v4_hybrid import get_messiness_score_v4_hybrid, load_all_engine_data

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
def run_PLR_predictive_test_v4():
    
    # First, load BOTH engine data maps
    if not load_all_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Predictive Test (v4.0 Hybrid) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using Engine v4.0 (Mod 6 Score + Mod 210 Tie-Breaker)")
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
            
            # --- Call the v4.0 Engine ---
            # This returns a tuple: (primary_score, secondary_score)
            messiness_score_tuple = get_messiness_score_v4_hybrid(S_cand)
            # ---
            
            candidate_scores.append((messiness_score_tuple, q_i))
            
        # --- 5. Find the Best Candidate (Hierarchical Sort) ---
        
        # This sort key is the *crucial* part of v4.0.
        # It sorts by item[0][0] (primary_score, mod 6) first.
        # Then, it uses item[0][1] (secondary_score, mod 210) to break ties.
        candidate_scores.sort(key=lambda x: (x[0][0], x[0][1]))
        
        # The best candidate is the first one in this 2-level sorted list
        best_score_tuple, predicted_p_n_plus_1 = candidate_scores[0]
        
        # --- 6. Tally the Prediction ---
        total_predictions += 1
        if predicted_p_n_plus_1 == true_p_n_plus_1:
            total_successes += 1
            
    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v4.0 HYBRID) TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    baseline_v_mod6_accuracy = 55.51 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:   {random_chance_accuracy:.2f}%")
    print(f"  v_mod6 Engine (Baseline): {baseline_v_mod6_accuracy:.2f}% (Mod 6 Only)")
    print(f"  v4.0 Hybrid Engine:       {accuracy:.2f}% (Mod 6 + Mod 210 Tie-Breaker)")
    print("  ---------------------------------")
    improvement_v4 = accuracy - baseline_v_mod6_accuracy
    print(f"  Improvement over Baseline:  {improvement_v4:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > baseline_v_mod6_accuracy:
        print("\n  [VERDICT: SUCCESS. v4.0 HYBRID MODEL IS SUPERIOR]")
        print("  The v4.0 'Tie-Breaker' engine is a stronger predictor")
        print(f"  than the v_mod6 (Mod 6) engine, achieving {accuracy:.2f}% accuracy.")
        print("  This proves that combining the filters hierarchically")
        print("  successfully adds precision without adding noise.")
    else:
        print("\n  [VERDICT: NO IMPROVEMENT. v_mod6 REMAINS CHAMPION]")
        print(f"  The v4.0 engine's accuracy ({accuracy:.2f}%) is not better than")
        print(f"  the v_mod6 baseline ({baseline_v_mod6_accuracy:.2f}%).")
        print("  The 'Mod 210' tie-breaker did not add predictive power,")
        print("  implying the 'Mod 6' signal is truly the only one that matters.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_predictive_test_v4()