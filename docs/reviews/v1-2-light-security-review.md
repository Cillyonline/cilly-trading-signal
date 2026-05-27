# v1.2 Light MVP Security Review

Date: 2026-05-27

Issue: #144 - Run light MVP security review for v1.2 release candidate

Context: Issue #143, "Fix protected route UX after logout", is closed as of 2026-05-27. This review covers the current repository state after that fix.

## Scope

Reviewed the v1.2 release-candidate security posture for:

- Auth and session cookie settings.
- Login and logout behavior.
- Protected route behavior after #143.
- CORS settings.
- `.env.example` defaults.
- Caddy HTTPS path assumptions.
- Admin/default credential guidance.
- Secret handling in docs.
- Backup/restore docs for accidental secrets or sensitive dumps.
- Browser API base URL behavior through Caddy.

## Evidence Reviewed

- Repository identity check:
  - `gh repo view Cillyonline/cilly-trading-signal --json nameWithOwner,name,owner,url,defaultBranchRef`
  - Confirmed `nameWithOwner` is `Cillyonline/cilly-trading-signal`.
  - Confirmed URL is `https://github.com/Cillyonline/cilly-trading-signal`.
- Git context:
  - `git status --short`
  - `git branch --show-current`
  - `git remote -v`
- GitHub issue context:
  - `gh issue view 143 --repo Cillyonline/cilly-trading-signal --json number,title,state,closedAt,url`
  - Confirmed #143 is closed.
- Runtime and config files:
  - `.env.example`
  - `infra/docker-compose.yml`
  - `infra/caddy/Caddyfile`
  - `apps/api/app/core/config.py`
  - `apps/api/app/core/security.py`
  - `apps/api/app/main.py`
  - `apps/api/app/api/deps.py`
  - `apps/api/app/api/routes/auth.py`
  - `apps/api/app/services/auth.py`
  - `apps/web/src/lib/api.ts`
  - `apps/web/src/lib/auth-guard.tsx`
  - `apps/web/src/app/login/page.tsx`
- Operational and release docs:
  - `docs/DEPLOYMENT_RUNBOOK.md`
  - `docs/MVP_RELEASE_CHECKLIST.md`
  - `docs/MVP_SMOKE_TEST.md`
  - `docs/TECH_ARCHITECTURE.md`
  - `docs/DATA_MODEL.md`
  - `docs/DECISIONS.md`
  - `README.md`
- Backup and restore scripts:
  - `scripts/backup_postgres.sh`
  - `scripts/restore_postgres.sh`
- Secret/dump sweep:
  - `rg --files -g "*.env" -g ".env*" -g "*.dump" -g "*.sql" -g "*.backup" -g "backups/**"`
  - Found local `.env` and tracked `.env.example`; no tracked dump files were found by this check.

## Findings By Severity

### Critical

No critical findings identified in this light MVP review.

### High

No high-severity findings identified in this light MVP review.

### Medium

1. Docker Compose exposes direct API and web host ports in addition to Caddy.

   Evidence: `infra/docker-compose.yml` publishes `8000:8000` for the API and `3000:3000` for the web service. The intended VPS path uses Caddy on ports 80 and 443, but these direct bindings may be reachable on a VPS unless firewall rules or deployment changes restrict them. This increases externally reachable surface area and allows bypassing the intended HTTPS reverse-proxy path.

   Impact: Direct API/web access could weaken the deployment assumption that browser traffic goes through Caddy over HTTPS. API auth still requires the session cookie on protected routes, but the extra exposed services are unnecessary for the Caddy deployment path.

   Recommendation: Open a follow-up issue to bind direct service ports to localhost for local development, move them behind a development profile, or document required firewall rules explicitly for VPS use.

2. Backup helper defaults to a repository-relative backup directory.

   Evidence: `scripts/backup_postgres.sh` defaults `BACKUP_DIR` to `backups/postgres`. `docs/DEPLOYMENT_RUNBOOK.md` recommends storing backups outside the repository when possible and warns that PostgreSQL dumps can contain sensitive app data.

   Impact: Operators who run the helper without setting `BACKUP_DIR` may create sensitive database dumps under the working tree. No dump files were found in the current repository sweep, and the docs warn not to commit backups, but the default still creates an avoidable footgun.

   Recommendation: Open a follow-up issue to make the backup script default safer, for example by requiring `BACKUP_DIR` for non-development use, defaulting outside the repo in deployment docs/scripts, and ensuring backup directories are ignored.

### Low

