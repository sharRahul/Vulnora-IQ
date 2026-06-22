# VulnoraIQ Incident Response Plan

## Severity Definitions

| Severity | Description | Response Time | Escalation |
|---|---|---|---|
| **Critical** | Active data exposure, compromised credentials, or system-wide outage | Immediate (< 15 min) | CTO + Security Lead |
| **High** | Suspected breach, persistent anomalous activity, or partial data loss | < 1 hour | Engineering Lead |
| **Medium** | Isolated misconfiguration, minor performance degradation, or non-critical data corruption | < 4 hours | Team Lead |
| **Low** | Informational alert, best-practice gap, or low-priority dependency issue | < 1 sprint | Assignee |

---

## Escalation Path

```
Assignee / On-Call Engineer
  → Engineering Lead / Team Lead
    → Security Lead
      → CTO
        → CEO (if legal/comms required)
```

**On-call contact**: `[oncall-channel]` / PagerDuty escalation policy `[link]`  
**Security team**: `#security` Slack channel / `security@vulnora.ai`  
**Engineering lead**: `#eng-leads` Slack channel

---

## Incident Types

### 1. Auth Token Leak

**Detection**
- Alert from secret scanning tool (GitGuardian, TruffleHog) on commit or CI
- Token reported in GitHub Security Advisories or leaked in public repo
- Unexpected API calls with a specific token in access logs
- SIEM rule: `source:cloudtrail AND event:token-use AND new-geo-location`

**Triage**
1. Confirm the token is valid and active — check `vault list` or secrets manager
2. Identify which service/user the token belongs to
3. Review access logs for unauthorized usage since the leak time window
4. Determine blast radius: what resources does the token grant access to?

**Containment**
1. **Immediately revoke the token** — `vault token revoke <id>` or rotate via secrets manager
2. If the token grants IAM access, disable the associated key in the cloud provider console
3. If committed to git, push a revert/force-push and use `git filter-repo` or BFG to purge from history
4. Notify downstream services that depend on the token

**Eradication**
1. Remove hardcoded secrets from source — replace with Vault/Secrets Manager references
2. Audit CI/CD pipelines, env files, and Docker layers for additional copies
3. Run `trufflehog --since-commit` or `ggshield scan ci` to detect other leaks

**Recovery**
1. Issue a new token with scoped permissions
2. Update consuming services with the new secret
3. Verify all systems are functional — run integration test suite
4. Monitor logs for 24h to catch any residual abuse

**Post-mortem**
- Root cause: how did the token end up in the leak location?
- Was the token overly permissive? Should it be scoped down?
- Was pre-commit/secret scanning in place? Why did it miss this?
- Add/improve guardrails (pre-commit hooks, `.gitignore` entries, secret detection CI)

---

### 2. Suspicious Scan Activity

**Detection**
- Spike in 4xx/5xx errors from a single IP or IP range
- Repeated requests to non-existent endpoints (`/wp-admin`, `.env`, `.git/config`)
- Alert from WAF (Cloudflare, AWS WAF, etc.) matching SQLi/XSS/SSRF patterns
- Unusual timing patterns — requests arriving at consistent intervals (indicating tooling)
- SIEM rule: `rate-limit-breach OR waf-blocked AND count > threshold`

**Triage**
1. Identify source IP(s), user-agent strings, and ASN
2. Check whether the activity targets a specific endpoint or is spray-and-pray
3. Pull access logs for the affected window — look for successful requests mixed in
4. Determine if any authenticated endpoints were hit and if valid tokens were used

**Containment**
1. Add offending IPs/CIDRs to WAF block rules
2. If targeting auth endpoints (login, register), enable rate-limiting or CAPTCHA
3. If a vulnerability was exploited, follow the relevant incident type (e.g., token leak, data exposure)
4. For DDoS-level volume, engage upstream DDoS protection provider

**Eradication**
1. Harden the targeted endpoint — add input validation, parameterized queries, CSRF tokens
2. If a specific payload attempted exploitation, add a WAF custom rule to block it
3. Review recent deployments — was the endpoint intentionally exposed?

**Recovery**
1. Remove temporary blocks once the scan subsides (24–48h)
2. Verify legitimate traffic is not impacted — review support tickets
3. Ensure rate-limiting stays in place as a permanent control

**Post-mortem**
- What attack surface was the scan probing?
- Were there any legitimate requests that got caught in blocks?
- Can the endpoint be further locked down (auth, IP whitelist, VPN)?
- Create or update runbook for common scan patterns

---

### 3. Rate-Limit Spikes

