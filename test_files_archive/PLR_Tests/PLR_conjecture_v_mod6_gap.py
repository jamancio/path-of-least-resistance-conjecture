# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) CONJECTURE - TEST (v_mod6_gap)
#
# This script tests the new "v_mod6_gap" engine.
#
# This engine combines our two strongest signals:
# 1. The S_n % 6 signature (the "power" filter)
# 2. The g_n Gap Correlation (the "precision" filter)
#
# HYPOTHESIS:
# This combined engine will achieve an accuracy *higher*
# than the 55.51% baseline from the v_mod6 engine alone.
# ==============================================================================

import time
import math
import json

# --- Gap Categorization (Must match the analysis script) ---
OVERALL_AVG_GAP = 19.6490 #
GAP_BIN_SMALL = 18.0
GAP_BIN_LARGE = 22.0

def categorize_gap(gap_g_n):
    """Categorizes the gap g_n into Small, Medium, or Large."""
    if gap_g_n < GAP_BIN_SMALL:
        return "Small"
    elif gap_g_n >= GAP_BIN_LARGE:
        return "Large"
    else:
        return "Medium"
# --- End Gap ---


# --- Engine Setup ---
ENGINE_DATA_FILE = "data/messiness_map_v_mod6_gap.json"
MESSINESS_MAP_V_MOD6_GAP = None

def load_engine_data():
    """Loads the v_mod6_gap messiness map from the JSON file."""
    global MESSINESS_MAP_V_MOD6_GAP
    try:
        with open(ENGINE_DATA_FILE, 'r') as f:
            data = json.load(f)
            # Convert string keys "0,Small" back into tuples (0, "Small")
            MESSINESS_MAP_V_MOD6_GAP = {}
            for k_str, v in data.items():
                residue_str, category = k_str.split(',')
                MESSINESS_MAP_V_MOD6_GAP[(int(residue_str), category)] = v
        return True
    except FileNotFoundError:
        print(f"FATAL ERROR: Engine file '{ENGINE_DATA_FILE}' not found.")
        print("Please run 'test-10_mod6-Gap-Analysis.py' first.")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v_mod6_gap(anchor_sn, gap_g_n):
    """The PAC Diagnostic Engine (v_mod6_gap)."""
    if MESSINESS_MAP_V_MOD6_GAP is None:
        return float('inf') 
    
    residue = anchor_sn % 6
    gap_category = categorize_gap(gap_g_n)
    
    score = MESSINESS_MAP_V_MOD6_GAP.get((residue, gap_category), float('inf'))
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
def run_PLR_predictive_test_v_mod6_gap():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Predictive Test (v_mod6_gap) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using Engine (Mod 6 + Gap) 2D Failure Rate Map")
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
            
            # --- Call the v_mod6_gap Engine ---
            messiness_score = get_messiness_score_v_mod6_gap(S_cand, gap_g_i)
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

    print("\n" + "="*20 + " PLR (v_mod6_gap) TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    baseline_v_mod6_accuracy = 55.51 #
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    print(f"\n  Random Chance Accuracy:      {random_chance_accuracy:.2f}%")
    print(f"  v_mod6 Engine (Baseline):    {baseline_v_mod6_accuracy:.2f}% (Mod 6 Only)")
    print(f"  v_mod6_gap Engine (New):   {accuracy:.2f}% (Mod 6 + Gap)")
    print("  ---------------------------------")
    improvement = accuracy - baseline_v_mod6_accuracy
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if accuracy > baseline_v_mod6_accuracy:
        print("\n  [VERDICT: SUCCESS. v_mod6_gap IS SUPERIOR]")
        print("  The new engine, which combines the Mod 6 signature AND")
        print("  the Gap Correlation data, is a stronger predictor.")
        print(f"  This is a new accuracy record: {accuracy:.2f}%")
    else:
        print("\n  [VERDICT: NO IMPROVEMENT. v_mod6 REMAINS CHAMPION]")
        print(f"  The new engine's accuracy ({accuracy:.2f}%) is not better than")
        print(f"  the v_mod6 baseline ({baseline_v_mod6_accuracy:.2f}%).")
        print("  The Gap Correlation, while real, does not add predictive")
        print("  power *on top of* the pure Mod 6 signal.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_predictive_test_v_mod6_gap()