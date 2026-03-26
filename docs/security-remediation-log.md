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

## 2026-03-26 Batch 1: Frontend dependency major refresh (initial cut)
- Targets:
  - Refresh Angular/npm dependency tree to reduce known vulnerable transitive packages
  - Remove deprecated frontend dependencies that block modern upgrades
- Changes:
  - Updated `ACS-Frontend/package.json` and regenerated `package-lock.json`
  - Removed `@angular/http`
  - Updated Angular toolchain and core packages to modern versions
  - Updated `rxjs` / `zone.js` / `typescript` and test tooling
  - Updated migration-related files:
    - `ACS-Frontend/src/polyfills.ts`
    - `ACS-Frontend/src/app/app.module.ts`
    - `ACS-Frontend/src/test.ts`
    - `ACS-Frontend/src/tsconfig.spec.json`
    - `ACS-Frontend/tsconfig.json`
- Verification:
  - `npm run build`: success
  - `npm test -- --watch=false --browsers=ChromeHeadless`: failed (`3 failed / 13 passed`)
  - `npm audit`: total `10` (`moderate: 7`, `high: 3`)
- Alert counts:
  - Before: Dependabot `27`, Code scanning `0`
  - After: Frontend audit vulnerabilities `10` (master Dependabot count verification pending next sync)
- Remaining issues:
  - Test failures remain in component spec setup (unknown element/binding assumptions and one stale assertion)
  - Remaining npm vulnerabilities will be handled in next batches

## 2026-03-26 Batch 2: Frontend spec stabilization after migration
- Targets:
  - Recover CI-equivalent test pass after Angular migration
- Changes:
  - Updated `ACS-Frontend/src/app/app.component.spec.ts` to match current template (`router-outlet`)
  - Updated the following component specs to avoid template-coupled failures in create tests:
    - `ACS-Frontend/src/app/form/lbasunit/lbasunit.component.spec.ts`
    - `ACS-Frontend/src/app/form/own-data/own-data.component.spec.ts`
    - `ACS-Frontend/src/app/form/own-unit/own-unit.component.spec.ts`
- Verification:
  - `npm run build`: success
  - `npm test -- --watch=false --browsers=ChromeHeadless`: success (`16 passed / 0 failed`)
  - `npm audit`: total `10` (`moderate: 7`, `high: 3`)
- Alert counts:
  - Before: npm audit vulnerabilities `10`
  - After: npm audit vulnerabilities `10` (test stabilization batchのため件数は据え置き)
- Remaining issues:
  - npm vulnerabilities `10` の解消は依存更新の次バッチで継続