**Detection**
- Alert from API gateway (Kong, Envoy, AWS API Gateway) that rate limit was exceeded
- Users or services receiving `429 Too Many Requests`
- Database connection pool exhaustion or elevated P95 latency
- Grafana dashboard showing request rate > threshold

**Triage**
1. Distinguish between legitimate traffic bursts vs. abuse vs. client bugs
2. Check top consumer by client ID or API key
3. Look at the time-series graph — is the spike gradual (organic) or immediate (scripted)?
4. Review recent deployments — did a config change lower the limit?

**Containment**
1. If abuse: apply per-client rate limit (reduce from 1000/min to 100/min)
2. If client bug: contact the offending client team and request they fix their retry logic
3. If legitimate traffic: temporarily increase the limit or scale up instances
4. If DDoS: fall back to shared rate-limit and enable WAF challenge mode

**Eradication**
1. Fix any client-side retry storms — implement exponential backoff if missing
2. Adjust rate-limit tiers to match actual usage patterns
3. If the spike exposed a performance bottleneck, fix the underlying issue (N+1 query, cache miss, etc.)

**Recovery**
1. Restore normal rate-limit values once the spike resolves
2. Confirm downstream services are caught up on any back-pressure
3. Verify client traffic returns to baseline

**Post-mortem**
- Was the rate limit appropriate for the use case?
- Did the alert trigger early enough?
- Are there clients that consistently burst? Consider dedicated tiers.
- Should we implement circuit breakers or adaptive rate-limiting?

---

### 4. Unauthorized Access Attempt

**Detection**
- Failed login attempts exceeding threshold (e.g., >10 in 5 min from same IP)
- Session token reuse from different geographies (impossible travel)
- MFA prompt spam or unexpected password reset emails
- SIEM rule: `failed-auth AND count > threshold OR geo-anomaly`

**Triage**
1. Identify the targeted account(s) — is it a known user or admin?
2. Check if any attempts succeeded — review auth logs for successful logins from the source IP
3. Determine if credentials are from a known breach (check HaveIBeenPwned or internal breach db)
4. Assess if the attack targeted a specific user (targeted) or is spray-and-pray (opportunistic)

**Containment**
1. Lock the affected account(s) — `user disable <id>`
2. Enforce password reset for affected accounts
3. If credential stuffing is suspected, force MFA re-enrollment
4. Block source IP/CIDR at the WAF
5. Enable CAPTCHA or rate-limiting on login endpoint

**Eradication**
1. If credentials were leaked, follow Auth Token Leak procedures
2. Review account recovery flows — is the security question/email reset too weak?
3. Check for session fixation or CSRF vulnerabilities in auth flow

**Recovery**
1. Unlock accounts after password reset and MFA verification
2. Notify affected users with instructions to review their account activity
3. Monitor the affected accounts for 72h post-recovery

**Post-mortem**
- Were the compromised credentials found in a known breach?
- Did MFA block the attacker? If not, why?
- Should we implement account lockout, geolocation gating, or risk-based auth?
- Is the password policy adequate (length, complexity, rotation)?

---

### 5. Report/Artifact Exposure

**Detection**
- Customer reports seeing another customer's data in a report or dashboard
- Publicly accessible S3 bucket or storage URL found by security scan
- Access logs show download of a report by an unauthorized user
- Alert from CSP/watermarking system

**Triage**
1. Confirm the exposure — access the artifact as the unauthorized user would
2. Identify what data is exposed (PII, credentials, scan results, metadata)
3. Determine the scope — how many artifacts, how long were they exposed
4. Check audit logs for who accessed the exposed data

**Containment**
1. Remove public access — switch bucket/object ACL to private, invalidate CDN cache
2. Generate new pre-signed URLs if applicable and revoke old ones
3. If data was scraped, engage legal for breach notification assessment
4. Take the affected endpoint/service offline if exposure is widespread

**Eradication**
1. Fix the root cause — wrong ACL, missing auth check, misconfigured CDN
2. Add integration tests that verify auth for artifact access
3. Implement automated scanning of storage buckets for public ACLs

**Recovery**
1. Restore service once fix is deployed and tested
2. If data was exposed, follow data breach notification procedures (GDPR, CCPA, etc.)
3. Re-issue report links with fresh tokens to all affected customers

**Post-mortem**
- How did the artifact become publicly accessible?
- Was there a missing access control check in the API?
- Do we have automated bucket/public-access scanning? If not, implement it.
- Should artifacts be encrypted at rest with per-customer keys?

---

### 6. Corrupted SQLite Store

