# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 41: The "Analytic Synthesis" Engine (v24.0)
#
# This is the final theoretical test, combining all known fixes.
#
# v24.0 SYNTHESIS LOGIC:
# 1. Runs the v23.0 "Internal Flip" logic (the f(p_n) Logic Gate).
# 2. IF the flip condition is met: PREDICT p_messy_low.
# 3. ELSE: Fallback to the v16.0 "Chained Signature" logic (Ranks 2-4 search).
#
# This tests if the final 100% solution is compatible with the established
# 75.94% structural framework.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup ---
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
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))

# --- v11.0 BASELINE FUNCTION (For v24.0 step 1) ---
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

# --- v24.0 SYNTHESIS FUNCTION ---
def get_v24_synthesis_prediction(p_n, candidates, v11_baseline_prediction):
    
    # 1. Build the full evidence list and isolate bins (needed for both v23 and v16 logic)
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
            
    # Sort data for ease of accessing the Rank 1/Rank 2/Rank 3 elements
    candidates_data.sort(key=lambda x: x[0]) 

    # --- PART A: Apply v23.0 Logic (The 100% Flip Gate) ---
    
    # Get v11.0 Winner data
    v11_winner_prime = candidates_data[0][1]
    v11_winner_gap = candidates_data[0][3]

    prediction_v24 = v11_winner_prime # Default starts at the v11 winner
    flip_triggered = False

    if messy_bin:
        messy_bin.sort(key=lambda x: x[3]) # Sort Messy Bin by gap
        g_messy_low = messy_bin[0][3]
        p_messy_low = messy_bin[0][1]
        
        # Analytic Logic Gate: If g_messy_low is LOWER than the winner's gap
        if g_messy_low < v11_winner_gap:
            # FLIP: The structural necessity overrides the arithmetic winner
            prediction_v24 = p_messy_low
            flip_triggered = True

    # --- PART B: Apply v16.0 Logic (The 75.94% Chained Signature Fix) ---
    
    # We only apply the v16.0 logic if the v23.0 flip DID NOT occur.
    if not flip_triggered:
        
        # Extract v16.0 required metrics from the v11 ranked list
        winner_v11_vmod6 = candidates_data[0][2] # Rank 1 vmod6 score
        
        if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean"
            for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH): # Ranks 2, 3, 4
                if rank_index >= len(candidates_data): break
                
                next_candidate_vmod6 = candidates_data[rank_index][2]
                
                if next_candidate_vmod6 > MESSY_THRESHOLD:
                    # Found the Messy suspect - OVERRIDE
                    prediction_v24 = candidates_data[rank_index][1]
                    break
                    
    return prediction_v24

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
def run_PLR_v24_synthesis_test():
    
    if not load_engine_data(): return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Analytic Synthesis' Test (v24.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Baseline: v11.0 (60.49% Core)")
    print(f"  - Challenger: v24.0 (v23 Logic + v16 Logic)")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v11_baseline = 0
    total_successes_v24_new_champ = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v24_acc = (total_successes_v24_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v24.0 Acc: {v24_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

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
        
        # v24.0 Challenger
        pred_v24 = get_v24_synthesis_prediction(p_n, candidates, pred_v11) # pred_v11 is unused here, but kept for future structure
        if pred_v24 == true_p_n_plus_1:
            total_successes_v24_new_champ += 1
            
        total_predictions += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v24_acc = (total_successes_v24_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {progress:,} | v24.0 Acc: {v24_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v24.0 'Analytic Synthesis') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    
    print(f"\nTotal Correct (v11.0 Baseline): {total_successes_v11_baseline:,}")
    print(f"Total Correct (v24.0 Challenger): {total_successes_v24_new_champ:,}")
    
    print(f"\n  v11.0 Multiplicative (Baseline): {v11_acc:.2f}%")
    print(f"  v24.0 'Analytic Synthesis' (New): {v24_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v24_acc - v11_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    if v24_acc > 76.0: # Check if it exceeds the v16.0 ceiling (75.94%)
        print("\n  [VERDICT: SUCCESS. THE 100% THEORETICAL MODEL IS REAL!]")
        print(f"  The new 'v24.0' engine's accuracy ({v24_acc:.2f}%) has")
        print("  achieved a monumental new record, validating the final analytic logic.")
    else:
        print("\n  [VERDICT: THE ANALYTIC TRAIL HAS GONE COLD.]")
        print(f"  The new 'v24.0' engine's accuracy ({v24_acc:.2f}%) did not")
        print(f"  exceed the v16.0 ceiling (75.94%), confirming that the")
        print("  final analytic truth is not solved by this simple synthesis.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v24_synthesis_test()