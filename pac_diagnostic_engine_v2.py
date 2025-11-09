# ==============================================================================
# PAC DIAGNOSTIC ENGINE (v2.0)
#
# This "Messiness Score" function is the core of the PLR conjecture.
#
# v2.0 incorporates all major PAC findings:
# 1. Module 1: Immunity Overrides (from PAC-2 & Test 4)
# 2. Module 2: Baseline Messiness Score (from Test 3)
# 3. Module 3: Gap Correlation Factor (from Test 6)
# ==============================================================================

# --- Module 2: Baseline Score (from test-3-result.txt) ---
# Score = Total failures observed for S_n % 30 == residue
FAILURE_COUNTS_MOD_30 = {
    0: 9907,    1: 0,       2: 654113,  3: 0,       4: 431661,
    5: 0,       6: 171547,  7: 0,       8: 662464,  9: 0,
    10: 751163, 11: 0,      12: 199190, 13: 0,      14: 424448,
    15: 0,      16: 426340, 17: 0,      18: 200139, 19: 0,
    20: 749951, 21: 0,      22: 661166, 23: 0,      24: 171854,
    25: 0,      26: 430955, 27: 0,      28: 654709, 29: 0
} #

# --- Module 3: Gap Correlation Data (from test-6-result.txt) ---
# Overall average gap g_n from 50M pair test
OVERALL_AVG_GAP = 19.6490 #

# Residues prone to failures DIVISIBLE BY 3 (k=9, 15...)
# (From test-3: e.g., 10, 20 are >60% k=9; 2, 4, 8... are mixed)
K_DIV_3_PRONE_RESIDUES = {2, 4, 8, 10, 14, 16, 20, 22, 26, 28} #

# Residues prone to failures NOT DIVISIBLE BY 3 (k=25, 35...)
# (From test-3: e.g., 6, 12, 18, 24 are >68% k=25)
K_NOT_DIV_3_PRONE_RESIDUES = {2, 4, 6, 8, 12, 14, 16, 18, 22, 24, 26, 28} #
# Note: Mixed residues (2, 4, 8...) are in both sets.

# We will apply a simple multiplier (penalty/bonus)
# This is a tunable parameter. Let's start with 25%.
GAP_FACTOR_PENALTY = 1.25  # 25% "messier"
GAP_FACTOR_BONUS   = 0.75  # 25% "cleaner"

def get_messiness_score_v2(anchor_sn, gap_g_n):
    """
    The PAC Diagnostic Engine (v2.0).
    Takes a hypothetical S_n anchor AND its gap g_n.
    Returns a "Messiness Score" (lower is better).
    """
    
    # --- Module 1: Immunity Overrides (The "Perfect" Anchors) ---
    
    # P5 Filter: 0 failures observed. This is the "cleanest" possible anchor.
    if anchor_sn % 2310 == 0:
        return 0  #
    
    # P4 Filter: 1 failure (k=121) observed.
    if anchor_sn % 210 == 0:
        return 1  #
        
    # --- Module 2: Baseline Score (from Mod 30) ---
    residue = anchor_sn % 30
    base_score = FAILURE_COUNTS_MOD_30.get(residue, 0)
    
    # If the base score is 0 (e.g., residue 1, 3, 5...), it's an
    # impossible anchor. Return an extremely high score.
    if base_score == 0 and residue not in {0}: # We already handled 0
        return float('inf') # Impossible anchor, infinitely "messy"
        
    # --- Module 3: Gap Correlation Factor ---
    gap_factor = 1.0 # Default: no change
    
    # Test 6 showed k-div-by-3 failures (like k=9) prefer LARGE gaps.
    # Test 6 showed k-not-div-by-3 failures (like k=25) prefer SMALL gaps.
    #
    
    is_large_gap = (gap_g_n > OVERALL_AVG_GAP)
    
    # Check for k_div_by_3 "perfect storm" or "mismatch"
    if residue in K_DIV_3_PRONE_RESIDUES:
        if is_large_gap: # (Prone to k=9 AND has large gap)
            gap_factor *= GAP_FACTOR_PENALTY # Perfect storm: MORE messy
        else: # (Prone to k=9 but has small gap)
            gap_factor *= GAP_FACTOR_BONUS   # Mismatch: LESS messy

    # Check for k_not_div_by_3 "perfect storm" or "mismatch"
    if residue in K_NOT_DIV_3_PRONE_RESIDUES:
        if not is_large_gap: # (Prone to k=25 AND has small gap)
            gap_factor *= GAP_FACTOR_PENALTY # Perfect storm: MORE messy
        else: # (Prone to k=25 but has large gap)
            gap_factor *= GAP_FACTOR_BONUS   # Mismatch: LESS messy
            
    # Return the final, gap-adjusted score
    return base_score * gap_factor