"""G-Eval benchmark judge — scores agent output against a rubric."""

import asyncio
import json
import os
import shutil

from eva.benchmark.models import DimensionScore, JudgeScore, Rubric

JUDGE_PROMPT_TEMPLATE = """\
You are a benchmark judge evaluating an AI agent's output against a scoring rubric.

## Agent: {agent}
## Task: {task_id}

## Rubric

{rubric_section}

## Agent Output

{agent_output}

## Instructions

For EACH dimension in the rubric:
1. Write chain-of-thought reasoning analyzing the output against dimension criteria
2. Then assign a score from 0 to 100
3. List specific evidence from the output supporting your score

Respond with ONLY valid JSON in this exact format:
{{
  "dimensions": [
    {{
      "dimension": "<dimension_name>",
      "reasoning": "<chain-of-thought analysis>",
      "score": <0-100>,
      "evidence": ["<specific evidence 1>", "<specific evidence 2>"]
    }}
  ]
}}

No markdown code blocks. No extra text. Just the JSON object."""


def _format_rubric_section(rubric: Rubric) -> str:
    """Format rubric dimensions as readable text for the judge prompt."""
    lines = []
    for dim in rubric.dimensions:
        lines.append(f"### {dim.name} (weight: {dim.weight})")
        lines.append(dim.description)
        if dim.criteria:
            lines.append("Criteria:")
            for c in dim.criteria:
                lines.append(f"  - {c}")
        lines.append("")
    return "\n".join(lines)


class BenchmarkJudge:
    """Scores agent output using G-Eval pattern via Claude CLI."""

    def __init__(
        self,
        model: str = "haiku",
        timeout_sec: int = 300,
    ) -> None:
        self._model = model
        self._timeout = timeout_sec
        self._claude_cli: str | None = shutil.which("claude")

    async def score(
        self,
        task_id: str,
        agent: str,
        rubric: Rubric,
        agent_output: str,
    ) -> JudgeScore:
        """Score agent output against rubric using G-Eval."""
        prompt = JUDGE_PROMPT_TEMPLATE.format(
            agent=agent,
            task_id=task_id,
            rubric_section=_format_rubric_section(rubric),
            agent_output=agent_output,
        )
        raw_response = await self._call_claude(prompt)
        dimension_scores = self._parse_response(raw_response)
        return JudgeScore(
            task_id=task_id,
            agent=agent,
            dimension_scores=dimension_scores,
            raw_output=agent_output,
            judge_model=self._model,
        )

    async def _call_claude(self, prompt: str) -> str:
        """Call Claude CLI with judge prompt.

        Uses create_subprocess_exec (not shell) to avoid injection.
        The prompt is passed as a single argument to the CLI.
        """
        cli = self._claude_cli
        if not cli:
            msg = "Claude CLI not found. Install: npm install -g @anthropic-ai/claude-code"
            raise RuntimeError(msg)

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        args = [cli, "-p", "--model", self._model, "--output-format", "text", prompt]

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=self._timeout)
        except TimeoutError:
            proc.kill()
            await proc.communicate()
            msg = f"Judge timed out after {self._timeout}s"
            raise TimeoutError(msg) from None

        if proc.returncode != 0:
            return ""

        return stdout.decode().strip()

    @staticmethod
    def _parse_response(raw: str) -> list[DimensionScore]:
        """Parse structured JSON response from judge."""
        if not raw:
            return []

        # Strip markdown code blocks if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [ln for ln in lines if not ln.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return []

        scores = []
        for dim_data in data.get("dimensions", []):
            scores.append(
                DimensionScore(
                    dimension=dim_data.get("dimension", ""),
                    score=int(dim_data.get("score", 0)),
                    reasoning=dim_data.get("reasoning", ""),
                    evidence=dim_data.get("evidence", []),
                )
            )
        return scores
