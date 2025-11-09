# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - HEURISTIC TEST 2 (The "Open Pool" Test)
#
# This script tests the "Limited Candidate Pool" counter-argument.
#
# It REPLACES the 10-prime candidate list with an "open pool" of
# *all integers* within a set range after p_n.
#
# It uses our BEST engine (v_mod6, 55.51% accuracy) to score
# *every* integer candidate in that range.
#
# HYPOTHESIS:
# The "Path of Least Resistance" conjecture predicts that the integer 'x'
# in the open pool that gets the LOWEST messiness score will be
# the *true next prime*, p_{n+1}.
# ==============================================================================

import time
import math
# Import our champion v_mod6 engine
from pac_diagnostic_engine_v_mod6_heuristics import get_messiness_score_v_mod6, load_engine_data

# --- Configuration ---
PRIME_INPUT_FILE = "../prime/primes_100m.txt"
# Let's test 10 million primes (this test is slower)
PRIMES_TO_TEST = 10000000
# Define the "open pool" search range after p_n
# We'll check the 150 integers immediately following p_n
OPEN_POOL_RANGE = 150
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
        return None, None
    
    prime_set = set(prime_list) # We need the prime set to find the *true* next prime
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes and created set in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + OPEN_POOL_RANGE + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None, None
        
    return prime_list, prime_set

# --- Main Testing Logic ---
def run_PLR_open_pool_test():
    
    # First, load the v_mod6 engine data
    if not load_engine_data():
        print("Stopping test: v_mod6 Engine data could not be loaded.")
        return
        
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Open Pool' Test for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using v_mod6 Engine (55.51% baseline)")
    print(f"  - Scoring ALL {OPEN_POOL_RANGE} integers after p_n.")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes = 0
    total_engine_failed_to_find_prime = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 10000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {elapsed:.0f}s", end='\r')

        # 1. Get Base Prime
        p_n = prime_list[i]
        
        # 2. Find the *true* next prime (our target)
        true_p_n_plus_1 = prime_list[i + 1]
        
        # Check if the true next prime is outside our search range
        if true_p_n_plus_1 > (p_n + OPEN_POOL_RANGE):
            # This is a large prime gap, we can't test this one.
            continue
            
        # --- 3. Score all candidates in the "Open Pool" ---
        candidate_scores = [] # Store as (score, integer)
        
        for x_offset in range(1, OPEN_POOL_RANGE + 1):
            candidate_x = p_n + x_offset
            
            # Create the hypothetical anchor
            S_cand = p_n + candidate_x
            
            # --- Call the v_mod6 Engine ---
            messiness_score = get_messiness_score_v_mod6(S_cand)
            # ---
            
            candidate_scores.append((messiness_score, candidate_x))
            
        # 4. Find the Best Candidate (lowest score)
        candidate_scores.sort(key=lambda x: x[0])
        best_score, predicted_x = candidate_scores[0]
        
        # 5. Tally the Prediction
        total_predictions += 1
        if predicted_x == true_p_n_plus_1:
            total_successes += 1
        
        # Check if the engine's pick was even a prime number
        if predicted_x not in prime_set:
            total_engine_failed_to_find_prime += 1
            
    # --- Final Summary ---
    progress = total_predictions
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    failure_rate = (total_engine_failed_to_find_prime / total_predictions) * 100 if total_predictions > 0 else 0
    
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Accuracy: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR 'OPEN POOL' TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,} (skipping large gaps)")
    print(f"Open Pool Size per Prime: {OPEN_POOL_RANGE} integers")
    
    print(f"\nTotal Correct Predictions (Engine's pick == p_n+1): {total_successes:,}")
    print(f"Prediction Accuracy: {accuracy:.2f}%")
    
    print(f"\nTotal Engine Failures (Engine's pick was composite): {total_engine_failed_to_find_prime:,}")
    print(f"Engine Failure Rate: {failure_rate:.2f}%")
    
    
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > 5.0: # Arbitrary "significantly better than random"
        print("\n  [VERDICT: The 55.51% signal is REAL]")
        print("  The 'Path of Least Resistance' holds in an open pool.")
        print(f"  Even when checking all {OPEN_POOL_RANGE} integers, the v_mod6 engine")
        print(f"  successfully identified the true next prime with {accuracy:.2f}% accuracy.")
        print(f"  This is a massive success and disproves the 'Limited Pool' counter-argument.")
    else:
        print("\n  [VERDICT: The 55.51% IS AN ARTIFACT]")
        print(f"  The engine's accuracy in an open pool collapsed to {accuracy:.2f}%.")
        print("  This proves the 'Limited Candidate Pool' counter-argument was correct.")
        print("  The 55.51% result was an illusion created by only testing primes.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_open_pool_test()