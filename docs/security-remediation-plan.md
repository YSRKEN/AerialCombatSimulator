# Security Remediation Plan (master)

## Goal
- Dependabot open alerts: `0`
- Code scanning open alerts: `0`
- Scope: `origin/master` only

## Current Snapshot (2026-03-26 JST)
- Dependabot open: `27`
- Code scanning open: `0`
- Ecosystem: npm only (`ACS-Frontend/package-lock.json`)

## Priority
1. Documentation and reproducible tracking
2. Frontend Angular major upgrades (6 -> latest stable)
3. Removal of legacy/vulnerable dependency chains
4. Build and runtime verification for each batch

## Rules
- One PR per theme.
- No `dismiss` unless technically impossible to remediate.
- Each batch must update `docs/security-remediation-log.md` with:
  - Target alerts
  - Changes
  - Verification commands/results
  - Before/After counts

## Validation Commands
- Frontend: `npm install`, `npm run build`, `npm test`, `npm audit`
- Server: `mvn test`, `mvn package`
- Alert check:
  - `gh api /repos/YSRKEN/AerialCombatSimulator/dependabot/alerts?state=open`
  - `gh api /repos/YSRKEN/AerialCombatSimulator/code-scanning/alerts?state=open`
