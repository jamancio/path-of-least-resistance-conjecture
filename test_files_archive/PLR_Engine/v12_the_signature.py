# ==============================================================================
# PATH OF LEAST RESISTANCE (PLR) - TEST 21: The "Signature" Engine (v12.0)
#
# This is the "smart" engine that attempts to correct its own failures.
#
# Our post-mortem tests (v11.2, v11.3) proved:
# 1. 100% of v11.0 failures are "Scenario B: Lost on Cleanliness"
#    (a "Clean" fake beats a "Messy" true prime).
# 2. In 21.85% of these failures, the "Messy" true prime
#    is "hiding" at Rank 2.
#
# HYPOTHESIS:
# We can create a "v12.0 Signature" rule to "fix" these failures.
#
# 1. Run the v11.0 engine to get the ranked list.
# 2. Get the #1 Winner and the #2 Candidate.
# 3. Check their v_mod6 scores (Cleanliness).
# 4. IF (Winner_#1 is "Clean" AND Candidate_#2 is "Messy"):
#       This is the "failure signature" we found.
#       OVERRIDE the prediction and choose Candidate_#2.
# 5. ELSE:
#       This is not the failure signature.
#       Trust the v11.0 engine and predict Winner_#1.
#
# This should "recover" a large portion of the 21.85% of 2nd-place
# failures and break the 60.49% barrier.
# ==============================================================================

import time
import math
import json
from collections import defaultdict

# --- Engine Setup (v11.0 "Weighted Gap") ---
MOD6_ENGINE_FILE = "data/messiness_map_v_mod6.json"
MESSINESS_MAP_V_MOD6 = None

# --- These are the "Signature" thresholds ---
# We define "Clean" as the v_mod6 score for the 0-residue class
CLEAN_THRESHOLD = 3.0  # (Actual score is 2.71%)
# We define "Messy" as the v_mod6 score for the 2- and 4-residue classes
MESSY_THRESHOLD = 20.0 # (Actual scores are ~26.2%)


def load_engine_data():
    """Loads the v_mod6 messiness map."""
    global MESSINESS_MAP_V_MOD6
    try:
        with open(MOD6_ENGINE_FILE, 'r') as f:
            MESSINESS_MAP_V_MOD6 = {int(k): v for k, v in json.load(f).items()}
        print(f"Loaded v_mod6 (Mod 6) engine data from '{MOD6_ENGINE_FILE}'.")
        print(f"  - 'Clean' Signature Threshold: < {CLEAN_THRESHOLD}%")
        print(f"  - 'Messy' Signature Threshold: > {MESSY_THRESHOLD}%")
        return True
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Engine file not found: {e.filename}")
        return False
    except Exception as e:
        print(f"FATAL ERROR: Could not load or parse engine file: {e}")
        return False

