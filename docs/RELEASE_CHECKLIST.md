# VulnoraIQ Release Checklist

> **Current target:** `0.2.0` / `0.2.0-rc1`  
> **Scope:** self-hosted laptop/server production-readiness release  
> **Last updated:** 2026-06-23

This checklist must be completed before tagging a production-readiness release candidate or final release.

## Release boundary

`0.2.0` may be described as:

> Self-hosted laptop/server AI security testing application with controlled internal production-readiness gate passed.

GenAI-specific wording may say:

> GenAI Security readiness gate completed for controlled internal assessment use with safe synthetic `DSGAI01–DSGAI21` scenario coverage.

Do **not** describe `0.2.0` as certified VAPT-grade ready or independently production-validated for every GenAI category.

## Pre-release requirements

- [ ] All planned release changes are merged or intentionally deferred.
- [ ] `README.md`, `SECURITY.md`, `CHANGELOG.md`, and `docs/` are aligned with current maturity.
- [ ] `docs/PRODUCTION_READINESS_SCORECARD.md` and `docs/PRODUCTION_HARDENING_BACKLOG.md` do not contradict each other.
- [ ] `docs/genai/PRODUCTION_READINESS_PLAN.md` reflects the current GenAI Security phase gate status.
- [ ] `docs/AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md` reflects the current Agentic Applications phase gate status.
- [ ] `docs/ASSESSMENT_ASSURANCE.md` clearly states scanner/evaluator limitations.
- [ ] Local launcher mode is documented as loopback-only and separate from production mode.
- [ ] Release artifact build process is documented in `docs/RELEASE_ARTIFACTS.md`.
- [ ] Python package publishing process is documented in `docs/PYPI_PACKAGE.md`.
- [ ] No P0/P1 release blockers remain.
- [ ] Known accepted risks are documented.
- [ ] CI is green on the release branch or `main`.

## Versioning

VulnoraIQ uses semantic versioning:

```text
MAJOR.MINOR.PATCH[-PRERELEASE]
```

Recommended flow for this release:

1. Tag `v0.2.0-rc1` after a clean local and CI validation pass.
2. Run one release-candidate validation cycle.
3. Publish a GitHub Release for the RC only when release artifacts should be built.
4. Tag and publish `v0.2.0` only after RC smoke, Docker smoke, backup/restore, GenAI readiness validation, launcher smoke, release artifact validation, Python package build validation, and docs review pass.

## Stage 1: version and changelog

- [ ] Confirm `pyproject.toml` version is correct.
- [ ] Confirm README maturity banner references the same version.
- [ ] Confirm `CHANGELOG.md` has a dated section for the version or clearly documents unreleased launcher/docs/release-build/package-publish changes.
- [ ] Confirm breaking changes are listed:
  - legacy `webui/server.py` removed
  - SQLite is default persistence
  - JSON backend is dev/legacy only
  - file auth disabled in production
  - `VULNORAIQ_ADMIN_TOKEN` required in production
- [ ] Confirm release notes include known limitations, including GenAI current-scope completion limitations, the launcher-mode local-only boundary, native artifact formats, unsigned macOS `.dmg` status, and the fact that signed native installers remain future maturity.

## Stage 2: local quality gates

Run:

```bash
python -m pip install -e .[dev]
ruff check .
mypy .
pytest -q
python -m pip check
pip-audit
```

Acceptance:

- [ ] Ruff passes.
- [ ] mypy passes.
- [ ] pytest passes.
- [ ] pip check passes or unrelated environment warnings are documented.
- [ ] pip-audit has no unaccepted high/critical runtime vulnerabilities.

## Stage 3: package, mapping, GenAI, and readiness validation

Run:

```bash
python scripts/validate_package_metadata.py
python scripts/validate_owasp_atlas_mappings.py
python scripts/validate_genai_readiness.py
python scripts/validate_production_testing_readiness.py
python scripts/validate_runtime_production_config.py
python scripts/validate_production_testing_readiness.py \
  --run-functional \
  --output-dir reports/output/production-readiness
```

Acceptance:

- [ ] Package metadata validation passes.
- [ ] OWASP/ATLAS mapping metadata validation passes.
- [ ] GenAI readiness validation passes.
- [ ] Production readiness validation passes all checks.
- [ ] Runtime production config validation passes under a valid production env.
- [ ] Functional acceptance passes.
- [ ] Dashboard example asset remains refreshed.

## Stage 4: Web UI and standalone launcher smoke test

Manual or scripted checks:

