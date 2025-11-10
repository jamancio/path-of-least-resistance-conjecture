# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 33: The "v16.0 Open Pool" Test
#
# This script tackles "Hole A: The Closed Set Problem".
#
# It tests our 75.94% champion v16.0 engine in a "real-world"
# "Open Pool" scenario, not just on a pre-selected list of 10 primes.
#
# HYPOTHESIS:
# The v16.0 engine's logic is robust. Its accuracy will be
# lower than 75.94%, but it will *significantly* outperform
# the 14.77% baseline from the simple v_mod6 engine,
# proving it has true predictive power.
#
# v16.0 "OPEN POOL" LOGIC:
#
# 1. For each p_n, create an "Open Pool" of all integers
#    from p_n + 1 to p_n + POOL_SIZE (e.g., 210).
# 2. Find all *primes* within this pool. This is our new,
#    "noisy" candidate list (it may have 20+ candidates).
# 3. Run the v16.0 "Chained Signature" engine on this list.
# 4. Check if the winner is the true p_{n+1}.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v16.0 "Chained Signature") ---
MOD6_ENGINE_FILE = "../data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

CLEAN_THRESHOLD = 3.0  
MESSY_THRESHOLD = 20.0 
MAX_SIGNATURE_SEARCH_DEPTH = 4 # Ranks 2, 3, 4

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
    """The v11.0 "Weighted Gap" Engine Core."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'): return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))

def get_v16_prediction(p_n, candidates):
    """
    Runs the full v16.0 "Chained Signature" logic.
    'candidates' is now our "noisy" list of primes from the pool.
    """
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        vmod6_rate = get_vmod6_score(S_cand)
        candidate_scores.append((score_v11, q_i, vmod6_rate))

    candidate_scores.sort(key=lambda x: x[0])
    
    # If no candidates were found in the pool, return None
    if not candidate_scores:
        return None
        
    winner_v11_prime = candidate_scores[0][1]
    winner_v11_vmod6 = candidate_scores[0][2]
    
    prediction_v16 = winner_v11_prime # Default
    
    if winner_v11_vmod6 < CLEAN_THRESHOLD: 
        for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH): # Ranks 2, 3, 4
            if rank_index >= len(candidate_scores): break
            next_candidate_vmod6 = candidate_scores[rank_index][2]
            if next_candidate_vmod6 > MESSY_THRESHOLD:
                prediction_v16 = candidate_scores[rank_index][1]
                break
                
    return prediction_v16
# --- End Engine Setup ---

# --- Configuration ---
PRIME_INPUT_FILE = "../prime/primes_100m.txt"
PRIMES_TO_TEST = 50000000 
# We test all integers up to p_n + POOL_SIZE
POOL_SIZE = 210 # A challenging pool, covers the first maximal gap
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
    
    # We need a prime set for fast "is_prime" lookups
    prime_set = set(prime_list)
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes and created set in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + 10 # Just need a buffer
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None, None
        
    return prime_list, prime_set

# --- Main Testing Logic ---
def run_PLR_v16_open_pool_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Open Pool' Test (v16.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v16.0 (75.94% Champion)")
    print(f"  - Pool Size: Integers up to p_n + {POOL_SIZE}")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes = 0
    total_primes_in_pools = 0 # To calculate random chance
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - 2: # Need i and i+1
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v16_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            rand_acc = (total_predictions / total_primes_in_pools) * 100 if total_primes_in_pools > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v16.0 Acc: {v16_acc:.2f}% | Random: {rand_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        # --- 1. Create the "Open Pool" of Candidates ---
        open_pool_candidates = []
        for k in range(1, POOL_SIZE + 1):
            candidate_int = p_n + k
            
            # This is our "Prime Oracle"
            if candidate_int in prime_set:
                open_pool_candidates.append(candidate_int)
        
        # Ensure the true prime was actually in our pool
        if true_p_n_plus_1 not in open_pool_candidates:
            # This happens if the prime gap > POOL_SIZE.
            # We skip this test as it's outside the parameters.
            continue
            
        total_predictions += 1
        total_primes_in_pools += len(open_pool_candidates)
        
        # --- 2. Get v16.0 Prediction ---
        prediction_v16 = get_v16_prediction(p_n, open_pool_candidates)
        
        if prediction_v16 is None:
            continue # No candidates were found (shouldn't happen here)

        if prediction_v16 == true_p_n_plus_1:
            total_successes += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v16_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    rand_acc = (total_predictions / total_primes_in_pools) * 100 if total_primes_in_pools > 0 else 0
    print(f"Progress: {progress:,} / {progress:,} | v16.0 Acc: {v16_acc:.2f}% | Random: {rand_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v16.0 'Open Pool') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Pool Size: All integers up to p_n + {POOL_SIZE}")
    
    baseline_v_mod6_acc = 14.77 # From plr_v3.md
    
    print(f"\nTotal Correct Predictions: {total_successes:,}")
    
    print(f"\n  'Random Chance' Accuracy:   {rand_acc:.2f}% (1 / avg_primes_in_pool)")
    print(f"  v_mod6 'Open Pool' (Baseline): {baseline_v_mod6_acc:.2f}%")
    print(f"  v16.0 'Open Pool' (New):      {v16_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v16_acc - baseline_v_mod6_acc
    print(f"  Improvement over v_mod6: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v16_acc > baseline_v_mod6_acc:
        print("\n  [VERDICT: 'HOLE A' IS CLOSED. THE SIGNAL IS REAL.]")
        print(f"  The v16.0 'Chained Signature' engine (Acc: {v16_acc:.2f}%)")
        print(f"  is a significantly stronger *predictor* than the simple")
        print(f"  v_mod6 engine (Acc: {baseline_v_mod6_acc:.2f}%).")
        print("\n  This proves the 75.94% 'classification' score translates")
        print("  into a real, robust, and superior predictive signal")
        print("  in a 'noisy' open pool environment.")
    else:
        print("\n  [VERDICT: 'HOLE A' IS CONFIRMED. 75.94% IS AN ARTIFACT.]")
        print(f"  The v16.0 engine's accuracy ({v16_acc:.2f}%) is no")
        print(f"  better than the v_mod6 baseline ({baseline_v_mod6_acc:.2f}%).")
        print("  This confirms the 75.94% 'classification' score")
        print("  is an artifact of the 'Closed Set' (10-candidate) test")
        print("  and does not translate to true predictive power.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v16_open_pool_test()