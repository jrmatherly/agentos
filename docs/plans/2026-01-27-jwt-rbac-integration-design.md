# JWT RBAC Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable JWT-based RBAC authentication in AgentOS backend to integrate with agent-ui's Better Auth SSO system, replacing the deprecated `OS_SECURITY_KEY` approach.

**Architecture:** Agent-ui issues JWTs via Better Auth with Agno-compatible scopes. AgentOS validates these tokens using a shared public key and enforces scope-based permissions on all endpoints. Uses RS256 asymmetric encryption for secure key distribution.

**Tech Stack:** Agno OS JWT Middleware, PyJWT, RS256 asymmetric keys, FastAPI, Better Auth

---

## Prerequisites

Before starting this implementation:

1. **agent-ui project** must have Better Auth SSO configured and working
2. **RSA key pair** will be generated as part of this plan
3. **agentos-docker** must be running with PostgreSQL

---

## Phase 1: Backend JWT Configuration

### Task 1: Generate RSA Key Pair

**Files:**

- Create: `keys/private.pem` (gitignored)
- Create: `keys/public.pem` (gitignored)
- Modify: `.gitignore`

**Step 1: Create keys directory and generate RSA key pair**

Run:

```bash
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

Expected: Two files created in `keys/` directory

**Step 2: Add keys directory to .gitignore**

Add to `.gitignore`:

```gitignore
# JWT Keys (never commit private keys)
keys/*.pem
keys/private.pem
keys/public.pem
```

**Step 3: Verify keys were generated**

Run: `ls -la keys/`

Expected:

```mermaid
-rw-------  1 user  staff  1675 Jan 27 12:00 private.pem
-rw-r--r--  1 user  staff   451 Jan 27 12:00 public.pem
```

**Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: add keys directory to gitignore for JWT key pair"
```

---

### Task 2: Update Environment Configuration Template

**Files:**

- Modify: `mise.local.toml.example`

**Step 1: Add JWT configuration section**

Add after the Redis section in `mise.local.toml.example`:

```toml
# JWT RBAC Authentication
# See: https://docs.agno.com/agent-os/security/rbac
#
# Option 1: Inline public key (escape newlines or use single line)
# JWT_VERIFICATION_KEY = "-----BEGIN PUBLIC KEY-----\nMIIB...\n-----END PUBLIC KEY-----"
#
# Option 2: JWKS file path (recommended for key rotation)
# JWT_JWKS_FILE = "/path/to/jwks.json"
#
# The private key should be configured in agent-ui for signing JWTs
# The public key here is used by AgentOS to verify tokens
```

**Step 2: Verify file syntax**

Run: `mise env 2>&1 | head -5`

Expected: No TOML syntax errors

**Step 3: Commit**

```bash
git add mise.local.toml.example
git commit -m "docs: add JWT RBAC configuration template to mise.local.toml.example"
```

---

### Task 3: Create Auth Configuration Module

**Files:**

- Create: `app/auth.py`

**Step 1: Create the auth configuration module**

Create file `app/auth.py`:

```python
"""
Auth Configuration
==================

JWT RBAC authentication configuration for AgentOS.

See: https://docs.agno.com/agent-os/security/rbac
"""

from os import getenv
from pathlib import Path
from typing import Optional

from agno.os.config import AuthorizationConfig


def get_authorization_config() -> Optional[AuthorizationConfig]:
    """Build AuthorizationConfig from environment variables.

    Configuration priority:
    1. JWT_JWKS_FILE - Path to JWKS file (recommended for production)
    2. JWT_VERIFICATION_KEY - Inline public key

    Returns:
        AuthorizationConfig if JWT auth is configured, None otherwise.
    """
    jwks_file = getenv("JWT_JWKS_FILE")
    verification_key = getenv("JWT_VERIFICATION_KEY")

    if not jwks_file and not verification_key:
        return None

    config_kwargs = {
        "algorithm": getenv("JWT_ALGORITHM", "RS256"),
    }

    if jwks_file:
        jwks_path = Path(jwks_file)
        if jwks_path.exists():
            config_kwargs["jwks_file"] = str(jwks_path)
        else:
            print(f"[Auth] Warning: JWKS file not found: {jwks_file}")
            return None
    elif verification_key:
        # Handle escaped newlines in environment variable
        key = verification_key.replace("\\n", "\n")
        config_kwargs["verification_keys"] = [key]

    return AuthorizationConfig(**config_kwargs)


def is_auth_enabled() -> bool:
    """Check if JWT authentication is configured."""
    return bool(getenv("JWT_JWKS_FILE") or getenv("JWT_VERIFICATION_KEY"))
```

**Step 2: Verify syntax**

Run: `python -m py_compile app/auth.py`

Expected: No output (successful compilation)

**Step 3: Commit**

```bash
git add app/auth.py
git commit -m "feat(auth): add JWT RBAC configuration module"
```

---

### Task 4: Enable Authorization in AgentOS

**Files:**

- Modify: `app/main.py`

**Step 1: Add auth imports**

After the existing imports (around line 41), add:

```python
# Auth configuration
from app.auth import get_authorization_config, is_auth_enabled  # noqa: E402
```

**Step 2: Update AgentOS instantiation**

Replace the AgentOS instantiation (lines 52-77) with:

```python
# ============================================================================
# Create AgentOS with tracing and optional JWT RBAC
# ============================================================================
auth_config = get_authorization_config()

agent_os = AgentOS(
    name="AgentOS",
    agents=[
        # Existing
        knowledge_agent,
        mcp_agent,
        # Reasoning showcase
        reasoning_model_agent,
        reasoning_tools_agent,
        reasoning_agent,
        # Tools showcase
        finance_agent,
        web_scraper_agent,
        research_agent,
        # Learning
        learning_assistant,
        # HITL
        confirmation_agent,
    ],
    teams=[research_team, support_team, reasoning_team],
    workflows=[content_workflow, blog_workflow],
    config=str(Path(__file__).parent / "config.yaml"),
    db=get_postgres_db(),  # Dedicated DB for traces
    tracing=True,  # Enable OpenTelemetry tracing
    enable_mcp_server=True,  # Expose as MCP server at /mcp
    # JWT RBAC (enabled if JWT_VERIFICATION_KEY or JWT_JWKS_FILE is set)
    authorization=is_auth_enabled(),
    authorization_config=auth_config,
)

if is_auth_enabled():
    print("[Auth] JWT RBAC authentication enabled")
else:
    print("[Auth] Running without authentication (development mode)")
```

**Step 3: Verify syntax and imports**

Run: `python -c "from app.main import agent_os; print('OK')"`

Expected: `OK` (or auth-related message if configured)

**Step 4: Commit**

```bash
git add app/main.py
git commit -m "feat(auth): enable JWT RBAC authorization in AgentOS"
```

---

### Task 5: Add PyJWT Dependency (if not present)

**Files:**

- Modify: `pyproject.toml`
- Regenerate: `requirements.txt`

**Step 1: Check if PyJWT is already a transitive dependency**

Run: `grep -i pyjwt requirements.txt`

If PyJWT is already present, skip to Step 4.

**Step 2: Add PyJWT to dependencies (if needed)**

Add to `pyproject.toml` dependencies list:

```python
  "pyjwt>=2.8.0",
  "cryptography>=41.0.0",  # For RS256 support
```

**Step 3: Regenerate requirements.txt**

Run: `mise run generate-requirements`

**Step 4: Verify dependency**

Run: `python -c "import jwt; print(jwt.__version__)"`

Expected: Version number (e.g., `2.8.0`)

**Step 5: Commit (if changes were made)**

```bash
git add pyproject.toml requirements.txt
git commit -m "build: add PyJWT dependency for JWT RBAC"
```

---

## Phase 2: Role-to-Scope Mapping Documentation

### Task 6: Create Scope Mapping Reference

**Files:**

- Create: `docs/guides/JWT_RBAC.md`

**Step 1: Create the JWT RBAC guide**

Create file `docs/guides/JWT_RBAC.md`:

```markdown
# JWT RBAC Authentication Guide

AgentOS uses JWT-based Role-Based Access Control (RBAC) to secure API endpoints. This guide covers configuration and integration with the agent-ui frontend.

## Overview

```

┌─────────────────────────────────────────────────────────────────────────────┐
│                            Agent-UI (Frontend)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Better Auth                                  │   │
│  │   • SSO (OIDC/SAML) authentication                                  │   │
│  │   • Issues JWT tokens with scopes                                   │   │
│  │   • Signs with private key (keys/private.pem)                       │   │
│  └──────────────────────────┬──────────────────────────────────────────┘   │
│                             │                                               │
│                             │ JWT Token with scopes                         │
│                             ▼                                               │
└─────────────────────────────┼───────────────────────────────────────────────┘
                              │
                              │ Authorization: Bearer <JWT>
                              │
┌─────────────────────────────┼───────────────────────────────────────────────┐
│                             ▼                                               │
│                    AgentOS (Backend)                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     JWT Middleware                                   │   │
│  │   • Validates signature with public key (JWT_VERIFICATION_KEY)      │   │
│  │   • Extracts scopes, user_id, session_id                           │   │
│  │   • Enforces scope requirements per endpoint                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

```markdown

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_VERIFICATION_KEY` | RSA public key for token verification | `-----BEGIN PUBLIC KEY-----\n...` |
| `JWT_JWKS_FILE` | Path to JWKS file (alternative to inline key) | `/path/to/jwks.json` |
| `JWT_ALGORITHM` | JWT signing algorithm | `RS256` (default) |

### Generate RSA Key Pair

```bash
# Generate private key (for agent-ui)
openssl genrsa -out private.pem 2048

# Extract public key (for agentos-docker)
openssl rsa -in private.pem -pubout -out public.pem
```

### Configure AgentOS

Add to `mise.local.toml`:

```toml
[env]
JWT_VERIFICATION_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""
```

Or use JWKS file:

```toml
[env]
JWT_JWKS_FILE = "/path/to/jwks.json"
```

## Role-to-Scope Mapping

Agent-ui roles must be mapped to Agno scopes in the JWT token.

### Agent-UI Roles → Agno Scopes

| Agent-UI Role | Agno Scopes |
|--------------|-------------|
| `user` | `agents:read`, `agents:run`, `sessions:write` |
| `powerUser` | `agents:read`, `agents:run`, `sessions:read`, `sessions:write` |
| `teamLead` | Above + `memories:read`, `teams:read` |
| `teamAdmin` | Above + `agents:write`, `teams:run` |
| `orgAdmin` | Above + `knowledge:read`, `knowledge:write`, `metrics:read` |
| `globalAdmin` | `agent_os:admin` (full access) |

### Agno Scope Reference

| Scope Format | Example | Description |
|-------------|---------|-------------|
| `resource:action` | `agents:read` | Access all resources of type |
| `resource:<id>:action` | `agents:knowledge-agent:run` | Access specific resource |
| `resource:*:action` | `agents:*:run` | Wildcard (all agents) |
| `agent_os:admin` | - | Full admin access |

### Complete Scope List

**Agents:**

- `agents:read` - List and view agents
- `agents:write` - Create/update agents
- `agents:delete` - Delete agents
- `agents:run` - Run any agent
- `agents:<id>:run` - Run specific agent

**Teams:**

- `teams:read` - List and view teams
- `teams:write` - Create/update teams
- `teams:run` - Run any team

**Workflows:**

- `workflows:read` - List and view workflows
- `workflows:run` - Run any workflow

**Sessions:**

- `sessions:read` - View sessions
- `sessions:write` - Create/update sessions
- `sessions:delete` - Delete sessions

**Memories:**

- `memories:read` - View memories
- `memories:write` - Create/update memories
- `memories:delete` - Delete memories

**Knowledge:**

- `knowledge:read` - Search knowledge
- `knowledge:write` - Add knowledge
- `knowledge:delete` - Delete knowledge

**System:**

- `system:read` - View config/models
- `metrics:read` - View metrics
- `agent_os:admin` - Full access

## JWT Token Structure

```json
{
  "sub": "user-123",
  "scopes": ["agents:read", "agents:run", "sessions:write"],
  "aud": "AgentOS",
  "exp": 1735689600,
  "iat": 1735603200
}
```

| Claim | Required | Description |
|-------|----------|-------------|
| `scopes` | Yes | Array of permission scopes |
| `sub` | No | User ID (extracted as `user_id`) |
| `session_id` | No | Session ID for tracking |
| `aud` | No | Audience (should match AgentOS name) |

## Error Responses

| Status | Description |
|--------|-------------|
| `401 Unauthorized` | Missing or invalid JWT token |
| `403 Forbidden` | Insufficient scopes for endpoint |

## Development Mode

When `JWT_VERIFICATION_KEY` is not set, AgentOS runs without authentication. All endpoints are accessible without tokens.

```bash
[Auth] Running without authentication (development mode)
```

## Testing

Test with curl:

```bash
# Without auth (development mode)
curl http://localhost:8000/agents

# With JWT token
curl -H "Authorization: Bearer <token>" http://localhost:8000/agents
```

## References

- [Agno RBAC Documentation](https://docs.agno.com/agent-os/security/rbac)
- [Agno JWT Middleware](https://docs.agno.com/agent-os/middleware/jwt)
- [Better Auth Documentation](https://better-auth.com)

**Step 2: Commit**

```bash
git add docs/guides/JWT_RBAC.md
git commit -m "docs: add JWT RBAC authentication guide"
```

---

### Task 7: Update Project Documentation

**Files:**

- Modify: `CLAUDE.md`

**Step 1: Add JWT RBAC section to Environment Variables table**

After the Redis section in the Environment Variables table, add:

```markdown
### JWT RBAC Authentication
| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_VERIFICATION_KEY` | - | RSA public key for JWT verification |
| `JWT_JWKS_FILE` | - | Path to JWKS file (alternative to inline key) |
| `JWT_ALGORITHM` | RS256 | JWT signing algorithm |
```

**Step 2: Add authentication section to Architecture**

After the MCP Server entry in the AgentOS Features table, add:

```markdown
| **JWT RBAC** | `authorization=True` + `JWT_VERIFICATION_KEY` - Scope-based endpoint authorization |
```

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add JWT RBAC configuration to CLAUDE.md"
```

---

### Task 8: Update Serena Memory

**Files:**

- Update via Serena: `project_overview` memory

**Step 1: Update the project_overview memory**

Use Serena's `edit_memory` tool to add the JWT RBAC section to the Features table:

Add after the Guardrails row:

```markdown
| **JWT RBAC** | `authorization=True` + `JWT_VERIFICATION_KEY` env var - Scope-based endpoint authorization |
```

Add new Environment Variables section:

```markdown
### JWT RBAC Authentication
| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_VERIFICATION_KEY` | - | RSA public key for JWT verification |
| `JWT_JWKS_FILE` | - | Path to JWKS file (alternative) |
| `JWT_ALGORITHM` | RS256 | JWT signing algorithm |
```

**Step 2: Commit memory changes**

Memory updates are automatically persisted.

---

## Phase 3: Integration Testing

### Task 9: Create Test JWT Token Generator Script

**Files:**

- Create: `scripts/generate_test_token.py`

**Step 1: Create the token generator script**

Create file `scripts/generate_test_token.py`:

```python
#!/usr/bin/env python3
"""
Generate Test JWT Token
=======================

Generate a test JWT token for development/testing.

Usage:
    python scripts/generate_test_token.py [--role ROLE] [--user USER]

Examples:
    python scripts/generate_test_token.py
    python scripts/generate_test_token.py --role admin
    python scripts/generate_test_token.py --role user --user test@example.com
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import jwt
except ImportError:
    print("PyJWT not installed. Run: pip install pyjwt")
    exit(1)


# Role to scope mappings (matches agent-ui)
ROLE_SCOPES = {
    "user": ["agents:read", "agents:run", "sessions:write"],
    "powerUser": [
        "agents:read",
        "agents:run",
        "sessions:read",
        "sessions:write",
    ],
    "teamLead": [
        "agents:read",
        "agents:run",
        "sessions:read",
        "sessions:write",
        "memories:read",
        "teams:read",
    ],
    "teamAdmin": [
        "agents:read",
        "agents:write",
        "agents:run",
        "sessions:read",
        "sessions:write",
        "memories:read",
        "teams:read",
        "teams:run",
    ],
    "orgAdmin": [
        "agents:read",
        "agents:write",
        "agents:run",
        "sessions:read",
        "sessions:write",
        "memories:read",
        "memories:write",
        "teams:read",
        "teams:run",
        "knowledge:read",
        "knowledge:write",
        "metrics:read",
    ],
    "globalAdmin": ["agent_os:admin"],
}


def main():
    parser = argparse.ArgumentParser(description="Generate test JWT token")
    parser.add_argument(
        "--role",
        choices=list(ROLE_SCOPES.keys()),
        default="user",
        help="Role for scope mapping (default: user)",
    )
    parser.add_argument(
        "--user",
        default="test@example.com",
        help="User email/ID for sub claim",
    )
    parser.add_argument(
        "--expires",
        type=int,
        default=3600,
        help="Token expiration in seconds (default: 3600)",
    )
    parser.add_argument(
        "--key",
        default="keys/private.pem",
        help="Path to private key (default: keys/private.pem)",
    )
    args = parser.parse_args()

    # Load private key
    key_path = Path(args.key)
    if not key_path.exists():
        print(f"Error: Private key not found: {key_path}")
        print("Generate keys with: openssl genrsa -out keys/private.pem 2048")
        exit(1)

    private_key = key_path.read_text()

    # Build token payload
    now = datetime.now(timezone.utc)
    payload = {
        "sub": args.user,
        "scopes": ROLE_SCOPES[args.role],
        "aud": "AgentOS",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=args.expires)).timestamp()),
    }

    # Generate token
    token = jwt.encode(payload, private_key, algorithm="RS256")

    print(f"Role: {args.role}")
    print(f"Scopes: {json.dumps(payload['scopes'], indent=2)}")
    print(f"Expires: {datetime.fromtimestamp(payload['exp'], timezone.utc).isoformat()}")
    print()
    print("Token:")
    print(token)
    print()
    print("Usage:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/agents')


if __name__ == "__main__":
    main()
```

**Step 2: Make script executable**

Run: `chmod +x scripts/generate_test_token.py`

**Step 3: Verify script works**

Run: `python scripts/generate_test_token.py --help`

Expected: Help output showing usage

**Step 4: Commit**

```bash
git add scripts/generate_test_token.py
git commit -m "feat(scripts): add JWT test token generator"
```

---

### Task 10: Test JWT Authentication End-to-End

**Step 1: Ensure keys are generated**

Run: `ls keys/*.pem`

If files don't exist, run:

```bash
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

**Step 2: Configure JWT verification key**

Add to `mise.local.toml`:

```toml
[env]
JWT_VERIFICATION_KEY = """-----BEGIN PUBLIC KEY-----
<paste content of keys/public.pem here>
-----END PUBLIC KEY-----"""
```

**Step 3: Start AgentOS**

Run: `docker compose down && docker compose up -d --build`
Run: `docker compose logs -f agentos-api`

Expected: Log shows `[Auth] JWT RBAC authentication enabled`

**Step 4: Test without token (should fail)**

Run: `curl -s http://localhost:8000/agents | head -20`

Expected: `401 Unauthorized` or authentication error

**Step 5: Generate test token**

Run: `python scripts/generate_test_token.py --role user`

Copy the generated token.

**Step 6: Test with token (should succeed)**

Run: `curl -s -H "Authorization: Bearer <TOKEN>" http://localhost:8000/agents | head -20`

Expected: JSON response with agent list

**Step 7: Test admin scope**

Run: `python scripts/generate_test_token.py --role globalAdmin`

Test admin endpoint:

Run: `curl -s -H "Authorization: Bearer <TOKEN>" http://localhost:8000/metrics`

Expected: Metrics response (admin-only endpoint)

---

### Task 11: Document Agent-UI Integration Requirements

**Files:**

- Create: `docs/plans/2026-01-27-agent-ui-jwt-integration.md`

**Step 1: Create integration requirements document**

Create file `docs/plans/2026-01-27-agent-ui-jwt-integration.md`:

```markdown
# Agent-UI JWT Integration Requirements

This document outlines changes needed in the agent-ui project to integrate with AgentOS JWT RBAC.

## Overview

Agent-ui must generate JWT tokens with Agno-compatible scopes when users authenticate via Better Auth SSO.

## Required Changes in agent-ui

### 1. JWT Signing Configuration

Better Auth must be configured to sign JWTs with the private key:

```typescript
// src/lib/auth.ts
import { betterAuth } from 'better-auth'

export const auth = betterAuth({
  // ... existing config
  advanced: {
    generateToken: async ({ user, session }) => {
      const scopes = mapRoleToAgnoScopes(user.role)
      return {
        sub: user.id,
        scopes,
        aud: 'AgentOS',
      }
    }
  }
})
```

### 2. Role-to-Scope Mapping Function

```typescript
// src/lib/auth/scopeMapping.ts
export function mapRoleToAgnoScopes(role: string): string[] {
  const scopeMap: Record<string, string[]> = {
    user: ['agents:read', 'agents:run', 'sessions:write'],
    powerUser: ['agents:read', 'agents:run', 'sessions:read', 'sessions:write'],
    teamLead: ['agents:read', 'agents:run', 'sessions:read', 'sessions:write', 'memories:read', 'teams:read'],
    teamAdmin: ['agents:read', 'agents:write', 'agents:run', 'sessions:*', 'teams:read', 'teams:run'],
    orgAdmin: ['agents:*', 'teams:*', 'sessions:*', 'knowledge:*', 'metrics:read'],
    globalAdmin: ['agent_os:admin'],
  }
  return scopeMap[role] || scopeMap.user
}
```

### 3. Environment Variables

```bash
# Private key for JWT signing (never commit!)
JWT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"

# AgentOS backend URL
NEXT_PUBLIC_AGENT_OS_URL=http://localhost:8000
```

### 4. API Request Interceptor

All requests to AgentOS must include the JWT:

```typescript
// src/lib/agentosClient.ts
export async function agentosRequest(endpoint: string, options: RequestInit = {}) {
  const session = await auth.api.getSession()

  return fetch(`${process.env.NEXT_PUBLIC_AGENT_OS_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${session?.token}`,
    },
  })
}
```

### 5. Key Distribution

1. Generate RSA key pair (one time)
2. Private key → agent-ui (`JWT_PRIVATE_KEY` env var)
3. Public key → agentos-docker (`JWT_VERIFICATION_KEY` env var)

### 6. Remove Deprecated Variables

The following are no longer needed:

- `NEXT_PUBLIC_OS_SECURITY_KEY` - Replaced by JWT RBAC

## Auth Testing

1. Login via SSO in agent-ui
2. Check browser dev tools for JWT in Authorization header
3. Verify token contains correct scopes for user's role
4. Confirm AgentOS API requests succeed with 200
5. Test permission denied (403) for elevated operations

**Step 2: Commit**

```bash
git add docs/plans/2026-01-27-agent-ui-jwt-integration.md
git commit -m "docs: add agent-ui JWT integration requirements"
```

---

## Phase 4: Final Validation

### Task 12: Run Full Validation

**Step 1: Format code**

Run: `mise run format`

**Step 2: Run linting**

Run: `mise run validate`

Expected: All checks pass

**Step 3: Test docker build**

Run: `docker compose build`

Expected: Build succeeds

**Step 4: Final commit (if any formatting changes)**

```bash
git add -A
git commit -m "chore: formatting and cleanup"
```

---

### Task 13: Create Summary Commit

**Step 1: Review all changes**

Run: `git log --oneline -10`

Verify all commits from this plan are present.

**Step 2: Tag release (optional)**

```bash
git tag -a v1.1.0 -m "feat: JWT RBAC authentication"
```

---

## Summary

| Phase | Tasks | Key Deliverables |
|-------|-------|------------------|
| 1 | Tasks 1-5 | RSA keys, auth module, AgentOS configuration |
| 2 | Tasks 6-8 | Documentation, CLAUDE.md update, Serena memory |
| 3 | Tasks 9-11 | Test token generator, E2E testing, agent-ui requirements |
| 4 | Tasks 12-13 | Validation, final commit |

**Files Created:**

- `app/auth.py` - JWT RBAC configuration module
- `docs/guides/JWT_RBAC.md` - Comprehensive authentication guide
- `docs/plans/2026-01-27-agent-ui-jwt-integration.md` - Agent-ui integration requirements
- `scripts/generate_test_token.py` - Test token generator
- `keys/` directory (gitignored) - RSA key pair

**Files Modified:**

- `app/main.py` - Enable JWT RBAC in AgentOS
- `mise.local.toml.example` - JWT configuration template
- `CLAUDE.md` - JWT documentation
- `.gitignore` - Exclude keys directory

**Environment Variables Added:**

| Variable | Purpose |
|----------|---------|
| `JWT_VERIFICATION_KEY` | RSA public key for token verification |
| `JWT_JWKS_FILE` | Alternative: path to JWKS file |
| `JWT_ALGORITHM` | Signing algorithm (default: RS256) |

**Integration Points:**

- Agent-ui: Sign JWTs with private key, include scopes based on user role
- AgentOS: Verify JWTs with public key, enforce scope requirements
- Shared: RSA key pair (private → agent-ui, public → agentos-docker)
