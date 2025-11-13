# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 43: The "v23.0 Replication" Test
#
# This script tests "Hole B: Over-fitting and Universality"
# for the "100% Accurate" v23.0 Engine.
#
# We will run our v23.0 "Internal Flip" engine on a BRAND NEW,
# UNSEEN data set: the primes from 50,000,001 to 100,000,000.
#
# We will use the *exact same* data map (messiness_map_v_mod6.json,
# trained on the first 50M primes) and the *exact same* thresholds
# (CLEAN=3.0, MESSY=20.0).
#
# HYPOTHESIS:
# If the v23.0 engine's accuracy is still 100.00%
# on this new data, it proves our model is a UNIVERSAL LAW
# and not an over-fitted artifact. If it collapses,
# it proves the 100% was an illusion of curve-fitting.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v23.0 "Internal Flip" Logic) ---
# IMPORTANT: We are using the *original* data maps trained on primes 1-50M.
# We are intentionally NOT retraining the model.
MOD6_ENGINE_FILE = "../data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# --- These are the "Signature" thresholds ---
CLEAN_THRESHOLD = 3.0  
MESSY_THRESHOLD = 20.0 

def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) data from '{MOD6_ENGINE_FILE}'.")
        print("Running in 'Replication' mode. Data map is from primes 1-50M.")
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
        
        # Store (v11_score, prime, vmod6_rate, gap)
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
# We test the *next* 50 million primes
PRIMES_TO_TEST = 49999900 
NUM_CANDIDATES_TO_CHECK = 10 
# We *start* from the 50,000,010th prime
START_INDEX = 50000010 

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
    
    # We must have 100M primes in the file for this test
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        print(f"This test requires at least {required_primes:,} primes.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_v23_replication_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Replication' Test (v23.0) for primes {START_INDEX:,} to {START_INDEX + PRIMES_TO_TEST:,}...")
    print(f"  - Engine: v23.0 (100.00% Theoretical Champion)")
    print(f"  - Data Maps: Trained on primes 1-50M")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST + START_INDEX is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v23_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v23.0 Acc: {v23_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        total_predictions += 1
        
        # Get v23.0 Prediction
        prediction_v23 = get_v23_internal_flip_prediction(p_n, candidates)
        
        if prediction_v23 is None:
            continue

        if prediction_v23 == true_p_n_plus_1:
            total_successes += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v23_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {progress:,} | v23.0 Acc: {v23_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v23.0 'Replication') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,} (from 50M to 100M)")
    
    baseline_acc = 100.00 # The accuracy from the first 50M
    
    print(f"\n  Accuracy on Primes 1-50M:   {baseline_acc:.2f}%")
    print(f"  Accuracy on Primes 50M-100M: {v23_acc:.2f}%")
    print("  ---------------------------------")
    drop_off = v23_acc - baseline_acc
    print(f"  Accuracy Drop-off: {drop_off:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if abs(drop_off) < 0.5: # Allow for a tiny margin
        print("\n  [VERDICT: 'HOLE B' IS CLOSED. THE MODEL IS UNIVERSAL.]")
        print(f"  The accuracy ({v23_acc:.2f}%) is statistically identical")
        print(f"  to the baseline ({baseline_acc:.2f}%).")
        print("\n  This proves the 100.00% signal is a UNIVERSAL LAW")
        print("  of the prime sequence, and the 'Analytic Logic Gate' is real.")
        print("  This is a conclusive, monumental finding.")
    else:
        print("\n  [VERDICT: 'HOLE B' IS CONFIRMED. THE 100% MODEL WAS OVER-FITTED.]")
        print(f"  The accuracy ({v23_acc:.2f}%) shows a significant")
        print(f"  drop-off of {drop_off:.2f} points from the baseline ({baseline_acc:.2f}%).")
        print("\n  This proves the 'v23.0 Internal Flip' logic was partially")
        print("  'over-fitted' to the 1-50M data set.")
        print(f"  The true, universal accuracy of this model is {v23_acc:.2f}%,")
        print("  which is *lower* than the robust v16.0 engine (75.90%).")
        print("  This confirms the v16.0 'Chained Signature' is the true champion.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v23_replication_test()