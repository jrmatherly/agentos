# JWT RBAC Authentication Guide

AgentOS uses JWT-based Role-Based Access Control (RBAC) to secure API endpoints. This guide covers configuration and integration with the agent-ui frontend.

## Overview

```mermaid
+-----------------------------------------------------------------------------+
|                            Agent-UI (Frontend)                              |
|  +---------------------------------------------------------------------+   |
|  |                         Better Auth                                  |   |
|  |   - SSO (OIDC/SAML) authentication                                  |   |
|  |   - Issues JWT tokens with scopes                                   |   |
|  |   - Signs with private key (keys/private.pem)                       |   |
|  +-----------------------------+---------------------------------------+   |
|                                |                                            |
|                                | JWT Token with scopes                      |
|                                v                                            |
+--------------------------------|--------------------------------------------+
                                 |
                                 | Authorization: Bearer <JWT>
                                 |
+--------------------------------|--------------------------------------------+
|                                v                                            |
|                    AgentOS (Backend)                                        |
|  +---------------------------------------------------------------------+   |
|  |                     JWT Middleware                                   |   |
|  |   - Validates signature with public key (JWT_VERIFICATION_KEY)      |   |
|  |   - Extracts scopes, user_id, session_id                           |   |
|  |   - Enforces scope requirements per endpoint                        |   |
|  +---------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------+
```

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_VERIFICATION_KEY` | RSA public key for token verification | `-----BEGIN PUBLIC KEY-----\n...` |
| `JWT_JWKS_FILE` | Path to JWKS file (alternative to inline key) | `/path/to/jwks.json` |
| `JWT_ALGORITHM` | JWT signing algorithm | `RS256` (default) |
| `JWT_VERIFY_AUDIENCE` | Validate aud claim matches AgentOS name | `true` or `false` (default) |

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

### Agent-UI Roles to Agno Scopes

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
