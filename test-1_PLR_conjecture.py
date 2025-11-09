# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) CONJECTURE - TEST 1
#
# This script tests the "Path of Least Resistance" conjecture using the
# "PAC Diagnostic Engine".
#
# HYPOTHESIS:
# The true next prime (p_{n+1}) is the candidate (q_i) that, when
# forming an anchor S_cand = p_n + q_i, produces the
# *lowest "Messiness Score"* from the engine.
#
# METHODOLOGY:
# 1. Loop through N primes p_n.
# 2. For each p_n, get the next 'NUM_CANDIDATES' primes (q_1...q_10).
#    (We know q_1 is the true p_{n+1}).
# 3. Create a "Candidate Anchor" (S_cand) for each q_i.
# 4. Score all S_cand anchors using the PAC Diagnostic Engine.
# 5. Find the S_cand with the minimum (best) score.
# 6. Check if this best-scoring anchor was the true one (S_cand_1).
# 7. Tally Successes and report the final prediction accuracy.
# ==============================================================================

import time
import math
# Import the engine from the other file
# (Make sure 'pac_diagnostic_engine.py' is in the same folder)
from pac_diagnostic_engine import get_messiness_score

# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
# Test the first 1,000,000 primes (adjust as needed)
PRIMES_TO_TEST = 50000000 
# How many "next primes" to check as candidates?
NUM_CANDIDATES_TO_CHECK = 10 
START_INDEX = 10 # Consistent start

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
def run_PLR_predictive_test():
    
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Predictive Test for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Scoring {NUM_CANDIDATES_TO_CHECK} candidates for each prime.")
    print("-" * 80)
    start_time = time.time()
    
    # --- Data structures for the test ---
    total_predictions = 0
    total_successes = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 10000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {elapsed:.0f}s", end='\r')

        # 1. Get Base Prime
        p_n = prime_list[i]
        
        # 2. Get Candidates
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            q_i = prime_list[i + j]
            candidates.append(q_i)
        
        # The true next prime is the first one
        true_p_n_plus_1 = candidates[0]
        
        # --- 3 & 4. Score all Candidate Anchors ---
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            messiness_score = get_messiness_score(S_cand)
            candidate_scores.append((messiness_score, q_i))
            
        # 5. Find the Best Candidate (lowest score)
        # Sort the list by score (item[0])
        candidate_scores.sort(key=lambda x: x[0])
        
        # The best candidate is the first one in the sorted list
        best_score, predicted_p_n_plus_1 = candidate_scores[0]
        
        # 6. Tally the Prediction
        total_predictions += 1
        if predicted_p_n_plus_1 == true_p_n_plus_1:
            total_successes += 1

    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR PREDICTIVE TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"Prediction Accuracy: {accuracy:.2f}%")
    print(f"Random Chance Accuracy: {random_chance_accuracy:.2f}%")

    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > random_chance_accuracy * 1.5: # e.g., > 15% if random is 10%
        print("\n  [VERDICT: CONJECTURE VERIFIED]")
        print("  The PAC Diagnostic Engine predicts the true next prime")
        print("  at a rate significantly higher than random chance.")
        print("  This provides strong evidence for the 'Path of Least Resistance' conjecture.")
    else:
        print("\n  [VERDICT: CONJECTURE FALSIFIED]")
        print("  The engine's accuracy is at or near random chance.")
        print("  The 'Path of Least Resistance' conjecture is not supported.")
        print("  The 'messiness score' alone is not enough to predict the next prime.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_predictive_test()