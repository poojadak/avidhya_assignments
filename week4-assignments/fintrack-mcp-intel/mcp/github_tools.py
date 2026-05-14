"""
GitHub MCP Tool Wrappers — TASK 2: Complete this file.

Each function wraps one or more GitHub MCP tool calls, handles errors
gracefully (returning [] on failure), and logs every call via AuditLogger.

The caller (workflow code) should never see an exception from this module.
"""
from __future__ import annotations
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

from mcp.audit import AuditLogger

if TYPE_CHECKING:
    from mcp.client import MCPClient


_audit = AuditLogger()


def get_open_prs(mcp: "MCPClient", repo: str, min_age_days: int = 1) -> list[dict]:
    """
    Fetch open, non-draft pull requests older than min_age_days.

    Args:
        mcp:          The MCPClient context (use mcp.call())
        repo:         GitHub repo in 'owner/repo' format
        min_age_days: Only return PRs open for at least this many days

    Returns:
        List of dicts with: number, title, author, days_open, review_count
        Returns [] on any error.
    """
    tool_input = {"repo": repo, "state": "open"}
    start = time.perf_counter()
    status = "success"
    try:
        raw = mcp.call("github_pull_requests", tool_input)
        results = []

        if not isinstance(raw, list):
            raw = []

        cutoff = datetime.now(timezone.utc) - timedelta(days=min_age_days)

        for pr in raw:
            # Skip draft PRs — they're not ready for review
            if pr.get("draft", False):
                continue

            created_raw = pr.get("created_at", "")
            try:
                created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                continue

            if created_at > cutoff:
                continue  # Too fresh — not old enough

            days_open = (datetime.now(timezone.utc) - created_at).days

            results.append({
                "number":       pr.get("number", 0),
                "title":        pr.get("title", ""),
                "author":       pr.get("user", {}).get("login", "unknown"),
                "days_open":    days_open,
                "review_count": len(pr.get("requested_reviewers", [])),
            })

        return results

    except Exception as exc:
        status = "error"
        print(f"[github_tools] get_open_prs failed: {exc}", file=sys.stderr)
        return []

    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        _audit.log(
            workflow="github_tools",
            tool="github_pull_requests",
            tool_input=tool_input,
            status=status,
            duration_ms=duration_ms,
        )


def get_priority_issues(
    mcp: "MCPClient",
    repo: str,
    labels: list[str] | None = None,
) -> list[dict]:
    """
    Fetch open issues matching any of the given labels.

    Args:
        mcp:    The MCPClient context
        repo:   GitHub repo in 'owner/repo' format
        labels: List of label names to filter by (default: ['P0', 'P1'])

    Returns:
        List of dicts with: number, title, priority, assignee, days_open
        Sorted by priority (P0 first), then by days_open descending.
        Returns [] on any error.
    """
    if labels is None:
        labels = ["P0", "P1"]

    tool_input = {"repo": repo, "state": "open", "labels": ",".join(labels)}
    start = time.perf_counter()
    status = "success"
    try:
        raw = mcp.call("github_issues", tool_input)

        if not isinstance(raw, list):
            raw = []

        results = []
        for issue in raw:
            issue_labels = [lbl.get("name", "") for lbl in issue.get("labels", [])]

            # Work out the highest priority label present
            priority = "unknown"
            if "P0" in issue_labels:
                priority = "P0"
            elif "P1" in issue_labels:
                priority = "P1"
            else:
                # Check caller-supplied labels in order
                for lbl in labels:
                    if lbl in issue_labels:
                        priority = lbl
                        break

            created_raw = issue.get("created_at", "")
            try:
                created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                days_open = (datetime.now(timezone.utc) - created_at).days
            except (ValueError, AttributeError):
                days_open = 0

            assignees = issue.get("assignees", [])
            assignee = assignees[0].get("login", "unassigned") if assignees else "unassigned"

            results.append({
                "number":    issue.get("number", 0),
                "title":     issue.get("title", ""),
                "priority":  priority,
                "assignee":  assignee,
                "days_open": days_open,
            })

        # P0 before P1; within same priority, oldest first
        priority_order = {"P0": 0, "P1": 1}
        results.sort(key=lambda x: (priority_order.get(x["priority"], 99), -x["days_open"]))
        return results

    except Exception as exc:
        status = "error"
        print(f"[github_tools] get_priority_issues failed: {exc}", file=sys.stderr)
        return []

    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        _audit.log(
            workflow="github_tools",
            tool="github_issues",
            tool_input=tool_input,
            status=status,
            duration_ms=duration_ms,
        )


def search_recent_commits(
    mcp: "MCPClient",
    repo: str,
    service: str,
    hours: int = 4,
) -> list[dict]:
    """
    Find commits touching files under services/{service}/ in the last N hours.

    Args:
        mcp:     The MCPClient context
        repo:    GitHub repo in 'owner/repo' format
        service: Service name (e.g. 'payments')
        hours:   How many hours back to search

    Returns:
        List of dicts with: sha_short, author, message, timestamp, files_changed
        Returns [] on any error.
    """
    tool_input = {"repo": repo, "path": f"services/{service}/"}
    start = time.perf_counter()
    status = "success"
    try:
        raw = mcp.call("github_commits", tool_input)

        if not isinstance(raw, list):
            raw = []

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        results = []

        for commit in raw:
            committed_raw = commit.get("commit", {}).get("author", {}).get("date", "")
            try:
                committed_at = datetime.fromisoformat(committed_raw.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                continue

            if committed_at < cutoff:
                continue  # Outside the time window

            sha = commit.get("sha", "")
            author = commit.get("author", {})
            login = author.get("login", "unknown") if isinstance(author, dict) else "unknown"
            message_full = commit.get("commit", {}).get("message", "")
            message_first_line = message_full.split("\n")[0]
            files = commit.get("files", [])

            results.append({
                "sha_short":     sha[:7],
                "author":        login,
                "message":       message_first_line,
                "timestamp":     committed_at.isoformat(),
                "files_changed": len(files),
            })

        return results

    except Exception as exc:
        status = "error"
        print(f"[github_tools] search_recent_commits failed: {exc}", file=sys.stderr)
        return []

    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        _audit.log(
            workflow="github_tools",
            tool="github_commits",
            tool_input=tool_input,
            status=status,
            duration_ms=duration_ms,
        )
