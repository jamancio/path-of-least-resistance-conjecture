# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 38: The "Forensic Analyzer"
#
# (Corrected Version - v1.1)
#
# This script is a "black box recorder" to find the first 20 failures
# of our v16.0 champion and print a detailed "Case File" for each one.
#
# CORRECTION (v1.1):
# - Fixed a "ValueError: too many values to unpack" in the
#   get_v16_final_decision function. The function now correctly
#   unpacks the 4-item tuple (score, prime, vmod6_rate, gap)
#   that the main loop creates.
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
    # Add 1.0 to avoid 0*gap issues and normalize scoring
    return (score_mod6 + 1.0) * gap_g_n

def get_vmod6_score(anchor_sn):
    """Helper to get *only* the v_mod6 rate."""
    if MESSINESS_MAP_V_MOD6 is None: return float('inf')
    return MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))

def get_v16_final_decision(p_n, candidates_ranked_list):
    """
    Runs the v16.0 logic and returns the final prediction AND the reason.
    'candidates_ranked_list' is a list of 4-item tuples.
    """
    if not candidates_ranked_list: 
        return None, "No candidates"
        
    # --- THIS IS THE FIX (v1.1) ---
    # Get v11.0 winner data (Unpack all 4 items)
    v11_score, winner_v11_prime, winner_v11_vmod6, _ = candidates_ranked_list[0]
    
    final_prediction = winner_v11_prime # Default
    decision_reason = f"Defaulted to v11.0 Winner (Score: {v11_score:.2f})"
    
    # Run v16.0 "Signature" Logic
    if winner_v11_vmod6 < CLEAN_THRESHOLD: # If #1 is "Clean"
        for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH): # Ranks 2, 3, 4
            if rank_index >= len(candidates_ranked_list): break
            
            # --- THIS IS THE FIX (v1.1) ---
            # Get data for the 'Messy' suspect (Unpack all 4 items)
            suspect_score, suspect_prime, suspect_vmod6, _ = candidates_ranked_list[rank_index]
            
            if suspect_vmod6 > MESSY_THRESHOLD:
                # *** OVERRIDE ***
                final_prediction = suspect_prime
                decision_reason = f"TRIGGERED RANK {rank_index+1} OVERRIDE (Clean #1 vs. Messy #{rank_index+1})"
                break
                
    return final_prediction, decision_reason
# --- End Engine Setup ---

# --- Configuration ---
PRIME_INPUT_FILE = "prime/primes_100m.txt"
PRIMES_TO_TEST = 50000000 # Max primes to search
NUM_CANDIDATES_TO_CHECK = 10 
START_INDEX = 10 
FAILURES_TO_FIND = 20 # Stop after finding this many failures

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
def run_forensic_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Forensic Analyzer' (Test 38 v1.1)...")
    print(f"  - Engine: v16.0 (75.94% Champion)")
    print(f"  - Searching for first {FAILURES_TO_FIND} failures...")
    print("-" * 80)
    start_time = time.time()
    
    failures_found = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if failures_found >= FAILURES_TO_FIND:
            break # We're done

        p_n = prime_list[i]
        true_p_n_plus_1 = prime_list[i + 1]
        
        candidates = []
        for j in range(1, NUM_CANDIDATES_TO_CHECK + 1):
            candidates.append(prime_list[i + j])
        
        # --- Get v11.0 Ranked List (The "Evidence") ---
        candidate_scores = []
        for q_i in candidates:
            S_cand = p_n + q_i
            gap_g_i = q_i - p_n
            
            # Get all 4 key metrics
            score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
            vmod6_rate = get_vmod6_score(S_cand)
            
            # Store (v11_score, prime, vmod6_rate, gap)
            candidate_scores.append((score_v11, q_i, vmod6_rate, gap_g_i))

        # Sort by v11.0 weighted score
        candidate_scores.sort(key=lambda x: x[0])
        
        # --- Get v16.0 Final Prediction ---
        prediction_v16, decision_reason = get_v16_final_decision(p_n, candidate_scores)

        if prediction_v16 != true_p_n_plus_1:
            # --- THIS IS A v16.0 FAILURE. PRINT THE CASE FILE. ---
            failures_found += 1
            
            print(f"\n" + "="*20 + f" CASE FILE #{failures_found} " + "="*20)
            print(f"PRIME p_n: {p_n}")
            print(f"v16.0 FINAL DECISION: {prediction_v16} (FAILURE)")
            print(f"REASON: {decision_reason}")
            print("-" * 60)
            
            print(f"{'Rank':<5} | {'Prime (q_i)':<12} | {'v11.0 Score':<15} | {'v_mod6 (%)':<12} | {'Gap (g_n)':<10} | {'STATUS':<15}")
            print("-" * 75)
            
            for rank in range(len(candidate_scores)):
                score, prime, vmod6, gap = candidate_scores[rank]
                
                status = ""
                if prime == true_p_n_plus_1:
                    status = "--> TRUE PRIME (L)"
                elif prime == prediction_v16:
                    status = "--> FAKE WINNER (W)"
                
                print(f"{rank+1:<5} | {prime:<12} | {score:<15.2f} | {vmod6:<12.2f} | {gap:<10} | {status:<15}")
            
            print("="*60)
            
    # --- Final Summary ---
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print(f"Found {failures_found} failure cases.")

if __name__ == "__main__":
    run_forensic_analysis()