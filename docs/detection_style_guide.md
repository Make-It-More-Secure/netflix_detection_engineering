# Detection Style Guide

## Principles
- Optimize for high-risk attack paths and business impact.
- Make detections testable and explainable.
- Prefer high-confidence signals; document expected false positives.
- Every detection must be tunable (allowlists, thresholds, suppression).

## Required rule fields (YAML)
- id: stable UUID (never reuse)
- name: human-readable name
- description: what and why
- severity: low|medium|high|critical
- risk_score: 0-100
- data_sources: e.g., cloudtrail, auth_logs
- mitre_attack:
  - tactic:
  - technique:
- tags: e.g., aws, iam, persistence
- owner: team or handle
- runbook: link/path to triage steps
- false_positives: list of known benign causes
- tuning:
  - allowlist: lookup/macro name or file path
  - thresholds: numeric params
  - suppression_key: fields to dedupe on

## Required alert fields
- alert_id
- rule_id / rule_name
- created_at
- severity / risk_score
- entities: users, roles, IPs, accounts, resources
- evidence: minimal fields to support triage
- raw_event_refs: pointer or hash, not full blobs when possible

## Naming conventions
- Rules: `AWS - IAM - Suspicious AccessKey Creation`
- Files: `aws_iam_suspicious_access_key_creation.yml`

## Tuning guidance
- Always include at least one suppression strategy:
  - suppression_key: e.g., (user, account, region, action) per 1h
- Document allowlist approach:
  - e.g., break-glass roles, CI principals, known automation accounts