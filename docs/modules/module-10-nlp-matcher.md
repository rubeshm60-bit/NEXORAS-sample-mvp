# MODULE 10 — NLP PROJECT INTELLIGENCE ENGINE

## Purpose
Apply Natural Language Processing (NLP), text normalization, and semantic vectorization to detect duplicate project descriptions, potential contract splitting, and vague/low-information project proposals across MPLADS works.

## Why NEXORAS Needs It
Financial and network models track money; NLP inspects **what public money was purportedly spent on**.
In public procurement and MPLADS:
- **Contract Splitting Risk**: Government procurement rules mandate competitive open tenders above specific financial thresholds (e.g. ₹5 Lakh / ₹10 Lakh). Corrupt entities frequently split a large tender into dozens or hundreds of identical small contracts (e.g. 100 identical solar lights or hand pumps) to keep each below the mandatory tender threshold and award them directly to favored contractors.
- **Ghost Project Risk**: Re-submitting identical or near-identical descriptions across consecutive funding tranches without physical execution.
- **Vague Ledger Descriptions**: Entries like `"[No description]"`, `"Development work"`, or `"Miscellaneous work"` that conceal actual project scope from citizen oversight.

## NLP Architecture & Methodology

1. **Text Normalization**:
   - Punctuation removal, case folding, unicode normalization, and multi-space collapsing.
   - Missing descriptions standardized to neutral sentinel: `"[no description]"`.
2. **Semantic Vectorization**:
   - `TfidfVectorizer` (scikit-learn) with unigrams and bigrams (`ngram_range=(1, 2)`), English stop-word filtering, and frequency pruning.
3. **Within-Constituency Duplicate Mining**:
   - Measures exact and near-duplicate recurrence of project descriptions sanctioned under each MP.
   - Computes `duplicate_work_ratio` ($0.0 \text{ to } 1.0$) and `max_single_description_repeat`.
4. **Contract Splitting Detection**:
   - Algorithmically flags any constituency where the exact same project description is repeated $\ge 15$ times (`has_contract_splitting_pattern = True`).
5. **Vague Description Auditing**:
   - Identifies entries containing $\le 3$ words or generic boilerplate terms.
6. **NLP Composite Risk Scoring ($0.0 \text{ to } 100.0$)**:
   $$\text{Score}_{\text{NLP}} = (\text{duplicate\_ratio} \times 50) + (15 \text{ if contract\_splitting else } 0) + (\text{vague\_ratio} \times 35)$$

## Empirical Findings on MPLADS
- **Total Works Analyzed**: 44,028 completed works
- **Unique Descriptions**: 38,362
- **In-Constituency Duplicate Works**: 6,332 projects
- **Vague Descriptions Detected**: 1,196 projects
- **MPs with Contract Splitting Patterns**: 57 parliamentarians
- **MPs with >50% Duplicate Descriptions**: 58 parliamentarians

### Notable Case Studies Identified:
1. `Shri B.L. Verma`: 204 identical repeats of `"High Mast LED Light (9.5 mtrs MS Pole with 6 LED Light 150 W)"` (260/350 total works repeated, 74.3% duplication).
2. `SAMBIT PATRA`: 178 identical repeats of `"Installation of Solar Light at Creamation Ground."` (222/548 total works repeated, 40.5% duplication).
3. `CHANDRA SHEKHAR`: 118 identical repeats of `"HIGH MAST LIGHT WITH FOUR LED RECOMMENDED IN MY CONSTITUENCY NAGINA..."` (128/286 total works repeated, 44.8% duplication).
4. `Shri Baburam Nishad`: 420 out of 436 works (96.3%) share duplicate LED light descriptions.
5. `Shri Brij Lal`: 107 out of 113 works (94.7%) share duplicate library procurement descriptions.

## Files
| File | Purpose |
|---|---|
| `backend/engine/nlp_matcher.py` | `NLPProjectMatcher` class, text normalization, duplicate mining, and MP metrics |
| `tests/test_nlp_matcher.py` | 9-test comprehensive validation suite |

## Tests & Verification
9 unit tests covering:
- Text normalization accuracy on edge cases (empty strings, punctuation, whitespace)
- Scored works schema validation across all 44,028 completed works
- Complete coverage of all 774 MPs in MP metrics
- Score and ratio bounds ($[0.0, 100.0]$ and $[0.0, 1.0]$)
- Accurate contract splitting identification ($\ge 15$ threshold)
- Vague description classification
- Query API (`get_mp_nlp_profile`)
- Summary statistics consistency
- End-to-end pipeline execution

## Test Results
**9/9 PASS** (2026-09-10)

## Definition of Done
✅ Text normalization and TF-IDF semantic vectorizer implemented  
✅ Within-constituency duplicate mining executed on all 44,028 works  
✅ Contract splitting patterns identified across 57 MPs  
✅ Vague description auditor flags low-information projects  
✅ Continuous NLP Risk Score ($0-100$) and explainable signals generated  
✅ 9/9 unit tests pass  