def get_messiness_score_v11_weighted(anchor_sn, gap_g_n):
    """The v11.0 "Weighted Gap" Engine."""
    if MESSINESS_MAP_V_MOD6 is None:
        return float('inf')
    score_mod6 = MESSINESS_MAP_V_MOD6.get(anchor_sn % 6, float('inf'))
    if score_mod6 == float('inf'):
        return float('inf')
    return (score_mod6 + 1.0) * gap_g_n

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
def run_PLR_v12_signature_test():
    
    if not load_engine_data():
        print("Stopping test: Engine data could not be loaded.")
        return
        
    prime_list = load_primes_from_file(PRIME_INPUT_FILE)
    if prime_list is None: return

    print(f"\nStarting PLR 'Signature' Test (v12.0) for {PRIMES_TO_TEST:,} primes...")
    print(f"  - Engine: v11.0 + 'Clean #1 vs. Messy #2' Override Rule")
    print("-" * 80)
    start_time = time.time()
    
    total_predictions = 0
    total_successes_v11_baseline = 0
    total_successes_v12_new_champ = 0
    total_overrides_attempted = 0
    
    loop_end_index = PRIMES_TO_TEST + START_INDEX
    
    if loop_end_index >= len(prime_list) - (NUM_CANDIDATES_TO_CHECK + 2):
        print("FATAL ERROR: PRIMES_TO_TEST is too large for the loaded prime list.")
        return

    for i in range(START_INDEX, loop_end_index):
        if (i - START_INDEX + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = i - START_INDEX + 1
            v12_acc = (total_successes_v12_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
            v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
            print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v12.0 Acc: {v12_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Overrides: {total_overrides_attempted:,} | Time: {elapsed:.0f}s", end='\r')

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

        # --- Get v11.0 Baseline Prediction ---
        total_predictions += 1
        candidate_scores.sort(key=lambda x: x[0])
        
        winner_v11 = candidate_scores[0][1] # Get the prime
        if winner_v11 == true_p_n_plus_1:
            total_successes_v11_baseline += 1
            
        # --- Run v12.0 "Signature" Logic ---
        final_prediction = winner_v11 # Default to v11.0
        
        # We need at least 2 candidates to check for the signature
        if len(candidate_scores) >= 2:
            # 1. Get #1 and #2 candidates' data
            winner_v11_prime = candidate_scores[0][1]
            candidate_2_prime = candidate_scores[1][1]

            # 2. Get their "Cleanliness" scores (v_mod6 rate)
            winner_v11_anchor = p_n + winner_v11_prime
            winner_v11_vmod6 = get_vmod6_score(winner_v11_anchor)
            
            candidate_2_anchor = p_n + candidate_2_prime
            candidate_2_vmod6 = get_vmod6_score(candidate_2_anchor)
            
            # 3. Apply the "Signature Test"
            is_winner_clean = (winner_v11_vmod6 < CLEAN_THRESHOLD)
            is_c2_messy = (candidate_2_vmod6 > MESSY_THRESHOLD)
            
            if is_winner_clean and is_c2_messy:
                # *** OVERRIDE ***
                # This is the "Clean #1 vs. Messy #2" signature.
                # We bet that this is a Scenario B failure.
                final_prediction = candidate_2_prime
                total_overrides_attempted += 1

        # 4. Tally the final v12.0 prediction
        if final_prediction == true_p_n_plus_1:
            total_successes_v12_new_champ += 1
            
    # --- Final Summary ---
    progress = total_predictions
    v12_acc = (total_successes_v12_new_champ / total_predictions) * 100 if total_predictions > 0 else 0
    v11_acc = (total_successes_v11_baseline / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"Progress: {progress:,} / {PRIMES_TO_TEST:,} | v12.0 Acc: {v12_acc:.2f}% | v11.0 Acc: {v11_acc:.2f}% | Overrides: {total_overrides_attempted:,} | Time: {time.time() - start_time:.0f}s")
    print(f"\nAnalysis completed in {time.time() - start_time:.2f} seconds.")
    print("-" * 80)

    print("\n" + "="*20 + " PLR (v12.0 'Signature') TEST REPORT " + "="*20)
    print(f"\nTotal Primes Tested (p_n): {total_predictions:,}")
    print(f"Candidates Checked per Prime: {NUM_CANDIDATES_TO_CHECK}")
    print(f"Total 'Signature' Overrides Attempted: {total_overrides_attempted:,}")
    
    print(f"\nTotal Correct (v11.0 Baseline): {total_successes_v11_baseline:,}")
    print(f"Total Correct (v12.0 'Signature'): {total_successes_v12_new_champ:,}")
    
    print(f"\n  v11.0 'Weighted Gap' (Baseline): {v11_acc:.2f}%")
    print(f"  v12.0 'Signature' (New):         {v12_acc:.2f}%")
    print("  ---------------------------------")
    improvement = v12_acc - v11_acc
    print(f"  Improvement over Baseline: {improvement:+.2f} percentage points")


    # --- Final Conclusion ---
    print("\n\n" + "="*20 + " FINAL CONCLUSION " + "="*20)
    if v12_acc > v11_acc:
        print("\n  [VERDICT: SUCCESS. THE 'FAILURE SIGNATURE' IS REAL!]")
        print(f"  The new 'v12.0' engine's accuracy ({v12_acc:.2f}%) has")
        print(f"  broken the 60.49% barrier!")
        print("\n  This PROVES the final hypothesis:")
        print("  The 39.51% of failures are not random noise, but a")
        print("  predictable 'Clean #1 vs. Messy #2' signature that")
        print("  can be identified and corrected.")
    else:
        print("\n  [VERDICT: FALSIFIED. v11.0 REMAINS CHAMPION.]")
        print(f"  The new 'v12.0' engine's accuracy ({v12_acc:.2f}%) is")
        print(f"  not better than the v11.0 baseline ({v11_acc:.2f}%).")
        print("  This means the 'Clean #1 vs. Messy #2' signature")
        print("  is not a reliable indicator of a Scenario B failure.")
        print("  The 39.51% of failures are more complex than this.")

    print("=" * (50 + len(" FINAL CONCLUSION ")))

if __name__ == "__main__":
    run_PLR_v12_signature_test()