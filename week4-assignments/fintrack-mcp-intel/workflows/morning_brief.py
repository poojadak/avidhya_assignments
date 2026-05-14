"""
Morning Intelligence Brief Workflow (WF-01) — TASK 3: Complete this file.

This workflow runs every morning and gives the FinTrack engineering team
a concise, data-driven overview of what needs attention.

Data sources:
  - GitHub: open PRs needing review, open P0/P1 issues
  - PostgreSQL: services with elevated error rates overnight

Output: A markdown string with 4 required sections (see task description).
"""
from __future__ import annotations
import json

from mcp import github_tools, db_tools
from workflows.base import BaseWorkflow


class MorningBriefWorkflow(BaseWorkflow):
    name = "morning_brief"

    def execute(self) -> str:
        """
        Chains three data sources, injects them into a prompt template,
        and asks Claude to produce a structured markdown brief.

        Returns:
            str: Formatted markdown containing all 4 required sections.
        """
        repo = self.config.GITHUB_REPO

        # Step 1 — Pull GitHub data
        prs = github_tools.get_open_prs(self.mcp, repo)
        issues = github_tools.get_priority_issues(self.mcp, repo)

        # Step 2 — Pull database overnight alerts
        db_alerts = db_tools.get_overnight_alerts()

        # Step 3 — Format data for the prompt, handling empty cases gracefully
        pr_data = json.dumps(prs, indent=2) if prs else "[]"
        issue_data = json.dumps(issues, indent=2) if issues else "[]"
        alerts_data = json.dumps(db_alerts, indent=2) if db_alerts else "[]"

        # Step 4 — Load template and inject data
        template = self._load_prompt("morning_brief.txt")
        prompt = (
            template
            .replace("{{PR_DATA}}", pr_data)
            .replace("{{ISSUE_DATA}}", issue_data)
            .replace("{{DB_ALERTS}}", alerts_data)
        )

        # Step 5 — Ask Claude to produce the formatted report
        response = self.mcp.ask(prompt)
        return response
