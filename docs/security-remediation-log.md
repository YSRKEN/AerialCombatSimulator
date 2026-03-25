# Security Remediation Log

## 2026-03-26 Batch 0: Baseline and build-noise stabilization
- Targets:
  - Operational baseline for alert remediation workflow
  - Maven log-noise reduction in normal builds
- Changes:
  - Added `docs/security-remediation-plan.md`
  - Added this log file
  - Updated `ACS-Server/pom.xml`:
    - Added Maven prerequisite `3.6.3`
    - Removed `versions-maven-plugin` from default compile phase
    - Added manual profile `dependency-updates` with `versions-maven-plugin:2.21.0`
- Verification:
  - Server build commands remain available: `mvn test`, `mvn package`, `mvn appengine:run`
  - Dependency update report can be run manually with profile:
    - `mvn -Pdependency-updates versions:display-dependency-updates versions:display-plugin-updates`
- Alert counts:
  - Before: Dependabot `27`, Code scanning `0`
  - After: Pending frontend remediation batches
- Remaining issues:
  - All 27 open alerts are npm alerts in `ACS-Frontend`