**Detection**
- Application returns `500` with `database disk image is malformed`
- Health check endpoint fails for the store
- Backup job reports checksum mismatch
- Data inconsistencies in reports — missing rows, NULL values in non-nullable fields

**Triage**
1. Identify which SQLite file(s) are affected — `PRAGMA integrity_check;`
2. Check filesystem health — disk space (`df -h`), inode count, disk SMART status
3. Determine the time range of the corruption — review backup timestamps
4. Check if the corruption spread to replicas or snapshots

**Containment**
1. **Stop all writes** to the corrupted database immediately
2. Take a forensic copy: `copy "store.db" "store.db.corrupted"`
3. If the store is critical, fail over to a warm replica or read-replica
4. If no replica exists, spin up a new instance from the last known-good backup

**Eradication**
1. Restore from the most recent clean backup
2. If the corruption was caused by disk failure, migrate the store to a healthy volume
3. If caused by bug (e.g., concurrent write issue), deploy the fix
4. Run `PRAGMA quick_check;` on the restored database to confirm integrity

**Recovery**
1. Point the application to the restored database file
2. Replay any transactions from the write-ahead log if available
3. Verify data consistency by comparing report outputs with source data
4. Resume writes

**Post-mortem**
- What caused the corruption? (disk, bug, power loss, concurrent access)
- Should we migrate to PostgreSQL/MySQL for this data?
- Are backups verified with regular restore drills?
- Do we have proper file locking or WAL mode configured?
- Should we add automated `integrity_check` as a cron job?

---

### 7. Failed Backup

