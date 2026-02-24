---
name: cloud-operations
description: "Install, deploy, and manage systemprompt.io cloud infrastructure - DNS, SSL certificates, multi-tenant routing, and troubleshooting"
---

# Cloud Operations

Installation, cloud deployment, DNS configuration, SSL certificate management, and multi-tenant routing.

## Installation

### Prerequisites

```bash
rustc --version    # 1.75.0+
git --version
gh --version       # Optional but recommended
```

PostgreSQL 15+ is the only external dependency.

### Clone Template

**GitHub CLI (Recommended):**

```bash
gh repo create my-ai --template systempromptio/systemprompt-template --clone --private
cd my-ai
git submodule update --init --recursive
```

**Manual Clone:**

```bash
git clone --recursive https://github.com/systempromptio/systemprompt-template.git my-ai
cd my-ai
```

### Build

```bash
SQLX_OFFLINE=true cargo build --release -p systemprompt-cli
```

The `SQLX_OFFLINE=true` flag is required for first build (no database yet).

### Login

**Manual command only. Do not run via agents.**

```bash
systemprompt cloud auth login
```

Opens a browser for GitHub or Google OAuth. Free, required, one-time. Credentials persist in `.systemprompt/credentials.json`.

### Create Tenant

**Local development:**

```bash
systemprompt cloud tenant create --type local
```

| Host | DATABASE_URL |
|------|--------------|
| Local | `postgres://user:pass@localhost:5432/systemprompt` |
| Docker | `postgres://postgres:postgres@localhost:5432/systemprompt` |
| Neon | `postgres://user:pass@ep-xxx.us-east-2.aws.neon.tech/systemprompt` |
| Supabase | `postgres://postgres:pass@db.xxx.supabase.co:5432/postgres` |

**Cloud (managed PostgreSQL):**

```bash
systemprompt cloud tenant create --region iad
```

### Create Profile and Migrate

```bash
systemprompt cloud profile create local
systemprompt infra db migrate
```

### Start and Verify

```bash
systemprompt infra services start --all
systemprompt infra services status
systemprompt infra db status
systemprompt admin agents list
```

Visit `http://localhost:8080` to see the homepage.

## Cloud Architecture

Multi-tenant architecture with a central Management API for SSL termination and request routing.

```
Internet -> DNS (Cloudflare) -> Management API (Proxy) -> Tenant Apps
```

- Wildcard DNS: `*.systemprompt.io` points to Management API IP
- Management API reads `Host` header, extracts subdomain, routes to `sp-{tenant-id}`
- Each tenant has its own IP address and resources

## DNS Configuration

All tenant subdomains use a wildcard DNS record:

```
*.systemprompt.io -> Management API IP
```

### Verify DNS

```bash
dig +short '*.systemprompt.io' A
dig +short {tenant-id}.systemprompt.io A
```

Both should return the same IP.

## SSL Certificates

**Critical Rule**: All SSL certificates for `*.systemprompt.io` subdomains MUST be on the Management API, never on tenant apps.

If a certificate exists on both Management API and tenant app for the same hostname, the edge router cannot determine which app handles TLS, causing SSL handshake failures.

### Certificate Commands

```bash
systemprompt cloud certs list
systemprompt cloud certs show {subdomain}.systemprompt.io
systemprompt cloud certs add {subdomain}.systemprompt.io
systemprompt cloud certs remove {subdomain}.systemprompt.io -y
```

### Certificate States

| Status | Meaning | Action |
|--------|---------|--------|
| Ready | Certificate issued and active | None |
| Awaiting certificates | Let's Encrypt is issuing | Wait 30-60 seconds |
| Awaiting configuration | DNS not pointing to correct IP | Fix DNS or remove conflicting cert |

## Troubleshooting

### SSL Error (Site Unreachable)

```bash
curl -sI https://sp-{tenant-id}.fly.dev/
systemprompt cloud certs list
fly certs list -a sp-{tenant-id}
```

Fix: Remove certificate from tenant app, add to Management API:

```bash
fly certs remove {subdomain}.systemprompt.io -a sp-{tenant-id} -y
fly certs add {subdomain}.systemprompt.io -a management-api-prod
```

### 502 Bad Gateway

```bash
systemprompt cloud status
systemprompt cloud logs -f
```

Causes: Tenant app crashed, app name mismatch, internal network issue.

### DNS Mismatch (Awaiting Configuration)

```bash
dig +short {subdomain}.systemprompt.io A
fly ips list -a management-api-prod
```

Fix: Ensure wildcard DNS points to Management API IP. Do not create individual DNS records that override the wildcard.

### Installation Issues

| Issue | Solution |
|-------|----------|
| Build fails on macOS | Install OpenSSL: `brew install openssl` |
| Database connection refused | Verify PostgreSQL is running, check `DATABASE_URL` |
| Login fails | Ensure browser access, check network |
| Migrations fail | Check `DATABASE_URL` format, verify database exists |

## Post-Deployment Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Tenant app running | `systemprompt cloud status` | Status: started |
| SSL certificate | `fly certs show {subdomain} -a management-api-prod` | Status: Ready |
| Site accessible | `curl -sI https://{subdomain}.systemprompt.io/` | HTTP/2 200 |
| No conflicting certs | `fly certs list -a sp-{tenant-id}` | Empty |

## Quick Reference

| Task | Command |
|------|---------|
| Build | `SQLX_OFFLINE=true cargo build --release -p systemprompt-cli` |
| Login | `systemprompt cloud auth login` |
| Create local tenant | `systemprompt cloud tenant create --type local` |
| Create cloud tenant | `systemprompt cloud tenant create --region iad` |
| Create profile | `systemprompt cloud profile create <name>` |
| Run migrations | `systemprompt infra db migrate` |
| Start services | `systemprompt infra services start --all` |
| Check status | `systemprompt cloud status` |
| View logs | `systemprompt cloud logs -f` |
| List certificates | `systemprompt cloud certs list` |
| Add certificate | `systemprompt cloud certs add {subdomain}.systemprompt.io` |
| Check DNS | `dig +short {subdomain}.systemprompt.io A` |
| Test connectivity | `curl -sI https://{subdomain}.systemprompt.io/` |
