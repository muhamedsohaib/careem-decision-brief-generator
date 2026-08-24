# Careem Decision Brief Generator

**Careem Challenge Selected: #1 â€” Decision Brief Generator**

> Create a tool that turns raw data into summaries and recommended business actions.

**Live prototype:** https://careem-decision-brief-generator-nalpmx.v2.appdeploy.ai/

## Submission summary

I built an evidence-first Decision Brief Generator that converts raw operational CSV data into a concise business decision brief. The tool identifies metrics, calculates operating performance, checks data quality, separates observed facts from hypotheses, and recommends next actions. Users can explore a transformed Amazon operations sample or upload a CSV and change the primary KPI to see the analysis update dynamically. Conflicting data blocks recommendations rather than allowing unsupported conclusions. Calculations happen deterministically before the AI reasoning layer, so AI is used for explanation and decision framing rather than inventing metrics, replacing evidence, or taking authority from the human operator.

## What the prototype does

- Loads a transformed representative Amazon operations sample or a CSV uploaded in the browser.
- Detects the analysis mode from the schema rather than the filename.
- Selects a business-relevant primary KPI and recalculates when the KPI changes.
- Infers AED, USD, SAR, EUR, and GBP when the currency is unambiguous.
- Produces an executive summary, observed facts, hypotheses, recommended actions, and explicit unknowns.
- Fails closed when duplicate entity records conflict.
- Generates a downloadable decision brief from the active dataset.
- Provides an optional evidence-constrained LLM prompt with a clear instruction/data boundary.

## Data and privacy

The built-in sample is representative and transformed. Product IDs are synthetic and the numerical values are not original commercial figures. It contains no ASINs, SKUs, listing IDs, product names, customer information, credentials, or confidential marketplace data.

CSV uploads are processed entirely in the browser by the deployed prototype and are not sent to an application backend. The UI limits uploads to 5 MB. Do not upload credentials, personally identifiable information, or confidential commercial data to any public demo.

## Architecture

```text
CSV / transformed sample
        â†“
Browser-side parsing and schema profiling
        â†“
Data-quality gate
        â†“
Deterministic KPI calculations
        â†“
Executive summary + observed facts
        â†“
Hypotheses + evidence-backed actions
        â†“
Optional evidence-constrained LLM prompt
        â†“
Human decision
```

The optional prompt is downstream of the calculations. It is not trusted to calculate revenue, detect stockouts, establish causality, or override the deterministic guardrails.

## Run locally

```bash
npm ci
npm run dev
```

## Verification

```bash
npm run typecheck
npm test
npm run build
npm audit --audit-level=high
```

GitHub Actions runs the same test, build, and dependency-audit gates on pushes to `main` and on pull requests.

## Limits

This prototype does not claim causal effects or forecast financial uplift from a snapshot. For inventory decisions, supplier lead time, contribution margin, demand while unavailable, and inbound inventory remain explicit unknowns until provided.

## License

Copyright Â© 2026 Muhammad Sohaib. See [LICENSE](LICENSE) for the applicable terms.
