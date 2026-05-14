## 1. Module Boundary

`payments/processor.py` is responsible for orchestrating the full payment lifecycle: accepting a charge request, calling the Stripe API, retrying on failure, and persisting a transaction record. It should not own database schema logic, directly import HTTP transport, or handle authentication/authorisation of the caller. Right now it crosses those boundaries by building raw SQL strings and holding a hardcoded API key.

---

## 2. API Surface

**process_payment(amount, currency, card_token, user_id)**
- Input: payment amount (untyped numeric), ISO currency string, Stripe card token, internal user identifier
- Returns: dict with keys `success` (bool), `charge_id` (str or None), `error` (str or None)
- Clear and self-documenting? Mostly yes — the docstring explains the fields, but `amount` lacks a type hint, so it is unclear whether it should be an integer (cents) or a float (dollars). That ambiguity is risky in a payments context.

**record_transaction(user_id, amount, charge_id)**
- Input: user id, amount, charge id string
- Returns: nothing (implicit None)
- Clear and self-documenting? No — the function is public but it is really an internal step of process_payment. It should either be prefixed with an underscore or documented that callers should not call it directly.

**refund_payment(charge_id, amount=None)**
- Input: Stripe charge id, optional partial refund amount
- Returns: whatever _call_stripe_api returns (dict)
- Clear and self-documenting? Partially — the optional `amount` for partial refunds is noted in the docstring, but the return type is unspecified. The docstring also omits that there is no authorisation check on who can call this.

**get_payment_history(user_id)**
- Input: user id string
- Returns: list of raw database rows
- Clear and self-documenting? No — the return type is opaque. The docstring acknowledges over-fetching PII but does not say what fields come back. Callers cannot tell what shape the data is without reading the internals.

---

## 3. Data Flow

1. Caller invokes `process_payment(amount, currency, card_token, user_id)`.
2. A `payload` dict is assembled with the four input values and passed to `_call_stripe_api()`.
3. `_call_stripe_api()` sends the payload to Stripe (stubbed) and returns a dict containing a charge `id`.
4. On success, `record_transaction(user_id, amount, charge["id"])` is called to persist the charge.
5. Inside `record_transaction`, a raw SQL INSERT string is built and passed to `_execute_query()`.
6. `_execute_query()` runs the query against the database (stubbed).
7. `process_payment` returns `{"success": True, "charge_id": charge["id"], "error": None}`.
8. If any exception occurs during steps 2–6, the attempt is retried up to `MAX_RETRIES` times with exponential backoff. After all retries are exhausted, `{"success": False, "charge_id": None, "error": "Max retries exceeded"}` is returned.

---

## 4. Dependencies

| Dependency | Type | Notes |
|---|---|---| 
| `time` | Standard library | Used for `sleep()` in retry backoff and for simulating a charge ID |
| `logging` | Standard library | Module-level logger — appropriate use |
| `typing.Optional` | Standard library | Imported but not used in any function signature — dead import |
| `STRIPE_API_KEY` (module constant) | Internal hardcoded value | Should be injected via environment variable; this is currently a third-party credential baked into source code |
| `_call_stripe_api()` | Internal stub | Stands in for a real Stripe HTTP client; in production this would be a third-party dependency (`stripe` library or `requests`) and should be injected or abstracted behind an interface so it can be mocked in tests |
| `_execute_query()` | Internal stub | Stands in for a real DB driver or ORM; same concern — should be injectable |