1. Login UI pre-fills the local default admin email.

   Evidence: `apps/web/src/app/login/page.tsx` initializes the email field with the local default admin email. Deployment config guards reject the same default outside development/test, and docs require replacing the default.

   Impact: Low. The value is intended for local MVP convenience, but it can confuse operators during staging/prod-like validation and may normalize default credentials.

   Recommendation: Consider a follow-up to avoid pre-filling the admin email outside local development or to keep this explicitly local-only.

2. Login endpoint has no rate limiting or lockout.

   Evidence: `apps/api/app/api/routes/auth.py` authenticates the single admin user and returns a generic failure message, but there is no rate limiting, backoff, or lockout.

   Impact: Low for internal RC handoff and controlled staging. This should not be treated as internet-exposed production hardening.

   Recommendation: Track rate limiting/backoff as a future hardening issue before any public or production-like exposure.

3. Session model is intentionally simple and stateless.

   Evidence: `apps/api/app/core/security.py` signs a stateless token with an expiry and nonce. Logout deletes the browser cookie, but there is no server-side session revocation list.

   Impact: Low for the single-user MVP and internal RC handoff. A copied token remains valid until expiry unless `SECRET_KEY` is rotated.

   Recommendation: Track server-side session invalidation or shorter-lived sessions as a future hardening issue if the app moves beyond controlled single-user operation.

## Positive Security Observations

- Session cookies are set as `HttpOnly`, `SameSite=Lax`, path-scoped to `/`, and use configurable `Secure`.
- Non-local environments fail fast when `AUTH_COOKIE_SECURE` is false.
- Non-local environments fail fast for known placeholder secrets, default admin email, unsafe database credentials, and wildcard CORS origins.
- CORS uses configured exact origins and `allow_credentials=True`; wildcard CORS is rejected outside local development/test.
- The frontend uses credentialed fetches and defaults `NEXT_PUBLIC_API_BASE_URL` to `/api`, matching same-origin Caddy routing.
- Protected API dependencies reject missing, invalid, expired, or inactive-user session cookies.
- The #143 protected-route guard now checks `/auth/me` and redirects auth errors to `/login`; pages using the guard no longer depend only on failed data fetches for auth handling.
- Deployment docs clearly state that `.env` and secrets must not be committed or pasted into issues, PRs, logs, or screenshots.
- Backup/restore docs correctly treat database dumps as sensitive and warn against committing or sharing them.
- The current review did not find committed dump files.

## Known Gaps

- This was a light review, not a penetration test.
- No live browser session, packet capture, TLS scanner, dependency vulnerability scan, or container image scan was performed.
- No production VPS firewall state was inspected.
- No real deployment secrets were inspected.
- No automated test was run because the change is documentation-only.
- The local `.env` file exists in the working tree but was not opened or reported, and it is outside the intended committed artifact scope.

## Non-Goals / Out Of Scope

- Full penetration test.
- New auth provider.
- Role or permission redesign.
- Broker integration.
- Automatic trading.
- Strategy or scoring changes.
- Production-readiness claim.
- Profitability claims.
- Trading advice.

## Follow-Up Issue Recommendations

1. Harden Docker Compose service exposure for Caddy deployments.

   Proposed title: `Restrict direct API/web host port exposure in Caddy deployments`

   Proposed scope: Adjust Docker Compose profiles or port bindings so production-like Caddy deployments do not expose direct API/web ports publicly, or document mandatory firewall rules if direct bindings remain.

2. Make PostgreSQL backup output safer by default.

   Proposed title: `Make backup script default output path safer for sensitive dumps`

   Proposed scope: Avoid repository-relative backup output by default for non-local use, require or strongly validate `BACKUP_DIR`, and ensure accidental dumps stay out of version control.

3. Add basic auth brute-force hardening.

   Proposed title: `Add basic login rate limiting for single-admin auth`

   Proposed scope: Add conservative rate limiting or backoff for failed login attempts without changing the auth provider or role model.

4. Review local-only login defaults.

   Proposed title: `Avoid production-like login UI defaults`

   Proposed scope: Keep local development convenience while preventing default admin email prefill from appearing in staging/prod-like builds.

5. Track future server-side session invalidation.

   Proposed title: `Evaluate server-side session invalidation for post-MVP hardening`

   Proposed scope: Assess whether a server-side session table, token versioning, or shorter TTL is needed before broader exposure.

## Final Security Posture

Acceptable for internal RC handoff.

This conclusion is limited to the reviewed MVP release-candidate scope and controlled/internal handoff. It is not a production-readiness claim. The medium findings should be tracked before any broader or production-like internet exposure.
