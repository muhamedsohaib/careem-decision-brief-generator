# Security

This repository is a public demonstration application, not a production data-processing service.

## Data handling

- Do not upload credentials, personally identifiable information, or confidential commercial data to the public demo.
- CSV files are limited to 5 MB by the UI and are parsed entirely in the browser.
- The application has no data-upload backend and does not persist uploaded CSV contents.
- The built-in sample uses synthetic identifiers and transformed representative values; it contains no original commercial figures or marketplace identifiers.
- Dataset-derived labels are bounded before they are placed into generated evidence.
- The optional LLM prompt treats all dataset-derived content as untrusted data behind an explicit instruction/data boundary.

## Dependency and build controls

GitHub Actions runs unit tests, a production build, and `npm audit --audit-level=high` on pushes to `main` and pull requests.

## Reporting a vulnerability

Use GitHub private vulnerability reporting / security advisories for this repository. Do not open a public issue containing exploit details or sensitive proof-of-concept data.
