"""Tests for Eva CLI."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from eva.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestMainGroup:
    def test_version_flag(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "eva" in result.output

    def test_no_args_shows_help(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert "Eva" in result.output
        assert "scan" in result.output

    def test_help_flag(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "scan" in result.output


class TestScanCommand:
    def test_scan_dry_run(self, runner, tmp_path):
        config_path = tmp_path / "eva.yaml"

        mock_run = EvaRunResult()
        mock_pipeline = MagicMock()
        mock_pipeline.run = AsyncMock(return_value=mock_run)
        mock_pipeline.print_summary = MagicMock()
        mock_pipeline.save_report = MagicMock()

        with patch("eva.pipeline.EvaPipeline", return_value=mock_pipeline) as mock_cls:
            result = runner.invoke(
                main, ["scan", "-c", str(config_path), "-r", str(tmp_path / "report.json")]
            )

        assert result.exit_code == 0
        mock_cls.assert_called_once()
        mock_pipeline.run.assert_called_once()
        mock_pipeline.print_summary.assert_called_once()
        mock_pipeline.save_report.assert_called_once()

    def test_scan_live_mode(self, runner, tmp_path):
        config_path = tmp_path / "eva.yaml"

        mock_run = EvaRunResult()
        mock_pipeline = MagicMock()
        mock_pipeline.run = AsyncMock(return_value=mock_run)
        mock_pipeline.print_summary = MagicMock()
        mock_pipeline.save_report = MagicMock()

        with patch("eva.pipeline.EvaPipeline", return_value=mock_pipeline):
            result = runner.invoke(
                main,
                ["scan", "--live", "-c", str(config_path), "-r", str(tmp_path / "report.json")],
            )

        assert result.exit_code == 0

    def test_scan_with_marketplace(self, runner, tmp_path):
        config_path = tmp_path / "eva.yaml"
        marketplace_dir = tmp_path / "marketplace"
        marketplace_dir.mkdir()

        mock_run = EvaRunResult()
        mock_pipeline = MagicMock()
        mock_pipeline.run = AsyncMock(return_value=mock_run)
        mock_pipeline.print_summary = MagicMock()
        mock_pipeline.save_report = MagicMock()

        with patch("eva.pipeline.EvaPipeline", return_value=mock_pipeline):
            result = runner.invoke(
                main,
                [
                    "scan",
                    "-c",
                    str(config_path),
                    "-m",
                    str(marketplace_dir),
                    "-r",
                    str(tmp_path / "report.json"),
                ],
            )

        assert result.exit_code == 0

    def test_scan_exception_reraises(self, runner, tmp_path):
        config_path = tmp_path / "eva.yaml"

        mock_pipeline = MagicMock()
        mock_pipeline.run = AsyncMock(side_effect=RuntimeError("Pipeline failed"))

        with patch("eva.pipeline.EvaPipeline", return_value=mock_pipeline):
            result = runner.invoke(
                main, ["scan", "-c", str(config_path), "-r", str(tmp_path / "report.json")]
            )

        assert result.exit_code != 0


class TestStatusCommand:
    def test_status_default_config(self, runner, tmp_path):
        config_path = tmp_path / "eva.yaml"
        result = runner.invoke(main, ["status", "-c", str(config_path)])
        assert result.exit_code == 0
        assert "dry-run" in result.output


class TestInitCommand:
    def test_init_creates_config(self, runner, tmp_path):
        output_path = tmp_path / "eva.yaml"
        result = runner.invoke(main, ["init", "-o", str(output_path)])
        assert result.exit_code == 0
        assert output_path.exists()

    def test_init_aborts_on_existing(self, runner, tmp_path):
        output_path = tmp_path / "eva.yaml"
        output_path.write_text("existing")
        result = runner.invoke(main, ["init", "-o", str(output_path)], input="n\n")
        assert result.exit_code == 0
        assert "Aborted" in result.output

    def test_init_overwrites_on_confirm(self, runner, tmp_path):
        output_path = tmp_path / "eva.yaml"
        output_path.write_text("existing")
        result = runner.invoke(main, ["init", "-o", str(output_path)], input="y\n")
        assert result.exit_code == 0
        assert "Created" in result.output


class TestExportMemoryCommand:
    def test_export_no_data(self, runner, tmp_path):
        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        (agent_dir / "memory").mkdir()
        result = runner.invoke(main, ["export-memory", "--agent-dir", str(agent_dir)])
        assert result.exit_code == 0
        assert "No memory entries" in result.output

    def test_export_to_stdout(self, runner, tmp_path):
        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        memory = agent_dir / "memory"
        memory.mkdir()
        (memory / "DECISIONS.md").write_text(
            "| ID | Date | Decision | Rationale | Status |\n"
            "|----|------|----------|-----------|--------|\n"
            "| D-001 | 2026-02-28 | Test | Reason | Active |\n"
        )
        result = runner.invoke(main, ["export-memory", "--agent-dir", str(agent_dir)])
        assert result.exit_code == 0
        assert "D-001" in result.output
        assert "entries" in result.output

    def test_export_to_file(self, runner, tmp_path):
        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        memory = agent_dir / "memory"
        memory.mkdir()
        (memory / "DECISIONS.md").write_text(
            "| ID | Date | Decision | Rationale | Status |\n"
            "|----|------|----------|-----------|--------|\n"
            "| D-001 | 2026-02-28 | Test | Reason | Active |\n"
        )
        output_path = tmp_path / "memory.txt"
        result = runner.invoke(
            main, ["export-memory", "-o", str(output_path), "--agent-dir", str(agent_dir)]
        )
        assert result.exit_code == 0
        assert output_path.exists()
        assert "D-001" in output_path.read_text()

    def test_export_with_include_filter(self, runner, tmp_path):
        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        memory = agent_dir / "memory"
        memory.mkdir()
        (memory / "DECISIONS.md").write_text(
            "| ID | Date | Decision | Rationale | Status |\n"
            "|----|------|----------|-----------|--------|\n"
            "| D-001 | 2026-02-28 | Test | Reason | Active |\n"
        )
        (memory / "HISTORY.md").write_text(
            "| # | Date | Topic | Key outcome |\n"
            "|---|------|-------|-------------|\n"
            "| 001 | 2026-02-28 | Build | Built everything |\n"
        )
        result = runner.invoke(
            main, ["export-memory", "--include", "decisions", "--agent-dir", str(agent_dir)]
        )
        assert result.exit_code == 0
        assert "D-001" in result.output

    def test_export_from_report(self, runner, tmp_path):
        import json

        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        (agent_dir / "memory").mkdir()
        report = {
            "signals": [
                {
                    "id": "sig-1",
                    "type": "github_issue",
                    "source": "test",
                    "title": "Test Signal",
                    "severity": "medium",
                    "tags": [],
                }
            ],
            "patterns": [],
            "mutations": [],
        }
        report_path = tmp_path / "report.json"
        report_path.write_text(json.dumps(report))
        result = runner.invoke(
            main,
            ["export-memory", "--from-report", str(report_path), "--agent-dir", str(agent_dir)],
        )
        assert result.exit_code == 0
        assert "Test Signal" in result.output


class TestApproveCommand:
    def test_approve_placeholder(self, runner):
        result = runner.invoke(main, ["approve", "mut-0001"])
        assert result.exit_code == 0
        assert "Phase 2" in result.output
        assert "mut-0001" in result.output


class TestPublishCommand:
    def test_publish_dry_run(self, runner):
        result = runner.invoke(
            main,
            [
                "publish",
                "--title",
                "Test evolution",
                "--type",
                "milestone",
                "--agent",
                "eva",
            ],
        )
        assert result.exit_code == 0
        assert "Preview" in result.output
        assert "--live" in result.output

    def test_publish_live(self, runner):
        mock_publisher = MagicMock()
        mock_publisher.publish_entries = AsyncMock(return_value=1)

        with (
            patch(
                "eva.github.evolution_publisher.EvolutionPublisher",
                return_value=mock_publisher,
            ),
            patch("eva.telegram.client.TelegramClient", side_effect=ValueError("No token")),
        ):
            result = runner.invoke(
                main,
                [
                    "publish",
                    "--title",
                    "Test",
                    "--type",
                    "milestone",
                    "--live",
                ],
            )

        assert result.exit_code == 0

    def test_publish_live_no_github_token(self, runner):
        with (
            patch(
                "eva.github.evolution_publisher.EvolutionPublisher",
                side_effect=ValueError("No token"),
            ),
            patch("eva.telegram.client.TelegramClient", side_effect=ValueError("No tg")),
        ):
            result = runner.invoke(
                main,
                [
                    "publish",
                    "--title",
                    "Test",
                    "--type",
                    "milestone",
                    "--live",
                ],
            )

        assert result.exit_code == 0
        assert "No token" in result.output

    def test_publish_live_zero_published(self, runner):
        mock_publisher = MagicMock()
        mock_publisher.publish_entries = AsyncMock(return_value=0)

        with (
            patch(
                "eva.github.evolution_publisher.EvolutionPublisher",
                return_value=mock_publisher,
            ),
            patch("eva.telegram.client.TelegramClient", side_effect=ValueError("No tg")),
        ):
            result = runner.invoke(
                main,
                [
                    "publish",
                    "--title",
                    "Test",
                    "--type",
                    "milestone",
                    "--live",
                ],
            )

        assert result.exit_code == 0
        assert "Nothing published" in result.output

    def test_publish_live_with_telegram(self, runner):
        mock_tg = MagicMock()
        mock_publisher = MagicMock()
        mock_publisher.publish_entries = AsyncMock(return_value=1)

        with (
            patch(
                "eva.github.evolution_publisher.EvolutionPublisher",
                return_value=mock_publisher,
            ),
            patch("eva.telegram.client.TelegramClient", return_value=mock_tg),
        ):
            result = runner.invoke(
                main,
                [
                    "publish",
                    "--title",
                    "Test",
                    "--type",
                    "milestone",
                    "--live",
                ],
            )

        assert result.exit_code == 0


class TestTgProcessCommand:
    def test_tg_process_no_telegram(self, runner):
        with patch(
            "eva.telegram.client.TelegramClient",
            side_effect=ValueError("No token"),
        ):
            result = runner.invoke(main, ["tg-process"])

        assert result.exit_code == 0
        assert "No token" in result.output

    def test_tg_process_no_responder(self, runner):
        mock_tg = MagicMock()
        with (
            patch("eva.telegram.client.TelegramClient", return_value=mock_tg),
            patch(
                "eva.telegram.responder.EvaResponder",
                side_effect=ValueError("No Claude CLI or Anthropic API key"),
            ),
        ):
            result = runner.invoke(main, ["tg-process"])

        assert result.exit_code == 0
        assert "No Claude CLI" in result.output

    def test_tg_process_no_messages(self, runner):
        mock_tg = MagicMock()
        mock_tg.get_updates = AsyncMock(return_value=[])
        mock_responder = MagicMock()

        with (
            patch("eva.telegram.client.TelegramClient", return_value=mock_tg),
            patch("eva.telegram.responder.EvaResponder", return_value=mock_responder),
        ):
            result = runner.invoke(main, ["tg-process"])

        assert result.exit_code == 0
        assert "No new messages" in result.output

    def test_tg_process_with_messages(self, runner):
        from eva.telegram.client import TelegramResult

        mock_tg = MagicMock()
        mock_tg.get_updates = AsyncMock(
            side_effect=[
                [
                    {
                        "update_id": 1,
                        "message": {
                            "message_id": 42,
                            "text": "How do agents work?",
                            "from": {"username": "alice"},
                        },
                    }
                ],
                [],  # offset confirmation call
            ]
        )
        mock_tg.send_message = AsyncMock(
            return_value=TelegramResult(success=True, message_id=99),
        )

        mock_responder = MagicMock()
        mock_responder.respond = AsyncMock(return_value="The agents collaborate.")

        with (
            patch("eva.telegram.client.TelegramClient", return_value=mock_tg),
            patch("eva.telegram.responder.EvaResponder", return_value=mock_responder),
        ):
            result = runner.invoke(main, ["tg-process"])

        assert result.exit_code == 0
        assert "alice" in result.output
        assert "Processed 1" in result.output
        # Verify offset confirmation: get_updates called with offset=2
        assert mock_tg.get_updates.call_count == 2
        confirm_kwargs = mock_tg.get_updates.call_args_list[1][1]
        assert confirm_kwargs["offset"] == 2

    def test_tg_process_noise_skipped(self, runner):
        mock_tg = MagicMock()
        mock_tg.get_updates = AsyncMock(
            side_effect=[
                [
                    {
                        "update_id": 1,
                        "message": {
                            "message_id": 42,
                            "text": "random spam",
                            "from": {"first_name": "Spammer"},
                        },
                    }
                ],
                [],  # offset confirmation
            ]
        )

        mock_responder = MagicMock()
        mock_responder.respond = AsyncMock(return_value="")

        with (
            patch("eva.telegram.client.TelegramClient", return_value=mock_tg),
            patch("eva.telegram.responder.EvaResponder", return_value=mock_responder),
        ):
            result = runner.invoke(main, ["tg-process"])

        assert result.exit_code == 0
        assert "Spammer" in result.output
        assert "Processed 0" in result.output

    def test_tg_process_skips_empty_text(self, runner):
        mock_tg = MagicMock()
        mock_tg.get_updates = AsyncMock(
            side_effect=[
                [
                    {
                        "update_id": 1,
                        "message": {"message_id": 42, "from": {"first_name": "Photo"}},
                    }
                ],
                [],  # offset confirmation
            ]
        )

        mock_responder = MagicMock()

        with (
            patch("eva.telegram.client.TelegramClient", return_value=mock_tg),
            patch("eva.telegram.responder.EvaResponder", return_value=mock_responder),
        ):
            result = runner.invoke(main, ["tg-process"])

        assert result.exit_code == 0
        assert "Processed 0" in result.output

    def test_tg_process_skips_bot_messages(self, runner):
        mock_tg = MagicMock()
        mock_tg.get_updates = AsyncMock(
            side_effect=[
                [
                    {
                        "update_id": 1,
                        "message": {
                            "message_id": 42,
                            "text": "I am a bot message",
                            "from": {"username": "ievo_ai_bot", "is_bot": True},
                        },
                    }
                ],
                [],  # offset confirmation
            ]
        )

        mock_responder = MagicMock()

        with (
            patch("eva.telegram.client.TelegramClient", return_value=mock_tg),
            patch("eva.telegram.responder.EvaResponder", return_value=mock_responder),
        ):
            result = runner.invoke(main, ["tg-process"])

        assert result.exit_code == 0
        assert "Processed 0" in result.output
        mock_responder.respond.assert_not_called()


# --- Helpers ---


class EvaRunResult:
    """Minimal mock for EvaRun."""

    def __init__(self):
        self.signals = []
        self.patterns = []
        self.mutations = []
        self.pr_results = []
