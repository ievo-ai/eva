#!/usr/bin/env python3
"""Generate a GitHub App installation token for Eva.

Usage:
    python generate-app-token.py --app-id 123456 --private-key key.pem --org ievo-ai

Requires: pip install PyJWT cryptography httpx
"""

import argparse
import sys
import time

import httpx
import jwt


def generate_jwt(app_id: int, private_key: str) -> str:
    """Generate a JWT for GitHub App authentication."""
    now = int(time.time())
    payload = {
        "iat": now - 60,  # issued at (60s in the past for clock drift)
        "exp": now + (10 * 60),  # expires in 10 minutes
        "iss": app_id,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_id(token: str, org: str) -> int:
    """Get the installation ID for the org."""
    resp = httpx.get(
        "https://api.github.com/app/installations",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    resp.raise_for_status()

    for installation in resp.json():
        if installation.get("account", {}).get("login") == org:
            return installation["id"]

    print(f"Error: No installation found for org '{org}'", file=sys.stderr)
    print("Make sure the app is installed on the organization.", file=sys.stderr)
    sys.exit(1)


def create_installation_token(jwt_token: str, installation_id: int) -> str:
    """Create an installation access token."""
    resp = httpx.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return data["token"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GitHub App token for Eva")
    parser.add_argument("--app-id", type=int, required=True, help="GitHub App ID")
    parser.add_argument("--private-key", required=True, help="Path to .pem private key file")
    parser.add_argument("--org", default="ievo-ai", help="GitHub org name (default: ievo-ai)")
    parser.add_argument("--export", action="store_true", help="Output as export command")
    args = parser.parse_args()

    # Read private key
    with open(args.private_key) as f:
        private_key = f.read()

    # Generate JWT
    jwt_token = generate_jwt(args.app_id, private_key)

    # Get installation ID
    installation_id = get_installation_id(jwt_token, args.org)

    # Create installation token
    token = create_installation_token(jwt_token, installation_id)

    if args.export:
        print(f"export EVA_GITHUB_TOKEN={token}")
    else:
        print(token)


if __name__ == "__main__":
    main()
