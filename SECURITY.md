# Security

This repository is a demonstration application and must not be treated as a production data-processing service.

## Data handling

- Do not upload credentials, personally identifiable information, or confidential commercial data to a public deployment.
- CSV uploads are limited to 5 MB and are processed in the active Streamlit server session.
- The built-in sample uses transformed representative values and contains no marketplace identifiers or original commercial figures.
- The optional LLM prompt is generated only from deterministic analysis output and places dataset-derived text behind an explicit instruction/data boundary.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting / security advisory flow for this repository rather than opening a public issue with exploit details.
