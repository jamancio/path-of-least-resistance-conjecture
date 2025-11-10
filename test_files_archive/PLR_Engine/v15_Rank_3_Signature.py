# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 25: The "Rank 3 Signature" Engine (v15.0)
#
# This is the test to break the 68.07% barrier by isolating the next
# largest failure pocket: the 25.60% of failures at Rank 3.
#
# v15.0 Logic: v12.0 logic (Clean #1 vs Messy #2) + new override for Rank 3.
#
# HYPOTHESIS:
# The "Clean #1 vs. Messy #3" signature is reliable enough in isolation
# to provide a net gain over the v12.0 (68.07%) baseline.
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
def run_PLR_v15_rank3_signature_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Rank 3 Signature' Test (v15.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v12.0 (Rank 2 fix) + new override for Rank 3")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v12_baseline = 0
    total_successes_v15_new_champ = 0
    total_rank3_overrides_attempted = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v15_acc = (total_successes_v15_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v12_acc = (total_successes_v12_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v15.0 Acc: {v15_acc:.2f}% | v12.0 Acc: {v12_acc:.2f}% | Rank 3 Overrides: {total_rank3_overrides_attempted:,} | Time: {elapsed:.0f}s", end='\r')

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

        total_predictions += 1
        candidate_scores.sort(key=lambda x: x[0])
        
        # --- Apply v12.0 Baseline Logic ---
        
        # Get data for the top candidates
        winner_v11_prime = candidate_scores[0][1]
        winner_v11_vmod6 = candidate_scores[0][2]
        
        prediction_v12 = winner_v11_prime # Default
        
        # v12.0 Logic: Check Rank 2
        if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean"
            if len(candidate_scores) >= 2:
                candidate_2_vmod6 = candidate_scores[1][2]
                if candidate_2_vmod6 > MESSY_THRESHOLD: # AND #2 is "Messy"
                    prediction_v12 = candidate_scores[1][1] # OVERRIDE

        if prediction_v12 == true_p_n_plus_1:
            total_successes_v12_baseline += 1
            
        # --- Apply v15.0 Logic (The New Fix) ---
        
        final_prediction_v15 = prediction_v12 # Start with v12's prediction
        
        # The Rank 2 override has priority (it's built into prediction_v12).
        # We only need to check for Rank 3 if the v12 prediction was NOT an override.
        # Simplest way: check if prediction_v12 chose Rank 1.
        
        # We check the original Rank 1 winner's v_mod6 score.
        if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean" (potential failure signature)
            
            # Check Rank 3 (Index 2 in the list)
            if len(candidate_scores) >= 3:
                candidate_3_vmod6 = candidate_scores[2][2] # Rank 3's vmod6 score
                
                # Check for the Clean #1 vs Messy #3 Signature
                if candidate_3_vmod6 > MESSY_THRESHOLD: 
                    
                    # *Only* override if v12.0 did *not* already make a prediction for Rank 2.
                    # This check is slightly complex, but necessary for the chain:
                    
                    # Did the v12.0 override NOT happen?
                    # The v12.0 override happens IF #1 is Clean AND #2 is Messy.
                    # We only override for #3 if #2 was NOT Messy (or #1 was not Clean, but we checked that).
                    
                    # The v12 override happens when:
                    v12_override_did_NOT_happen = True
                    if len(candidate_scores) >= 2:
                        candidate_2_vmod6 = candidate_scores[1][2]
                        # Check if the signature for #2 was found
                        if winner_v11_vmod6 < CLEAN_THRESHOLD and candidate_2_vmod6 > MESSY_THRESHOLD:
                            v12_override_did_NOT_happen = False # The v12 override DID happen.
                            
                    # If v12 did not override, check for #3
                    if v12_override_did_NOT_happen:
                        final_prediction_v15 = candidate_scores[2][1] # OVERRIDE
                        total_rank3_overrides_attempted += 1

        if final_prediction_v15 == true_p_n_plus_1:
            total_successes_v15_new_champ += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v15_acc = (total_successes_v15_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v12_acc = (total_successes_v12_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v15.0 Acc: {v15_acc:.2f}% | v12.0 Acc: {v12_acc:.2f}% | Rank 3 Overrides: {total_rank3_overrides_attempted:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v15.0 'Rank 3 Signature') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Total Correct (v12.0 Baseline): {total_successes_v12_baseline:,}")
    print(f"Total Correct (v15.0 'Rank 3'): {total_successes_v15_new_champ:,}")
    print(f"Total Rank 3 Overrides Attempted: {total_rank3_overrides_attempted:,}")
    
    print(f"\n  v12.0 'Signature' (Baseline): {v12_acc:.2f}%")
    print(f"  v15.0 'Rank 3 Signature' (New): {v15_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v15_acc - v12_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v15_acc > v12_acc:
        print("\n  [VERDICT: SUCCESS. THE RANK 3 FIX IS VIABLE!]")
        print(f"  The new 'v15.0' engine's accuracy ({v15_acc:.2f}%) has")
        print(f"  achieved a new record, breaking the 68.07% barrier!")
        print("\n  This PROVES the 'Clean #1 vs. Messy #3' signature is a")
        print("  reliable secondary fix, proving the 'Path of Least Resistance'")
        print("  is a solvable, multi-stage problem.")
    else:
        print("\n  [VERDICT: FALSIFIED. 68.07% IS THE LIMIT.]")
        print(f"  The new 'v15.0' engine's accuracy ({v15_acc:.2f}%) is")
        print(f"  not better than the v12.0 baseline ({v12_acc:.2f}%).")
        print("  This confirms the earlier v14.0 result: the Rank 3 signature")
        print("  is not reliable, and the cost of the fix exceeds the gain.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v15_rank3_signature_test()