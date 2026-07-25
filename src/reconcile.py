"""
Deterministic reconciliation engine.

Design principle: matching logic is 100% deterministic Python.
The LLM (see explain.py) is used ONLY to explain exceptions in plain
English — never to decide matches. This keeps reconciliation
reproducible and auditable, which is what serious finance clients require.
"""

import pandas as pd


def load_data(path_a: str, path_b: str):
    """Load two CSVs from disk. Returns (df_a, df_b)."""
    return pd.read_csv(path_a), pd.read_csv(path_b)


def reconcile(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    key: str = "transaction_id",
    amount_col: str = "amount",
    tolerance: float = 0.01,
) -> pd.DataFrame:
    """
    Reconcile two datasets on a shared key.

    Detects three exception types:
      1. Present in A, missing in B
      2. Present in B, missing in A
      3. Key exists in both, but amount differs beyond `tolerance`

    Returns a DataFrame of exceptions. Empty DataFrame if fully reconciled.
    """
    # Validate inputs early with clear errors.
    for name, df in (("Source A", df_a), ("Source B", df_b)):
        if key not in df.columns:
            raise ValueError(f"{name} is missing the key column '{key}'. "
                             f"Available columns: {list(df.columns)}")
        if amount_col not in df.columns:
            raise ValueError(f"{name} is missing the amount column '{amount_col}'. "
                             f"Available columns: {list(df.columns)}")

    merged = df_a.merge(
        df_b,
        on=key,
        how="outer",
        suffixes=("_a", "_b"),
        indicator=True,
    )

    exceptions = []

    for _, row in merged.iterrows():
        merge_flag = row["_merge"]

        if merge_flag == "left_only":
            exceptions.append({
                key: row[key],
                "reason": "Present in Source A, missing in Source B",
                "amount_a": row.get(f"{amount_col}_a"),
                "amount_b": None,
            })

        elif merge_flag == "right_only":
            exceptions.append({
                key: row[key],
                "reason": "Present in Source B, missing in Source A",
                "amount_a": None,
                "amount_b": row.get(f"{amount_col}_b"),
            })

        else:  # both
            amt_a = row.get(f"{amount_col}_a")
            amt_b = row.get(f"{amount_col}_b")
            if pd.notna(amt_a) and pd.notna(amt_b):
                if abs(float(amt_a) - float(amt_b)) > tolerance:
                    exceptions.append({
                        key: row[key],
                        "reason": f"Amount mismatch: {amt_a} vs {amt_b} "
                                  f"(diff {abs(float(amt_a) - float(amt_b)):.2f})",
                        "amount_a": amt_a,
                        "amount_b": amt_b,
                    })

    return pd.DataFrame(exceptions)


def summarize(exceptions: pd.DataFrame) -> dict:
    """Quick summary stats for the exception set."""
    if exceptions.empty:
        return {"total_exceptions": 0}

    return {
        "total_exceptions": len(exceptions),
        "missing_in_b": int((exceptions["reason"]
                             .str.contains("missing in Source B")).sum()),
        "missing_in_a": int((exceptions["reason"]
                             .str.contains("missing in Source A")).sum()),
        "amount_mismatches": int((exceptions["reason"]
                                  .str.contains("Amount mismatch")).sum()),
    }