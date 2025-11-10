# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 19: v11.0 Failure Analysis (v12.0)
#
# This is a "post-mortem" analysis of our 60.49% champion v11.0 engine.
#
# Our goal is to dissect the 39.51% of failures and categorize them.
# A "failure" occurs when a "fake" candidate's score is lower than
# the "true" prime's score.
#
#    Final_Score = (v_mod6_rate + 1.0) * (gap_g_n)
#
# We will check *why* the true prime lost to the fake winner:
#
# 1. SCENARIO A ("Lost on Closeness"):
#    - True_vmod6_Score == Fake_vmod6_Score
#    - The "Cleanliness" was a TIE, but the fake was closer (smaller gap).
#
# 2. SCENARIO B ("Lost on Cleanliness"):
#    - True_vmod6_Score > Fake_vmod6_Score
#    - The true prime was genuinely "messier" than the fake,
#      so the engine logically (but incorrectly) chose the cleaner path.
#
# 3. SCENARIO C ("Lost on Gap, Despite Being Cleaner"):
#    - True_vmod6_Score < Fake_vmod6_Score
#    - The true prime was *cleaner*, but its gap was *so massive*
#      that it still lost the final weighted score.
#
# This analysis will tell us if 100% is possible, or if the
# "Path of Least Resistance" is not always the true path.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v11.0 "Weighted Gap") ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

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
    """
    The v11.0 "Weighted Gap" Engine.
    Final_Score = (v_mod6_rate + 1.0) * (gap_g_n)
    Returns a single float value.
    """
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')

    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    
    # Handle 'inf' scores to avoid math errors
    if score_mod6 == float('inf'):
        return float('inf')
        
    final_weighted_score = (score_mod6 + 1.0) * gap_g_n
    return final_weighted_score

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
def run_PLR_v11_failure_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR v11.0 Failure Analysis for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v11.0 (v_mod6_rate * gap_g_n)")
    print(f"  - Categorizing all 39.51% of failures...")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes = 0
    total_failures = 0
    
    # --- Failure Category Counters ---
    scenario_A_failures = 0 # Lost on Closeness (v_mod6 scores were tied)
    scenario_B_failures = 0 # Lost on Cleanliness (True prime was "messier")
    scenario_C_failures = 0 # Lost on Gap (True prime was "cleaner" but too far)
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v11_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Acc: {v11_acc:.2f}% | Failures: {total_failures:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            
            score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
            candidate_scores.append((score_v11, q_i))

        # --- Tally Winners ---
        total_predictions += 1
        
        candidate_scores.sort(key=lambda x: x[0])
        min_score = candidate_scores[0][0]
        winners_list = [q_i for score, q_i in candidate_scores if score == min_score]
        winner = winners_list[0] # Smallest prime in case of a tie

        if winner == true_p_n_plus_1:
            total_successes += 1
        else:
            # --- THIS IS A FAILURE. ANALYZE IT. ---
            total_failures += 1
            
            # 1. Get True Prime's data
            true_anchor = p_n + true_p_n_plus_1
            true_gap = true_p_n_plus_1 - p_n
            true_vmod6 = get_vmod6_score(true_anchor)

            # 2. Get Fake Winner's data
            fake_anchor = p_n + winner
            fake_gap = winner - p_n
            fake_vmod6 = get_vmod6_score(fake_anchor)
            
            # 3. Categorize the failure
            if true_vmod6 == fake_vmod6:
                scenario_A_failures += 1
            elif true_vmod6 > fake_vmod6:
                scenario_B_failures += 1
            else: # true_vmod6 < fake_vmod6
                scenario_C_failures += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v11_acc = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Acc: {v11_acc:.2f}% | Failures: {total_failures:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v11.0) FAILURE ANALYSIS REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"  - Total SUCCESSES: {total_successes:,} ({v11_acc:.2f}%)")
    print(f"  - Total FAILURES:  {total_failures:,} ({(100-v11_acc):.2f}%)")
    
    print("\n" + "-" * 20 + " Analysis of the 39.51% Failures " + "-" * 20)
    
    perc_A = (scenario_A_failures / total_failures) * 100 if total_failures > 0 else 0
    perc_B = (scenario_B_failures / total_failures) * 100 if total_failures > 0 else 0
    perc_C = (scenario_C_failures / total_failures) * 100 if total_failures > 0 else 0
    
    print(f"\n  SCENARIO A ('Lost on Closeness'): {scenario_A_failures:>12,}")
    print(f"     (True & Fake had same v_mod6 score)     {perc_A:>6.2f}% of failures")

    print(f"\n  SCENARIO B ('Lost on Cleanliness'): {scenario_B_failures:>11,}")
    print(f"     (True prime was 'messier' than fake)  {perc_B:>6.2f}% of failures")
    
    print(f"\n  SCENARIO C ('Lost on Gap'):         {scenario_C_failures:>12,}")
    print(f"     (True prime was 'cleaner' but too far) {perc_C:>6.2f}% of failures")

    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    print("\n  This table shows the *exact composition* of our failures.")
    
    if (scenario_A_failures + scenario_C_failures) > scenario_B_failures:
        print("\n  [VERDICT: 'PATH OF LEAST RESISTANCE' IS NOT ALWAYS TRUE PATH]")
        print("  The majority of failures are from Scenarios A and C.")
        print("  This means the engine is working *correctly*, but the")
        print("  true prime *is not* always the 'closest-cleanest' candidate.")
        print("  This suggests 60.49% is the 'hard dead end' for this model.")
    else:
        print("\n  [VERDICT: 'CLEANLINESS' SIGNAL IS STILL FLAWED]")
        print("  The majority of failures are from Scenario B.")
        print("  This means our `v_mod6` signal is still too simple.")
        print("  The engine is being 'deceived' by messy true anchors,")
        print("  which implies a *smarter 'Cleanliness' filter* is needed")
        print("  to break the 60.49% barrier.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v11_failure_analysis()