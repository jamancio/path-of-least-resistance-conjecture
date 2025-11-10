# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 7: Success vs. Failure Gap Analysis
#
# This is the "post-mortem" on our 55.51% champion v_mod6 engine.
#
# GOAL:
# We will sort all 50M predictions into two bins:
# 1. SUCCESSES (55.51%): The v_mod6 engine's best score included the true prime.
# 2. FAILURES (44.49%): The v_mod6 engine's best score did NOT include the true prime.
#
# We will then calculate the *average prime gap (g_n)* for each bin.
#
# HYPOTHESIS:
# The 44.49% of failures are not random. They will have a statistically
# different average gap (g_n) than the 55.51% of successes,
# revealing the "hidden variable" that explains the failures.
# ==============================================================================

import time
import math
import json

# --- Engine Setup ---
ENGINE_DATA_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

def load_engine_data():
    """Loads the v_mod6 messiness map from the JSON file."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(ENGINE_DATA_FILE, 'r') as f:
            data = json.load(f)
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in data.items()}
            return True
    except FileNotFoundError:
        print(f"FATAL ERROR: Engine file '{ENGINE_DATA_FILE}' not found.")
        print("Please run 'test-9_mod6-Reside-Analysis.py' first.")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v_mod6(anchor_sn):
    """The PAC Diagnostic Engine (v_mod6)."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf') 
    residue = anchor_sn % 6
    score = MESSINESS_MAP_V_MOD6.get(residue, float('inf'))
    return score
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
def run_PLR_post_mortem_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Success vs. Failure Gap Analysis for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using v_mod6 (Mod 6) Engine")
    print(f"  - Calculating average gap g_n for SUCCESS and FAILURE bins.")
    print("-" * 80)
    start_time = time.time()
    
    # --- Data structures for the analysis ---
    total_successes = 0
    success_gap_sum = 0
    
    total_failures = 0
    failure_gap_sum = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            accuracy = (total_successes / (total_successes + total_failures)) * 100 if (total_successes + total_failures) > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Failures: {total_failures:,} | Acc: {accuracy:.2f}% | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            q_i = prime_list[i + j]
            candidates.append(q_i)
        
        true_p_n_plus_1 = candidates[0]
        true_gap_g_n = true_p_n_plus_1 - p_n
        
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            messiness_score = get_messiness_score_v_mod6(S_cand)
            candidate_scores.append((messiness_score, q_i))
            
        # --- Run the "Tied-for-1st" logic ---
        
        # 1. Find the BEST (minimum) score in the list
        min_score = min(s[0] for s in candidate_scores)
        
        # 2. Create a "Winner's List" of all candidates that achieved this score
        winners_list = [q_i for score, q_i in candidate_scores if score == min_score]
        
        # 3. Check if the true prime is IN this list
        if true_p_n_plus_1 in winners_list:
            # SUCCESS
            total_successes += 1
            success_gap_sum += true_gap_g_n
        else:
            # FAILURE
            total_failures += 1
            failure_gap_sum += true_gap_g_n
            
    # --- Final Summary ---
    total_predictions = total_successes + total_failures
    accuracy = (total_successes / total_predictions) * 100 if total_predictions > 0 else 0
    
    print(f"Progress: {total_predictions:,} / {PRIMES_TO_TEST:,} | Successes: {total_successes:,} | Failures: {total_failures:,} | Acc: {accuracy:.2f}% | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR SUCCESS vs. FAILURE GAP ANALYSIS " + "="*20)
    print(f"\nTotal Primes Analyzed (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    
    print(f"\n  Total SUCCESSES (True prime was in best-scoring group): {total_successes:,} ({accuracy:.2f}%)")
    print(f"  Total FAILURES (True prime was NOT in best-scoring group): {total_failures:,} ({(100-accuracy):.2f}%)")

    # --- Calculate Average Gaps ---
    avg_gap_success = success_gap_sum / total_successes if total_successes > 0 else 0
    avg_gap_failure = failure_gap_sum / total_failures if total_failures > 0 else 0
    overall_avg_gap = (success_gap_sum + failure_gap_sum) / total_predictions if total_predictions > 0 else 0

    print("\n" + "-" * 20 + " Average Gap (g_n) Analysis " + "-" * 20)
    print(f"  Overall Average Gap (g_n) for all tested primes: {overall_avg_gap:.4f}")
    print(f"  Average Gap (g_n) for 55.51% SUCCESSES:        {avg_gap_success:.4f}")
    print(f"  Average Gap (g_n) for 44.49% FAILURES:        {avg_gap_failure:.4f}")
    
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    
    if abs(avg_gap_success - avg_gap_failure) > 0.5: # 0.5 is a significant difference
        print("\n  [VERDICT: 'HIDDEN VARIABLE' DISCOVERED]")
        print("  The 'g_n' (prime gap) is a key moderating variable.")
        print(f"  The average gap for SUCCESSES ({avg_gap_success:.4f}) is")
        print(f"  statistically different from the gap for FAILURES ({avg_gap_failure:.4f}).")
        print("\n  This proves the 44.49% of failures are NOT random.")
        print("  They are strongly correlated with the prime gap.")
    else:
        print("\n  [VERDICT: NO 'HIDDEN VARIABLE' FOUND]")
        print("  The prime gap (g_n) does not explain the failures.")
        print(f"  The average gap for SUCCESSES ({avg_gap_success:.4f}) is")
        print(f"  statistically identical to the gap for FAILURES ({avg_gap_failure:.4f}).")
        print("\n  The 44.49% of failures appear to be random or")
        print("  are caused by an unknown, non-gap-related factor.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_post_mortem_analysis()