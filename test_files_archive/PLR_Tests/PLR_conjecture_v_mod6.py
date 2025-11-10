# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) CONJECTURE - TEST (v_mod6)
#
# This script tests the PLR conjecture using the "PAC Diagnostic Engine v_mod6".
#
# HYPOTHESIS:
# The v_mod6 engine (Mod 6 failure rates) will have an accuracy
# *lower* than the v1.0 (Mod 30) baseline of 18.57%, but
# *higher* than the v3.0 (Mod 210) score of 10.97%.
# ==============================================================================

import time
import math
import json

# --- Engine Setup ---
ENGINE_DATA_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

def load_engine_data():
    """Loads the v_mod6 messiness map from the JSON file."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(ENGINE_DATA_FILE, 'r') as f:
            data = json.load(f)
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in data.items()}
            return True
    except FileNotFoundError:
        print(f"FATAL ERROR: Engine file '{ENGINE_DATA_FILE}' not found.")
        print("Please run 'test-9_mod6-Residue-Analysis.py' first.")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v_mod6(anchor_sn):
    """The PAC Diagnostic Engine (v_mod6)."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf') 
    residue = anchor_sn % 6
    score = MESSINESS_MAP_V_MOD6.get(residue, float('inf'))
    return score
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
        return None
    
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_predictive_test_v_mod6():
    
    # First, load the engine data
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Predictive Test (v_mod6) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using Engine v_mod6 (Mod 6 Failure Rate Map)")
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
            
            # --- Call the v_mod6 Engine ---
            messiness_score = get_messiness_score_v_mod6(S_cand)
            # ---
            
            candidate_scores.append((messiness_score, q_i))
            
        # Find the Best Candidate (lowest score / lowest failure rate)
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

    print("\n" + "="*20 + " PLR (v_mod6) TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    baseline_v1_accuracy = 18.57 #
    baseline_v3_accuracy = 10.97 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:   {random_chance_accuracy:.2f}%")
    print(f"  v3.0 Engine (Mod 210):    {baseline_v3_accuracy:.2f}%")
    print(f"  v_mod6 Engine (Mod 6):    {accuracy:.2f}%")
    print(f"  v1.0 Engine (Mod 30):     {baseline_v1_accuracy:.2f}% (The 'Sweet Spot')")
    print("  ---------------------------------")
    
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy < baseline_v1_accuracy and accuracy > baseline_v3_accuracy:
        print("\n  [VERDICT: 'SWEET SPOT' HYPOTHESIS CONFIRMED]")
        print("  The 'Mod 30' (v1.0) engine remains the most predictive model.")
        print(f"  The 'Mod 6' engine ({accuracy:.2f}%) is weaker than 'Mod 30',")
        print("  as it lacks the ability to filter k % 5 failures.")
        print("  This strongly supports the 'Goldilocks' theory.")
    else:
        print("\n  [VERDICT: HYPOTHESIS FALSIFIED]")
        print(f"  The result ({accuracy:.2f}%) breaks the expected pattern.")
        print("  This implies the predictive mechanism is more complex.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_predictive_test_v_mod6()