"""Tests for Eva telemetry — Sentry SDK integration."""

from unittest.mock import patch

import eva.telemetry as telemetry_module
from eva.telemetry import _before_send, capture_scan_context, init_sentry


class TestInitSentry:
    def setup_method(self):
        # Reset module state between tests
        telemetry_module._initialized = False

    def test_skips_without_dsn(self):
        with patch.dict("os.environ", {}, clear=True):
            telemetry_module._initialized = False
            result = init_sentry()
            assert result is False

    def test_initializes_with_dsn(self):
        with (
            patch.dict("os.environ", {"EVA_SENTRY_DSN": "https://key@sentry.io/123"}),
            patch("eva.telemetry.sentry_sdk") as mock_sdk,
        ):
            telemetry_module._initialized = False
            result = init_sentry()
            assert result is True
            mock_sdk.init.assert_called_once()
            mock_sdk.set_tag.assert_any_call("agent", "eva")
            mock_sdk.set_tag.assert_any_call("platform", "ievo")

    def test_only_initializes_once(self):
        telemetry_module._initialized = True
        result = init_sentry()
        assert result is True

    def test_uses_environment_var(self):
        with (
            patch.dict(
                "os.environ",
                {"EVA_SENTRY_DSN": "https://key@sentry.io/123", "EVA_ENVIRONMENT": "staging"},
            ),
            patch("eva.telemetry.sentry_sdk") as mock_sdk,
        ):
            telemetry_module._initialized = False
            init_sentry()
            call_kwargs = mock_sdk.init.call_args[1]
            assert call_kwargs["environment"] == "staging"

    def test_defaults_to_production(self):
        with (
            patch.dict("os.environ", {"EVA_SENTRY_DSN": "https://key@sentry.io/123"}, clear=True),
            patch("eva.telemetry.sentry_sdk") as mock_sdk,
        ):
            telemetry_module._initialized = False
            init_sentry()
            call_kwargs = mock_sdk.init.call_args[1]
            assert call_kwargs["environment"] == "production"


class TestCaptureScanContext:
    def test_sets_context(self):
        with patch("eva.telemetry.sentry_sdk") as mock_sdk:
            capture_scan_context(mode="dry-run", signals=5, patterns=2, mutations=1, prs_created=0)
            mock_sdk.set_context.assert_called_once_with(
                "eva_scan",
                {
                    "mode": "dry-run",
                    "signals_collected": 5,
                    "patterns_detected": 2,
                    "mutations_proposed": 1,
                    "prs_created": 0,
                },
            )


class TestBeforeSend:
    def test_returns_event(self):
        event = {"message": "test"}
        result = _before_send(event, {})
        assert result == event

    def test_redacts_authorization_header(self):
        event = {
            "breadcrumbs": {
                "values": [
                    {
                        "data": {
                            "headers": {
                                "Authorization": "Bearer secret-token",
                                "Content-Type": "application/json",
                            }
                        }
                    }
                ]
            }
        }
        result = _before_send(event, {})
        assert result is not None
        headers = result["breadcrumbs"]["values"][0]["data"]["headers"]
        assert headers["Authorization"] == "[REDACTED]"
        assert headers["Content-Type"] == "application/json"

    def test_redacts_sentry_auth_header(self):
        event = {"breadcrumbs": {"values": [{"data": {"headers": {"x-sentry-auth": "secret"}}}]}}
        result = _before_send(event, {})
        assert result is not None
        assert (
            result["breadcrumbs"]["values"][0]["data"]["headers"]["x-sentry-auth"] == "[REDACTED]"
        )

    def test_handles_no_breadcrumbs(self):
        event = {"message": "test"}
        result = _before_send(event, {})
        assert result == event

    def test_handles_non_dict_breadcrumbs(self):
        event = {"breadcrumbs": "not-a-dict"}
        result = _before_send(event, {})
        assert result == event

    def test_handles_breadcrumb_without_headers(self):
        event = {"breadcrumbs": {"values": [{"data": {"url": "https://example.com"}}]}}
        result = _before_send(event, {})
        assert result == event

    def test_handles_breadcrumb_without_data(self):
        event = {"breadcrumbs": {"values": [{"category": "http"}]}}
        result = _before_send(event, {})
        assert result == event

    def test_handles_non_dict_headers(self):
        event = {"breadcrumbs": {"values": [{"data": {"headers": "not-a-dict"}}]}}
        result = _before_send(event, {})
        assert result == event