**Detection**
- Backup cron job exits non-zero — alert from cron monitor (Healthchecks.io, Dead Man's Snitch)
- Cloud backup tool (Velero, Restic, Duplicati) reports failure in dashboard
- Monitoring alert: `backup_age > 24h`
- Backup file size is 0 bytes or suspiciously small compared to expected

**Triage**
1. Review the backup job logs for error messages
2. Check the backup destination — is the bucket/volume full, unavailable, or misconfigured?
3. Determine when the last successful backup occurred
4. Check if the source data is still healthy (see Corrupted SQLite Store)

**Containment**
1. Trigger an immediate manual backup of critical data
2. If the destination is full, free up space or rotate old backups
3. If the source is unavailable, troubleshoot the source before retrying
4. If backup tool is broken, fall back to a secondary method (e.g., `sqlite3 .backup` + `aws s3 cp`)

**Eradication**
1. Fix the root cause (expired credentials, full volume, broken cron syntax, tool bug)
2. Update alert thresholds if they were too tight for legitimate backup size variation
3. Add backup destination monitoring (disk space, object count)

**Recovery**
1. Confirm the manual backup completed and is restorable
2. Restart the automated backup schedule
3. Verify backup integrity — `restic check` or perform a restore test to a staging environment
4. Continue monitoring for 3 consecutive successful backup runs

**Post-mortem**
- How long was the gap between the last successful backup and detection?
- Was there a single point of failure?
- Do we follow the 3-2-1 backup rule? (3 copies, 2 media types, 1 offsite)
- When was the last full restore test? Schedule one if overdue.
- Should we implement backup alerting at multiple stages (start, complete, size check)?

---

### 8. Dependency Vulnerability

**Detection**
- Dependabot / Renovate / Snyk / Trivy opens an alert for a critical CVE
- CI/CD pipeline fails on `npm audit` / `poetry check` / `grype` scan
- Penetration test report identifies a known CVE in a direct or transitive dependency
- Exploit published publicly (e.g., Proof of Concept on GitHub)

**Triage**
1. Confirm the CVE applies — check if the vulnerable code path is actually exercised
2. Assess the exploitability — is there a known PoC? Remote or local? Authenticated or unauthenticated?
3. Determine impact — data exposure? RCE? DoS? Privilege escalation?
4. Identify the affected deployment — all environments or just some?

**Containment**
1. **If critical and remotely exploitable**: patch immediately — use `npm audit fix --force`, `pip install --upgrade`, or direct version bump
2. **If no patch exists**: add a WAF rule, restrict network access, or remove the vulnerable feature at runtime
3. **If transitive dependency**: use `overrides`/`resolutions` in package manager to force a safe version
4. **If patching breaks API**: pin the version, test, and deploy to staging first; fast-track through review

**Eradication**
1. Apply the vendor-issued patch or upgrade to the fixed version
2. Remove the dependency if it is no longer needed
3. Use dependency pinning in lockfiles to prevent future surprises

**Recovery**
1. Deploy the fix to all environments after verifying tests pass
2. Run a full security scan to confirm the CVE is resolved
3. Monitor for regressions

**Post-mortem**
- Why was the vulnerable version introduced? Was it a fresh install or an upgrade?
- Do we have automated dependency scanning in CI? Does it block merges for critical CVEs?
- Are we tracking dependency freshness with a dashboard?
- Should we use a software bill of materials (SBOM) generator in CI?

---

### 9. Web UI Security Issue

**Detection**
- User reports unexpected behavior (popups, redirected pages, injected content)
- CSP violation report received
- Penetration test finding (XSS, CSRF, Clickjacking, DOM clobbering)
- Bug bounty submission

**Triage**
1. Reproduce the issue in a sandboxed browser (no saved passwords, incognito mode)
2. Determine if the issue is stored, reflected, or DOM-based
3. Check if authenticated users are affected or if it is exploitable without login
4. Assess blast radius — can an attacker extract data, execute actions, or deface the UI?

**Containment**
1. **If stored XSS**: remove the malicious payload from the database and sanitize the input
2. **If reflected XSS**: add output encoding / CSP nonce; consider a WAF rule to block the payload pattern
3. **If CSRF**: ensure proper anti-CSRF tokens on state-changing endpoints
4. **If active exploitation**: take the vulnerable page/feature offline via feature flag or Nginx block
5. Add or tighten CSP headers (`default-src 'self'`, `script-src 'nonce-...'`)

**Eradication**
1. Fix the root cause — use a sanitization library (DOMPurify, Bleach), proper encoding, or framework-safe rendering
2. Add automated security tests (ZAP, Burp passive scan, or Playwright with CSP checks)
3. Review adjacent endpoints/pages for the same pattern

**Recovery**
1. Deploy the fix and verify through a staging test
2. If the page was taken offline, re-enable it
3. Clear any cached malicious content via CDN purge
4. Notify affected users if any data was compromised

**Post-mortem**
- Was there an existing secure coding guideline that was missed?
- Do we run SAST (ESLint security plugin, Semgrep) in CI?
- Should we add a bug bounty program or VDP?
- Update the secure coding guide with the specific pattern that caused the issue

---

## Contact Information Template

Maintain a private `contacts.json` or vault entry with the following:

```json
{
  "incident_responders": {
    "on_call": {
      "name": "",
      "phone": "",
      "slack": "",
      "email": ""
    },
    "security_lead": {
      "name": "",
      "phone": "",
      "slack": "",
      "email": ""
    },
    "engineering_lead": {
      "name": "",
      "phone": "",
      "slack": "",
      "email": ""
    }
  },
  "channels": {
    "slack_primary": "#security-incidents",
    "slack_readonly": "#security-notifications",
    "email_list": "security@vulnora.ai",
    "pagerduty": "https://vulnora.pagerduty.com/schedules/..."
  },
  "vendors": {
    "cloud_provider": { "name": "AWS/Azure/GCP", "support_phone": "", "support_email": "" },
    "waf_provider": { "name": "Cloudflare/Akamai", "support_phone": "", "support_email": "" },
    "secrets_manager": { "name": "HashiCorp Vault/AWS Secrets Manager", "support_email": "" }
  },
  "legal": {
    "dpo": { "name": "", "email": "" },
    "compliance": { "name": "", "email": "" }
  },
  "backup_provider": { "name": "", "contact": "" }
}
```

---

## Post-Incident Review Checklist

- [ ] **Root cause identified** — what was the initiating event?
- [ ] **Timeline created** — all events from detection to recovery, with timestamps
- [ ] **Impact assessed** — what data, users, or systems were affected?
- [ ] **Containment verified** — is the issue fully contained with no active exploitation?
- [ ] **Fix deployed** — has the root cause been eradicated in all environments?
- [ ] **Tests added** — regression and/or security tests that would catch a recurrence
- [ ] **Monitoring improved** — alert added or threshold adjusted for earlier detection
- [ ] **Documentation updated** — runbooks, architecture docs, incident templates
- [ ] **Communication sent** — internal stakeholders + affected customers (if applicable)
- [ ] **Action items filed** — each remediation step is tracked as a Jira/GitHub issue with owner and deadline
- [ ] **PIR published** — post-incident review document shared with the team
- [ ] **Lessons learned presented** — in a team-wide or cross-team meeting
- [ ] **Severity rating validated** — was the initial severity correct? Adjust criteria if not.

---

*Maintain this document in the team's version control. Review and update every quarter or after any significant incident.*
