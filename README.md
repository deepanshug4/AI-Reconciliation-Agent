# 🔍 AI Reconciliation Agent

**Automated, auditable data reconciliation with materiality-based prioritization and AI-explained exceptions.**

Upload two datasets that *should* agree (e.g., invoices vs. bank ledger). The tool validates data quality, matches records, flags every discrepancy, ranks them by financial impact, and produces a stakeholder-ready summary — in seconds.

🔗 **Live demo:** https://ai-reconciliation-agent.streamlit.app/
<img width="1907" height="998" alt="Screenshot 2026-07-26 000341" src="https://github.com/user-attachments/assets/885bd47b-a4fb-44a9-a165-970e25e38a36" />


---

## The problem

Finance and operations teams routinely reconcile data across disconnected systems — payments vs. orders, vendor statements vs. accounts payable, internal records vs. filings. Done manually, this is slow, error-prone, and hard to audit. Small discrepancies hide in thousands of rows, and no one knows which ones actually matter.

## The approach

This tool automates reconciliation while staying **auditable and business-focused**:

- **Deterministic matching core** — record matching is 100% reproducible Python. The LLM is *never* used to decide matches, only to explain them. Financial reconciliation must be auditable, so this separation is deliberate.
- **Data-quality checks first** — duplicate keys, blank/non-numeric amounts, and missing columns are surfaced *before* reconciliation, so results can be trusted.
- **Materiality-based severity** — exceptions are scored and ranked by the dollar value at stake, so teams triage what matters instead of drowning in a flat list.
- **Business insights, not just a diff** — an executive summary quantifies total financial exposure, % of value unreconciled, and match rate.
- **AI explanation layer (optional)** — converts each exception into a plain-English explanation with a suggested resolution.

## What it detects

| Exception type | Meaning |
|---|---|
| Missing in Source B | Record exists in A but not B (e.g., billed but not paid) |
| Missing in Source A | Record exists in B but not A (e.g., unexpected payment) |
| Amount mismatch | Same record, differing amounts beyond tolerance |

Each exception is tagged **High / Medium / Low** severity based on financial materiality.

## Key features

- ✅ Data-quality validation before processing
- 🔑 Configurable matching on **single or composite keys**
- 🎚️ Both **absolute and percentage** amount tolerances
- 📊 Materiality-based severity scoring & prioritized output
- 📈 Executive summary + visual breakdown (exceptions by type, discrepancy distribution)
- 🤖 Optional AI-generated explanations (graceful fallback when no API key is set)
- ⬇️ One-click exception report export (CSV)

## Design principle: why matching is deterministic

A common shortcut is to let an LLM "figure out" what matches. For financial data this is unacceptable — results must be reproducible and defensible in an audit. Here, matching logic is pure Python; the LLM is confined to *explaining* results a human can already verify. This mirrors how these systems should be built in production.

## Tech stack

Python · pandas · Streamlit · Plotly · Anthropic (Claude, optional)

## Project structure
```
ai-reconciliation-agent/

├── README.md
├── requirements.txt
│
├── data/
│   ├── sample_a.csv
│   ├── sample_b.csv
│
├── src/
│   ├── explain.py
│   ├── insights.py
│   ├── quality.py
│   └── reconcile.py
│
└── app.py
```

## Run locally

```bash
git clone https://github.com/deepanshug4/ai-reconciliation-agent.git
cd ai-reconciliation-agent

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py

The app runs fully without an API key — AI explanations fall back to a deterministic message, so the demo always works.
```

## Enabling AI explanations (optional)
Set an ANTHROPIC_API_KEY (via a local .env file or Streamlit secrets) to enable real AI-generated explanations.

## Sample data
Sample files in data/ demonstrate all three exception types with easily verifiable numbers, so you can confirm the tool's output by eye.
