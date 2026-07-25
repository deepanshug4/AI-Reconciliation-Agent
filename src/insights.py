"""
Turns raw exceptions into a business-level summary. This is the layer
that makes the tool INFORMATIVE rather than just a diff — it answers
'so what?' the way a stakeholder would ask.
"""

import pandas as pd


def build_summary(exceptions: pd.DataFrame, df_a: pd.DataFrame,
                  df_b: pd.DataFrame, amount_col: str = "amount") -> dict:
    total_rows = max(len(df_a), len(df_b))
    total_a = pd.to_numeric(df_a.get(amount_col), errors="coerce").sum()

    if exceptions.empty:
        return {
            "total_exceptions": 0,
            "total_exposure": 0.0,
            "pct_value_unreconciled": 0.0,
            "largest_discrepancy": 0.0,
            "high_severity": 0,
            "match_rate": 100.0,
        }

    exposure = exceptions["discrepancy"].fillna(0).abs().sum()
    return {
        "total_exceptions": len(exceptions),
        "total_exposure": float(exposure),
        "pct_value_unreconciled": float(exposure / total_a * 100) if total_a else 0.0,
        "largest_discrepancy": float(exceptions["discrepancy"].fillna(0).abs().max()),
        "high_severity": int((exceptions["severity"] == "High").sum()),
        "match_rate": float((1 - len(exceptions) / total_rows) * 100) if total_rows else 0.0,
    }


def executive_summary_text(summary: dict) -> str:
    """A deterministic, paste-into-an-email exec summary. Always available."""
    if summary["total_exceptions"] == 0:
        return ("Reconciliation complete: both sources match fully. "
                "No exceptions or financial exposure identified.")
    return (
        f"Reconciliation identified **{summary['total_exceptions']} exceptions** "
        f"with a total financial exposure of **${summary['total_exposure']:,.2f}** "
        f"({summary['pct_value_unreconciled']:.1f}% of total value). "
        f"**{summary['high_severity']}** are high-severity. "
        f"The largest single discrepancy is **${summary['largest_discrepancy']:,.2f}**. "
        f"Overall match rate: **{summary['match_rate']:.1f}%**. "
        f"Recommend prioritizing high-severity items for immediate review."
    )
