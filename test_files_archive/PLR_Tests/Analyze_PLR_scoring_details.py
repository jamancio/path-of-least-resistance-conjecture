# ==============================================================================
# PLR SCORING ANALYSIS
#
# This is not a test, but a detailed *analyzer*.
#
# It runs the 'v_mod6' (55.51%) and 'v1.0' (18.57%) engines in parallel
# for a small number of primes and prints the *entire* scoring process
# for each candidate.
#
# This will show us *why* the v_mod6 engine is so much more accurate.
# ==============================================================================

import time
import math
import json

# --- Engine Setup ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# v1.0 (Mod 30) Engine Data (Hard-coded from test-3-result.txt)
# Score = Failure Rate % (approximated from total counts)
# We use the raw failure counts as the "Messiness Score"
MESSINESS_MAP_V1_MOD30 = {
    0: 9907,    1: float('inf'), 2: 654113,  3: float('inf'), 4: 431661,
    5: float('inf'), 6: 171547,  7: float('inf'), 8: 662464,  9: float('inf'),
    10: 751163, 11: float('inf'), 12: 199190, 13: float('inf'), 14: 424448,
    15: float('inf'), 16: 426340, 17: float('inf'), 18: 200139, 19: float('inf'),
    20: 749951, 21: float('inf'), 22: 661166, 23: float('inf'), 24: 171854,
    25: float('inf'), 26: 430955, 27: float('inf'), 28: 654709, 29: float('inf')
} #

def load_mod6_engine_data():
    """Loads the v_mod6 messiness map from the JSON file."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            data = json.load(f)
            # We need the *raw failure counts* from test-9, not the rate,
            # to be comparable to the mod 30 counts.
            # Let's assume test-9 saved {residue: failure_rate}
            # For this analysis, we'll just use the rates.
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in data.items()}
            return True
    except FileNotFoundError:
        print(f"FATAL ERROR: Engine file '{MOD6_ENGINE_FILE}' not found.")
        print("Please run 'test-9_mod6-Reside-Analysis.py' first.")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v_mod6(anchor_sn):
    """The PAC Diagnostic Engine (v_mod6)."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf') 
    residue = anchor_sn % 6
    score = MESSINESS_MAP_V_MOD6.get(residue, float('inf'))
    return score

def get_messiness_score_v1_mod30(anchor_sn):
    """The PAC Diagnostic Engine (v1.0 - Mod 30)."""
    residue = anchor_sn % 30
    score = MESSINESS_MAP_V1_MOD30.get(residue, float('inf'))
    return score
# --- End Engine Setup ---


# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
# Let's analyze the first 100 testable primes
PRIMES_TO_ANALYZE = 100 
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
    
    required_primes = PRIMES_TO_ANALYZE + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None
        
    return prime_list

# --- Main Testing Logic ---
def run_PLR_scoring_analysis():
    
    if not load_mod6_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\n--- Starting PLR Scoring Analysis for {PRIMES_TO_ANALYZE} Primes ---")
    print("-" * 80)
    
    total_predictions = 0
    total_successes_v_mod6 = 0
    total_successes_v1_mod30 = 0
    
    loop_end_index = PRIMES_TO_ANALYZE + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        print(f"\n--- Analyzing p_n = {p_n} (True next prime is {true_p_n_plus_1}) ---")
        print(f"{'Candidate (q_i)':<18} | {'Anchor (S_cand)':<15} | {'v_mod6 Score':<15} | {'v1.0 (Mod 30) Score':<20}")
        print("-" * 72)
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            q_i = prime_list[i + j]
            candidates.append(q_i)
        
        candidate_scores_v_mod6 = []
        candidate_scores_v1_mod30 = []
        
        for q_i in candidates:
            S_cand = p_n + q_i
            
            # Get scores from both engines
            score_v_mod6 = get_messiness_score_v_mod6(S_cand)
            score_v1_mod30 = get_messiness_score_v1_mod30(S_cand)
            
            candidate_scores_v_mod6.append((score_v_mod6, q_i))
            candidate_scores_v1_mod30.append((score_v1_mod30, q_i))
            
            # Print the detailed log line
            is_true_str = "(True)" if q_i == true_p_n_plus_1 else ""
            print(f"{q_i:<18} {is_true_str:<8} | {S_cand:<15} | {score_v_mod6:<15.4f} | {score_v1_mod30:<20,}")

        # --- Find winners and tally ---
        total_predictions += 1
        
        # v_mod6 winner
        candidate_scores_v_mod6.sort(key=lambda x: x[0])
        best_score_mod6, predicted_mod6 = candidate_scores_v_mod6[0]
        if predicted_mod6 == true_p_n_plus_1:
            total_successes_v_mod6 += 1
            print(f"  > v_mod6 Prediction:   {predicted_mod6} (Score: {best_score_mod6:.2f}) -> [SUCCESS]")
        else:
            print(f"  > v_mod6 Prediction:   {predicted_mod6} (Score: {best_score_mod6:.2f}) -> [FAILURE]")

        # v1_mod30 winner
        candidate_scores_v1_mod30.sort(key=lambda x: x[0])
        best_score_mod30, predicted_mod30 = candidate_scores_v1_mod30[0]
        if predicted_mod30 == true_p_n_plus_1:
            total_successes_v1_mod30 += 1
            print(f"  > v1.0 (Mod 30) Pred: {predicted_mod30} (Score: {best_score_mod30:,}) -> [SUCCESS]")
        else:
            print(f"  > v1.0 (Mod 30) Pred: {predicted_mod30} (Score: {best_score_mod30:,}) -> [FAILURE]")

            
    # --- Final Summary ---
    print("\n" + "="*20 + " SCORING ANALYSIS SUMMARY " + "="*20)
    print(f"\nTotal Primes Analyzed (p_n): {total_predictions:,}")
    
    acc_v_mod6 = (total_successes_v_mod6 / total_predictions) * 100 if total_predictions > 0 else 0
    acc_v1_mod30 = (total_successes_v1_mod30 / total_predictions) * 100 if total_predictions > 0 else 0
    
    print(f"\n  v_mod6 (Mod 6) Accuracy:      {acc_v_mod6:.2f}% ({total_successes_v_mod6}/{total_predictions})")
    print(f"  v1.0 (Mod 30) Accuracy:     {acc_v1_mod30:.2f}% ({total_successes_v1_mod30}/{total_predictions})")
    
    print("\nReview the log above to see *why* the scores differed.")

if __name__ == "__main__":
    run_PLR_scoring_analysis()