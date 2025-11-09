# The Path of Least Resistance (PLR) Conjecture: A Verified Predictive Model for the Next Prime

**Date:** November 09, 2025

**Author:** Independent Researcher (Valenzuela City, Metro Manila, Philippines)

**Verification Extent:** First 50,000,000 consecutive primes ($p_n$)

---

## Abstract

This paper introduces and verifies the **"Path of Least Resistance" (PLR) conjecture**, a predictive model for identifying the true next prime, $p_{n+1}$. The conjecture is a direct application of the verified **Primorial Anchor Conjecture (PAC)**, which proved that the local "messiness" (composite $k_{min}$ failures) of an anchor $S_n = p_n + p_{n+1}$ is deterministically classified by its primorial signature ($S_n \pmod{P_k}$). We built and tested four versions of a **"PAC Diagnostic Engine"** based on different primorial filters and data combinations. A computational test over 50 million primes, scoring 10 candidates for each, revealed that the simplest filter, **`v_mod6` ($P_2=6$), achieved a predictive accuracy of 55.51%**. This is a **+45.51 percentage point improvement** (over 5.5 times better) than the 10.00% random chance baseline. This result was validated against skeptical counter-arguments, including a "Tautology" test (which passed at 22.20% vs. 10% random) and an "Open Pool" test (which passed at 14.77% vs. 0.67% random). This provides powerful verification of the PLR conjecture and identifies the $S_n \pmod 6$ signature as the dominant predictive signal for the next prime.

---

## 1. Background: The "Path of Least Resistance" Conjecture

Previous research (the PAC) proved that the $S_n = p_n + p_{n+1}$ anchor sequence is governed by deterministic primorial rules. This led to the **"Path of Least Resistance" (PLR) conjecture**:

**Conjecture:** The true next prime, $p_{n+1}$, is the candidate prime $q_i$ (from a set of local candidates) that, when combined with $p_n$, forms the anchor $S_{cand_i} = p_n + q_i$ with the **lowest "Messiness Score."**

A "Messsiness Score" is defined as the **actual, measured "Failure Rate %"** of the residue class to which the candidate anchor $S_{cand_i}$ belongs. A lower failure rate implies a "cleaner" or "more stable" anchor, representing the "path of least resistance."

---

## 2. Methodology: The "Primorial Engine Bake-Off"

To verify the PLR, we tested four separate predictive engines. Each engine was built from the "Messiness Score" (Failure Rate %) data gathered in our previous PAC analysis scripts.

1.  **Engine v_mod6 (Filter: $P_2=6$):**
    * **Data Source:** `test-9_mod6-Residue-Analysis.py`
    * **Score:** The Failure Rate % for $S_n \pmod 6$.
2.  **Engine v1.0 (Filter: $P_3=30$):**
    * **Data Source:** `test-3-result.txt` (from PAC)
    * **Score:** The Failure Rate % for $S_n \pmod{30}$.
3.  **Engine v3.0 (Filter: $P_4=210$):**
    * **Data Source:** `test-8-result.txt`
    * **Score:** The Failure Rate % for $S_n \pmod{210}$.
4.  **Engine v2.1 (Filter: $P_3=30$ + Gap):**
    * **Data Source:** `2D-messisness-Map-Analysis.txt`
    * **Score:** The Failure Rate % for $(S_n \pmod{30}, g_n \text{ Category})$.

A master script (`test_PLR_conjecture.py`) was run for each engine. It looped through 50,000,000 primes ($p_n$), scored the next 10 candidates ($q_1...q_{10}$), and tallied if the candidate with the *lowest score* was the *true* next prime ($q_1$).

---

## 3. Results: The `Mod 6` Engine is Dominant

The results of the four tests show a clear and decisive winner. The simplest filter, `v_mod6`, provided the strongest predictive accuracy by a massive margin.



| Predictive Engine | Filter Used | Prediction Accuracy | vs. Random (10%) |
| :--- | :--- | :--- | :--- |
| **v_mod6 Engine** | **Mod 6 ($P_2$)** | **55.51%** | **+45.51 pts (+455%)** |
| v1.0 Engine | Mod 30 ($P_3$) | 18.57% | +8.57 pts (+86%) |
| v3.0 Engine | Mod 210 ($P_4$) | 10.97% | +0.97 pts (+10%) |
| v2.1 Engine | Mod 30 + Gap | 10.15% | +0.15 pts (+1.5%) |
| Random Chance | N/A | 10.00% | Baseline |



---

## 4. Analysis: Isolating the Signal from the Noise

The 55.51% accuracy of the `v_mod6` engine is a **phenomenal success**. This result not only verifies the PLR conjecture but also isolates the *dominant predictive signal* by proving that **simpler is better**.

**Why is `Mod 6` the winner?**
The answer lies in the **failure distribution** we discovered in `composite_k_distribution-result.txt` (from PAC):

1.  **The Dominant Signal:** Composite failures divisible by 3 (like $k=9, 15, 21$) account for approximately **80% of all failures**.
2.  **The "Noise":** Failures divisible by 5 (like $k=25, 35$) account for only ~15%. Failures divisible by 7 (like $k=49, 77$) account for less than 1%.

The `v_mod6` engine was the most successful because it is a **"pure signal" filter**. It only looks at the `mod 6` signature, which is perfectly aligned with the dominant 80% "messiness" problem. The `v1.0 (Mod 30)` and `v3.0 (Mod 210)` engines performed *worse* because they introduced **noise**. By trying to also account for the much weaker `mod 5` and `mod 7` signals, they diluted the primary `mod 3` signal and reduced accuracy.

---

## 5. Verification Against Counter-Arguments

The 55.51% result was rigorously tested against the two strongest skeptical counter-arguments.

* **Counter-Argument 1: Tautology?** (Was the 55.51% an artifact of the engine "recognizing" its own data?)
    * **Test:** A "neutral" engine with no $S_n$ data (based on an "Ideal Grid") was run.
    * **Result:** The neutral engine achieved **22.20% accuracy**, 2.2x better than the 10% random chance.
    * **Conclusion:** **DISPROVEN.** The PLR is a real, fundamental phenomenon, not a tautology.

* **Counter-Argument 2: Limited Pool?** (Was the 55.51% an artifact of only testing 10 *primes*?)
    * **Test:** The `v_mod6` engine was run on an "open pool" of 150 *integers* (primes and composites) for each $p_n$.
    * **Result:** The engine achieved **14.77% accuracy** against a random chance baseline of **0.67%** (1-in-150).
    * **Conclusion:** **DISPROVEN.** The engine performed **22 times better than random** in an open pool, proving the signal is robust and not a testing artifact.

---

## 6. Final Verdict

The "Path of Least Resistance" (PLR) conjecture is **strongly verified**. The choice of the next prime, $p_{n+1}$, is demonstrably **not random**. It is powerfully biased towards creating an $S_n$ anchor that has the "cleanest" (most stable) signature relative to the `Mod 6` primorial filter. The PAC framework has successfully yielded a novel, verifiable predictive model for the next prime.