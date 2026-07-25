"""
Deterministic reconciliation engine.

Upgrades over the basic version:
  - Composite keys (match on one OR multiple columns)
  - Absolute AND percentage amount tolerance
  - Severity scoring based on financial materiality
The LLM is still never used for matching — only explanation.
"""

import pandas as pd


def _severity(amount: float, thresholds=(1000, 100)) -> str:
    """Rank an exception by the dollar value at stake."""
    a = abs(amount or 0)
    if a >= thresholds[0]:
        return "High"
    if a >= thresholds[1]:
        return "Medium"
    return "Low"


def reconcile(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    keys: list[str],
    amount_col: str = "amount",
    abs_tolerance: float = 0.01,
    pct_tolerance: float = 0.0,
) -> pd.DataFrame:
    """
    Reconcile two datasets on one or more keys.

    Detects:
      1. Present in A, missing in B
      2. Present in B, missing in A
      3. Amount mismatch beyond BOTH absolute and % tolerance

    Returns a DataFrame of exceptions with materiality + severity.
    """
    # Coerce amounts to numeric so dirty data doesn't crash the join.
    df_a = df_a.copy()
    df_b = df_b.copy()
    df_a[amount_col] = pd.to_numeric(df_a[amount_col], errors="coerce")
    df_b[amount_col] = pd.to_numeric(df_b[amount_col], errors="coerce")

    merged = df_a.merge(
        df_b, on=keys, how="outer", suffixes=("_a", "_b"), indicator=True
    )

    exceptions = []
    key_repr = lambda row: " | ".join(str(row[k]) for k in keys)

    for _, row in merged.iterrows():
        flag = row["_merge"]

        if flag == "left_only":
            amt = row.get(f"{amount_col}_a")
            exceptions.append({
                "key": key_repr(row), "type": "Missing in Source B",
                "amount_a": amt, "amount_b": None,
                "discrepancy": amt, "severity": _severity(amt),
                "reason": "Record exists in Source A but not Source B",
            })

        elif flag == "right_only":
            amt = row.get(f"{amount_col}_b")
            exceptions.append({
                "key": key_repr(row), "type": "Missing in Source A",
                "amount_a": None, "amount_b": amt,
                "discrepancy": amt, "severity": _severity(amt),
                "reason": "Record exists in Source B but not Source A",
            })

        else:  # both
            amt_a = row.get(f"{amount_col}_a")
            amt_b = row.get(f"{amount_col}_b")
            if pd.notna(amt_a) and pd.notna(amt_b):
                diff = abs(float(amt_a) - float(amt_b))
                base = max(abs(float(amt_a)), abs(float(amt_b)), 1e-9)
                pct_diff = diff / base * 100
                # Flag only if it breaks BOTH tolerances.
                if diff > abs_tolerance and pct_diff > pct_tolerance:
                    exceptions.append({
                        "key": key_repr(row), "type": "Amount mismatch",
                        "amount_a": amt_a, "amount_b": amt_b,
                        "discrepancy": diff, "severity": _severity(diff),
                        "reason": f"Amounts differ by {diff:.2f} ({pct_diff:.1f}%)",
                    })

    cols = ["key", "type", "severity", "amount_a", "amount_b",
            "discrepancy", "reason"]
    result = pd.DataFrame(exceptions)
    if result.empty:
        return pd.DataFrame(columns=cols)
    # Sort so the most material exceptions surface first.
    sev_order = {"High": 0, "Medium": 1, "Low": 2}
    result["_sev"] = result["severity"].map(sev_order)
    result = result.sort_values(
        ["_sev", "discrepancy"], ascending=[True, False]
    ).drop(columns="_sev")
    return result[cols].reset_index(drop=True)
