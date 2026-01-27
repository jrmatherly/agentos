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
2. Private key -> agent-ui (`JWT_PRIVATE_KEY` env var)
3. Public key -> agentos-docker (`JWT_VERIFICATION_KEY` env var)

### 6. Remove Deprecated Variables

The following are no longer needed:

- `NEXT_PUBLIC_OS_SECURITY_KEY` - Replaced by JWT RBAC

## Auth Testing

1. Login via SSO in agent-ui
2. Check browser dev tools for JWT in Authorization header
3. Verify token contains correct scopes for user's role
4. Confirm AgentOS API requests succeed with 200
5. Test permission denied (403) for elevated operations

## Role Hierarchy

```
globalAdmin
    └── agent_os:admin (full access)

orgAdmin
    └── agents:*, teams:*, sessions:*, knowledge:*, metrics:read

teamAdmin
    └── agents:read/write/run, sessions:*, teams:read/run

teamLead
    └── agents:read/run, sessions:read/write, memories:read, teams:read

powerUser
    └── agents:read/run, sessions:read/write

user (default)
    └── agents:read/run, sessions:write
```

## Security Considerations

1. **Private key protection**: Never commit private keys to git
2. **Token expiration**: Set reasonable expiration (1 hour recommended)
3. **Scope validation**: Backend validates scopes on every request
4. **Audience verification**: Token `aud` claim must match AgentOS ID

## Implementation Checklist

- [ ] Add `mapRoleToAgnoScopes` function to agent-ui
- [ ] Configure Better Auth to include scopes in JWT
- [ ] Add JWT_PRIVATE_KEY to agent-ui environment
- [ ] Add JWT_VERIFICATION_KEY to agentos-docker environment
- [ ] Update API client to include Authorization header
- [ ] Remove deprecated OS_SECURITY_KEY references
- [ ] Test all role levels for correct access
- [ ] Document role assignment process for admins
