# Workflow Map — Development Pipeline

## Current Workflow (Annotated)

```mermaid
flowchart TD
    A[📋 Pick up ticket\nJira board\n~10 min\nPain: context switching] --> B

    B[🔍 Understand the task\nRead ticket + code\n~20 min\nPain: unfamiliar areas take longer] --> C

    C[🌿 Create branch\ngit checkout -b\n~2 min\nLow pain] --> D

    D[💻 Implement changes\nVS Code + docs + Stack Overflow\n~90 min\nPain: looking up conventions, forgetting standards] --> E

    E[✅ Write tests\nJest\n~30 min\nPain: figuring out what to test, coverage gaps] --> F

    F[🔬 Self-review\nManual diff reading\n~15 min\nPain: easy to miss things, inconsistent] --> G

    G[📝 Write commit message\ngit commit -m\n~5 min\nPain: forgetting format, vague messages] --> H

    H[🚀 Push + open PR\ngit push + GitHub UI\n~10 min\nPain: filling out PR template manually] --> I

    I[👀 Wait for review\nSlack ping\n~60-120 min\nPain: back-and-forth, context loss] --> J

    J[🔀 Merge to main\nGitHub UI\n~5 min\nLow pain] --> K

    K[🚢 Deploy\nCI/CD auto or manual\n~10-30 min\nPain: sometimes fails silently]

    style A fill:#fff3cd
    style D fill:#f8d7da
    style E fill:#f8d7da
    style F fill:#f8d7da
    style I fill:#f8d7da
```

## Step Breakdown

| Step | Time (min) | Tools | Main Pain Points |
|------|-----------|-------|-----------------|
| Ticket pickup | 10 | Jira, Slack | Context switching costs focus |
| Understanding | 20 | Code editor, Jira | Unknown areas need exploration |
| Branch creation | 2 | Git | Minimal — just typing |
| Implementation | 90 | VS Code, docs, SO | Remembering conventions, looking up patterns |
| Writing tests | 30 | Jest, docs | Figuring out what to test, hitting coverage targets |
| Self-review | 15 | Git diff, manual | Inconsistent — easy to miss things |
| Commit message | 5 | Git | Vague messages, forgetting format |
| Push + PR | 10 | Git, GitHub | Manual PR description writing |
| Code review wait | 60–120 | GitHub, Slack | Blocking time, context loss when it comes back |
| Merge + deploy | 15 | GitHub, CI | Occasional flaky deploys |

**Total active work per feature: ~182 min (3+ hours)**
**Total wall clock time (inc. review wait): ~300 min (5 hours)**
