# ==============================================================================
# PLR ANALYSIS - TEST 29: Density Factor (p_n Residue)
#
# This script analyzes the final 24.06% of failures from the v16.0 engine.
#
# HYPOTHESIS:
# The failures are concentrated in specific p_n % 30 residue classes,
# implying a structural/density constraint that creates the failure.
#
# Logic: Run v16.0 logic. On every failure, log the p_n % 30 residue.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v16.0 Chained Signature) ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# --- Signature Thresholds for v16.0 ---
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

# --- Full v16.0 Prediction Logic ---
def get_v16_prediction(p_n, candidates):
    
    # 1. Get the v11.0 ranked list
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        vmod6_rate = get_vmod6_score(S_cand)
        candidate_scores.append((score_v11, q_i, vmod6_rate))

    candidate_scores.sort(key=lambda x: x[0])
    
    winner_v11_prime = candidate_scores[0][1]
    winner_v11_vmod6 = candidate_scores[0][2]
    
    prediction_v16 = winner_v11_prime # Default
    
    # 2. Apply Chained Signature Logic (R2, R3, R4)
    if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean" (potential failure signature)
        for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH + 1):
            if rank_index >= len(candidate_scores): break
                
            next_candidate_vmod6 = candidate_scores[rank_index][2]
            
            if next_candidate_vmod6 > MESSY_THRESHOLD:
                # Prediction is the first 'Messy' candidate found
                prediction_v16 = candidate_scores[rank_index][1]
                break
                
    return prediction_v16

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
def run_PLR_pn_residue_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR p_n Residue Analysis (Test 29) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v16.0 (75.94% Champion)")
    print(f"  - Analyzing Failures by p_n % 30 Residue...")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_failures = 0
    # Dictionary: {residue: failure_count}
    pn_residue_failure_counts = defaultdict(int) 
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | Failures: {total_failures:,} | Time: {elapsed:.0f}s", end='\r')

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        total_predictions += 1
        
        # 1. Get the v16.0 Prediction
        prediction_v16 = get_v16_prediction(p_n, candidates)

        if prediction_v16 != true_p_n_plus_1:
            # --- THIS IS A v16.0 FAILURE. ANALYZE THE STARTING POINT. ---
            total_failures += 1
            
            # 2. Log the p_n % 30 residue
            pn_residue = p_n % 30
            pn_residue_failure_counts[pn_residue] += 1
            
    # --- Final Summary ---
    print(f"Progress: {total_predictions:,} / {PRIMES_TO_TEST:,} | Failures: {total_failures:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " v16.0 FAILURE DISTRIBUTION BY p_n % 30 RESIDUE " + "="*20)
    print(f"\nTotal Primes Tested: {total_predictions:,}")
    print(f"Total Failures Analyzed (24.06%): {total_failures:,}")
    
    # Process and sort data
    residue_data = []
    for residue in range(30):
        if residue % 6 != 1: continue # Only check valid prime residues
        
        count = pn_residue_failure_counts.get(residue, 0)
        percentage = (count / total_failures) * 100
        
        residue_data.append((residue, count, percentage))
    
    # Sort by count (descending)
    residue_data.sort(key=lambda x: x[1], reverse=True)
    
    print("\n" + "-" * 20 + " Failure Distribution (Only Prime Residues of 30) " + "-" * 20)
    print(f"\n{'p_n % 30 Residue':<20} | {'Failure Count':<15} | {'% of All Failures':<25}")
    print("-" * 60)
    
    total_failure_perc = 0
    for residue, count, percentage in residue_data:
        total_failure_perc += percentage
        print(f"{residue:<20} | {count:<15,} | {percentage:>24.2f}%")
        
    print("-" * 60)
    print(f"Total Percentage Logged: {total_failure_perc:.2f}%")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL ANALYTIC CONCLUSION " + "="*20)
    print("\n  We are looking for a highly non-uniform distribution.")
    print("  If the distribution is uniform (~12.5% per residue),")
    print("  it confirms the failure is due to *local* randomness.")

    print("=" * (50 + len(" FINAL ANALYTIC CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_pn_residue_analysis()