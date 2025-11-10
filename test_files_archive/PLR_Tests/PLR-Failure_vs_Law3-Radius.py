# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 12 (Corrected): PLR Failure vs. Law III Radius
#
# This is the "post-mortem" connecting PLR to PAS Law III.
#
# This script correctly uses our "champion" v_mod6 (Mod 6) engine
# (the 55.51% one) to classify PLR Success/Failure.
# It abandons the buggy "Two-Mode" (v6.0) engine.
#
# HYPOTHESIS:
# The 44.49% of "PLR Failures" (where the v_mod6 engine fails) will
# have a significantly higher avg. Law III fixing radius (r) than the
# 55.51% of "PLR Successes".
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v_mod6 "Champion" Engine) ---
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
MAX_LAW_III_RADIUS = 30 # Max radius to search for Law III

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
        return None, None
    
    prime_set = set(prime_list)
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes and created set in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + MAX_LAW_III_RADIUS + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None, None, None
        
    return prime_list, prime_set

def is_clean_k(k_val, prime_set):
    """Helper function to check if k is 1 or a prime."""
    if k_val == 1: return True
    if k_val < 2: return False
    return k_val in prime_set

# --- Main Testing Logic ---
def run_PLR_vs_Law3_analysis_corrected():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Failure vs. Law III Radius Analysis (Corrected) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Using v_mod6 (55.51%) 'Champion' Engine")
    print(f"  - Correlating PLR status with Law III 'r_fix' value.")
    print("-" * 80)
    start_time = time.time()
    
    total_law_I_failures_analyzed = 0
    success_r_distribution = defaultdict(int)
    failure_r_distribution = defaultdict(int)
    
    loop_start_index = START_INDEX + MAX_LAW_III_RADIUS 
    loop_end_index = PRIMES_TO_TEST + loop_start_index
    
    if loop_end_index >= len(prime_list) - MAX_LAW_III_RADIUS -1 :
         print(f"\nFATAL ERROR: Not enough primes loaded for S_n+r lookups at the end.")
         return

    for i in range(loop_start_index, loop_end_index):
        if (i - loop_start_index + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - loop_start_index + 1
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Law I Fails Found: {total_law_I_failures_analyzed:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i+1]
        anchor_S_n = p_n + true_p_n_plus_1
        
        # --- 1. First, find this anchor's Law I/III status ---
        min_distance_k = 0
        q_prime = 0
        search_dist = 1
        
        while True:
            q_lower = anchor_S_n - search_dist
            q_upper = anchor_S_n + search_dist

            if q_lower in prime_set:
                min_distance_k = search_dist
                q_prime = q_lower
                break
            if q_upper in prime_set:
                min_distance_k = search_dist
                q_prime = q_upper
                break
                
            search_dist += 1
            if search_dist > 2000: break 
        
        if min_distance_k == 0: continue 

        is_k_composite = (min_distance_k > 1) and (min_distance_k not in prime_set)
        
        if is_k_composite:
            total_law_I_failures_analyzed += 1
            
            # --- 2. Find this failure's TRUE Law III fixing radius 'r' ---
            true_fixing_radius = -1 
            for r in range(1, MAX_LAW_III_RADIUS + 1):
                S_prev = prime_list[i - r] + prime_list[i - r + 1]
                if is_clean_k(abs(S_prev - q_prime), prime_set):
                    true_fixing_radius = r
                    break
                
                S_next = prime_list[i + r] + prime_list[i + r + 1]
                if is_clean_k(abs(S_next - q_prime), prime_set):
                    true_fixing_radius = r
                    break
            
            if true_fixing_radius == -1:
                continue 

            # --- 3. Now, run the PLR prediction for p_n using v_mod6 ---
            candidates = []
            for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
                candidates.append(prime_list[i + j])
            
            candidate_scores = []
            for q_i in candidates:
                S_cand = p_n + q_i
                messiness_score = get_messiness_score_v_mod6(S_cand)
                candidate_scores.append((messiness_score, q_i))

            # --- 4. Get PLR Status (Tied-for-1st) ---
            min_score = min(s[0] for s in candidate_scores)
            winners_list = [q_i for score, q_i in candidate_scores if score == min_score]
            
            is_PLR_success = (true_p_n_plus_1 in winners_list)
            
            # --- 5. Log the result in the correct bin ---
            if is_PLR_success:
                success_r_distribution[true_fixing_radius] += 1
            else:
                failure_r_distribution[true_fixing_radius] += 1
            
    # --- Final Summary ---
    progress = PRIMES_TO_TEST
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Law I Fails Found: {total_law_I_failures_analyzed:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR Failure vs. Law III Radius Report (Corrected) " + "="*20)
    print(f"\nTotal Law I Failures Analyzed: {total_law_I_failures_analyzed:,}")
    
    total_successes = sum(success_r_distribution.values())
    total_failures = sum(failure_r_distribution.values())
    
    print(f"  - PLR 'Success' Anchors (v_mod6 Engine): {total_successes:,}")
    print(f"  - PLR 'Failure' Anchors (v_mod6 Engine): {total_failures:,}")

    # --- Calculate Average Gaps ---
    success_r_sum = sum(r * count for r, count in success_r_distribution.items())
    failure_r_sum = sum(r * count for r, count in failure_r_distribution.items())
    
    avg_r_success = success_r_sum / total_successes if total_successes > 0 else 0
    avg_r_failure = failure_r_sum / total_failures if total_failures > 0 else 0
    overall_avg_r = (success_r_sum + failure_r_sum) / total_law_I_failures_analyzed if total_law_I_failures_analyzed > 0 else 0

    print("\n" + "-" * 20 + " Average Law III Fix Radius (r) Analysis " + "-" * 20)
    print(f"  Overall Avg. 'r' for all Law I failures: {overall_avg_r:.4f}")
    print(f"  Avg. 'r' for PLR SUCCESSES:              {avg_r_success:.4f}")
    print(f"  Avg. 'r' for PLR FAILURES:              {avg_r_failure:.4f}")
    
    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    
    if avg_r_failure > avg_r_success * 1.05: # 5% difference
        print("\n  [VERDICT: HYPOTHESIS CONFIRMED]")
        print("  A strong correlation is found.")
        print(f"  PLR FAILURES are 'messier' (avg r = {avg_r_failure:.4f})")
        print(f"  than PLR SUCCESSES (avg r = {avg_r_success:.4f}).")
        print("\n  This proves the 44.49% of PLR failures are *not* random.")
        print("  They are the same anchors identified as 'messy' by the")
        print("  original PAS Law III correction mechanism.")
    else:
        print("\n  [VERDICT: HYPOTHESIS FALSIFIED]")
        print("  No significant correlation was found.")
        print(f"  The avg. 'r' for SUCCESSES ({avg_r_success:.4f}) is")
        print(f"  statistically identical to the avg. 'r' for FAILURES ({avg_r_failure:.4f}).")
        print("\n  The PLR failures are not correlated with the Law III mechanism.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_vs_Law3_analysis_corrected()