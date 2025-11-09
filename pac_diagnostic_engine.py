# ==============================================================================
# PAC DIAGNOSTIC ENGINE (v1.0)
#
# This script contains the scoring function for the
# "Path of Least Resistance" (PLR) conjecture.
#
# The engine's "Messiness Score" is based on the verified
# 'Total Failures in this Class' data from the
# 'PAC Test 3: Residue Class Analysis (Mod 30)'.
# ==============================================================================

# Hard-coded failure counts from test-3-result.txt
# This is the core of the engine's "Module 2: Failure Signature Predictor"
# Score = Total failures observed for S_n % 30 == residue
FAILURE_COUNTS_MOD_30 = {
    0: 9907,
    1: 0,
    2: 654113,
    3: 0,
    4: 431661,
    5: 0,
    6: 171547,
    7: 0,
    8: 662464,
    9: 0,
    10: 751163,
    11: 0,
    12: 199190,
    13: 0,
    14: 424448,
    15: 0,
    16: 426340,
    17: 0,
    18: 200139,
    19: 0,
    20: 749951,
    21: 0,
    22: 661166,
    23: 0,
    24: 171854,
    25: 0,
    26: 430955,
    27: 0,
    28: 654709,
    29: 0
}

def get_messiness_score(anchor_sn):
    """
    The PAC Diagnostic Engine.
    Takes a hypothetical S_n anchor and returns its "Messiness Score".
    A lower score implies a more "stable" or "clean" anchor.
    """
    # Get the residue class for this anchor
    residue = anchor_sn % 30
    
    # Look up the score from our verified data
    # We use .get() as a safety, defaulting to 0 if residue is invalid
    score = FAILURE_COUNTS_MOD_30.get(residue, 0)
    
    return score

# --- Main function (for standalone testing of the engine) ---
if __name__ == "__main__":
    # Test the engine with the examples from the PLR conjecture
    
    # Example 1: S_cand_1 = 68 (True Anchor S_10)
    sn_1 = 68
    score_1 = get_messiness_score(sn_1)
    # S_n=68 -> 68 % 30 = 8. Score = 662,464
    print(f"Anchor S_n = {sn_1} (Residue {sn_1 % 30}) -> Messiness Score: {score_1:,}")
    
    # Example 2: S_cand_2 = 72 (Fake Anchor)
    sn_2 = 72
    score_2 = get_messiness_score(sn_2)
    # S_n=72 -> 72 % 30 = 12. Score = 199,190
    print(f"Anchor S_n = {sn_2} (Residue {sn_2 % 30}) -> Messiness Score: {score_2:,}")

    # Example 3: S_cand_3 = 74 (Fake Anchor)
    sn_3 = 74
    score_3 = get_messiness_score(sn_3)
    # S_n=74 -> 74 % 30 = 14. Score = 424,448
    print(f"Anchor S_n = {sn_3} (Residue {sn_3 % 30}) -> Messiness Score: {score_3:,}")