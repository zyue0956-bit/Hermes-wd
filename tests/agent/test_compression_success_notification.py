"""Compression success notification: _emit_status after compress_context.

After compress_context finishes, the user should see a status message
reporting the before/after message count and estimated token count.
Previously only the start ("Compacting context") and failures were
surfaced — success was silent.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from hermes_state import SessionDB


def _build_agent(tmp_path: Path) -> tuple:
    """Build an AIAgent with a stub compressor, return (agent, emitted list)."""
    db = SessionDB(db_path=tmp_path / "state.db")
    session_id = "TEST_COMPRESS_NOTIFY"
    db.create_session(session_id, source="cli")

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        from run_agent import AIAgent

        agent = AIAgent(
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="test/model",
            quiet_mode=True,
            session_db=db,
            session_id=session_id,
            skip_context_files=True,
            skip_memory=True,
        )

    compressor = MagicMock()
    compressor.compress.return_value = [
        {"role": "user", "content": "[CONTEXT COMPACTION] summary"},
        {"role": "user", "content": "tail msg 1"},
        {"role": "user", "content": "tail msg 2"},
    ]
    compressor.compression_count = 1
    compressor.last_prompt_tokens = 0
    compressor.last_completion_tokens = 0
    compressor._last_summary_error = None
    compressor._last_compress_aborted = False
    compressor._last_aux_model_failure_model = None
    compressor._last_aux_model_failure_error = None
    agent.context_compressor = compressor

    emitted = []
    agent._emit_status = lambda msg: emitted.append(msg)

    return agent, emitted


def test_compress_context_emits_success_status(tmp_path: Path) -> None:
    """compress_context should emit a status with message and token counts."""
    agent, emitted = _build_agent(tmp_path)

    messages = [{"role": "user", "content": f"message {i}"} for i in range(20)]
    agent._compress_context(messages, "system prompt", approx_tokens=120_000)

    success_msgs = [m for m in emitted if "compressed" in m.lower() or "compress" in m.lower()]
    assert len(success_msgs) >= 1, (
        f"Expected a compression success status message, got: {emitted}"
    )

    msg = success_msgs[-1]
    assert "20" in msg or "20 " in msg, f"Should mention pre-compression message count: {msg}"
    assert "3" in msg, f"Should mention post-compression message count: {msg}"
    assert "token" in msg.lower() or "," in msg, f"Should mention token estimate: {msg}"