- [ ] `python launch-vulnoraiq-webui.py --no-browser` starts on loopback.
- [ ] The startup panel reports dependency checks and quick-start actions.
- [ ] The **Refresh checks** button refreshes startup status.
- [ ] The **Stop local server** button stops a launcher-mode server cleanly.
- [ ] `/healthz` returns HTTP `200`.
- [ ] `/readyz` returns HTTP `200` when config is loaded.
- [ ] `/metrics` requires auth by default in hosted/production mode.
- [ ] unauthenticated `/api/scans` returns `401` in hosted/production mode.
- [ ] valid admin token can retrieve `/api/csrf-token` in hosted/production mode.
- [ ] `POST /api/scans` without CSRF returns `403` in hosted/production mode.
- [ ] valid CSRF token allows demo scan creation.
- [ ] artifact download works for completed demo scan.
- [ ] artifact path-protection check rejects unsafe artifact paths.
- [ ] audit logs contain request IDs and do not contain tokens or request bodies.

## Stage 5: GenAI Security readiness review

Review:

- [ ] `benchmarks/fixtures/genai/scenarios.yaml` covers `DSGAI01–DSGAI21`.
- [ ] The manifest preserves the `DSGAI22–DSGAI25` source discrepancy as tracked/map-later.
- [ ] Each source-confirmed DSGAI category has secure, vulnerable, ambiguous, and edge-case fixture coverage.
- [ ] Required evidence fields include `genai_id`, `genai_risk_area`, `data_classification`, `data_surface`, `redaction_status`, `manual_review_reason`, and `mitre_atlas_tactics`.
- [ ] `core/genai_evaluators.py` exposes deterministic safe-fixture evaluators.
- [ ] `tests/test_genai_readiness_validation.py` passes.
- [ ] Docs state that GenAI coverage is complete for the current controlled-internal scenario-harness scope, not certified assurance.

## Stage 6: Docker and container smoke

Run:

```bash
docker build -t vulnoraiq:0.2.0-rc .
python scripts/container_smoke_test.py
```

Acceptance:

- [ ] Image builds successfully.
- [ ] Container runs as non-root.
- [ ] `/data` volume is used for DB/reports.
- [ ] healthcheck passes.
- [ ] production mode fails without admin token.
- [ ] production mode starts with valid admin token.

## Stage 7: backup and restore

Run on a temporary/test SQLite DB:

```bash
python scripts/backup_sqlite_store.py \
  /data/jobs.db \
  /data/backups/jobs-$(date +%Y%m%d-%H%M%S).db \
  --compress \
  --validate \
  --retention 90

python scripts/restore_sqlite_store.py \
  /data/backups/jobs-YYYYMMDD-HHMMSS.db.gz \
  /tmp/vulnoraiq-restore-test.db \
  --compressed \
  --validate
```

Acceptance:

- [ ] Backup completes.
- [ ] Backup validation passes.
- [ ] Restore completes to test DB.
- [ ] Restored DB validates.
- [ ] Restore drill result is recorded.

## Stage 8: release artifact build

The release artifact workflow is intentionally separate from normal CI. It must only run from:

- a published GitHub Release; or
- a manual `workflow_dispatch` run by a maintainer.

Local dry run for one platform:

```bash
python scripts/build_platform_release_package.py \
  --platform linux \
  --version 0.2.0-rc1 \
  --output-dir dist/release
```

Expected artifacts from the GitHub release workflow:

- [ ] `vulnoraiq-<version>-windows.zip`
- [ ] `vulnoraiq-<version>-linux.tar.gz`
- [ ] `vulnoraiq-<version>-macos.dmg`

Acceptance:

- [ ] `.github/workflows/release-build.yml` does not include `push` or `pull_request` triggers.
- [ ] Workflow artifacts upload successfully.
- [ ] Published-release runs attach artifacts to the GitHub Release.
- [ ] Archives/images include `START_HERE.txt`, platform launchers, `LICENSE`, `NOTICE`, `SECURITY.md`, `ACCEPTABLE_USE.md`, `THIRD_PARTY_NOTICES.md`, Web UI assets, docs, safe config, and source packages.
- [ ] Archives/images exclude generated reports, SQLite databases, secrets, private keys, virtual environments, build outputs, and local config.
- [ ] Linux `.tar.gz` extracts cleanly and preserves executable launcher bits.
- [ ] macOS `.dmg` mounts and contains the expected release folder.
- [ ] A platform package is extracted/mounted and smoke-tested before final release approval.

## Stage 9: Python package build and optional publish

The Python package workflow is intentionally separate from normal CI. It must only run from:

- a published GitHub Release; or
- a manual `workflow_dispatch` run by a maintainer.

Local dry run:

```bash
python -m pip install -e .[release]
python scripts/validate_package_metadata.py
python -m build
python -m twine check dist/*
```

Acceptance:

- [ ] `.github/workflows/python-package-publish.yml` does not include `push` or `pull_request` triggers.
- [ ] Wheel and source distribution build successfully.
- [ ] `twine check dist/*` passes.
- [ ] TestPyPI is used before PyPI.
- [ ] PyPI/TestPyPI publication requires manual workflow input and protected environment approval.

## Stage 10: documentation review

