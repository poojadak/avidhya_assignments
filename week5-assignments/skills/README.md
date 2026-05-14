# Skills Library — OrderFlow

This folder contains reusable agent prompt Skills built during the Week 5 mini project.
Each Skill is a self-contained folder with a SKILL.md file that describes the agent role, inputs, prompt, expected output, and test results.

## Skill Index

| Skill | Folder | Category | Version | Status | What it does |
|---|---|---|---|---|---|
| Code Architecture Reviewer | `architect-review/` | code-quality | 1.0.0 | draft | Analyses a Python module's boundary, API surface, data flow, and dependencies. Run this first in a pipeline. |
| Security Vulnerability Auditor | `security-audit/` | security | 1.0.0 | draft | Finds OWASP Top 10 vulnerabilities in a Python module and returns a JSON array of findings ordered by severity. Run after the Architecture Reviewer. |

## Recommended Pipeline Order

1. **architect-review** — establishes structure and produces design.md
2. **security-audit** — uses design.md + source to find vulnerabilities

## Adding a New Skill

1. Copy `SKILL_TEMPLATE.md` into a new folder: `skills/[your-skill-name]/SKILL.md`
2. Fill in all five sections: Header, Purpose, Input Spec, Prompt Body, Output Spec
3. Run three test cases (typical, edge, minimal) and fill in the Tests table
4. Add an entry to this README index
5. Set Status to `stable` once you have run it successfully on at least two different inputs
