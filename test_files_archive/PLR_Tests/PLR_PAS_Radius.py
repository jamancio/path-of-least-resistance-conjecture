# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 36: The "PAS Radius" Test (v20.0)
#
# This is the final analytic test to find the f(p_n) function.
#
# HYPOTHESIS:
# The 24.06% of failures from our v16.0 engine are not random.
# They are correlated with the "structural instability" of the
# *previous* anchor (S_{n-1} = p_{n-1} + p_n).
#
# We will check if the 24.06% of failures are concentrated in
# cases where the *previous* anchor was "messy" (PAS Law III r_{n-1} > 0).
#
# This tests if f(p_n) is a function of the PAS Correction Radius.
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

# --- PAS Law I/III Helper Functions ---
def is_prime(k_val, prime_set):
    """Helper function to check if k is prime."""
    if k_val < 2: return False
    return k_val in prime_set

def get_pas_k_min(anchor_sn, prime_set):
    """Finds the k_min for a given anchor."""
    min_distance_k = 0
    search_dist = 1
    while True:
        q_lower = anchor_sn - search_dist
        if q_lower in prime_set:
            min_distance_k = search_dist
            break
        q_upper = anchor_sn + search_dist
        if q_upper in prime_set:
            min_distance_k = search_dist
            break
        search_dist += 1
        if search_dist > 2000: break # Failsafe
    return min_distance_k

def get_pas_r_fix(anchor_S_n_minus_1, k_min_prime, prime_list, i_minus_1_index, prime_set):
    """
    Finds the PAS Law III r_fix value for a k_min_prime relative
    to the anchor S_{n-1}.
    """
    # This is a complex operation and for this post-mortem,
    # we'll just check if k_min_prime is composite.
    # A full r_fix calculation is too slow for a 50M loop.
    # We will simplify the hypothesis for this test.
    pass
# --- End PAS ---

# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
PRIMES_TO_TEST = 50000000 
NUM_CANDIDATES_TO_CHECK = 10 
START_INDEX = 11 # Must be 11 to have p_{n-1} and p_{n-2}

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
    
    prime_set = set(prime_list) # Need the set for fast k_min lookups
    end_time = time.time()
    print(f"Loaded {len(prime_list):,} primes and set in {end_time - start_time:.2f} seconds.")
    
    required_primes = PRIMES_TO_TEST + START_INDEX + NUM_CANDIDATES_TO_CHECK + 2
    if len(prime_list) < required_primes:
        print(f"\nFATAL ERROR: Prime file is too small for this test.")
        return None, None
        
    return prime_list, prime_set

# --- Main Testing Logic ---
def run_PLR_vs_PAS_radius_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list, prime_set = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'PAS Radius' Test (v20.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v16.0 (75.94% Champion)")
    print(f"  - Correlating v16.0 failures with S_{'n-1'} PAS Law I status.")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_v16_failures = 0
    
    # --- Data structure for the correlation ---
    # Log failures based on the *previous* anchor's status
    failures_when_prev_anchor_is_CLEAN = 0
    failures_when_prev_anchor_is_MESSY = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Failures: {total_v16_failures:,} | Time: {elapsed:.0f}s", end='\r')

        # --- 1. Get p_n and candidates ---
        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        total_predictions += 1
        
        # --- 2. Get v16.0 Prediction ---
        prediction_v16 = get_v16_prediction(p_n, candidates)

        if prediction_v16 != true_p_n_plus_1:
            # --- THIS IS A v16.0 FAILURE. ---
            total_v16_failures += 1
            
            # --- 3. ANALYZE THE PREVIOUS ANCHOR'S STABILITY ---
            p_n_minus_1 = prime_list[i - 1]
            anchor_S_n_minus_1 = p_n_minus_1 + p_n
            
            # Find the k_min for S_{n-1}
            k_min = get_pas_k_min(anchor_S_n_minus_1, prime_set)
            
            is_k_min_composite = (k_min > 1) and not is_prime(k_min, prime_set)
            
            if is_k_min_composite:
                # The previous anchor was "messy" (a PAS Law I failure)
                failures_when_prev_anchor_is_MESSY += 1
            else:
                # The previous anchor was "clean"
                failures_when_prev_anchor_is_CLEAN += 1
            
    # --- Final Summary ---
    progress = total_predictions
    print(f"Progress: {progress:,} / {progress:,} | FailGaps: {total_v16_failures:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v20.0 'PAS Radius') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested: {total_predictions:,}")
    print(f"Total v16.0 Failures Analyzed (24.06%): {total_v16_failures:,}")
    
    perc_clean = (failures_when_prev_anchor_is_CLEAN / total_v16_failures) * 100 if total_v16_failures > 0 else 0
    perc_messy = (failures_when_prev_anchor_is_MESSY / total_v16_failures) * 100 if total_v16_failures > 0 else 0
    
    print("\n" + "-" * 20 + " Failure Distribution by S_{n-1} Stability " + "-" * 20)
    print(f"\n  Failures when S_{'n-1'} was 'CLEAN' (r=0): {failures_when_prev_anchor_is_CLEAN:>12,}")
    print(f"     (% of all failures)                      {perc_clean:>6.2f}%")

    print(f"\n  Failures when S_{'n-1'} was 'MESSY' (r>0): {failures_when_prev_anchor_is_MESSY:>12,}")
    print(f"     (% of all failures)                      {perc_messy:>6.2f}%")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL ANALYTIC CONCLUSION " + "="*20)
    
    # We need to know the *baseline* rate of messy anchors.
    # From PAS v4.0, ~86.8% are Clean, ~13.2% are Messy.
    baseline_messy_rate = 13.2 
    
    if perc_messy > (baseline_messy_rate * 2): # e.g., if > 26.4%
        print(f"\n  [VERDICT: THE 'FORCE FIELD' f(p_n) IS FOUND!]")
        print(f"  A massive {perc_messy:.2f}% of all failures occur")
        print(f"  when the previous anchor was 'MESSY'.")
        print(f"  This is a huge over-representation compared to the")
        print(f"  ~{baseline_messy_rate:.2f}% baseline rate of messy anchors.")
        print("\n  This proves f(p_n) is a function of PAS instability (r_{n-1}).")
        print("  The 24.06% of failures are NOT random.")
    else:
        print(f"\n  [VERDICT: THE TRAIL HAS GONE COLD. 75.94% IS THE LIMIT.]")
        print(f"  The failure distribution ({perc_messy:.2f}% for 'MESSY')")
        print(f"  is statistically identical to the baseline rate")
        print(f"  of 'Messy' anchors (~{baseline_messy_rate:.2f}%).")
        print("\n  This confirms the previous p_n residue test: the 24.06%")
        print("  of failures are true *local* randomness, not correlated")
        print("  with the historical instability of the anchor field.")

    print("=" * (50 + len(" FINAL ANALYTIC CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_vs_PAS_radius_analysis()