# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 23: The "Chained Signature" Engine (v14.0)
#
# This is our most advanced, multi-stage "smart" engine.
#
# Our v13.0 engine (64.31%) failed because it was too aggressive.
# It proved we cannot just group Ranks 2-6 together.
#
# HYPOTHESIS:
# We must "chain" our override rules, starting with the most
# reliable signature (Rank 2) and moving down.
#
# 1. Get the v11.0 ranked list.
# 2. IF "Clean #1 vs. Messy #2" signature exists:
#       PREDICT #2 (This is the v12.0 engine logic)
# 3. ELIF "Clean #1 vs. Messy #3" signature exists:
#       PREDICT #3 (This is our new override rule)
# 4. ELIF "Clean #1 vs. Messy #4" signature exists:
#       PREDICT #4 (And so on...)
# 5. ... down to Rank 6 ...
# 6. ELSE:
#       TRUST the original #1 winner from v11.0.
#
# This should "stack" our accuracy gains from each rank
# and finally break the 68.07% barrier.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v11.0 "Weighted Gap") ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# --- These are the "Signature" thresholds ---
CLEAN_THRESHOLD = 3.0  # (v_mod6 score < 3.0 is "Clean")
MESSY_THRESHOLD = 20.0 # (v_mod6 score > 20.0 is "Messy")
# How far down the list we will search
MAX_SIGNATURE_SEARCH_DEPTH = 6 # (Will check Ranks 2, 3, 4, 5, 6)


def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
        print(f"  - 'Clean' Signature Threshold: < {CLEAN_THRESHOLD}%")
        print(f"  - 'Messy' Signature Threshold: > {MESSY_THRESHOLD}%")
        print(f"  - 'Chained Search Depth': Ranks 2-{MAX_SIGNATURE_SEARCH_DEPTH}")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    """The v11.0 "Weighted Gap" Engine."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'):
        return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
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
        print("Please ensure 'primes_100m.txt' is in a 'prime' folder.")
        return None
    
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_v14_chained_signature_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Chained Signature' Test (v14.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v11.0 + 'Clean #1 vs. Messy #(2-6)' Chained Override")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v11_baseline = 0
    total_successes_v12_baseline = 0 # Our true champion (68.07%)
    total_successes_v14_new_champ = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v14_acc = (total_successes_v14_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v12_acc = (total_successes_v12_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v14.0 Acc: {v14_acc:.2f}% | v12.0 Acc: {v12_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        # Get the v11.0 ranked list
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
            # Store (score, prime, vmod6_score)
            vmod6_rate = get_vmod6_score(S_cand)
            candidate_scores.append((score_v11, q_i, vmod6_rate))

        # --- Get v11.0 Baseline Prediction ---
        total_predictions += 1
        candidate_scores.sort(key=lambda x: x[0])
        
        winner_v11_prime = candidate_scores[0][1]
        if winner_v11_prime == true_p_n_plus_1:
            total_successes_v11_baseline += 1
            
        # --- Run v12.0 and v14.0 Logic ---
        
        # Get data for the top candidates
        winner_v11_vmod6 = candidate_scores[0][2]
        
        prediction_v12 = winner_v11_prime # Default
        prediction_v14 = winner_v11_prime # Default
        
        # --- v12.0 LOGIC (Our 68.07% Champion Baseline) ---
        if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean"
            if len(candidate_scores) >= 2:
                candidate_2_vmod6 = candidate_scores[1][2]
                if candidate_2_vmod6 > MESSY_THRESHOLD: # AND #2 is "Messy"
                    prediction_v12 = candidate_scores[1][1] # OVERRIDE

        if prediction_v12 == true_p_n_plus_1:
            total_successes_v12_baseline += 1
            
        # --- v14.0 "CHAINED" LOGIC (Our New Challenger) ---
        if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean"
            
            # Start searching from Rank 2 down to our max depth
            for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH):
                if rank_index >= len(candidate_scores):
                    break # Stop if we run out of candidates
                
                next_candidate_vmod6 = candidate_scores[rank_index][2]
                
                if next_candidate_vmod6 > MESSY_THRESHOLD:
                    # *** OVERRIDE ***
                    # We found a "Messy" candidate in the failure zone
                    prediction_v14 = candidate_scores[rank_index][1]
                    # IMPORTANT: We stop at the *first one* we find.
                    break 

        if prediction_v14 == true_p_n_plus_1:
            total_successes_v14_new_champ += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v14_acc = (total_successes_v14_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v12_acc = (total_successes_v12_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v14.0 Acc: {v14_acc:.2f}% | v12.0 Acc: {v12_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v14.0 'Chained Signature') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    print(f"\nTotal Correct (v12.0 Baseline):  {total_successes_v12_baseline:,}")
    print(f"Total Correct (v14.0 'Chained'): {total_successes_v14_new_champ:,}")
    
    print(f"\n  v12.0 'Signature' (Baseline):    {v12_acc:.2f}%")
    print(f"  v14.0 'Chained Signature' (New): {v14_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v14_acc - v12_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v14_acc > v12_acc:
        print("\n  [VERDICT: SUCCESS. THE 'CHAINED' MODEL IS SUPERIOR!]")
        print(f"  The new 'v14.0' engine's accuracy ({v14_acc:.2f}%) has")
        print(f"  achieved a new record, breaking the 68.07% barrier!")
        print("\n  This PROVES the final hypothesis:")
        print("  The 'Clean #1 vs. Messy #X' signature is a real,")
        print("  predictable signal that can be 'fixed' by searching")
        print("  down through the ranked list.")
    else:
        print("\n  [VERDICT: FALSIFIED. v12.0 REMAINS CHAMPION.]")
        print(f"  The new 'v14.0' engine's accuracy ({v14_acc:.2f}%) is")
        print(f"  not better than the v12.0 baseline ({v12_acc:.2f}%).")
        print("  This means our 'v13.0' test was right: searching")
        print("  deeper (past Rank 2) just adds noise and hurts accuracy.")
        print("  The 68.07% from the 'Clean #1 vs. Messy #2' signature")
        print("  appears to be the true 'hard dead end'.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v14_chained_signature_test()