"""Eva telemetry — Sentry SDK integration.

Initializes Sentry for error tracking and performance monitoring.
Eva reports her own errors to the `eva` project in Sentry.

Env vars:
    EVA_SENTRY_DSN  — Sentry DSN for the eva project (required to enable)
    EVA_ENVIRONMENT — environment tag: production, staging, development (default: production)
"""

import os

import sentry_sdk

from eva import __version__

_initialized = False


def init_sentry() -> bool:
    """Initialize Sentry SDK. Returns True if initialized, False if skipped.

    Safe to call multiple times — only initializes once.
    Silently skips if EVA_SENTRY_DSN is not set.
    """
    global _initialized
    if _initialized:
        return True

    dsn = os.environ.get("EVA_SENTRY_DSN", "")
    if not dsn:
        return False

    environment = os.environ.get("EVA_ENVIRONMENT", "production")

    sentry_sdk.init(
        dsn=dsn,
        release=f"eva@{__version__}",
        environment=environment,
        traces_sample_rate=1.0,
        profiles_sample_rate=0.1,
        send_default_pii=False,
        # Tag every event with Eva metadata
        before_send=_before_send,
    )

    # Set global context
    sentry_sdk.set_tag("agent", "eva")
    sentry_sdk.set_tag("platform", "ievo")

    _initialized = True
    return True


def capture_scan_context(
    mode: str,
    signals: int = 0,
    patterns: int = 0,
    mutations: int = 0,
    prs_created: int = 0,
) -> None:
    """Set Sentry context for the current scan run."""
    sentry_sdk.set_context(
        "eva_scan",
        {
            "mode": mode,
            "signals_collected": signals,
            "patterns_detected": patterns,
            "mutations_proposed": mutations,
            "prs_created": prs_created,
        },
    )


def _before_send(event: dict, hint: dict) -> dict:
    """Pre-process events before sending to Sentry.

    - Strips any accidental token leaks from breadcrumbs
    """
    # Scrub authorization headers from HTTP breadcrumbs
    for breadcrumb in event.get("breadcrumbs", {}).get("values", []):
        data = breadcrumb.get("data", {})
        if "headers" in data:
            headers = data["headers"]
            if isinstance(headers, dict):
                for key in list(headers.keys()):
                    if key.lower() in ("authorization", "x-sentry-auth"):
                        headers[key] = "[REDACTED]"
    return event
