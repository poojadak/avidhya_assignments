# Automation Leverage Analysis

## Scoring Framework

Each workflow step is scored across four dimensions:

- **Frequency**: How often does this happen? (daily = 3, weekly = 2, monthly = 1)
- **Time per occurrence**: Minutes spent manually
- **AI capability**: How well can AI handle this? (very high = 4, high = 3, medium = 2, low = 1)
- **ROI score**: Overall 1–10 estimate of automation value

---

## Step Scores

| Step | Frequency | Time (min) | AI Capability | ROI Score |
|------|-----------|-----------|---------------|-----------|
| Ticket understanding | Daily | 20 | Medium | 5 |
| Branch creation | Daily | 2 | Low | 1 |
| Implementation | Daily | 90 | Medium | 4 |
| **Writing tests** | Daily | 30 | **Very High** | **9** |
| **Self-review** | Daily | 15 | **Very High** | **9** |
| **Commit message** | Daily | 5 | **Very High** | **8** |
| **Push + PR creation** | Daily | 10 | **High** | **8** |
| Review response | Daily | 20 | Medium | 4 |
| Merge | Weekly | 5 | Low | 2 |
| Deploy monitoring | Weekly | 15 | Medium | 5 |

---

## Top 3 Automation Targets

### 🥇 Target 1: Code Review + Test Generation (combined as /review + /test-gen)

**Why this tops the list:**

Manual self-review is unreliable. Developers miss things when reviewing their own code — it's just human nature. You're too close to the work. On top of that, writing tests is the step most developers drag their feet on. It's repetitive, it takes 30 minutes, and it often gets deprioritized when there's deadline pressure.

AI is genuinely very good at both of these. It can read a diff and check it against a rulebook (our CLAUDE.md) consistently, every single time. It can also look at a function and generate sensible test cases faster than a human who has to think from scratch.

**Estimated daily savings: 30–40 minutes per developer**

---

### 🥈 Target 2: Commit Messages + PR Creation (/commit and /ship)

**Why this is #2:**

Commit messages sound trivial but they're a real source of friction. Developers forget the format, write vague messages like "fix bug" or "update code", and then the PR description is equally thin. This creates problems downstream — reviewers don't know what to look for, and git history becomes useless for debugging.

The full /ship pipeline turns a 15-minute multi-step manual process into a single command. The time savings are modest individually, but the consistency improvement is significant — every PR goes out with a proper commit message and a useful description.

**Estimated daily savings: 10–15 minutes per developer**

---

### 🥉 Target 3: New Developer Onboarding (/onboard)

**Why this makes the top 3:**

This one has a lower frequency (you don't onboard someone every day) but the time cost when it happens is huge. Getting a new person up to speed on a codebase typically takes multiple hours of senior developer time — code walkthroughs, architecture explanations, answering the same questions repeatedly.

A well-generated onboarding guide from /onboard doesn't replace human mentorship, but it reduces the "dumb question" load significantly. The new person can self-serve for a lot of the basics and ask smarter questions sooner.

**Estimated savings per onboarding: 2–4 hours of senior dev time**
