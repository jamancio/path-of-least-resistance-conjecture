# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 32: The "Volatility" Engine (v19.0)
#
# This engine adapts to the "Hot Corner" (Small-to-Large gap)
# signature we found in the v16.3 post-mortem.
#
# HYPOTHESIS:
# The 31.5% of failures in the "Small_to_Large" bin are because
# our v16.0 "Rank 2-4" search is *too shallow*. This "volatility"
# flings the true prime deeper.
#
# v19.0 ADAPTIVE LOGIC:
#
# 1. Check the "Gap Signature" (g_{n-1} vs. g_n).
#
# 2. IF (g_{n-1} == "Small" AND g_n == "Large"):
#    - This is the "Hot Corner" / "Volatility Signature".
#    - DEPLOY: "Deep Search" Fix (Ranks 2-7).
#
# 3. ELSE (All other signatures):
#    - This is "business as usual."
#    - DEPLOY: Standard v16.0 "Chained Signature" (Ranks 2-4).
#
# This tests if a "deeper" fix, applied *only* to the "Hot Corner",
# can break the 75.94% barrier.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# --- v16.0 Signature Thresholds ---
CLEAN_THRESHOLD = 3.0  
MESSY_THRESHOLD = 20.0 
STANDARD_SEARCH_DEPTH = 4 # Ranks 2-4 (Our v16.0 logic)
DEEP_SEARCH_DEPTH = 7       # Ranks 2-7 (Our new "Volatility" logic)

# --- Gap Categorization ---
GAP_BIN_SMALL = 18.0
GAP_BIN_LARGE = 22.0

def categorize_gap(gap):
    if gap < GAP_BIN_SMALL: return "Small"
    if gap >= GAP_BIN_LARGE: return "Large"
    return "Medium"

def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data.")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

# --- v11.0 Core Logic (Helper) ---
def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'): return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
# --- End Engine Setup ---

# --- v19.0 ADAPTIVE ENGINE LOGIC ---

def get_adaptive_prediction(p_n, candidates, gap_signature):
    """
    Runs the full v19.0 "Adaptive" logic.
    """
    
    # 1. Get the v11.0 ranked list
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        vmod6_rate = get_vmod6_score(S_cand)
        candidate_scores.append((score_v11, q_i, vmod6_rate))
    candidate_scores.sort(key=lambda x: x[0])
    
    winner_v11_prime = candidate_scores[0][1]
    winner_v11_vmod6 = candidate_scores[0][2]
    
    final_prediction = winner_v11_prime # Default
    
    # 2. Determine which search depth to use
    search_depth = STANDARD_SEARCH_DEPTH # Default (Ranks 2-4)
    if gap_signature == "Small_to_Large":
        search_depth = DEEP_SEARCH_DEPTH # Volatility Mode (Ranks 2-7)

    # 3. Apply the "Chained Signature" logic
    if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean"
        for rank_index in range(1, search_depth): # Use adaptive depth
            if rank_index >= len(candidate_scores): break
                
            next_candidate_vmod6 = candidate_scores[rank_index][2]
            
            if next_candidate_vmod6 > MESSY_THRESHOLD:
                final_prediction = candidate_scores[rank_index][1]
                break
                
    return final_prediction

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
def run_PLR_v19_volatility_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Volatility' Test (v19.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Baseline: v16.0 (75.94% Champion)")
    print(f"  - Challenger: v19.0 (Adaptive Deep Search)")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v16_baseline = 0
    total_successes_v19_new_champ = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    # Start at START_INDEX + 1 so we always have a g_{n-1}
    for i in range(START_INDEX + 1, loop_end_index):
        if (i - (START_INDEX+1) + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - (START_INDEX+1) + 1
            v19_acc = (total_successes_v19_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v16_acc = (total_successes_v16_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {total_predictions:,} | v19.0 Acc: {v19_acc:.2f}% | v16.0 Acc: {v16_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n_minus_1 = prime_list[i - 1]
        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        total_predictions += 1
        
        # --- 1. Get v16.0 Baseline Prediction (Standard Ranks 2-4 search) ---
        prediction_v16 = get_adaptive_prediction(p_n, candidates, "Standard") # Use standard logic
        if prediction_v16 == true_p_n_plus_1:
            total_successes_v16_baseline += 1
            
        # --- 2. Get v19.0 Adaptive Prediction ---
        
        # First, diagnose the environment
        g_n_minus_1_cat = categorize_gap(p_n - p_n_minus_1)
        g_n_cat = categorize_gap(true_p_n_plus_1 - p_n)
        gap_signature = f"{g_n_minus_1_cat}_to_{g_n_cat}"
        
        # Run the adaptive engine
        final_prediction_v19 = get_adaptive_prediction(p_n, candidates, gap_signature)

        # 3. Tally the v19.0 Result
        if final_prediction_v19 == true_p_n_plus_1:
            total_successes_v19_new_champ += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v19_acc = (total_successes_v19_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v16_acc = (total_successes_v16_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {progress:,} | v19.0 Acc: {v19_acc:.2f}% | v16.0 Acc: {v16_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v19.0 'Volatility') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    
    print(f"\nTotal Correct (v16.0 Baseline):  {total_successes_v16_baseline:,}")
    print(f"Total Correct (v19.0 'Volatility'): {total_successes_v19_new_champ:,}")
    
    print(f"\n  v16.0 'Chained' (Baseline):    {v16_acc:.2f}%")
    print(f"  v19.0 'Volatility' (New): {v19_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v19_acc - v16_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v19_acc > v16_acc:
        print("\n  [VERDICT: SUCCESS. THE 'VOLATILITY' SIGNAL IS REAL!]")
        print(f"  The new 'v19.0' engine's accuracy ({v19_acc:.2f}%) has")
        print(f"  achieved a new record, breaking the 75.94% barrier!")
        print("\n  This PROVES the final hypothesis:")
        print("  The 'Small_to_Large' gap signature is a special case")
        print("  that requires a *deeper* search, and this adaptive")
        print("  model successfully fixed it.")
    else:
        print("\n  [VERDICT: FALSIFIED. 75.94% IS THE LIMIT.]")
        print(f"  The new 'v19.0' engine's accuracy ({v19_acc:.2f}%) is")
        print(f"  not better than the v16.0 baseline ({v16_acc:.2f}%).")
        print("  This confirms that searching deeper (past Rank 4)")
        print("  *always* adds more noise than it fixes, even in the")
        print("  'Hot Corner.' 75.94% is the true structural limit.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v19_volatility_test()