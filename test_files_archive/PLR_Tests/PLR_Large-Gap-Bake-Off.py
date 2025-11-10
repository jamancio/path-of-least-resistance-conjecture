# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 10: The "Large-Gap Bake-Off"
#
# This script finds the "champion" engine for the "Large-Gap Mode."
#
# It tests the hypothesis from our v6.0 (64.14%) success: that the
# 44.49% of failures
# are governed by a *different* primorial signal.
#
# We will compare the predictive accuracy of all three engines
# (Mod 6, Mod 30, Mod 210) *only* on anchors with a large gap.
# ==============================================================================

import time
import math
import json

# --- Gap Configuration ---
GAP_MODE_SWITCH_POINT = 20.0

# --- Engine Setup ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MOD30_ENGINE_FILE = "data/messiness_map_v1_mod30.json" # Using hard-coded data
MOD210_ENGINE_FILE = "data/messiness_map_v3_mod210.json"

MESSINESS_MAP_V_MOD6 = None
MESSINESS_MAP_V1_MOD30 = None
MESSINESS_MAP_V3_MOD210 = None

def load_all_engine_data():
    """Loads all three messiness maps."""
    global MESSINESS_MAP_V_MOD6, MESSINESS_MAP_V1_MOD30, MESSINESS_MAP_V3_MOD210
    
    try:
        # Load Mod 6 Data
        with open(MOD6_ENGINE_FILE, 'r') as f:
            data_mod6 = json.load(f)
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in data_mod6.items()}
        print(f"Loaded v_mod6 (Mod 6) engine data.")
            
        # Hard-code Mod 30 Data (from test-3-result.txt)
        MESSINESS_MAP_V1_MOD30 = {
            0: 9907,    1: float('inf'), 2: 654113,  3: float('inf'), 4: 431661,
            5: float('inf'), 6: 171547,  7: float('inf'), 8: 662464,  9: float('inf'),
            10: 751163, 11: float('inf'), 12: 199190, 13: float('inf'), 14: 424448,
            15: float('inf'), 16: 426340, 17: float('inf'), 18: 200139, 19: float('inf'),
            20: 749951, 21: float('inf'), 22: 661166, 23: float('inf'), 24: 171854,
            25: float('inf'), 26: 430955, 27: float('inf'), 28: 654709, 29: float('inf')
        }
        print("Loaded v1.0 (Mod 30) engine data (hard-coded).")

        # Load Mod 210 Data
        with open(MOD210_ENGINE_FILE, 'r') as f:
            data_mod210 = json.load(f)
            MESSINESS_MAP_V3_MOD210 = {int(k): v for k, v in data_mod210.items()}
        print(f"Loaded v3.0 (Mod 210) engine data.")
        
        return True
        
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v_mod6(anchor_sn):
    if MESSINESS_MAP_V_MOD6 is None: return float('inf') 
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))

def get_messiness_score_v1_mod30(anchor_sn):
    if MESSINESS_MAP_V1_MOD30 is None: return float('inf')
    return MESSINESS_MAP_V1_MOD30.get(anchor_sn % 30, float('inf'))
    
def get_messiness_score_v3_mod210(anchor_sn):
    if MESSINESS_MAP_V3_MOD210 is None: return float('inf')
    return MESSINESS_MAP_V3_MOD210.get(anchor_sn % 210, float('inf'))
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
def run_PLR_large_gap_bakeoff():
    
    if not load_all_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Large-Gap Bake-Off' (Test 10) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Testing engines *only* on anchors where true gap g_n >= {GAP_MODE_SWITCH_POINT}")
    print("-" * 80)
    start_time = time.time()
    
    # --- Data structures for the test ---
    total_large_gap_predictions = 0
    
    total_successes_mod6 = 0
    total_successes_mod30 = 0
    total_successes_mod210 = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Large Gap Anchors: {total_large_gap_predictions:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        true_gap_g_n = true_p_n_plus_1 - p_n
        
        # --- THIS IS THE KEY: ONLY TEST "LARGE-GAP" ANCHORS ---
        if true_gap_g_n < GAP_MODE_SWITCH_POINT:
            continue
            
        total_large_gap_predictions += 1
        
        # --- Score all 10 candidates with all 3 engines ---
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        scores_mod6 = []
        scores_mod30 = []
        scores_mod210 = []
        
        for q_i in candidates:
            S_cand = p_n + q_i
            
            scores_mod6.append((get_messiness_score_v_mod6(S_cand), q_i))
            scores_mod30.append((get_messiness_score_v1_mod30(S_cand), q_i))
            scores_mod210.append((get_messiness_score_v3_mod210(S_cand), q_i))
            
        # --- Tally the "Tied-for-1st" winner for each engine ---
        
        # Mod 6
        min_score_mod6 = min(s[0] for s in scores_mod6)
        winners_mod6 = [q_i for score, q_i in scores_mod6 if score == min_score_mod6]
        if true_p_n_plus_1 in winners_mod6:
            total_successes_mod6 += 1

        # Mod 30
        min_score_mod30 = min(s[0] for s in scores_mod30)
        winners_mod30 = [q_i for score, q_i in scores_mod30 if score == min_score_mod30]
        if true_p_n_plus_1 in winners_mod30:
            total_successes_mod30 += 1
            
        # Mod 210
        min_score_mod210 = min(s[0] for s in scores_mod210)
        winners_mod210 = [q_i for score, q_i in scores_mod210 if score == min_score_mod210]
        if true_p_n_plus_1 in winners_mod210:
            total_successes_mod210 += 1
            
    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Large Gap Anchors: {total_large_gap_predictions:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v10.0 'Large-Gap Bake-Off') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {PRIMES_TO_TEST:,}")
    print(f"Total 'Large-Gap' Anchors Analyzed (g_n >= {GAP_MODE_SWITCH_POINT}): {total_large_gap_predictions:,}")
    
    random_chance_accuracy = (1 / NUM_CANDIDATES_TO_CHECK) * 100
    
    acc_mod6 = (total_successes_mod6 / total_large_gap_predictions) * 100 if total_large_gap_predictions > 0 else 0
    acc_mod30 = (total_successes_mod30 / total_large_gap_predictions) * 100 if total_large_gap_predictions > 0 else 0
    acc_mod210 = (total_successes_mod210 / total_large_gap_predictions) * 100 if total_large_gap_predictions > 0 else 0
    
    print(f"\n--- Accuracy *Only in Large-Gap Mode* (g_n >= {GAP_MODE_SWITCH_POINT}) ---")
    print(f"  Random Chance Accuracy:   {random_chance_accuracy:.2f}%")
    print(f"  v_mod6 (Mod 6) Engine:    {acc_mod6:.2f}%")
    print(f"  v1.0 (Mod 30) Engine:   {acc_mod30:.2f}%")
    print(f"  v3.0 (Mod 210) Engine:  {acc_mod210:.2f}%")
    print("  ---------------------------------")
    
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  Analysis complete. This test reveals the 'champion' engine")
    print("  for the 'Large-Gap' failure mode.")
    print("  We can now build the ultimate hierarchical engine (v7.0) by")
    print(f"  using the v_mod6 engine for small gaps and the winner")
    print("  of this test for large gaps.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_large_gap_bakeoff()