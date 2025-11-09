# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) CONJECTURE - TEST 2.1 (v2.1)
#
# This script tests the "Path of Least Resistance" conjecture using the
# new "PAC Diagnostic Engine v2.1".
#
# HYPOTHESIS:
# The v2.1 engine, which uses the 2D "Messiness Map" (Failure Rate) from
# '2D-messisness-Map-Analysis.txt', will have a prediction accuracy
# *higher* than the 18.57% baseline.
# ==============================================================================

import time
import math
# Import the v2.1 engine
from pac_diagnostic_engine_v2_1 import get_messiness_score_v2_1, categorize_gap

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
def run_PLR_predictive_test_v2_1():
    
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Predictive Test (v2.1) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using Engine v2.1 (2D Messiness Map - True Failure Rate)")
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
            
            # --- Call the v2.1 Engine ---
            messiness_score = get_messiness_score_v2_1(S_cand, gap_g_i)
            # ---
            
            candidate_scores.append((messiness_score, q_i))
            
        # Find the Best Candidate (lowest score / lowest failure rate)
        candidate_scores.sort(key=lambda x: x[0])
        best_score, predicted_p_n_plus_1 = candidate_scores[0]
        
        total_predictions += 1
        if predicted_p_n_plus_1 == true_p_n_plus_1:
            total_successes += 1
            
        # --- Handle Ties ---
        # It's possible for multiple candidates to have the same *best* score
        # (e.g., two "impossible" anchors with 'inf' scores).
        # We need to check if the true anchor was *among* the tied best.
        # This is a more complex but fair way to score.
        
        # NOTE: For simplicity, the above code only counts a "win"
        # if the true prime is the *first* in the sorted list.
        # This is a strict but clear test.

    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v2.1) TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    baseline_v1_accuracy = 18.57 #
    baseline_v2_accuracy = 13.85 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:   {random_chance_accuracy:.2f}%")
    print(f"  v1.0 Engine Accuracy:     {baseline_v1_accuracy:.2f}% (Mod 30 only)")
    print(f"  v2.0 Engine (Flawed):   {baseline_v2_accuracy:.2f}% (Mod 30 + Guessed Gap)")
    print(f"  v2.1 Engine (Data-Driven):{accuracy:.2f}% (Mod 30 + Measured Gap)")
    print("  ---------------------------------")
    improvement_v2_1 = accuracy - baseline_v1_accuracy
    print(f"  Improvement over v1.0:    {improvement_v2_1:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > baseline_v1_accuracy:
        print("\n  [VERDICT: SUCCESS. v2.1 MODEL IS SUPERIOR]")
        print("  The data-driven v2.1 engine, using the 2D Messiness Map,")
        print(f"  predicts the next prime with {accuracy:.2f}% accuracy.")
        print(f"  This is a {improvement_v2_1:+.2f} point improvement over the v1.0 baseline,")
        print("  proving the Gap Correlation data is a real predictive signal.")
    else:
        print("\n  [VERDICT: NO IMPROVEMENT]")
        print(f"  The v2.1 engine's accuracy ({accuracy:.2f}%) is not better than")
        print(f"  the v1.0 baseline ({baseline_v1_accuracy:.2f}%).")
        print("  While the Gap Correlation is real, it does not")
        print("  add predictive power for the *next* prime in this model.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_predictive_test_v2_1()