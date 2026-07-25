"""AI Reconciliation Agent — upgraded UI with quality checks, insights, and charts."""

import streamlit as st
import pandas as pd
import plotly.express as px

from src.quality import check_quality
from src.reconcile import reconcile
from src.insights import build_summary, executive_summary_text
from src.explain import explain_exception

st.set_page_config(page_title="AI Reconciliation Agent", layout="wide")
st.title("🔍 AI Reconciliation Agent")
st.caption("Deterministic, auditable reconciliation with data-quality checks, "
           "materiality-based severity scoring, and business insights.")

with st.expander("ℹ️ What this does"):
    st.markdown(
        "- Validates input data quality before reconciling\n"
        "- Matches records on one or more keys with configurable tolerances\n"
        "- Scores exceptions by **financial materiality**\n"
        "- Produces an executive summary and visual breakdown\n\n"
        "*Matching is fully deterministic; AI is used only to explain exceptions.*"
    )

col1, col2 = st.columns(2)
file_a = col1.file_uploader("Source A (e.g., invoices)", type="csv")
file_b = col2.file_uploader("Source B (e.g., ledger)", type="csv")

if file_a and file_b:
    df_a, df_b = pd.read_csv(file_a), pd.read_csv(file_b)

    st.sidebar.header("⚙️ Configuration")
    common_cols = [c for c in df_a.columns if c in df_b.columns]
    keys = st.sidebar.multiselect("Match key column(s)", common_cols,
                                  default=common_cols[:1])
    amount_col = st.sidebar.selectbox("Amount column", common_cols,
                                      index=min(1, len(common_cols) - 1))
    abs_tol = st.sidebar.number_input("Absolute tolerance", value=0.01, step=0.01)
    pct_tol = st.sidebar.number_input("Percentage tolerance (%)", value=0.0, step=0.5)
    use_ai = st.sidebar.checkbox("AI explanations (uses key if set)", value=False)

    if not keys:
        st.warning("Select at least one match key in the sidebar.")
        st.stop()

    # --- Data quality ---
    findings = (check_quality(df_a, keys, amount_col, "Source A")
                + check_quality(df_b, keys, amount_col, "Source B"))

    tab1, tab2, tab3 = st.tabs(["📋 Summary", "⚠️ Exceptions", "🧪 Data Quality"])

    exceptions = reconcile(df_a, df_b, keys, amount_col, abs_tol, pct_tol)
    summary = build_summary(exceptions, df_a, df_b, amount_col)

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Match rate", f"{summary['match_rate']:.1f}%")
        c2.metric("Exceptions", summary["total_exceptions"])
        c3.metric("Financial exposure", f"${summary['total_exposure']:,.2f}")
        c4.metric("High severity", summary["high_severity"])
        st.markdown("#### Executive Summary")
        st.info(executive_summary_text(summary))

        if not exceptions.empty:
            colA, colB = st.columns(2)
            by_type = exceptions["type"].value_counts().reset_index()
            by_type.columns = ["type", "count"]
            colA.plotly_chart(
                px.bar(by_type, x="type", y="count", title="Exceptions by type"),
                use_container_width=True)
            colB.plotly_chart(
                px.histogram(exceptions, x="discrepancy",
                             title="Distribution of discrepancy amounts"),
                use_container_width=True)

    with tab2:
        if exceptions.empty:
            st.success("✅ No exceptions — sources reconcile cleanly.")
        else:
            if use_ai:
                with st.spinner("Generating AI explanations..."):
                    exceptions["ai_explanation"] = exceptions.apply(
                        lambda r: explain_exception(r.to_dict()), axis=1)
            st.dataframe(exceptions, use_container_width=True)
            st.download_button("⬇️ Download exception report",
                               exceptions.to_csv(index=False),
                               "exceptions.csv", "text/csv")

    with tab3:
        if findings:
            st.warning(f"{len(findings)} data-quality issue(s) found:")
            st.dataframe(pd.DataFrame(findings), use_container_width=True)
        else:
            st.success("✅ No data-quality issues detected in either source.")
else:
    st.info("Upload both files to begin.")
