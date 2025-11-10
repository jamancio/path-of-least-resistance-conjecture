# ==============================================================================
# PAC DIAGNOSTIC ENGINE (v2.1)
#
# This "Messiness Score" function is the core of the PLR v2.1 conjecture.
#
# v2.1 uses the VERIFIED 2D "Messiness Map" from the 'PAC-7'
# (2D-messisness-Map-Analysis.txt) test.
#
# The "Messiness Score" is now the *actual, measured failure rate*
# for a given (S_n % 30, Gap Category) combination.
# ==============================================================================

import math

# --- Gap Categorization (from test-7_2D-Messiness-Map.py) ---
# Must be identical to the bins used in the analysis script
OVERALL_AVG_GAP = 19.6490 #
GAP_BIN_SMALL = 18.0
GAP_BIN_LARGE = 22.0

def categorize_gap(gap_g_n):
    """Categorizes the gap g_n into Small, Medium, or Large."""
    if gap_g_n < GAP_BIN_SMALL:
        return "Small"
    elif gap_g_n >= GAP_BIN_LARGE:
        return "Large"
    else:
        return "Medium"

# --- v2.1 Engine Data: 2D Messiness Map ---
# The "Messiness Score" is the 'FAILURE RATE (%)' from 2D-messisness-Map-Analysis.txt
# Format: {(residue, gap_category): failure_rate_percent}
#
MESSINESS_MAP_V2_1 = {
    (0, "Small"): 0.1468,  (0, "Large"): 0.1272,
    (2, "Small"): 32.9259, (2, "Large"): 33.3726,
    (4, "Small"): 24.4134, (4, "Medium"): 21.2283, (4, "Large"): 23.6586,
    (6, "Small"): 3.4541,  (6, "Medium"): 3.1766,  (6, "Large"): 3.1887,
    (8, "Small"): 31.9059, (8, "Large"): 30.8648,
    (10, "Small"): 23.7988, (10, "Medium"): 21.3690, (10, "Large"): 22.3325,
    (12, "Small"): 4.0594, (12, "Medium"): 3.5175, (12, "Large"): 3.3869,
    (14, "Small"): 22.9096, (14, "Medium"): 21.0282, (14, "Large"): 22.4500,
    (16, "Small"): 22.9340, (16, "Medium"): 21.1565, (16, "Large"): 22.5176,
    (18, "Small"): 4.0784, (18, "Medium"): 3.4875, (18, "Large"): 3.4216,
    (20, "Small"): 23.7749, (20, "Medium"): 21.3136, (20, "Large"): 22.3276,
    (22, "Small"): 31.9118, (22, "Large"): 30.8288,
    (24, "Small"): 3.4560, (24, "Medium"): 3.1808, (24, "Large"): 3.2031,
    (26, "Small"): 24.4130, (26, "Medium"): 21.3267, (26, "Large"): 23.4702,
    (28, "Small"): 32.9994, (28, "Large"): 33.3786,
}

# --- Immunity Overrides (from PAC-2 & Test-4) ---
#
IMMUNITY_P5_SCORE = 0.0  # (0 failures)
IMMUNITY_P4_SCORE = 0.0001 # (1 failure / ~6.6M total). A tiny, non-zero score.

def get_messiness_score_v2_1(anchor_sn, gap_g_n):
    """
    The PAC Diagnostic Engine (v2.1).
    Takes a hypothetical S_n anchor AND its gap g_n.
    Returns a "Messiness Score" (lower is better).
    """
    
    # --- Module 1: Immunity Overrides ---
    if anchor_sn % 2310 == 0:
        return IMMUNITY_P5_SCORE #
    
    if anchor_sn % 210 == 0:
        return IMMUNITY_P4_SCORE #
        
    # --- Module 2: 2D Messiness Map (v2.1) ---
    residue = anchor_sn % 30
    gap_category = categorize_gap(gap_g_n)
    
    # Look up the score from our 2D data map
    score = MESSINESS_MAP_V2_1.get((residue, gap_category), float('inf'))
    
    # If the score is 'inf', it means this combination of
    # (residue, gap) never appeared in our 50M test.
    # It is either impossible or extremely rare.
    # We treat it as "infinitely messy" so it's not predicted.
    
    return score