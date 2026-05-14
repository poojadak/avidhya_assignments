"""
Incident Triage Workflow (WF-02) — TASK 4: Complete this file.

Triggered during a live incident. Chains 4 MCP calls to diagnose
the probable cause and recommend an action.

Output: A JSON dict matching the IncidentReport schema below.
"""
from __future__ import annotations
import json
import sys
from typing import TypedDict

from mcp import github_tools, db_tools
from workflows.base import BaseWorkflow


class IncidentReport(TypedDict):
    """The exact JSON schema your workflow must return."""
    service:              str
    error_rate_now:       float
    error_rate_30min_avg: float
    likely_cause:         str
    recent_deploys:       list[str]
    recommended_action:   str
    escalate:             bool


# Fallback returned when parsing fails or a critical error occurs
ESCALATE_FALLBACK: IncidentReport = {
    "service":              "unknown",
    "error_rate_now":       -1.0,
    "error_rate_30min_avg": -1.0,
    "likely_cause":         "Triage workflow failed — see stderr for details",
    "recent_deploys":       [],
    "recommended_action":   "Page on-call immediately — automated triage unavailable",
    "escalate":             True,
}


class IncidentTriageWorkflow(BaseWorkflow):
    name = "incident_triage"

    def execute(self, service_name: str = "payments") -> IncidentReport:
        """
        Chains 4 data calls, asks Claude for a diagnosis, and returns
        a structured JSON report.

        Args:
            service_name: The microservice being investigated.

        Returns:
            IncidentReport dict.
        """
        repo = self.config.GITHUB_REPO

        # Step 1 — 30-min error rate baseline
        try:
            rate_30min = db_tools.get_error_rate(service_name, window_minutes=30)
        except Exception as exc:
            print(f"[incident_triage] db_tools.get_error_rate(30min) failed: {exc}", file=sys.stderr)
            rate_30min = {}

        # Step 2 — Recent commits to this service
        try:
            commits = github_tools.search_recent_commits(self.mcp, repo, service_name, hours=4)
        except Exception as exc:
            print(f"[incident_triage] search_recent_commits failed: {exc}", file=sys.stderr)
            commits = []

        # Step 3 — Open bugs tagged with this service
        try:
            bugs = github_tools.get_priority_issues(self.mcp, repo, labels=["bug", service_name])
        except Exception as exc:
            print(f"[incident_triage] get_priority_issues failed: {exc}", file=sys.stderr)
            bugs = []

        # Step 4 — Current 5-min error rate snapshot
        try:
            rate_now = db_tools.get_error_rate(service_name, window_minutes=5)
        except Exception as exc:
            print(f"[incident_triage] db_tools.get_error_rate(5min) failed: {exc}", file=sys.stderr)
            rate_now = {}

        # Step 5 — Build and send the prompt
        template = self._load_prompt("incident_triage.txt")
        prompt = (
            template
            .replace("{{SERVICE_NAME}}", service_name)
            .replace("{{ERROR_RATE_30MIN}}", json.dumps(rate_30min, indent=2))
            .replace("{{ERROR_RATE_NOW}}", json.dumps(rate_now, indent=2))
            .replace("{{RECENT_COMMITS}}", json.dumps(commits, indent=2))
            .replace("{{OPEN_BUGS}}", json.dumps(bugs, indent=2))
        )

        raw_response = self.mcp.ask(prompt)

        # Step 6 — Parse Claude's JSON response
        try:
            # Strip markdown fences in case Claude adds them despite instructions
            clean = raw_response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            report: IncidentReport = json.loads(clean)
            return report
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[incident_triage] JSON parse failed: {exc}\nRaw response:\n{raw_response}", file=sys.stderr)
            fallback = dict(ESCALATE_FALLBACK)
            fallback["service"] = service_name
            return fallback
