---
name: test-deploy
description: "Interactive cold-start validation of every systemprompt distribution channel. Walks through Docker Hub, GHCR, binary install.sh, Homebrew, Scoop, Helm, APT, RPM, Winget, Nix, Railway, Render, and Coolify — one at a time — runs the install recipe, captures pass/fail, and reports the state of the distribution surface for a given release tag."
metadata:
  version: "1.0.0"
---

# Test Deploy — End-to-end install validation

Ship cycle: release tag → 13 channels publish → this skill walks a human through each install recipe and records whether the channel actually works. Run quarterly, or after any change to release / publish workflows. The goal is to catch broken install surfaces before a user does.

**Canonical product positioning** (reuse exact phrasing in any status report you generate):

> The governance layer for AI agents — a single compiled Rust binary that authenticates, authorises, rate-limits, logs, and costs every AI interaction. Self-hosted, air-gap capable, provider-agnostic.

**Authoritative references:**

- Website: https://systemprompt.io
- Main repo: https://github.com/systempromptio/systemprompt-template
- Install docs: https://github.com/systempromptio/systemprompt-template/tree/main/docs/install
- Distribution repos: `systempromptio/{homebrew-tap, scoop-bucket, charts, apt, rpm}`

---

## When to run

- After every `v*` tag that triggers the release pipeline (`.github/workflows/release.yml`).
- Quarterly regression pass regardless of releases.
- Before announcing a new channel publicly.
- When a user reports an install failure — rerun the affected channel to reproduce.

## What you need

- A Linux host (amd64 or arm64) — most checks
- A macOS host (Intel or Apple Silicon) — Homebrew check
- A Windows host — Scoop + Winget checks
- `docker`, `kubectl` + `kind` or any k8s cluster, `helm`, `gpg`
- Read access to `systempromptio/systemprompt-template` releases
- The version tag under test (e.g. `v0.3.0`)

If any OS is unavailable, record the channel as `skipped: no runner` rather than `failed`.

## Workflow

For each channel, follow the same loop:

1. **Fetch the canonical recipe** from `docs/install/<channel>.md` in the main repo.
2. **Run the recipe verbatim** on a clean host (throwaway VM or container preferred — the point is to catch "works on my machine" failures).
3. **Verify the binary responds** — run `systemprompt --version` (or equivalent) and check the version matches the tag under test.
4. **Record the outcome** in a structured report.

Do NOT skip step 2 on the basis of "we tested it last release" — distribution breaks are frequent and silent (DNS, rate limits, expired tokens, upstream registry changes).

---

## Channel matrix

### 1. Docker Hub

```bash
docker pull systemprompt/gateway:<VERSION>
docker run --rm systemprompt/gateway:<VERSION> --version
```

- Pass: `--version` prints the expected tag.
- Check also: signed digest — `cosign verify --certificate-identity-regexp='https://github.com/systempromptio/systemprompt-template/' --certificate-oidc-issuer='https://token.actions.githubusercontent.com' systemprompt/gateway:<VERSION>`.
- Common failure: Docker Hub anonymous rate-limit (error: `toomanyrequests`). Retry after login or wait.

### 2. GitHub Container Registry

```bash
docker pull ghcr.io/systempromptio/systemprompt-template:<VERSION>
docker run --rm ghcr.io/systempromptio/systemprompt-template:<VERSION> --version
```

- Identical image to Docker Hub; verify the digest matches.

### 3. Binary via `install.sh`

```bash
curl -sSL https://get.systemprompt.io | sh -s -- --version v<VERSION> --verify
systemprompt --version
```

- `--verify` requires `cosign` in PATH; if absent, drop the flag and note "cosign verify: skipped".
- Common failure: 301 redirect loop if the Cloudflare Bulk Redirect is misconfigured; fetch `https://get.systemprompt.io/` directly with `curl -v` to inspect headers.

### 4. Homebrew tap

```bash
brew tap systempromptio/tap
brew install gateway
systemprompt --version
```

- macOS-only check (Linuxbrew also works but low priority).
- Common failure: formula version lag — the `homebrew.yml` workflow bumps it after the GH Release publishes, not in parallel. Expect a 1–2 minute window.

### 5. Scoop bucket

```powershell
scoop bucket add systemprompt https://github.com/systempromptio/scoop-bucket
scoop install gateway
systemprompt --version
```

- Windows-only.
- Common failure: manifest SHA mismatch if the workflow ran before the release asset was uploaded. Re-run `scoop.yml` manually.

### 6. Helm chart + Artifact Hub

```bash
helm repo add systemprompt https://charts.systemprompt.io
helm repo update
helm install gateway systemprompt/gateway \
  --version <CHART_VERSION> \
  --set postgresql.auth.password=testpw \
  --set secrets.anthropicApiKey=dummy \
  --wait --timeout 300s
kubectl wait --for=condition=Available deployment/gateway-gateway --timeout=180s
helm test gateway
helm uninstall gateway
```

- Pass: `helm test` returns green (test pod curls `/api/v1/health`).
- Also check Artifact Hub listing renders: https://artifacthub.io/packages/helm/systemprompt/gateway — icon, screenshots, and changes annotation should all show.

