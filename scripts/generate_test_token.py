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


# Role to scope mappings (matches agent-ui and docs/plans/2026-01-27-agent-ui-jwt-alignment.md)
ROLE_SCOPES = {
    "user": [
        "agents:read",
        "agents:run",
        "sessions:read",
        "sessions:write",
    ],
    "powerUser": [
        "agents:read",
        "agents:run",
        "sessions:read",
        "sessions:write",
        "system:read",
    ],
    "teamLead": [
        "agents:read",
        "agents:run",
        "sessions:read",
        "sessions:write",
        "system:read",
        "teams:read",
        "teams:run",
        "memories:read",
    ],
    "teamAdmin": [
        "agents:read",
        "agents:write",
        "agents:run",
        "sessions:read",
        "sessions:write",
        "sessions:delete",
        "system:read",
        "teams:read",
        "teams:run",
        "memories:read",
        "workflows:read",
        "workflows:run",
    ],
    "orgAdmin": [
        "agents:read",
        "agents:write",
        "agents:run",
        "sessions:read",
        "sessions:write",
        "sessions:delete",
        "system:read",
        "teams:read",
        "teams:run",
        "memories:read",
        "memories:write",
        "memories:delete",
        "workflows:read",
        "workflows:run",
        "knowledge:read",
        "knowledge:write",
        "knowledge:delete",
        "metrics:read",
        "evals:read",
        "traces:read",
    ],
    "globalAdmin": ["agent_os:admin"],
}


def main() -> None:
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
