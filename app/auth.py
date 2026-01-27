"""
Auth Configuration
==================

JWT RBAC authentication configuration for AgentOS.

See: https://docs.agno.com/agent-os/security/rbac
"""

from os import getenv
from pathlib import Path
from typing import Any, Optional

from agno.os.config import AuthorizationConfig


def get_authorization_config() -> Optional[AuthorizationConfig]:
    """Build AuthorizationConfig from environment variables.

    Configuration priority:
    1. JWT_JWKS_FILE - Path to JWKS file (recommended for production)
    2. JWT_VERIFICATION_KEY - Inline public key

    Optional settings:
    - JWT_ALGORITHM - Signing algorithm (default: RS256)
    - JWT_VERIFY_AUDIENCE - Enable audience verification (default: false)

    Returns:
        AuthorizationConfig if JWT auth is configured, None otherwise.
    """
    jwks_file = getenv("JWT_JWKS_FILE")
    verification_key = getenv("JWT_VERIFICATION_KEY")

    if not jwks_file and not verification_key:
        return None

    config_kwargs: dict[str, Any] = {
        "algorithm": getenv("JWT_ALGORITHM", "RS256"),
    }

    # Audience verification (optional, defaults to false)
    # When enabled, tokens must have aud claim matching AgentOS name
    verify_audience = getenv("JWT_VERIFY_AUDIENCE", "").lower() in ("true", "1", "yes")
    if verify_audience:
        config_kwargs["verify_audience"] = True
        print("[Auth] Audience verification enabled (aud claim will be validated)")

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
