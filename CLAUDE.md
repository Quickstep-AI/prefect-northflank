# Security rules for this project (non-negotiable)

This app deploys to octonomy's Northflank BYOC cluster. Follow these rules while
writing code. If a rule blocks the task, stop and say so - do not work around it.

## Dependencies
- Before adding ANY dependency: state the exact package name and version, and confirm
  it exists on the official registry. Never install a near-miss of a name you are
  unsure about - hallucinated names are pre-registered by attackers.
- Prefer the standard library. Do not add a dependency for something under ~30 lines.
- Never add: request, node-fetch v2, vm2, node-serialize, crypto-js, python-jose,
  pycrypto, pickle on untrusted input, yaml.load without SafeLoader, moment, the
  original faker, shelljs, jsonwebtoken below 9, handlebars below 4.7.7, AngularJS,
  Vue 2, CRA / react-scripts, or dotenv in production.
- Commit lockfiles. Install with: npm ci --ignore-scripts, or pinned requirements.
- Licences: MIT, Apache-2.0, BSD, ISC or MPL-2.0 only. Never AGPL, SSPL, BUSL or
  unlicensed code.

## Secrets
- Never hardcode a secret, key, token, password or connection string - not even a
  placeholder that looks real. Read them from environment variables injected by the
  Northflank secret group.
- Never put a secret behind NEXT_PUBLIC_, VITE_ or REACT_APP_. Those ship to the
  browser in plaintext.
- Never write a .env file into the Docker image, and never put a secret in a build
  argument - build values are baked into the image permanently.
- Keep .env* in .gitignore.
- Never log Authorization headers, cookies, tokens or connection strings.

## Network and TLS
- The app listens on one HTTP port, non-privileged (8080), bound to 0.0.0.0. That is
  the only port exposed. Databases, caches, admin and metrics stay internal.
- Never disable TLS verification (rejectUnauthorized: false, verify=False,
  NODE_TLS_REJECT_UNAUTHORIZED=0). If TLS fails, fix the certificate - do not bypass it.
- CORS: an explicit origin allowlist. Never origin '*' together with credentials.
- Set security headers (helmet or secure): CSP without unsafe-inline and unsafe-eval,
  HSTS, nosniff, frame-deny, strict referrer policy.
- Cookies: Secure, HttpOnly, SameSite.

## Auth and access
- Do not implement authentication yourself. Use the configured OIDC/SSO provider.
- Every endpoint checks authorisation server-side, including ownership of the
  requested resource. Deny by default.
- No admin backdoor, no debug route, no token passed in a query string.

## Code safety
- Parameterised SQL or an ORM only. Never string-interpolate SQL.
- Validate all input against a schema (zod or pydantic) before use.
- No eval(), exec(), new Function(), or shell=True on anything derived from user
  input - and never execute, render as HTML, or run as SQL any output from an LLM.
- If fetching a user-supplied URL, allowlist the destination and block private and
  link-local ranges, including 169.254.169.254.
- Never build a filesystem path from raw user input.
- Errors: no stack traces to the client. Debug mode off.
- Rate-limit authentication, email/SMS and any paid LLM endpoint.

## Container
- Multi-stage Dockerfile. Base image pinned by digest. Never :latest.
- Must build for ARM - the cluster node pool is ARM.
- The final image runs as a non-root user and contains no build tooling, no .git
  and no .env.
- Provide a /health endpoint that responds quickly and leaks no version or config
  detail. Declare CPU and memory limits in the deploy config.
- Never run as root, never privileged, never hostNetwork, never chmod 777.

## When you finish a feature, report
1. Dependencies added, and why.
2. Every endpoint created, and the authorisation check on it.
3. Anything touching secrets, auth, networking or file handling.
