"""
Integration tests for workflows — TASK 5: Write 3 tests here.

Use unittest.mock to mock MCP calls — never make real API calls in tests.
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from workflows.morning_brief import MorningBriefWorkflow
from workflows.incident_triage import IncidentTriageWorkflow, ESCALATE_FALLBACK


# ─── Shared sample data ────────────────────────────────────────────────────────

SAMPLE_PRS = [
    {"number": 42, "title": "Fix payment retry logic", "author": "alice",
     "days_open": 3, "review_count": 0},
]

SAMPLE_ISSUES = [
    {"number": 7, "title": "Payments service OOM on peak load", "priority": "P0",
     "assignee": "bob", "days_open": 2},
]

SAMPLE_DB_ALERTS = [
    {"service": "payments", "hour_utc": 3, "error_rate": 0.82,
     "baseline": 0.21, "delta_pct": 290.5},
]

SAMPLE_COMMITS = [
    {"sha_short": "abc1234", "author": "carol",
     "message": "bump payments retry timeout", "timestamp": "2025-04-24T08:00:00+00:00",
     "files_changed": 2},
]

SAMPLE_RATE_30 = {"service": "payments", "window_minutes": 30,
                  "error_rate": 0.15, "baseline": 0.12}

SAMPLE_RATE_5  = {"service": "payments", "window_minutes": 5,
                  "error_rate": 0.65, "baseline": 0.12}


# ─── Test 1 ────────────────────────────────────────────────────────────────────

def test_morning_brief_structure():
    """
    Mock all MCP/DB calls and verify the output has all 4 required section headers.
    """
    mock_mcp = MagicMock()
    mock_config = MagicMock()
    mock_config.GITHUB_REPO = "owner/repo"

    # Claude's ask() returns a plausible brief
    mock_mcp.ask.return_value = (
        "## PRs_NEEDING_REVIEW\n"
        "- PR #42: Fix payment retry logic — alice — 3 days open\n\n"
        "## OPEN_P0_P1\n"
        "- #7 [P0] Payments service OOM on peak load — bob — 2 days\n\n"
        "## OVERNIGHT_DB_ALERTS\n"
        "- payments spiked to 0.82 at 03:00 UTC (+290%)\n\n"
        "## ACTION_ITEMS\n"
        "- Review PR #42\n"
        "- Investigate payments OOM issue #7\n"
        "- Monitor payments error rate through morning\n"
    )

    with (
        patch("workflows.morning_brief.github_tools.get_open_prs", return_value=SAMPLE_PRS),
        patch("workflows.morning_brief.github_tools.get_priority_issues", return_value=SAMPLE_ISSUES),
        patch("workflows.morning_brief.db_tools.get_overnight_alerts", return_value=SAMPLE_DB_ALERTS),
    ):
        wf = MorningBriefWorkflow(mock_mcp, mock_config)
        result = wf.run()

    required_headers = [
        "## PRs_NEEDING_REVIEW",
        "## OPEN_P0_P1",
        "## OVERNIGHT_DB_ALERTS",
        "## ACTION_ITEMS",
    ]
    for header in required_headers:
        assert header in result, f"Missing required section header: {header}"


# ─── Test 2 ────────────────────────────────────────────────────────────────────

def test_incident_triage_valid_json():
    """
    Mock all MCP/DB calls and verify execute() returns a dict with
    all required keys and correct types.
    """
    mock_mcp = MagicMock()
    mock_config = MagicMock()
    mock_config.GITHUB_REPO = "owner/repo"

    expected_report = {
        "service":              "payments",
        "error_rate_now":       0.65,
        "error_rate_30min_avg": 0.15,
        "likely_cause":         "Recent commit bumped retry timeout, causing cascading delays.",
        "recent_deploys":       ["abc1234: bump payments retry timeout"],
        "recommended_action":   "Roll back abc1234 and monitor error rate.",
        "escalate":             True,
    }
    mock_mcp.ask.return_value = json.dumps(expected_report)

    with (
        patch("workflows.incident_triage.db_tools.get_error_rate",
              side_effect=[SAMPLE_RATE_30, SAMPLE_RATE_5]),
        patch("workflows.incident_triage.github_tools.search_recent_commits",
              return_value=SAMPLE_COMMITS),
        patch("workflows.incident_triage.github_tools.get_priority_issues",
              return_value=SAMPLE_ISSUES),
    ):
        wf = IncidentTriageWorkflow(mock_mcp, mock_config)
        result = wf.run(service_name="payments")

    # All required keys must be present
    required_keys = {
        "service", "error_rate_now", "error_rate_30min_avg",
        "likely_cause", "recent_deploys", "recommended_action", "escalate",
    }
    assert required_keys == set(result.keys()), f"Missing keys: {required_keys - set(result.keys())}"

    # Type checks
    assert isinstance(result["service"], str)
    assert isinstance(result["error_rate_now"], float)
    assert isinstance(result["error_rate_30min_avg"], float)
    assert isinstance(result["likely_cause"], str)
    assert isinstance(result["recent_deploys"], list)
    assert isinstance(result["recommended_action"], str)
    assert isinstance(result["escalate"], bool)


# ─── Test 3 ────────────────────────────────────────────────────────────────────

def test_incident_triage_degraded():
    """
    When the first DB call raises an exception, execute() must return a fallback
    dict with escalate=True — NOT an unhandled exception.
    """
    mock_mcp = MagicMock()
    mock_config = MagicMock()
    mock_config.GITHUB_REPO = "owner/repo"

    # Even if Claude returns valid JSON, we want to confirm the fallback path
    # when the very first DB call explodes
    mock_mcp.ask.return_value = "{}"  # Should not be reached in degraded path ideally

    def db_error_rate_side_effect(service, window_minutes=30):
        if window_minutes == 30:
            raise ConnectionError("pg-mcp unreachable")
        return SAMPLE_RATE_5

    with (
        patch("workflows.incident_triage.db_tools.get_error_rate",
              side_effect=db_error_rate_side_effect),
        patch("workflows.incident_triage.github_tools.search_recent_commits",
              return_value=SAMPLE_COMMITS),
        patch("workflows.incident_triage.github_tools.get_priority_issues",
              return_value=[]),
    ):
        # Mock ask to return invalid JSON so fallback triggers
        mock_mcp.ask.return_value = "THIS IS NOT JSON"

        wf = IncidentTriageWorkflow(mock_mcp, mock_config)
        result = wf.run(service_name="payments")

    # Must not raise — must return the fallback
    assert isinstance(result, dict), "Expected a dict result, not an exception"
    assert result["escalate"] is True, "Degraded mode must always escalate"
    assert "service" in result
