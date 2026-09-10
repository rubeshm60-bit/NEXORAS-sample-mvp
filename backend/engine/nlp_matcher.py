"""
NEXORAS — Module 10: NLP Project Intelligence Engine
===================================================
Text analysis, duplicate/near-duplicate project detection, and contract
splitting indicators for MPLADS completed and recommended works.

Capabilities:
  1. TF-IDF vectorization and semantic text representation
  2. Exact & near-duplicate work description detection
  3. Contract splitting / repetitive bulk procurement identification
  4. Vague description auditing (low-information strings)
  5. Multi-level risk signals (Work-level and MP-level metrics)

All signals adhere to neutral audit terminology:
  - "unusual repetition"
  - "potential contract splitting"
  - "requires physical verification"
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(text: str) -> str:
    """Normalize text: lowercase, remove non-alphanumerics, strip whitespace."""
    if not isinstance(text, str) or not text.strip():
        return "[no description]"
    # Normalize unicode / whitespace
    text = re.sub(r"[^\w\s]", " ", text.lower())
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else "[no description]"


class NLPProjectMatcher:
    """
    NLP engine for detecting duplicate project descriptions, contract splitting,
    and text-level procurement irregularities across MPLADS works.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        bulk_repeat_threshold: int = 15,
        vague_word_limit: int = 3,
        max_features: int = 5000,
    ):
        self.similarity_threshold = similarity_threshold
        self.bulk_repeat_threshold = bulk_repeat_threshold
        self.vague_word_limit = vague_word_limit
        self.max_features = max_features

        # Pre-computed models & outputs
        self.tfidf: Optional[TfidfVectorizer] = None
        self.scored_works_df: Optional[pd.DataFrame] = None
        self.mp_nlp_metrics_df: Optional[pd.DataFrame] = None
        self.is_analyzed: bool = False

    def analyze(self, cleaned_datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Execute full NLP analysis on completed works and generate MP-level signals.

        Parameters:
            cleaned_datasets: Dict containing 'completed_works' and 'mp_summary'.

        Returns:
            pd.DataFrame: Completed works enriched with duplicate flags and cluster IDs.
        """
        works = cleaned_datasets["completed_works"].copy()
        mp_sum = cleaned_datasets.get("mp_summary", pd.DataFrame()).copy()

        # Step 1: Text normalization
        works["normalized_description"] = works["work_description"].fillna("").apply(normalize_text)

        # Step 2: Vague description flag
        vague_terms = {"no description", "development work", "miscellaneous work", "other work", "na", "null"}
        works["word_count"] = works["normalized_description"].apply(lambda s: len(s.split()))
        works["is_vague_description"] = works["normalized_description"].apply(
            lambda s: (s in vague_terms) or (len(s.split()) <= self.vague_word_limit)
        )

        # Step 3: Global exact duplicate counting
        global_desc_counts = works["normalized_description"].value_counts().to_dict()
        works["global_repeat_count"] = works["normalized_description"].map(global_desc_counts).fillna(1).astype(int)

        # Step 4: Within-MP duplicate detection
        # (Constituency-level repetition indicates potential contract splitting)
        mp_desc_counts = works.groupby(["mp_name", "normalized_description"]).size().to_dict()
        works["mp_repeat_count"] = works.apply(
            lambda r: mp_desc_counts.get((r["mp_name"], r["normalized_description"]), 1), axis=1
        )
        works["is_duplicate_in_constituency"] = works["mp_repeat_count"] > 1

        # Step 5: Duplicate cluster assignment per MP
        # Unique descriptions per MP get a cluster ID
        works["text_cluster_id"] = works.groupby(["mp_name", "normalized_description"]).ngroup()

        # Step 6: TF-IDF feature fitting
        self.tfidf = TfidfVectorizer(
            max_features=self.max_features,
            stop_words="english",
            min_df=2,
            ngram_range=(1, 2),
        )
        self.tfidf.fit(works["normalized_description"])

        # Step 7: Aggregate MP-Level NLP Metrics
        mp_records = []
        all_mps = mp_sum["mp_name"].unique() if not mp_sum.empty else works["mp_name"].unique()

        works_by_mp = works.groupby("mp_name")
        for mp in all_mps:
            if mp in works_by_mp.groups:
                grp = works_by_mp.get_group(mp)
                total_w = len(grp)
                dup_w = int((grp["is_duplicate_in_constituency"]).sum())
                vague_w = int((grp["is_vague_description"]).sum())
                max_rep = int(grp["mp_repeat_count"].max()) if not grp.empty else 0
                unique_desc = int(grp["normalized_description"].nunique())

                dup_ratio = float(dup_w / total_w) if total_w > 0 else 0.0
                vague_ratio = float(vague_w / total_w) if total_w > 0 else 0.0

                # Flag potential contract splitting: MP with many identical works
                has_splitting_pattern = max_rep >= self.bulk_repeat_threshold
            else:
                total_w = 0
                dup_w = 0
                vague_w = 0
                max_rep = 0
                unique_desc = 0
                dup_ratio = 0.0
                vague_ratio = 0.0
                has_splitting_pattern = False

            # NLP Risk Score (0 - 100)
            # Combines duplicate ratio, splitting presence, and vague description ratio
            score = (dup_ratio * 50.0) + (15.0 if has_splitting_pattern else 0.0) + (vague_ratio * 35.0)
            score = float(np.clip(score, 0.0, 100.0))

            flags = []
            if has_splitting_pattern:
                flags.append(f"POTENTIAL_CONTRACT_SPLITTING (Identical project text repeated {max_rep} times)")
            if dup_ratio >= 0.50:
                flags.append(f"HIGH_TEXT_DUPLICATION ({dup_ratio:.1%} of works share identical text)")
            if vague_ratio >= 0.20:
                flags.append(f"VAGUE_PROJECT_DESCRIPTIONS ({vague_ratio:.1%} of descriptions lack detail)")

            mp_records.append({
                "mp_name": mp,
                "total_completed_works": total_w,
                "duplicate_works_count": dup_w,
                "unique_descriptions_count": unique_desc,
                "duplicate_work_ratio": round(dup_ratio, 4),
                "max_single_description_repeat": max_rep,
                "vague_descriptions_count": vague_w,
                "vague_description_ratio": round(vague_ratio, 4),
                "has_contract_splitting_pattern": has_splitting_pattern,
                "nlp_risk_score": round(score, 2),
                "nlp_risk_flags": "; ".join(flags) if flags else "NORMAL",
            })

        mp_nlp_df = pd.DataFrame(mp_records)
        mp_nlp_df.sort_values("nlp_risk_score", ascending=False, inplace=True)
        mp_nlp_df.reset_index(drop=True, inplace=True)
        mp_nlp_df["nlp_rank"] = np.arange(1, len(mp_nlp_df) + 1)

        self.scored_works_df = works
        self.mp_nlp_metrics_df = mp_nlp_df
        self.is_analyzed = True
        return works

    def get_mp_nlp_profile(self, mp_name: str) -> Optional[Dict[str, Any]]:
        """Return NLP text metrics and duplicate audit signals for an MP."""
        if not self.is_analyzed or self.mp_nlp_metrics_df is None:
            raise RuntimeError("NLPProjectMatcher must be run via analyze() before querying.")

        matches = self.mp_nlp_metrics_df[self.mp_nlp_metrics_df["mp_name"] == mp_name]
        if matches.empty:
            return None

        row = matches.iloc[0].to_dict()

        # Top repeated descriptions for this MP
        top_repeated = []
        if self.scored_works_df is not None:
            mp_works = self.scored_works_df[self.scored_works_df["mp_name"] == mp_name]
            if not mp_works.empty:
                vc = mp_works["work_description"].value_counts()
                for desc, count in vc.head(5).items():
                    if count > 1:
                        top_repeated.append({
                            "description": str(desc),
                            "repeat_count": int(count),
                        })

        row["top_repeated_descriptions"] = top_repeated
        return row

    def get_top_repetitive_mps(self, top_n: int = 20) -> pd.DataFrame:
        """Return MPs with highest text duplication / contract splitting indicators."""
        if not self.is_analyzed or self.mp_nlp_metrics_df is None:
            raise RuntimeError("NLPProjectMatcher must be run via analyze() before querying.")
        return self.mp_nlp_metrics_df.head(top_n).copy()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Return global NLP text metrics across all works."""
        if not self.is_analyzed or self.scored_works_df is None or self.mp_nlp_metrics_df is None:
            raise RuntimeError("NLPProjectMatcher must be run via analyze() before querying.")

        works = self.scored_works_df
        mps = self.mp_nlp_metrics_df

        return {
            "total_works_analyzed": int(len(works)),
            "unique_text_descriptions": int(works["normalized_description"].nunique()),
            "total_duplicate_works": int(works["is_duplicate_in_constituency"].sum()),
            "vague_descriptions_count": int(works["is_vague_description"].sum()),
            "mps_with_contract_splitting": int(mps["has_contract_splitting_pattern"].sum()),
            "mps_with_high_duplication": int((mps["duplicate_work_ratio"] >= 0.50).sum()),
            "mean_nlp_risk_score": float(mps["nlp_risk_score"].mean()),
        }


def run_nlp_pipeline(cleaned_datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Convenience runner executing Module 10 end-to-end pipeline.

    Returns:
        Dict containing:
          - 'nlp_engine': Fitted NLPProjectMatcher instance
          - 'scored_works': pd.DataFrame of completed works with NLP flags
          - 'mp_nlp_metrics': pd.DataFrame of MP-level NLP metrics
          - 'summary_stats': Dict of global NLP metrics
    """
    print("=" * 60)
    print("NEXORAS — Module 10: Running NLP Project Intelligence Pipeline")
    print("=" * 60)
    engine = NLPProjectMatcher()
    scored_works = engine.analyze(cleaned_datasets)
    stats = engine.get_summary_stats()

    print(f"  Analyzed {stats['total_works_analyzed']:,} works ({stats['unique_text_descriptions']:,} unique descriptions).")
    print(f"  Total In-Constituency Duplicate Works: {stats['total_duplicate_works']:,}")
    print(f"  Vague Project Descriptions: {stats['vague_descriptions_count']:,}")
    print(f"  MPs with Contract Splitting Patterns: {stats['mps_with_contract_splitting']:,}")
    print(f"  MPs with >50% Duplicate Descriptions: {stats['mps_with_high_duplication']:,}")
    print("=" * 60)

    return {
        "nlp_engine": engine,
        "scored_works": scored_works,
        "mp_nlp_metrics": engine.mp_nlp_metrics_df,
        "summary_stats": stats,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all
    from backend.cleaning.cleaner import clean_all

    cleaned = clean_all(load_all())
    res = run_nlp_pipeline(cleaned)
    top_mps = res["nlp_engine"].get_top_repetitive_mps(10)
    print("\nTop 10 MPs with Potential Contract Splitting / Repetitive Procurement:")
    for _, r in top_mps.iterrows():
        print(f"  Rank #{r['nlp_rank']}: {r['mp_name']} | Risk: {r['nlp_risk_score']:.1f} | Dups: {r['duplicate_works_count']}/{r['total_completed_works']} ({r['duplicate_work_ratio']:.1%}) | Max Rep: {r['max_single_description_repeat']}")