- [ ] README quick start is current.
- [ ] README Web UI instructions include standalone launcher, self-hosted startup, and shutdown guidance.
- [ ] `SECURITY.md` reflects `0.2.0` controls, supported versions, local launcher boundary, and production-mode expectations.
- [ ] `ACCEPTABLE_USE.md` is present and linked from security/release docs.
- [ ] `DEPLOYMENT.md` includes latest launcher files, env vars, proxy/TLS guidance, and local-vs-production boundaries.
- [ ] `RUNBOOK.md` uses real `0.2.0` commands and includes launcher troubleshooting plus GenAI readiness validation in upgrade checks.
- [ ] `RELEASE_ARTIFACTS.md` explains release-only build triggers and artifact expectations.
- [ ] `PYPI_PACKAGE.md` explains package build, TestPyPI/PyPI controls, and trusted publishing setup.
- [ ] `INCIDENT_RESPONSE.md` references current audit events, SQLite, metrics, and token/proxy auth.
- [ ] `MIGRATION.md` covers `0.0.1.x` to `0.2.0`.
- [ ] `ASSESSMENT_ASSURANCE.md` warns that findings are framework evidence, not certified VAPT assurance.
- [ ] `docs/genai/PRODUCTION_READINESS_PLAN.md` shows the current GenAI Security phase-by-phase gate status.
- [ ] `AGENTIC_APPLICATIONS_PRODUCTION_READINESS_PLAN.md` shows the current Agentic Applications phase-by-phase gate status.
- [ ] `PRODUCTION_HARDENING_BACKLOG.md` documents complete current-scope readiness and post-completion maturity items.

## Stage 11: security review

- [ ] No real secrets in repository.
- [ ] `.env.production.example` contains placeholders only.
- [ ] Production auth is fail-closed.
- [ ] Local launcher mode remains loopback-only and is not used as a shared production deployment path.
- [ ] `listen_address_safe` check is reachable in `validate_all()`.
- [ ] OWASP/ATLAS mapping metadata validator passes for active oracles/checks.
- [ ] GenAI readiness validator passes for source-confirmed GenAI scenario coverage and docs.
- [ ] Trusted proxy identity spoofing tests pass.
- [ ] CSRF, rate-limit, request-size, artifact access, metrics auth, and audit tests pass.
- [ ] Dependency audit is reviewed.
- [ ] Maintainer signs off.

## Stage 12: release candidate tag and release artifact build

```bash
git tag -a v0.2.0-rc1 -m "Release candidate v0.2.0-rc1"
git push origin v0.2.0-rc1
```

After tag:

- [ ] GitHub Actions pass for the tag.
- [ ] Release notes are generated from `CHANGELOG.md`.
- [ ] GitHub Release is published only when platform artifacts should be built.
- [ ] `Build Release Artifacts` completes successfully for Windows, Linux, and macOS.
- [ ] `Build Python Package` builds wheel/source artifacts; publish remains manual.
- [ ] RC deployment smoke is run.
- [ ] Local launcher smoke is run on at least one laptop/workstation.
- [ ] No blocker found during RC observation window.

## Stage 13: final release tag

Only after RC validation:

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

Post-release:

- [ ] GitHub Release created and published.
- [ ] Changelog copied into release notes.
- [ ] Deployment docs linked.
- [ ] Security policy linked.
- [ ] Acceptable-use policy linked.
- [ ] Known limitations clearly visible.
- [ ] Windows `.zip`, Linux `.tar.gz`, and macOS `.dmg` artifacts are attached to the GitHub Release.
- [ ] Python wheel/source artifacts are available from the package workflow; PyPI publish is approved separately.
- [ ] Smoke test run against released artifact/image.
- [ ] Logs and metrics monitored for at least one hour in the target environment.

## Rollback plan

Trigger rollback for:

- auth bypass or fail-open behaviour
- token leakage
- artifact exposure
- data integrity issue
- repeatable production startup failure
- broken backup/restore
- broken standalone launcher on the release branch
- broken release artifact build or malformed release archive/image
- broken Python package build or malformed wheel/source distribution
- critical/high dependency vulnerability without mitigation
- GenAI readiness validator regression on release branch

Rollback steps:

1. Stop the service.
2. Revert to previous image/tag/code revision.
3. Restore pre-release SQLite backup if needed.
4. Validate `/healthz`, `/readyz`, `/metrics`, scan history, artifact access, standalone launcher path where applicable, release artifact build where applicable, Python package build where applicable, and GenAI readiness gates.
5. Document root cause and create a hotfix issue.

## Final release decision

Final release is approved only when the selected release branch/tag has green CI, completed documentation review, local launcher smoke, hosted/production Web UI smoke, GenAI readiness validation, backup/restore validation, Docker/container smoke where applicable, Windows/Linux/macOS release artifact validation, Python package build validation, and explicit maintainer sign-off.
