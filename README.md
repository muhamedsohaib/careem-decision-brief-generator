# Decision Brief Generator

An evidence-first operations tool that turns raw CSV data into a decision brief without allowing the narrative layer to invent facts.

The application separates **measurement**, **inference**, and **action**. Calculations are deterministic; the optional AI reasoning prompt receives only evidence already computed by the engine and explicitly treats dataset-derived text as untrusted data.

## What it demonstrates

- Schema-based analysis mode detection rather than filename-based routing
- Safe CSV parsing with a 5 MB upload limit
- Explicit data-quality checks before recommendations are produced
- KPI selection based on business semantics rather than the first numeric column
- Currency-aware display for AED, SAR, USD, EUR, and GBP when the currency can be inferred
- Chronological comparisons only when a usable date field exists
- Separate observed facts, hypotheses, recommended actions, and unknowns
- Fail-closed behavior when duplicate entity records conflict
- Bounded dataset labels plus an explicit instruction/data boundary for the optional LLM prompt
- Downloadable decision brief generated from the active dataset

## Sanitized operating sample

The built-in Amazon operations sample preserves a representative inventory/revenue decision pattern while protecting the underlying business data.

Identifiers are synthetic and **all numerical values have been transformed**. The sample does not contain original revenue, units, stock, target-stock values, ASINs, SKUs, listing IDs, product names, customer information, or credentials.

The included fields are:

```text
product_id
revenue_aed
units
current_stock
target_stock
tier
```

The sample is intended to demonstrate the decision logic, not reproduce a commercial dataset.

## Architecture

```text
CSV / transformed sample
        ↓
Safe parsing and schema profiling
        ↓
Data-quality gate
        ↓
Deterministic KPI calculations
        ↓
Observed facts
        ↓
Hypotheses + evidence-backed actions
        ↓
Optional evidence-constrained LLM prompt
        ↓
Human decision
```

The LLM layer is deliberately downstream of the calculations. It can be used for compression, explanation, and decision framing; it is not trusted to calculate revenue, detect stockouts, establish causality, or override the deterministic guardrails.

## Safety rules

The engine blocks recommendations when it finds conflicting records for the same entity. It avoids time-based claims when no usable date field exists and avoids percentage-share calculations when the denominator is zero.

Dataset-derived labels are collapsed to bounded single-line values before they are used in generated evidence. The optional reasoning prompt serializes evidence as JSON inside a marked untrusted-data boundary and tells the model never to follow instructions that appear inside dataset values.

A reviewer can enable **Demonstrate safety gate** in the sidebar. This injects a conflicting duplicate into the transformed sample and shows the application refusing to produce an operational action until the conflict is resolved.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Verification

Install the development dependencies and run the same core gates used by CI:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
python -m py_compile analysis_engine.py streamlit_app.py
```

CI also boots Streamlit headlessly and checks its health endpoint so a passing workflow verifies more than syntax alone.

The regression suite covers dynamic stockout decisions, conflicting duplicates, row-order-independent chronological comparisons, zero denominators, tiny datasets, quoted commas in CSV values, file-size enforcement, non-numeric datasets, unrelated schemas, formatted business numbers, currency inference, and prompt-injection boundary handling.

## Privacy and deployment

A public Streamlit deployment is a server-side application. Do not upload credentials, personally identifiable information, or confidential commercial data. See [SECURITY.md](SECURITY.md) for the repository's data-handling expectations.

## Limits

This prototype does not claim causal effects or forecast financial uplift from the supplied snapshot. For inventory decisions, supplier lead time, contribution margin, demand while unavailable, and inbound inventory remain explicit unknowns until provided.

## License

Copyright © 2026 Muhammad Sohaib. This repository is public for evaluation, portfolio review, and demonstration; see [LICENSE](LICENSE) for the applicable terms.
