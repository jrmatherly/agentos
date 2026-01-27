# Agent-UI JWT Integration Alignment

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
s
**Goal:** Document the verified JWT RBAC contract between Agent-UI (frontend) and AgentOS (backend) to ensure seamless authentication integration.

**Architecture:** Agent-UI issues RS256-signed JWTs with Agno-compatible scopes. AgentOS validates tokens using the shared public key and enforces RBAC based on the `scopes` claim. Token extraction is header-based by default.

**Tech Stack:** PyJWT (backend), jose (frontend), RS256 asymmetric encryption, FastAPI middleware

---

## Verified Contract Specifications

This document captures findings from analysis of the Agno framework source code (`agno==latest` in this project's `.venv`).

### 1. Import Path

**Status:** ✅ Verified Correct

```python
from agno.os.config import AuthorizationConfig
```

**Source:** `app/auth.py:14`, `/agno/os/config.py`

**AuthorizationConfig fields:**

```python
class AuthorizationConfig(BaseModel):
    verification_keys: Optional[List[str]] = None
    jwks_file: Optional[str] = None
    algorithm: Optional[str] = None
    verify_audience: Optional[bool] = None
```

---

### 2. Environment Variable Precedence

**Status:** ✅ Verified

**Order (first match wins):**

1. `JWT_JWKS_FILE` - Path to JWKS file (recommended for production)
2. `JWT_VERIFICATION_KEY` - Inline RSA public key (development/simple setups)

**Source:** `/agno/os/middleware/jwt.py:112-120`

```python
# Try jwks_file parameter first
if jwks_file:
    self._load_jwks_file(jwks_file)
else:
    jwks_file_env = getenv("JWT_JWKS_FILE", "")
    if jwks_file_env:
        self._load_jwks_file(jwks_file_env)
```

**During validation, JWKS keys are tried first, then static keys as fallback.**

---

### 3. Audience Claim (`aud`)

**Status:** ✅ Optional (disabled by default)

**Default:** `verify_audience=False`

**Source:** `/agno/os/middleware/jwt.py:402, 689-691`

```python
verify_audience: bool = False,  # Constructor default

# When enabled:
if self.verify_audience:
    expected_audience = self.audience or agent_os_id
```

**Expected value:** `"AgentOS"` (matches `app/main.py:58` AgentOS name)

**Recommendation for Agent-UI:**

- Include `aud: "AgentOS"` in JWT payload for forward compatibility
- Can be enabled via `JWT_VERIFY_AUDIENCE=true` environment variable

---

### 4. User ID Extraction

**Status:** ✅ Uses standard `sub` claim

**Source:** `/agno/os/middleware/jwt.py:87, 695, 708`

```python
user_id_claim: str = "sub",  # Default claim name
user_id = payload.get(self.user_id_claim)
request.state.user_id = user_id
```

**Agent-UI Implementation:**

```typescript
const jwt = new SignJWT({ scopes })
  .setSubject(userId)  // Sets "sub" claim
```

---

### 5. Scopes Format

**Status:** ✅ Array format (strings auto-converted)

**Source:** `/agno/os/middleware/jwt.py:295-299, 697-704`

```python
scopes = payload.get(self.scopes_claim, [])
if isinstance(scopes, str):
    scopes = [scopes]  # Single string -> array
elif not isinstance(scopes, list):
    scopes = []
```

**Supported formats:**

| Format | Example | Result |
|--------|---------|--------|
| Array (recommended) | `["agents:read", "agents:run"]` | ✅ Works |
| Single string | `"agents:read"` | ✅ Auto-converted to `["agents:read"]` |
| Space-delimited | `"agents:read agents:run"` | ❌ Treated as single scope |

**Agent-UI Implementation:**

```typescript
const scopes = getAgnoScopes(role)  // Returns string[]
const jwt = new SignJWT({ scopes })  // Array format
```

---

### 6. Error Response Format

**Status:** ✅ JSON with `detail` field

**Source:** `/agno/os/middleware/jwt.py:632-650`

```python
def _create_error_response(self, status_code, detail, ...):
    response = JSONResponse(status_code=status_code, content={"detail": detail})
```

**Error responses:**

| Status | Condition | `detail` Value |
|--------|-----------|----------------|
| 401 | Missing token (header) | `"Authorization header missing"` |
| 401 | Missing token (cookie) | `"JWT cookie 'access_token' missing"` |
| 401 | Missing token (both) | `"JWT token missing from both Authorization header and 'access_token' cookie"` |
| 401 | Expired | `"Token has expired"` |
| 401 | Invalid signature | `"Invalid token: {error_message}"` |
| 401 | Wrong audience | `"Invalid token audience - token not valid for this AgentOS instance"` |
| 403 | Insufficient scopes | `"Insufficient permissions"` |

**Agent-UI error handling:**

```typescript
if (response.status === 401) {
  const data = await response.json()
  console.error('Auth error:', data.detail)
  // Clear token, redirect to login
}
if (response.status === 403) {
  const data = await response.json()
  console.error('Permission denied:', data.detail)
  // Show "insufficient permissions" UI
}
```

---

### 7. Token Source

**Status:** ✅ Header-only by default

**Source:** `/agno/os/middleware/jwt.py:25-30, 394`

```python
class TokenSource(str, Enum):
    HEADER = "header"   # Authorization header only
    COOKIE = "cookie"   # Cookie only
    BOTH = "both"       # Try header first, then cookie

token_source: TokenSource = TokenSource.HEADER,  # Default
```

**Header extraction:**

```python
authorization = request.headers.get("Authorization", "")
if authorization.lower().startswith("bearer "):
    return authorization[7:].strip()
```

**Agent-UI Implementation:**

```typescript
headers: {
  'Authorization': `Bearer ${token}`,
}
```

**SSR considerations:**

- Default header-based auth works for all API calls
- For SSR with cookies, AgentOS can be configured with `token_source="both"`
- Cookie name: `access_token` (configurable)

---

## JWT Token Structure

**Required payload:**

```json
{
  "sub": "user-123",
  "scopes": ["agents:read", "agents:run", "sessions:write"],
  "exp": 1735689600,
  "iat": 1735603200
}
```

**Optional claims:**

```json
{
  "aud": "AgentOS",
  "session_id": "session-456"
}
```

**Claim mapping:**

| JWT Claim | Request State | Default Claim Name |
|-----------|---------------|-------------------|
| `sub` | `request.state.user_id` | Configurable via `user_id_claim` |
| `scopes` | `request.state.scopes` | Configurable via `scopes_claim` |
| `session_id` | `request.state.session_id` | Configurable via `session_id_claim` |
| `aud` | `request.state.audience` | Configurable via `audience_claim` |

---

## Scope Reference

### Global Resource Scopes

| Scope | Endpoint Pattern | Description |
|-------|-----------------|-------------|
| `system:read` | `GET /config`, `GET /models` | View system config |
| `agents:read` | `GET /agents`, `GET /agents/*` | List/view agents |
| `agents:write` | `POST /agents`, `PATCH /agents/*` | Create/update agents |
| `agents:delete` | `DELETE /agents/*` | Delete agents |
| `agents:run` | `POST /agents/*/runs` | Run agents |
| `teams:read` | `GET /teams`, `GET /teams/*` | List/view teams |
| `teams:write` | `POST /teams`, `PATCH /teams/*` | Create/update teams |
| `teams:run` | `POST /teams/*/runs` | Run teams |
| `workflows:read` | `GET /workflows` | List workflows |
| `workflows:run` | `POST /workflows/*/runs` | Run workflows |
| `sessions:read` | `GET /sessions` | View sessions |
| `sessions:write` | `POST /sessions`, `PATCH /sessions/*` | Create/update sessions |
| `sessions:delete` | `DELETE /sessions/*` | Delete sessions |
| `memories:read` | `GET /memories` | View memories |
| `memories:write` | `POST /memories` | Create memories |
| `memories:delete` | `DELETE /memories/*` | Delete memories |
| `knowledge:read` | `GET /knowledge/*`, `POST /knowledge/search` | View/search knowledge |
| `knowledge:write` | `POST /knowledge/content` | Add knowledge |
| `knowledge:delete` | `DELETE /knowledge/*` | Delete knowledge |
| `metrics:read` | `GET /metrics` | View metrics |
| `evals:read` | `GET /eval-runs` | View evaluations |
| `traces:read` | `GET /traces` | View traces |
| `agent_os:admin` | All endpoints | Full admin access |

### Per-Resource Scopes

| Format | Example | Description |
|--------|---------|-------------|
| `resource:<id>:action` | `agents:web-agent:run` | Access specific resource |
| `resource:*:action` | `agents:*:run` | Wildcard access to all |

---

## Role-to-Scope Mapping (Agent-UI Reference)

| Role | Scopes |
|------|--------|
| `user` | `agents:read`, `agents:run`, `sessions:read`, `sessions:write` |
| `powerUser` | Above + `system:read` |
| `teamLead` | Above + `teams:read`, `teams:run`, `memories:read` |
| `teamAdmin` | Above + `agents:write`, `sessions:delete`, `workflows:read`, `workflows:run` |
| `orgAdmin` | Above + `knowledge:*`, `memories:write`, `memories:delete`, `metrics:read`, `evals:read`, `traces:read` |
| `globalAdmin` | `agent_os:admin` |

---

## Configuration Checklist

### AgentOS (Backend)

```toml
# mise.local.toml
[env]
JWT_VERIFICATION_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""

# Or use JWKS file:
# JWT_JWKS_FILE = "/path/to/jwks.json"
```

### Agent-UI (Frontend)

```bash
# .env.local
AGENTOS_JWT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
AGENTOS_JWT_EXPIRES_IN=900
NEXT_PUBLIC_AGENT_OS_URL=http://localhost:8000
```

---

## Testing Checklist

- [ ] Generate RSA key pair with `openssl`
- [ ] Configure private key in Agent-UI
- [ ] Configure public key in AgentOS
- [ ] Start both services
- [ ] Login via Better Auth
- [ ] Verify JWT in Authorization header (browser dev tools)
- [ ] Verify `scopes` claim contains expected array
- [ ] Test `agents:read` → GET /agents succeeds
- [ ] Test `agents:run` → POST /agents/{id}/runs succeeds
- [ ] Test missing scope → 403 Forbidden with `{"detail": "Insufficient permissions"}`
- [ ] Test expired token → 401 Unauthorized with `{"detail": "Token has expired"}`
- [ ] Test invalid signature → 401 Unauthorized with `{"detail": "Invalid token: ..."}`

---

## References

- AgentOS JWT Middleware: `/agno/os/middleware/jwt.py`
- AgentOS Scopes: `/agno/os/scopes.py`
- AgentOS Auth Helpers: `/agno/os/auth.py`
- Project Auth Config: `app/auth.py`
- JWT RBAC Guide: `docs/guides/JWT_RBAC.md`
- [Agno RBAC Documentation](https://docs.agno.com/agent-os/security/rbac)
