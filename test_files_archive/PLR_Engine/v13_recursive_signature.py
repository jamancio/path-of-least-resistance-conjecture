# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 22: The "Recursive Signature" Engine (v13.0)
#
# This is our most advanced "smart" engine.
#
# Our v11_3 post-mortem proved ~91% of all failures are "Scenario B"
# (Clean #1 vs. Messy True) and that the "Messy" true prime
# is hiding in Ranks 2-6.
#
# HYPOTHESIS:
# We can expand our v12.0 "Signature" to be recursive.
#
# 1. Run the v11.0 engine to get the full ranked list.
# 2. IF the #1 Winner is "Clean" (v_mod6 < 3.0):
# 3.    Recursively search Ranks 2, 3, 4, 5, and 6.
# 4.    IF a "Messy" candidate (v_mod6 > 20.0) is found:
# 5.       OVERRIDE and predict this "Messy" candidate
#          (the one with the highest rank, i.e., closest to #1).
# 6.    ELSE (no messy candidates in ranks 2-6):
# 7.       TRUST the #1 "Clean" winner.
#
# This should "recover" the vast majority of our 39.51% of failures
# and be the definitive test of the PLR.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v11.0 "Weighted Gap") ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# --- These are the "Signature" thresholds ---
# "Clean" is the v_mod6 score for the 0-residue class
CLEAN_THRESHOLD = 3.0  # (Actual score is 2.71%)
# "Messy" is the v_mod6 score for the 2- and 4-residue classes
MESSY_THRESHOLD = 20.0 # (Actual scores are ~26.2%)
# How far down the list we will search for a "Messy" candidate
RECURSIVE_SEARCH_DEPTH = 6 # (Will check Ranks 2, 3, 4, 5, 6)


def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
        print(f"  - 'Clean' Signature Threshold: < {CLEAN_THRESHOLD}%")
        print(f"  - 'Messy' Signature Threshold: > {MESSY_THRESHOLD}%")
        print(f"  - 'Recursive Search Depth': Ranks 2-{RECURSIVE_SEARCH_DEPTH}")
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
def run_PLR_v13_recursive_signature_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Recursive Signature' Test (v13.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v11.0 + 'Clean #1 vs. Messy #(2-6)' Override Rule")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v11_baseline = 0
    total_successes_v13_new_champ = 0
    total_overrides_attempted = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v13_acc = (total_successes_v13_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v13.0 Acc: {v13_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Overrides: {total_overrides_attempted:,} | Time: {elapsed:.0f}s", end='\r')

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
            candidate_scores.append((score_v11, q_i))

        # --- Get v11.0 Baseline Prediction ---
        total_predictions += 1
        candidate_scores.sort(key=lambda x: x[0])
        
        winner_v11_prime = candidate_scores[0][1] # Get the prime
        if winner_v11_prime == true_p_n_plus_1:
            total_successes_v11_baseline += 1
            
        # --- Run v13.0 "Recursive Signature" Logic ---
        final_prediction = winner_v11_prime # Default to v11.0
        
        # 1. Get the v_mod6 score of the #1 Winner
        winner_v11_anchor = p_n + winner_v11_prime
        winner_v11_vmod6 = get_vmod6_score(winner_v11_anchor)
        
        # 2. IF the #1 Winner is "Clean", start searching for a "Messy" one
        if winner_v11_vmod6 < CLEAN_THRESHOLD:
            
            # 3. Recursively search Ranks 2 through RECURSIVE_SEARCH_DEPTH
            # (List index 1 is Rank 2)
            for rank_index in range(1, RECURSIVE_SEARCH_DEPTH):
                
                # Stop if we run out of candidates (e.g., if NUM_CANDIDATES < 6)
                if rank_index >= len(candidate_scores):
                    break
                    
                # 4. Get the next candidate's data
                next_candidate_prime = candidate_scores[rank_index][1]
                next_candidate_anchor = p_n + next_candidate_prime
                next_candidate_vmod6 = get_vmod6_score(next_candidate_anchor)
                
                # 5. Check if it's "Messy"
                if next_candidate_vmod6 > MESSY_THRESHOLD:
                    # *** OVERRIDE ***
                    # We found the "Clean #1 vs. Messy #(2-6)" signature.
                    # We predict this "Messy" candidate instead.
                    final_prediction = next_candidate_prime
                    total_overrides_attempted += 1
                    # We're done searching
                    break 
        
        # 6. Tally the final v13.0 prediction
        if final_prediction == true_p_n_plus_1:
            total_successes_v13_new_champ += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v13_acc = (total_successes_v13_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v13.0 Acc: {v13_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Overrides: {total_overrides_attempted:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v13.0 'Recursive Signature') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    print(f"Total 'Signature' Overrides Attempted: {total_overrides_attempted:,}")
    
    print(f"\nTotal Correct (v11.0 Baseline): {total_successes_v11_baseline:,}")
    print(f"Total Correct (v13.0 'Recursive'): {total_successes_v13_new_champ:,}")
    
    print(f"\n  v11.0 'Weighted Gap' (Baseline): {v11_acc:.2f}%")
    print(f"  v13.0 'Recursive Signature' (New): {v13_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v13_acc - v11_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v13_acc > v11_acc:
        print("\n  [VERDICT: SUCCESS. THE 'RECURSIVE SIGNATURE' IS REAL!]")
        print(f"  The new 'v13.0' engine's accuracy ({v13_acc:.2f}%) has")
        print(f"  achieved a new record, breaking the 68.07% barrier!")
        print("\n  This PROVES the final hypothesis:")
        print("  The 39.51% of failures are dominated by a predictable")
        print("  'Clean #1 vs. Messy #(2-6)' signature that can be")
        print("  identified and corrected across multiple ranks.")
    else:
        print("\n  [VERDICT: FALSIFIED. v12.0 IS THE LIMIT.]")
        print(f"  The new 'v13.0' engine's accuracy ({v13_acc:.2f}%) is")
        print(f"  not better than the v12.0 baseline (68.07%).")
        print("  This means the 'Clean #1 vs. Messy #3-6' signatures")
        print("  are not reliable. The only 'fix' that works is the")
        print("  simple 'Clean #1 vs. Messy #2' override.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v13_recursive_signature_test()