# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 27: The "Structural Ceiling" Engine (v17.0)
#
# This is the final test: replacing the v_mod6 core with the strongest
# structural filter available, v_mod210.
#
# HYPOTHESIS:
# The superior structural cleanliness of v_mod210 will overcome its
# complexity, yielding a predictive ceiling higher than 75.94%.
#
# Logic: (v_mod210_rate * gap_g_n) + Sequential Signature Override (Ranks 2-4)
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MOD210_ENGINE_FILE = "data/messiness_map_v3_mod210.json"
MESSINESS_MAP_V_MOD6 = None
MESSINESS_MAP_V_MOD210 = None

# --- Signature Thresholds for v17.0 ---
# The v_mod210 'clean' score is much lower than v_mod6
CLEAN_THRESHOLD_V17 = 0.5  
# The v_mod210 'messy' score is slightly lower than v_mod6
MESSY_THRESHOLD_V17 = 30.0 
MAX_SIGNATURE_SEARCH_DEPTH = 4 # Ranks 2, 3, 4


def load_engine_data():
    """Loads v_mod6 (for v16 baseline) and v_mod210 (for v17 core)."""
    global MESSINESS_MAP_V_MOD6, MESSINESS_MAP_V_MOD210
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) data for baseline.")
            
        with open(MOD210_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD210 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod210 (Mod 210) data for new core.")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

# --- v16.0 Engine (Baseline: v_mod6 core + R2/R3/R4 fixes) ---
# NOTE: This function is complex because it calculates the full v16.0 prediction.
def get_v16_prediction(p_n, candidates, prime_list):
    
    # 1. Get the v11.0 ranked list
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score_v11 = (MESSINESS_MAP_V_MOD6.get(S_cand % 6, float('inf')) + 1.0) * gap_g_i
        vmod6_rate = MESSINESS_MAP_V_MOD6.get(S_cand % 6, float('inf'))
        candidate_scores.append((score_v11, q_i, vmod6_rate))

    candidate_scores.sort(key=lambda x: x[0])
    
    winner_v11_prime = candidate_scores[0][1]
    winner_v11_vmod6 = candidate_scores[0][2]
    
    prediction_v16 = winner_v11_prime # Default
    
    if winner_v11_vmod6 < 3.0: # If #1 is "Clean" (potential failure signature)
        for rank_index in range(1, 4): # Check Ranks 2, 3, and 4
            if rank_index >= len(candidate_scores): break
                
            next_candidate_vmod6 = candidate_scores[rank_index][2]
            
            if next_candidate_vmod6 > 20.0:
                prediction_v16 = candidate_scores[rank_index][1]
                break
                
    return prediction_v16

# --- v17.0 Engine (Challenger: v_mod210 core + R2/R3/R4 fixes) ---
def get_v17_prediction(p_n, candidates, prime_list):
    
    # 1. Get the v17.0 ranked list (v_mod210 core)
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        
        # New Core Signal: v_mod210 weighted score
        vmod210_rate = MESSINESS_MAP_V_MOD210.get(S_cand % 210, float('inf'))
        score_v17_weighted = (vmod210_rate + 1.0) * gap_g_i
        
        candidate_scores.append((score_v17_weighted, q_i, vmod210_rate))

    candidate_scores.sort(key=lambda x: x[0])
    
    winner_v17_prime = candidate_scores[0][1]
    winner_v17_vmod210 = candidate_scores[0][2]
    
    prediction_v17 = winner_v17_prime # Default
    
    # 2. Apply v17.0 Signature Logic (Ranks 2, 3, and 4)
    if winner_v17_vmod210 < CLEAN_THRESHOLD_V17: # If #1 is "Clean"
        for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH + 1): # Check Ranks 2, 3, and 4
            if rank_index >= len(candidate_scores): break
                
            next_candidate_vmod210 = candidate_scores[rank_index][2]
            
            if next_candidate_vmod210 > MESSY_THRESHOLD_V17: # AND the candidate is "Messy"
                prediction_v17 = candidate_scores[rank_index][1]
                break
                
    return prediction_v17
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
def run_PLR_v17_structural_ceiling_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Structural Ceiling' Test (v17.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Baseline: v16.0 (v_mod6 Core) at 75.94%")
    print(f"  - Challenger: v17.0 (v_mod210 Core) + R2/R3/R4 Fixes")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v16_baseline = 0
    total_successes_v17_new_champ = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v17_acc = (total_successes_v17_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v16_acc = (total_successes_v16_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v17.0 Acc: {v17_acc:.2f}% | v16.0 Acc: {v16_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        total_predictions += 1
        
        # 1. Get v16.0 Baseline Prediction
        prediction_v16 = get_v16_prediction(p_n, candidates, prime_list)
        if prediction_v16 == true_p_n_plus_1:
            total_successes_v16_baseline += 1
            
        # 2. Get v17.0 Challenger Prediction
        prediction_v17 = get_v17_prediction(p_n, candidates, prime_list)
        if prediction_v17 == true_p_n_plus_1:
            total_successes_v17_new_champ += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v17_acc = (total_successes_v17_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v16_acc = (total_successes_v16_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v17.0 Acc: {v17_acc:.2f}% | v16.0 Acc: {v16_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v17.0 'Structural Ceiling') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Total Correct (v16.0 Baseline): {total_successes_v16_baseline:,}")
    print(f"Total Correct (v17.0 Challenger): {total_successes_v17_new_champ:,}")
    
    print(f"\n  v16.0 'Chained Signature' (Baseline): {v16_acc:.2f}%")
    print(f"  v17.0 'Structural Ceiling' (New): {v17_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v17_acc - v16_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v17_acc > v16_acc:
        print("\n  [VERDICT: SUCCESS. STRUCTURAL CLEANLINESS WINS!]")
        print(f"  The new 'v17.0' engine's accuracy ({v17_acc:.2f}%) has")
        print(f"  achieved a new record, breaking the 75.94% barrier!")
        print("\n  This PROVES the final hypothesis:")
        print("  The structural advantage of the v_mod210 filter")
        print("  is superior to the simple reliability of the v_mod6 filter.")
    elif v17_acc < v16_acc:
        print("\n  [VERDICT: FALSIFIED. COMPLEXITY ADDS NOISE.]")
        print(f"  The new 'v17.0' engine's accuracy ({v17_acc:.2f}%) is")
        print(f"  not better than the v16.0 baseline ({v16_acc:.2f}%).")
        print("\n  This confirms the prediction that the structural noise")
        print("  of the v_mod210 filter outweighs its structural benefits.")
        print("  The v_mod6 filter is the predictive maximum.")
    else:
        print("\n  [VERDICT: TIE. THE CEILING IS CONFIRMED.]")
        print("  The two engines perform identically, confirming 75.94% as the final limit.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v17_structural_ceiling_test()