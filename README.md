# 🔍 AI Reconciliation Agent

Automated data reconciliation with AI-explained exceptions. Upload two
datasets (e.g., invoices vs. ledger); the tool identifies missing records
and amount mismatches, then uses an LLM to explain each discrepancy in
plain English and suggest a resolution.

**Live demo:** _add your Streamlit Cloud link here_

---

## The problem
Finance and operations teams spend hours manually reconciling data across
systems. Errors are easy to miss and hard to trace.

## The approach
- **Deterministic matching core** (Python/pandas): reproducible, auditable
  logic detects missing records and amount mismatches. The LLM never
  decides matches.
- **AI explanation layer** (Claude): converts each raw exception into a
  plain-English explanation with a suggested action.
- **Streamlit UI**: upload files, review exceptions, download a report.

> Design choice: keeping matching deterministic and using AI only for
> explanation is deliberate — financial reconciliation must be reproducible.

## Results / value
- Eliminates manual line-by-line reconciliation.
- Produces an auditable, downloadable exception report in seconds.
- Plain-English explanations reduce the expertise needed to act on results.

## Tech stack
Python · pandas · Streamlit · Anthropic (Claude)

## Run locally
```bash
git clone https://github.com/deepanshug4/ai-reconciliation-agent.git
cd ai-reconciliation-agent
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY (optional)
streamlit run app.py