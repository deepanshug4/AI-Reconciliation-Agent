"""
AI Reconciliation Agent — Streamlit UI.

Run locally:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from src.reconcile import reconcile, summarize
from src.explain import explain_exception

st.set_page_config(page_title="AI Reconciliation Agent", layout="wide")

st.title("🔍 AI Reconciliation Agent")
st.caption(
    "Deterministic matching + AI-explained exceptions. "
    "Matching logic is fully reproducible; AI is used only to explain results."
)

with st.expander("ℹ️ How it works / How to use"):
    st.markdown(
        """
        1. Upload two CSV files (e.g., **invoices** and **ledger**).
        2. Both files must share a **key column** (default: `transaction_id`)
           and an **amount column** (default: `amount`).
        3. The engine flags: missing records and amount mismatches.
        4. Optionally, enable **AI explanations** for plain-English resolutions.

        *Tip:* Try the sample files in the `data/` folder.
        """
    )

col1, col2 = st.columns(2)
file_a = col1.file_uploader("Source A (e.g., invoices)", type="csv")
file_b = col2.file_uploader("Source B (e.g., ledger)", type="csv")

c1, c2, c3 = st.columns(3)
key = c1.text_input("Match key column", value="transaction_id")
amount_col = c2.text_input("Amount column", value="amount")
tolerance = c3.number_input("Amount tolerance", value=0.01, step=0.01, format="%.2f")

use_ai = st.checkbox("Generate AI explanations (uses API key if set)", value=False)

if file_a and file_b:
    try:
        df_a = pd.read_csv(file_a)
        df_b = pd.read_csv(file_b)
    except Exception as e:
        st.error(f"Could not read the CSV files: {e}")
        st.stop()

    try:
        exceptions = reconcile(
            df_a, df_b, key=key, amount_col=amount_col, tolerance=tolerance
        )
    except ValueError as e:
        st.error(str(e))
        st.stop()

    stats = summarize(exceptions)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total exceptions", stats.get("total_exceptions", 0))
    m2.metric("Missing in B", stats.get("missing_in_b", 0))
    m3.metric("Missing in A", stats.get("missing_in_a", 0))
    m4.metric("Amount mismatches", stats.get("amount_mismatches", 0))

    if exceptions.empty:
        st.success("✅ No exceptions found — the sources reconcile cleanly.")
    else:
        if use_ai:
            with st.spinner("Generating AI explanations..."):
                exceptions["ai_explanation"] = exceptions.apply(
                    lambda r: explain_exception(r.to_dict()), axis=1
                )

        st.subheader("Exceptions")
        st.dataframe(exceptions, use_container_width=True)

        st.download_button(
            "⬇️ Download exception report (CSV)",
            exceptions.to_csv(index=False),
            file_name="exceptions.csv",
            mime="text/csv",
        )
else:
    st.info("Upload both files to begin. Or load the sample files from `data/`.")