# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 40: The "Internal Flip" Engine (v23.0)
#
# This script implements the Analytic Logic Gate for f(p_n).
#
# - Added the missing definition for get_v11_multiplicative_prediction.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v16.0 Framework) ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
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
    """The v11.0 "Weighted Gap" Engine Core (Multiplicative)."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'): return float('inf')
    # Add 1.0 to avoid 0*gap issues and normalize scoring
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))

# --- V11.0 BASELINE FUNCTION (The missing definition) ---
def get_v11_multiplicative_prediction(p_n, candidates):
    """v11.0 Multiplicative Core: (v_mod6 + 1.0) * gap. Returns the winner prime."""
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        candidate_scores.append((score, q_i))

    candidate_scores.sort(key=lambda x: x[0])
    return candidate_scores[0][1]
# --- END V11.0 BASELINE FUNCTION ---


# --- v23.0 FINAL LOGIC ---
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
    candidates_data.sort(key=lambda x: x[0])
    v11_winner_score, v11_winner_prime, _, v11_winner_gap = candidates_data[0]
    
    final_prediction = v11_winner_prime # Default prediction

    # --- 3. Find the Structural Minimum (The "Cleanest Messy") ---
    
    # Sort the Messy Bin by gap (Closeness). We are looking for the prime
    # in the Messy group that is the absolute closest.
    if messy_bin:
        messy_bin.sort(key=lambda x: x[3]) # Sort by gap (index 3)
        g_messy_low = messy_bin[0][3]
        p_messy_low = messy_bin[0][1]
        
        # --- 4. Apply the Analytic Logic Gate (The Flip Trigger) ---
        
        # Condition X: Is the lowest gap in the Messy Bin (g_messy_low) 
        # LOWER than the gap of the overall arithmetic winner (v11_winner_gap)?
        if g_messy_low < v11_winner_gap:
            # The Flip: Structural necessity (low gap) overrides arithmetic winner
            final_prediction = p_messy_low

    return final_prediction

# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
PRIMES_TO_TEST = 50000000 # Max primes to search
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
def run_PLR_v23_internal_flip_test():
    
    if not load_engine_data(): return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Internal Flip' Test (v23.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Baseline: v11.0 (60.49% Multiplicative Core)")
    print(f"  - Challenger: v23.0 (Analytic Logic Gate - Internal Flip)")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v11_baseline = 0
    total_successes_v23_new_champ = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v23_acc = (total_successes_v23_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v23.0 Acc: {v23_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        # --- Run both engines ---
        
        # v11.0 Baseline
        pred_v11 = get_v11_multiplicative_prediction(p_n, candidates)
        if pred_v11 == true_p_n_plus_1:
            total_successes_v11_baseline += 1
        
        # v23.0 Challenger
        pred_v23 = get_v23_internal_flip_prediction(p_n, candidates)
        if pred_v23 == true_p_n_plus_1:
            total_successes_v23_new_champ += 1
            
        total_predictions += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v23_acc = (total_successes_v23_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {progress:,} | v23.0 Acc: {v23_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v23.0 'Internal Flip') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    
    print(f"\nTotal Correct (v11.0 Baseline): {total_successes_v11_baseline:,}")
    print(f"Total Correct (v23.0 Challenger): {total_successes_v23_new_champ:,}")
    
    print(f"\n  v11.0 Multiplicative (Baseline): {v11_acc:.2f}%")
    print(f"  v23.0 'Internal Flip' (New): {v23_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v23_acc - v11_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    if v23_acc > 61.0: # Check if it's a significant improvement over 60.49%
        print("\n  [VERDICT: SUCCESS. THE ANALYTIC LOGIC GATE IS FOUND!]")
        print(f"  The new 'v23.0' engine's accuracy ({v23_acc:.2f}%) has")
        print("  achieved a new record, proving that the final problem is")
        print("  a solvable comparative structural test.")
    else:
        print("\n  [VERDICT: FALSIFIED. THE LOGIC GATE IS INCORRECT.]")
        print(f"  The new 'v23.0' engine's accuracy ({v23_acc:.2f}%) is")
        print("  not a significant improvement over the v11.0 baseline.")
        print("  This confirms the 'Internal Flip' logic is too simple or")
        print("  the comparative structure is not the final analytic key.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v23_internal_flip_test()