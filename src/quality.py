"""
Input data-quality checks. Run BEFORE reconciliation so users trust
the results. Real reconciliation fails silently on dirty data — surfacing
these issues up front is what an experienced analyst does.
"""

import pandas as pd


def check_quality(df: pd.DataFrame, keys: list[str], amount_col: str, source_name: str) -> list[dict]:
    """Return a list of data-quality findings for one source."""
    findings = []

    # Missing columns
    for col in keys + [amount_col]:
        if col not in df.columns:
            findings.append({
                "source": source_name, "severity": "High",
                "issue": f"Missing required column '{col}'",
            })
    if findings:  # can't check further without required columns
        return findings

    # Duplicate keys (breaks 1:1 matching)
    dupes = df.duplicated(subset=keys, keep=False).sum()
    if dupes:
        findings.append({
            "source": source_name, "severity": "High",
            "issue": f"{dupes} rows have duplicate keys (may cause mismatched joins)",
        })

    # Blank / null amounts
    blank_amt = df[amount_col].isna().sum()
    if blank_amt:
        findings.append({
            "source": source_name, "severity": "Medium",
            "issue": f"{blank_amt} rows have a blank/null amount",
        })

    # Non-numeric amounts
    coerced = pd.to_numeric(df[amount_col], errors="coerce")
    non_numeric = coerced.isna().sum() - blank_amt
    if non_numeric > 0:
        findings.append({
            "source": source_name, "severity": "High",
            "issue": f"{non_numeric} rows have non-numeric amounts",
        })

    # Blank keys
    for k in keys:
        blank_keys = df[k].isna().sum()
        if blank_keys:
            findings.append({
                "source": source_name, "severity": "Medium",
                "issue": f"{blank_keys} rows have a blank key in '{k}'",
            })

    return findings
