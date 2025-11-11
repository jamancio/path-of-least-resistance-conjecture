# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 42: The "v23.0 Open Pool" Test
#
# This script tests the pure, 100% theoretical solution (v23.0 "Internal Flip")
# in the challenging "Open Pool" environment (Hole A).
#
# GOAL: Determine the final, robust predictive accuracy of the Analytic Logic Gate.
#
# v23.0 LOGIC:
# 1. Finds the g_messy_low candidate.
# 2. IF g_messy_low < g_winner: PREDICT p_messy_low (The Analytic Flip).
# 3. ELSE: PREDICT the standard v11.0 winner.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v23.0 Logic) ---
MOD6_ENGINE_FILE = "../data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

CLEAN_THRESHOLD = 3.0  
MESSY_THRESHOLD = 20.0 
POOL_SIZE = 210

def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    """The v11.0 "Weighted Gap" Engine Core (Multiplicative)."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'): return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))


# --- v23.0 FINAL LOGIC FUNCTION ---
def get_v23_internal_flip_prediction(p_n, candidates):
    
    # 1. Build the full evidence list and isolate bins
    candidates_data = []
    messy_bin = []
    
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        
        score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        vmod6_rate = get_vmod6_score(S_cand)
        
        data = (score_v11, q_i, vmod6_rate, gap_g_i)
        candidates_data.append(data)
        
        if vmod6_rate > MESSY_THRESHOLD:
            messy_bin.append(data)

    # 2. Get the Overall v11.0 Winner (The Baseline Arithmetic Winner)
    if not candidates_data: return None
        
    candidates_data.sort(key=lambda x: x[0])
    v11_winner_score, v11_winner_prime, _, v11_winner_gap = candidates_data[0]
    
    final_prediction = v11_winner_prime # Default prediction

    # --- 3. Find the Structural Minimum and Apply Logic Gate ---
    if messy_bin:
        messy_bin.sort(key=lambda x: x[3]) # Sort Messy Bin by gap
        g_messy_low = messy_bin[0][3]
        p_messy_low = messy_bin[0][1]
        
        # Analytic Logic Gate: If g_messy_low is LOWER than the winner's gap
        if g_messy_low < v11_winner_gap:
            # FLIP: Structural necessity overrides arithmetic winner
            final_prediction = p_messy_low

    return final_prediction
# --- End Engine Setup ---

# --- Configuration ---
PRIME_INPUT_FILE = "../prime/primes_100m.txt"
PRIMES_TO_TEST = 50000000 
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
    
    prime_set = set(prime_list)
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes and created set in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + 10 # Buffer
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None, None
        
    return prime_list, prime_set

# --- Main Testing Logic ---
def run_PLR_v23_open_pool_test():
    
    if not load_engine_data(): return
        
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'v23.0 Open Pool' Test (Test 42) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v23.0 (100% Theoretical Logic)")
    print(f"  - Pool Size: Integers up to p_n + {POOL_SIZE}")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes = 0
    total_primes_in_pools = 0 
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - POOL_SIZE:
        print("FATAL ERROR: Test range exceeds prime list length for Open Pool.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v23_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            rand_acc = (total_predictions / total_primes_in_pools) * 100 if total_primes_in_pools > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v23.0 Acc: {v23_acc:.2f}% | Random: {rand_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        # --- 1. Create the "Open Pool" of Candidates ---
        open_pool_candidates = []
        for k in range(1, POOL_SIZE + 1):
            candidate_int = p_n + k
            if candidate_int in prime_set:
                open_pool_candidates.append(candidate_int)
        
        # Ensure the true prime was actually in our pool
        if true_p_n_plus_1 not in open_pool_candidates:
            continue
            
        total_predictions += 1
        total_primes_in_pools += len(open_pool_candidates)
        
        # --- 2. Get v23.0 Prediction ---
        prediction_v23 = get_v23_internal_flip_prediction(p_n, open_pool_candidates)
        
        if prediction_v23 is None: continue

        if prediction_v23 == true_p_n_plus_1:
            total_successes += 1
            
    # --- Final Summary ---
    v23_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    rand_acc = (total_predictions / total_primes_in_pools) * 100 if total_primes_in_pools > 0 else 0
    
    print(f"Total Primes Tested: {total_predictions:,}")
    print(f"Total Correct Predictions: {total_successes:,}")
    print(f"v23.0 Open Pool Accuracy: {v23_acc:.2f}%")
    print(f"v16.0 Open Pool Baseline: 74.77%")
    print("---------------------------------")
    
    improvement = v23_acc - 74.77
    print(f"Improvement over v16.0 Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    if v23_acc > 74.77:
        print("\n  [VERDICT: SUCCESS. THE PURE LOGIC GATE IS ROBUST!]")
        print("  The 'Internal Flip' logic successfully improved accuracy")
        print("  over the complex v16.0 model, validating the theoretical shift.")
    else:
        print("\n  [VERDICT: FALSIFIED. THE LOGIC GATE IS TOO FRAGILE.]")
        print("  The theoretical 100% solution is too fragile for the")
        print("  'Open Pool' environment, confirming the v16.0 model's")
        print("  complex fixes are necessary for real-world robustness.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v23_open_pool_test()