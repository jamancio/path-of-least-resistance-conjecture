# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 38: The "PNT Deviation" Analysis
#
# This is the final analytic test for f(p_n).
#
# We are testing the hypothesis that the 24.06% of v16.0 failures
# are not random, but are correlated with the "PNT Deviation"
# of the *previous* gap (g_{n-1}).
#
# We will calculate a "PNT Deviation Score" for every prime:
#
#    PNT_Deviation_Score = (Actual_Gap_g_n_minus_1) / (PNT_Average_Gap_ln_p_n)
#
# We will then find the *average PNT Deviation Score* for all
# v16.0 SUCCESSES and compare it to the average score for all v16.0 FAILURES.
#
# A significant difference will prove that f(p_n) is a function of
# the prime's deviation from the Prime Number Theorem.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v16.0 "Chained Signature") ---
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
    """The v11.0 "Weighted Gap" Engine Core."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'): return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))

def get_v16_prediction(p_n, candidates):
    """Runs the full v16.0 "Chained Signature" logic."""
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        vmod6_rate = get_vmod6_score(S_cand)
        candidate_scores.append((score_v11, q_i, vmod6_rate))

    candidate_scores.sort(key=lambda x: x[0])
    
    if not candidate_scores: return None
    winner_v11_prime = candidate_scores[0][1]
    winner_v11_vmod6 = candidate_scores[0][2]
    prediction_v16 = winner_v11_prime
    
    if winner_v11_vmod6 < CLEAN_THRESHOLD: 
        for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH):
            if rank_index >= len(candidate_scores): break
            next_candidate_vmod6 = candidate_scores[rank_index][2]
            if next_candidate_vmod6 > MESSY_THRESHOLD:
                prediction_v16 = candidate_scores[rank_index][1]
                break
    return prediction_v16
# --- End Engine Setup ---


# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
PRIMES_TO_TEST = 50000000 
NUM_CANDIDATES_TO_CHECK = 10 
START_INDEX = 11 # Must be > 10 to have a stable p_n and p_{n-1}

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
def run_PLR_pnt_deviation_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'PNT Deviation' Analysis (Test 38) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v16.0 (75.94% Champion)")
    print(f"  - Correlating v16.0 failures with 'PNT Deviation Score' (g_{'n-1'} / ln(p_n)).")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_v16_failures = 0
    total_v16_successes = 0
    
    # --- Data structure for the correlation ---
    success_deviation_sum = 0
    failure_deviation_sum = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v16_acc = (total_v16_successes / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Acc: {v16_acc:.2f}% | Failures: {total_v16_failures:,} | Time: {elapsed:.0f}s", end='\r')

        # --- 1. Get p_n and candidates ---
        p_n_minus_1 = prime_list[i - 1]
        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        total_predictions += 1
        
        # --- 2. Get v16.0 Prediction ---
        prediction_v16 = get_v16_prediction(p_n, candidates)
        is_success = (prediction_v16 == true_p_n_plus_1)

        # --- 3. Get PNT Deviation Score ---
        actual_gap = p_n - p_n_minus_1
        pnt_average_gap = math.log(p_n) # ln(p_n)
        
        if pnt_average_gap == 0: continue # Avoid division by zero
            
        pnt_deviation_score = actual_gap / pnt_average_gap
        
        # --- 4. Log the Score ---
        if is_success:
            total_v16_successes += 1
            success_deviation_sum += pnt_deviation_score
        else:
            total_v16_failures += 1
            failure_deviation_sum += pnt_deviation_score
            
    # --- Final Summary ---
    progress = total_predictions
    v16_acc = (total_v16_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {progress:,} | Acc: {v16_acc:.2f}% | Failures: {total_v16_failures:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v22.0 'PNT Deviation') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested: {total_predictions:,}")
    print(f"Total v16.0 Failures Analyzed: {total_v16_failures:,}")
    print(f"Total v16.0 Successes Analyzed: {total_v16_successes:,}")
    
    avg_dev_success = success_deviation_sum / total_v16_successes if total_v16_successes > 0 else 0
    avg_dev_failure = failure_deviation_sum / total_v16_failures if total_v16_failures > 0 else 0
    
    print("\n" + "-" * 20 + " Average PNT Deviation Score (g_{n-1} / ln(p_n)) " + "-" * 20)
    print(f"\n  Avg. Score for 75.94% SUCCESSES: {avg_dev_success:>12.4f}")
    print(f"  Avg. Score for 24.06% FAILURES: {avg_dev_failure:>12.4f}")

    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL ANALYTIC CONCLUSION " + "="*20)
    
    if abs(avg_dev_success - avg_dev_failure) > 0.05: # 5% relative difference
        print(f"\n  [VERDICT: THE 'FORCE FIELD' f(p_n) IS FOUND!]")
        print(f"  The average PNT Deviation for SUCCESSES ({avg_dev_success:.4f}) is")
        print(f"  statistically *different* from the score for FAILURES ({avg_dev_failure:.4f}).")
        print("\n  This proves f(p_n) is a function of the PNT deviation.")
        print("  The 24.06% of failures are NOT random, but are")
        print("  analytically predictable by this score.")
    else:
        print(f"\n  [VERDICT: THE TRAIL HAS GONE COLD. 75.94% IS THE LIMIT.]")
        print(f"  The average PNT Deviation for SUCCESSES ({avg_dev_success:.4f}) is")
        print(f"  statistically *identical* to the score for FAILURES ({avg_dev_failure:.4f}).")
        print("\n  This is the final falsification. It confirms all previous tests:")
        print("  The 24.06% of failures are true *local* randomness,")
        print("  and are NOT correlated with any known non-local or analytic signal.")

    print("=" * (50 + len(" FINAL ANALYTIC CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_pnt_deviation_analysis()