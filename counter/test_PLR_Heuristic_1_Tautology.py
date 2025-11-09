# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - HEURISTIC TEST 1 (The Tautology Test)
#
# This script tests the "Tautology" counter-argument.
#
# It REPLACES the v_mod6 engine (which was based on S_n data) with a
# new, "NEUTRAL" engine that has ZERO knowledge of the S_n sequence.
#
# This new engine ('get_ideal_grid_score') scores candidates based on an
# *ideal* mathematical hierarchy (P_4, P_3, P_2).
#
# HYPOTHESIS:
# If the 55.51% result was a tautology,
# this test will fail (~10% accuracy).
# If the "Path of Least Resistance" is a REAL phenomenon, this test
# will still show an accuracy significantly > 10%.
# ==============================================================================

import time
import math

# --- The New "Neutral" Engine (v_Tautology) ---
def get_ideal_grid_score(anchor_sn):
    """
    The Neutral "Messiness Score" Engine.
    This engine has ZERO knowledge of S_n failure data.
    It scores based on the "ideal" primorial grid hierarchy.
    Lowest score is best (cleanest).
    """
    if anchor_sn % 210 == 0: # P_4
        return 0 # Best score
    elif anchor_sn % 30 == 0: # P_3
        return 1
    elif anchor_sn % 6 == 0: # P_2
        return 2
    else:
        return 3 # Worst score
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
def run_PLR_tautology_test():
    
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Tautology Test for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using NEUTRAL 'Ideal Grid Score' Engine (P_4, P_3, P_2)")
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
            
            # --- Call the NEUTRAL Engine ---
            messiness_score = get_ideal_grid_score(S_cand)
            # ---
            
            candidate_scores.append((messiness_score, q_i))
            
        # Find the Best Candidate (lowest score / cleanest)
        candidate_scores.sort(key=lambda x: x[0])
        best_score, predicted_p_n_plus_1 = candidate_scores[0]
        
        total_predictions += 1
        if predicted_p_n_plus_1 == true_p_n_plus_1:
            total_successes += 1
            
    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR TAUTOLOGY TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    v_mod6_accuracy = 55.51 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:          10.00%")
    print(f"  v_mod6 Engine (Tautology?):      {v_mod6_accuracy:.2f}%")
    print(f"  Neutral 'Ideal Grid' Accuracy:   {accuracy:.2f}%")
    print("  ---------------------------------")
    
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > (random_chance_accuracy * 1.1): # e.g., > 11%
        print("\n  [VERDICT: The 55.51% is a REAL SIGNAL]")
        print("  The 'Path of Least Resistance' is a real phenomenon.")
        print(f"  This neutral engine, with no S_n data, achieved {accuracy:.2f}% accuracy,")
        print("  which is significantly higher than the 10.00% random baseline.")
        print("  This proves the 55.51% was not a tautology, but the result of")
        print("  a highly-tuned engine correctly identifying a real primorial bias.")
    else:
        print("\n  [VERDICT: The 55.51% IS A TAUTOLOGY]")
        print("  The 'Path of Least Resistance' is an artifact.")
        print(f"  This neutral engine, with no S_n data, failed, achieving")
        print(f"  an accuracy of {accuracy:.2f}%, which is at/near the 10.00% random baseline.")
        print("  This proves the 55.51% result was a fluke of the v_mod6")
        print("  engine's self-referential data.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_tautology_test()