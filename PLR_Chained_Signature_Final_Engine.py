# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 26: The "Chained Signature" Engine (v16.0 - Metric Update)
#
# This script is the final test for the Rank 4 fix.
#
# UPDATE: This version includes a specific metric to track the *Total Overrides*
#         for the full v16.0 logic (Ranks 2, 3, and 4 combined).
#
# This allows us to definitively calculate the precision of the entire
# 75.94% accuracy gain.
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
MAX_SIGNATURE_SEARCH_DEPTH = 4 # (Will check Ranks 2, 3, and 4)


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
        return None
    
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_v16_chained_signature_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Chained Signature' Test (v16.0 - Metric Update) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v11.0 + 'Clean #1 vs. Messy #(2-4)' Chained Override")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v15_baseline = 0
    total_successes_v16_new_champ = 0
    
    # --- NEW METRIC ---
    total_v16_overrides_attempted = 0
    # ---
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v16_acc = (total_successes_v16_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v15_acc = (total_successes_v15_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v16.0 Acc: {v16_acc:.2f}% | v15.0 Acc: {v15_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

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
        
        # --- Apply v15.0 Baseline Logic (Ranks 2 and 3) ---
        
        winner_v11_prime = candidate_scores[0][1]
        winner_v11_vmod6 = candidate_scores[0][2]
        
        # We need to know the v15 prediction for the final tally
        prediction_v15 = winner_v11_prime
        
        # The new v16.0 engine's prediction
        prediction_v16 = winner_v11_prime # Default for new engine
        
        
        # --- CHAINED SEARCH: Ranks 2, 3, 4 ---
        if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean" (potential failure signature)
            
            # This flag tracks if *any* override was applied in this chain
            override_applied = False
            
            for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH + 1):
                if rank_index >= len(candidate_scores):
                    break
                    
                next_candidate_vmod6 = candidate_scores[rank_index][2]
                
                if next_candidate_vmod6 > MESSY_THRESHOLD:
                    # *** OVERRIDE ***
                    # The first 'Messy' candidate found is the prediction
                    
                    if not override_applied:
                        # Only count the override once (at the highest priority rank found)
                        total_v16_overrides_attempted += 1
                        override_applied = True
                        
                    # The override decision is the Messy candidate's prime
                    next_candidate_prime = candidate_scores[rank_index][1]

                    # Tallying logic for both baselines and new engine:
                    if rank_index == 1: # Rank 2 fix (v12.0 logic)
                        prediction_v15 = next_candidate_prime
                        prediction_v16 = next_candidate_prime
                    elif rank_index == 2: # Rank 3 fix (v15.0 logic)
                        # The v15 baseline uses Rank 2 OR Rank 3 fix
                        if not candidate_scores[1][2] > MESSY_THRESHOLD:
                            prediction_v15 = next_candidate_prime
                        prediction_v16 = next_candidate_prime
                    elif rank_index == 3: # Rank 4 fix (v16.0 new logic)
                        prediction_v16 = next_candidate_prime
                        
                    # Break the chain after the first fix is applied (highest priority)
                    break 

        # --- Tally v15.0 Baseline Result ---
        if prediction_v15 == true_p_n_plus_1:
            total_successes_v15_baseline += 1
            
        # --- Tally v16.0 Result ---
        if prediction_v16 == true_p_n_plus_1:
            total_successes_v16_new_champ += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v16_acc = (total_successes_v16_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v15_acc = (total_successes_v15_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v16.0 Acc: {v16_acc:.2f}% | v15.0 Acc: {v15_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v16.0 'Chained Signature') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Total Correct (v15.0 Baseline): {total_successes_v15_baseline:,}")
    print(f"Total Correct (v16.0 'Chained'): {total_successes_v16_new_champ:,}")
    
    # --- Final Metrics ---
    net_gain = total_successes_v16_new_champ - total_successes_v15_baseline
    precision = (net_gain / total_v16_overrides_attempted) * 100 if total_v16_overrides_attempted > 0 else 0
    
    print(f"\nTotal Overrides Attempted (R2+R3+R4): {total_v16_overrides_attempted:,}")
    print(f"Net Gain from Override (R4 fix):     {net_gain:,}")
    
    print(f"\n  v15.0 'Rank 3 Signature' (Baseline): {v15_acc:.2f}%")
    print(f"  v16.0 'Chained Signature' (New): {v16_acc:.2f}%")
    print("  ---------------------------------")
    print(f"  Improvement over Baseline: {v16_acc - v15_acc:+.2f} percentage points")
    print(f"  Calculated Precision of Fix: {precision:.2f}%")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v16_acc > v15_acc:
        print("\n  [VERDICT: SUCCESS. THE CHAIN IS VIABLE!]")
        print(f"  The new 'v16.0' engine's accuracy ({v16_acc:.2f}%) has")
        print(f"  achieved a new record, breaking the 73.65% barrier!")
        print("\n  This PROVES the final hypothesis:")
        print("  The 'Path of Least Resistance' is a multi-stage,")
        print("  multi-rank problem that can be solved sequentially.")
    else:
        print("\n  [VERDICT: FALSIFIED. 73.65% IS THE LIMIT.]")
        print(f"  The new 'v16.0' engine's accuracy ({v16_acc:.2f}%) is")
        print(f"  not better than the v15.0 baseline ({v15_acc:.2f}%).")
        print("  This confirms the reliability rapidly collapses past Rank 3.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v16_chained_signature_test()