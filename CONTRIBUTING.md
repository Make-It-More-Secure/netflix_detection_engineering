# Contributing

## Workflow
1. Create a feature branch.
2. Add/modify detections with required metadata.
3. Add/modify tests and fixtures.
4. Run locally:
   - `make lint`
   - `make test`
   - `make detections-test` (if applicable)
5. Open a PR with:
   - what changed
   - expected impact
   - tuning notes / false positives

## Adding a new detection
1. Copy the template rule.
2. Fill in required metadata.
3. Add test fixtures (positive + negative).
4. Add detection logic module (if Python-based).
5. Verify CI passes.

## Code quality
- Use ruff/black conventions.
- Prefer small functions with clear names.
- Add docstrings for detection logic.