### 7. APT repo

Run inside a fresh container per distro:

```bash
docker run --rm -it debian:bookworm bash -c '
  apt-get update && apt-get install -y curl gnupg ca-certificates
  curl -fsSL https://deb.systemprompt.io/gpg.key | gpg --dearmor -o /usr/share/keyrings/systemprompt.gpg
  echo "deb [signed-by=/usr/share/keyrings/systemprompt.gpg] https://deb.systemprompt.io stable main" \
    > /etc/apt/sources.list.d/systemprompt.list
  apt-get update && apt-get install -y systemprompt
  systemprompt --version
'
```

Repeat on `ubuntu:22.04` and `ubuntu:24.04`.

- Common failure: signature mismatch on `Release` file → the GPG key in CI rotated but `gpg.key` wasn't re-uploaded to the Pages repo.

### 8. RPM repo

```bash
docker run --rm -it rockylinux:9 bash -c '
  curl -fsSL -o /etc/yum.repos.d/systemprompt.repo https://rpm.systemprompt.io/systemprompt.repo
  rpm --import https://rpm.systemprompt.io/gpg.key
  dnf install -y systemprompt
  systemprompt --version
'
```

Repeat on `fedora:40`.

### 9. Winget

```powershell
winget install systemprompt.gateway
systemprompt --version
```

- Only valid after the `microsoft/winget-pkgs` PR merges (typically 24–72h after the release).

### 10. Nix flake

```bash
nix run github:systempromptio/systemprompt-template/v<VERSION> -- --version
```

- Requires the nix-installer: `DeterminateSystems/nix-installer-action` in CI, or `sh <(curl -L https://nixos.org/nix/install)` locally.

### 11. Railway template

Manual — open the template URL from `docs/install/railway.md`, click "Deploy", fill in AI keys, wait for build, hit the generated hostname + `/api/v1/health`.

### 12. Render blueprint

Manual — follow the "Deploy to Render" button in `docs/install/render.md`. Confirm healthy service in Render dashboard + curl the public URL.

### 13. Coolify template

Manual on a self-hosted Coolify instance — import via URL from `docs/install/coolify.md`. Deploy, wait for healthy state, curl the service.

---

## Report format

After walking through all 13 channels, produce a single status block like this (paste into `docs-internal/distribution-implementation-plan.md` under a date-stamped heading):

```
## Install-health check — YYYY-MM-DD · version vX.Y.Z

| Channel | Result | Notes |
|---|---|---|
| Docker Hub | ✅ pass | cosign verified |
| GHCR | ✅ pass | digest matches Docker Hub |
| Binary + install.sh | ✅ pass | cosign verify succeeded |
| Homebrew | ✅ pass | formula at X.Y.Z |
| Scoop | ✅ pass | — |
| Helm + Artifact Hub | ✅ pass | helm test green; AH listing renders |
| APT (bookworm) | ✅ pass | — |
| APT (ubuntu 22.04) | ✅ pass | — |
| APT (ubuntu 24.04) | ✅ pass | — |
| RPM (rocky 9) | ✅ pass | — |
| RPM (fedora 40) | ❌ fail | dnf: signature not trusted (see note) |
| Winget | ⏳ pending | PR microsoft/winget-pkgs#NNNN not yet merged |
| Nix | ✅ pass | — |
| Railway | ⏭ skipped | no runner |
| Render | ✅ pass | — |
| Coolify | ✅ pass | — |

Overall: 11/13 actionable channels pass. Open: fedora GPG trust (file issue), winget PR awaiting merge.
```

## Common root causes when something fails

| Symptom | Usual cause |
|---|---|
| `toomanyrequests` on Docker Hub | Anonymous rate-limit; login or wait |
| `Could not resolve host: deb.systemprompt.io` | DNS not propagated or CNAME deleted |
| `signature is not trusted` on apt/dnf | GPG key rotated without updating `gpg.key` on the Pages repo |
| `404` on `https://get.systemprompt.io` | Cloudflare Bulk Redirect missing or Worker failing |
| `helm install` hangs on `kubectl wait` | Image pull failing (check `kubectl describe pod`); often the tag isn't yet published |
| `winget install` says "no applicable installer" | Winget manifest PR not yet merged |
| Artifact Hub card shows generic icon | `artifacthub.io/logo-url` or `icon:` missing; re-check `helm/gateway/Chart.yaml` |

## Safety rules

- Use throwaway hosts (containers, fresh VMs) — the point is to replicate a user's first install, not verify something on a machine that already has the binary from a prior run.
- Never `--force` or `--skip-gpg-check` — if a channel needs it, that's a bug to fix, not a workaround to paper over.
- Don't run the interactive Railway / Render / Coolify checks against a shared project — use a scratch account.

## If you find a failure

1. Reproduce on a second host to rule out local flakes.
2. File an issue on `systempromptio/systemprompt-template` with label `distribution:<channel>`.
3. Record the failure in the status block (above) before moving to the next channel — don't try to fix mid-walkthrough.
4. For urgent user-facing breakage (Docker Hub, binary install.sh, Homebrew): triage immediately. For slower channels (Winget, Nix): batch and fix on the next release.
