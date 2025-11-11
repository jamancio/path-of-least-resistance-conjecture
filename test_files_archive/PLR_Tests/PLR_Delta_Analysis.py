# ==============================================================================
# PLR ANALYSIS - TEST 35: The Delta P / Delta S Final Post-Mortem
#
# This script analyzes the remaining 24.06% of failures from the v16.0 engine.
#
# GOAL: Find the unique arithmetic signature that distinguishes the True
# Prime from the Fake Winner in the final irreducible failure set.
#
# Metrics Logged:
# 1. Delta P: |p_true - p_fake| (Spatial Difference)
# 2. Delta S: (S_true % 6) - (S_fake % 6) (Structural Difference)
#
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v16.0 Final Logic) ---
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
    """
    Runs the full v16.0 "Chained Signature" logic.
    Returns: prediction, full_ranked_list
    """
    candidate_scores = []
    for q_i in candidates:
        S_cand = p_n + q_i
        gap_g_i = q_i - p_n
        score_v11 = get_messiness_score_v11_weighted(S_cand, gap_g_i)
        vmod6_rate = get_vmod6_score(S_cand)
        # Store as (score, prime, vmod6_score)
        candidate_scores.append((score_v11, q_i, vmod6_rate))

    candidate_scores.sort(key=lambda x: x[0])
    
    if not candidate_scores: return None, []
        
    winner_v11_prime = candidate_scores[0][1]
    winner_v11_vmod6 = candidate_scores[0][2]
    
    prediction_v16 = winner_v11_prime # Default
    
    if winner_v11_vmod6 < CLEAN_THRESHOLD: 
        for rank_index in range(1, MAX_SIGNATURE_SEARCH_DEPTH):
            if rank_index >= len(candidate_scores): break
            next_candidate_vmod6 = candidate_scores[rank_index][2]
            if next_candidate_vmod6 > MESSY_THRESHOLD:
                prediction_v16 = candidate_scores[rank_index][1]
                break
                
    return prediction_v16, candidate_scores
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
def run_PLR_delta_analysis():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR Delta P / Delta S Analysis (Test 35) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Analyzing the final, irreducible 24.06% v16.0 failures.")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_failures = 0
    
    # --- Data Structure for Final Analysis ---
    # Stores { (Delta_P, Delta_S): count }
    delta_signature_counts = defaultdict(int) 
    
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
        
        # 1. Get v16.0 Prediction
        prediction_v16, ranked_list = get_v16_prediction(p_n, candidates)

        if prediction_v16 != true_p_n_plus_1:
            # --- THIS IS A v16.0 FINAL FAILURE. ANALYZE THE DELTA. ---
            total_failures += 1
            
            # 2. Identify the True Prime (p_true) and Fake Winner (p_fake)
            p_true = true_p_n_plus_1
            p_fake = prediction_v16

            # 3. Calculate Delta P (Spatial Difference)
            delta_p = int(p_fake - p_true) 

            # 4. Calculate Delta S (Structural Difference)
            
            # Calculate Anchors
            S_true = p_n + p_true
            S_fake = p_n + p_fake
            
            # Get Mod 6 Residues
            S_true_mod6 = S_true % 6
            S_fake_mod6 = S_fake % 6
            
            # Get the *structural penalty* (v_mod6 rate)
            S_true_vmod6_rate = MESSINESS_MAP_V_MOD6.get(S_true_mod6, float('inf'))
            S_fake_vmod6_rate = MESSINESS_MAP_V_MOD6.get(S_fake_mod6, float('inf'))
            
            # Delta S is the difference in structural penalty (Messiness Score)
            # The True prime should be penalized more (higher score)
            delta_s = S_true_vmod6_rate - S_fake_vmod6_rate
            
            # 5. Log the signature
            # We log the rounded Delta P and the structural difference
            delta_signature = (delta_p, round(delta_s, 2))
            delta_signature_counts[delta_signature] += 1
            
    # --- Final Summary ---
    progress = total_predictions
    print(f"Progress: {progress:,} / {progress:,} | Failures: {total_failures:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " v16.0 FAILURE DELTA P / DELTA S ANALYSIS " + "="*20)
    print(f"\nTotal Irreducible Failures Analyzed (24.06%): {total_failures:,}")
    
    # Process and sort data
    delta_data = []
    for signature, count in delta_signature_counts.items():
        delta_data.append((signature, count))
    
    # Sort by count (descending)
    delta_data.sort(key=lambda x: x[1], reverse=True)
    
    print("\n" + "-" * 20 + " Top 10 Irreducible Delta Signatures " + "-" * 20)
    print(f"\n{'Delta P (p_fake - p_true)':<25} | {'Delta S (S_true Score - S_fake Score)':<40} | {'Failure Count':<15} | {'% of Total Failures':<20}")
    print("-" * 120)
    
    total_sum = sum(delta_signature_counts.values())
    
    for signature, count in delta_data[:10]:
        percentage = (count / total_sum) * 100
        delta_p_val = signature[0]
        delta_s_val = signature[1]
        
        print(f"{delta_p_val:<25,} | {delta_s_val:<40.2f} | {count:<15,} | {percentage:>19.2f}%")

    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL ANALYTIC CONCLUSION " + "="*20)
    print("\n  The strongest and most repeated Delta Signature is the key.")
    print("  This analysis reveals the final structural penalty that the")
    print("  function f(p_n) must solve.")

    print("=" * (50 + len(" FINAL ANALYTIC CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_delta_analysis()