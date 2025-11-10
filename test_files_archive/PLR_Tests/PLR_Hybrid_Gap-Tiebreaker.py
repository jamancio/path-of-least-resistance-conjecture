# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 8: The "Gap Tie-Breaker" Engine
#
# This is the test of our most advanced "v5.0" engine.
#
# It combines our two strongest, verified signals:
# 1. PRIMARY: The v_mod6 "Messiness Score" (our 55.51% signal)
# 2. TIE-BREAKER: The 'g_n' prime gap (our 18.33 vs 21.29 signal)
#
# HYPOTHESIS:
# By sorting candidates *first* by their Mod 6 score, and *then*
# by their gap size (g_n) to break ties, this v5.0 engine
# will achieve an accuracy *higher* than the 55.51% v_mod6 baseline.
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
        print("Please run 'test-9_mod6-Reside-Analysis.py' first.")
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
def run_PLR_hybrid_gap_tiebreaker_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Hybrid 'Gap Tie-Breaker' Test (v5.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using Engine v5.0 (Mod 6 Score + g_n Gap Tie-Breaker)")
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
            
            # --- Call the v_mod6 Engine for the PRIMARY score ---
            primary_score = get_messiness_score_v_mod6(S_cand)
            
            # --- The gap (g_n) is the SECONDARY score ---
            secondary_score = gap_g_i
            # ---
            
            # Store the (prime, (primary_score, secondary_score))
            candidate_scores.append((q_i, (primary_score, secondary_score)))
            
        # --- 5. Find the Best Candidate (Hierarchical Sort) ---
        
        # This sort key is the *crucial* part of v5.0.
        # It sorts by item[1][0] (primary_score, mod 6) first.
        # Then, it uses item[1][1] (secondary_score, the gap) to break ties.
        # A smaller gap is better, as shown by Test 7 
        candidate_scores.sort(key=lambda x: (x[1][0], x[1][1]))
        
        # The best candidate is the first one in this 2-level sorted list
        predicted_p_n_plus_1, best_scores = candidate_scores[0]
        
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

    print("\n" + "="*20 + " PLR (v5.0 'Gap Tie-Breaker') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    baseline_v_mod6_accuracy = 55.51 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:      {random_chance_accuracy:.2f}%")
    print(f"  v_mod6 Engine (Baseline):    {baseline_v_mod6_accuracy:.2f}% (Mod 6 Only)")
    print(f"  v5.0 'Gap Tie-Breaker' (New): {accuracy:.2f}% (Mod 6 + Gap Tie-Break)")
    print("  ---------------------------------")
    improvement = accuracy - baseline_v_mod6_accuracy
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > baseline_v_mod6_accuracy:
        print("\n  [VERDICT: SUCCESS. v5.0 HYBRID MODEL IS SUPERIOR]")
        print("  The new 'Gap Tie-Breaker' engine is a stronger predictor")
        print(f"  than the v_mod6 (Mod 6) engine, achieving {accuracy:.2f}% accuracy.")
        print(f"  This is a new accuracy record and proves the 44.49% of failures")
        print("  were partially caused by ties that the 'g_n' signal can resolve.")
    else:
        print("\n  [VERDICT: NO IMPROVEMENT. v_mod6 REMAINS CHAMPION]")
        print(f"  The new engine's accuracy ({accuracy:.2f}%) is not better than")
        print(f"  the v_mod6 baseline ({baseline_v_mod6_accuracy:.2f}%).")
        print("  The 'g_n' Gap Correlation, while real, does not provide a")
        print("  useful *tie-breaking* signal for the Mod 6 engine.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_hybrid_gap_tiebreaker_test()