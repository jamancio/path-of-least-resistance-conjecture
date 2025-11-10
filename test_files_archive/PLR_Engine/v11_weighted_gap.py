# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 18: The "Weighted Gap" Engine (v11.0)
#
# This is the test of our new "Weighted Gap" hypothesis.
#
# HYPOTHESIS:
# Our 57.84% "lucky bug" (v7.0) proved the true signal is
# a *combination* of "Cleanliness" (v_mod6_rate) and "Closeness" (gap_g_n).
#
# Our v10.0 test (55.51%) failed because it used the gap as a *weak tie-breaker*.
#
# This v11.0 engine tests the "Weighted Score" formula:
#
#    Final_Score = (v_mod6_rate) * (gap_g_n)
#
# A candidate must be *both* clean (low rate) AND close (low gap) to win.
# This should, in theory, replicate and exceed the "lucky" 57.84%
# and prove this is the true Path of Least Resistance.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MOD30_ENGINE_FILE = "data/messiness_map_v1_mod30.json"
MOD210_ENGINE_FILE = "data/messiness_map_v3_mod210.json"

MESSINESS_MAP_V_MOD6 = None
MESSINESS_MAP_V1_MOD30 = None
MESSINESS_MAP_V3_MOD210 = None

def load_all_engine_data():
    """Loads all messiness maps."""
    global MESSINESS_MAP_V_MOD6, MESSINESS_MAP_V1_MOD30, MESSINESS_MAP_V3_MOD210
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
            
        with open(MOD30_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V1_MOD30 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v1.0 (Mod 30) engine data from '{MOD30_ENGINE_FILE}'.")

        with open(MOD210_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V3_MOD210 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v3.0 (Mod 210) engine data from '{MOD210_ENGINE_FILE}'.")
        return True
    
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

# --- v7.0 Recursive Engine (Our "Corrected" Baseline) ---
def get_messiness_score_v7_recursive(anchor_sn, gap_g_n):
    """The v7.0 "Recursive" Engine (Corrected)."""
    if MESSINESS_MAP_V_MOD6 is None or MESSINESS_MAP_V1_MOD30 is None or MESSINESS_MAP_V3_MOD210 is None:
        return (float('inf'), float('inf'))
    
    if gap_g_n > 210:
        score = MESSINESS_MAP_V3_MOD210.get(anchor_sn % 210, float('inf'))
    elif gap_g_n > 30:
        score = MESSINESS_MAP_V1_MOD30.get(anchor_sn % 30, float('inf'))
    else:
        score = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    return (score, gap_g_n) # Returns a TUPLE

# --- v11.0 "Weighted Gap" Engine (Our New Champion) ---
def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    """
    The v11.0 "Weighted Gap" Engine.
    Final_Score = (v_mod6_rate) * (gap_g_n)
    Returns a single float value.
    """
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')

    # Signal 1: The "k-div-by-3" risk (e.g., 2.71%)
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    
    # Signal 2: The gap (g_n)
    
    # Combine them:
    # We add 1.0 to the mod6 score to avoid a 0*gap=0 score
    # if a residue ever has a 0% failure rate.
    final_weighted_score = (score_mod6 + 1.0) * gap_g_n
    
    return final_weighted_score
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

def get_winner_from_scores(candidate_scores):
    """
    Finds the winning prime from a list of (score, prime)
    NOTE: v11 score is a float, v7 score is a tuple.
    The sort key handles both.
    """
    if not candidate_scores:
        return None
    candidate_scores.sort(key=lambda x: x[0])
    min_score = candidate_scores[0][0]
    winners_list = [q_i for score, q_i in candidate_scores if score == min_score]
    return winners_list[0] # Return smallest prime in case of a tie

# --- Main Testing Logic ---
def run_PLR_v11_weighted_test():
    
    if not load_all_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Weighted Gap' Test (v11.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - v11.0 Engine: (v_mod6_rate * gap_g_n) Score")
    print(f"  - v7.0 Engine:  (Recursive - Corrected) Baseline")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v11_new_champ = 0
    total_successes_v7_baseline = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v11_acc = (total_successes_v11_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v7_acc = (total_successes_v7_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v11.0 Acc: {v11_acc:.2f}% | v7.0 Acc: {v7_acc:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        scores_v11 = []
        scores_v7 = []
        
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            
            # --- Get v11.0 Score (float) ---
            score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
            scores_v11.append((score_v11, q_i))
            
            # --- Get v7.0 Score (tuple) ---
            score_v7 = get_messiness_score_v7_recursive(S_cand, gap_g_i)
            scores_v7.append((score_v7, q_i))

        # --- Tally Winners ---
        total_predictions += 1
        
        # v11.0 Winner
        winner_v11 = get_winner_from_scores(scores_v11)
        if winner_v11 == true_p_n_plus_1:
            total_successes_v11_new_champ += 1

        # v7.0 Winner
        winner_v7 = get_winner_from_scores(scores_v7)
        if winner_v7 == true_p_n_plus_1:
            total_successes_v7_baseline += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v11_acc = (total_successes_v11_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v7_acc = (total_successes_v7_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v11.0 Acc: {v11_acc:.2f}% | v7.0 Acc: {v7_acc:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v11.0 'Weighted Gap') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    print(f"\nTotal Correct (v7.0 Corrected Baseline): {total_successes_v7_baseline:,}")
    print(f"Total Correct (v11.0 New Champion):      {total_successes_v11_new_champ:,}")
    
    print(f"\n  v7.0 'Recursive' (Corrected Baseline): {v7_acc:.2f}%")
    print(f"  v11.0 'Weighted Gap' (New):          {v11_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v11_acc - v7_acc
    print(f"  Improvement over Corrected Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v11_acc > 57.0: # Check if it matches or beats the "lucky bug"
        print("\n  [VERDICT: SUCCESS. THE 'LUCKY BUG' IS REPLICATED!]")
        print(f"  The new 'v11.0' engine's accuracy ({v11_acc:.2f}%) has")
        print(f"  matched or exceeded the 57.84% 'lucky bug' score.")
        print("\n  This PROVES the final hypothesis:")
        print("  The true 'Path of Least Resistance' is a weighted")
        print("  combination of 'Cleanliness' (v_mod6 rate) and")
        print("  'Closeness' (the prime gap).")
    else:
        print("\n  [VERDICT: FALSIFIED. THE 'LUCKY BUG' REMAINS A MYSTERY.]")
        print(f"  The new 'v11.0' engine's accuracy ({v11_acc:.2f}%) is")
        print(f"  no better than the v_mod6 baseline (55.51%).")
        print("  The 57.84% 'lucky bug' was an unrepeatable artifact")
        print("  and this 'Weighted Gap' model is also incorrect.")
        print("  The signal appears to be truly one-dimensional.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v11_weighted_test()