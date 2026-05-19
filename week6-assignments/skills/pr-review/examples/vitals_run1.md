# PR Review Example — app/vitals.py retry logic PR
# Skill: pr-review v1.2.0
# Run date: 2026-04-18
# Tested by: platform-team

## MUST_FIX

1. app/vitals.py:52 — `record_vitals()` has no guard against `value=None`.
   `_execute_write()` will receive None and crash silently with no error logged.
   Fix: add `if value is None: raise ValueError("value cannot be None")` at line 35.

2. app/vitals.py:61 — Retry loop catches bare `Exception` — this masks
   programming errors (TypeError from bad input) as DB failures, causing
   misleading retries that will always fail.
   Fix: catch `DBTimeoutError` specifically. Re-raise all other exceptions immediately.

## SHOULD_FIX

3. app/vitals.py:44 — Variable name `r` is not descriptive in the retry loop.
   A new team member won't know what `r` represents.
   Rename to `attempt` for clarity.

4. app/vitals.py:58 — `time.sleep(2 ** attempt)` with no cap means a 3rd retry
   waits 4 seconds — acceptable, but document the maximum wait time in a comment.

## NICE_TO_HAVE

5. app/vitals.py:38 — Inline comment on the backoff formula would help new devs.
   Add: `# exponential backoff: waits 1s, 2s, 4s between retries`

## SUMMARY

Two correctness issues must be fixed before merge: a None guard is missing on `value`
and the exception handler is too broad, causing silent failure masking.
All other items are optional improvements.
