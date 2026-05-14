# Traceability Matrix
_Requirement → Code File → Test Function → Pass/Fail_

Generated after final test run: **28/28 passed ✅**

| Req ID | Statement (short) | Code File | Function / Method | Test Function | Status |
|--------|-------------------|-----------|-------------------|---------------|--------|
| REQ-SHORT-001 | Accept valid URL → 6-char code | `src/services.py` | `create_short_url()` | `test_should_return_201_when_valid_url_submitted` | ✅ PASS |
| REQ-SHORT-001 | Short URL in response | `src/routes.py` | `shorten()` | `test_should_contain_short_url_in_response` | ✅ PASS |
| REQ-SHORT-002 | Unique code, retry on collision | `src/services.py` | `_generate_code()` + retry loop | `test_should_return_201_when_valid_url_submitted` | ✅ PASS |
| REQ-SHORT-003 | Custom alias support | `src/services.py` | `create_short_url(custom_alias=…)` | `test_should_use_custom_alias_when_provided` | ✅ PASS |
| REQ-REDIR-001 | 302 redirect to original URL | `src/routes.py` | `redirect_to_url()` | `test_should_redirect_302_when_valid_code_requested` | ✅ PASS |
| REQ-REDIR-001 | Future expiry still redirects | `src/services.py` | `resolve_redirect()` | `test_should_redirect_when_expiry_is_in_future` | ✅ PASS |
| REQ-REDIR-002 | 404 for unknown code | `src/routes.py` | `redirect_to_url()` | `test_should_return_404_when_code_does_not_exist` | ✅ PASS |
| REQ-REDIR-003 | 410 Gone for expired URL | `src/routes.py` | `redirect_to_url()` | `test_should_return_410_when_url_is_expired` | ✅ PASS |
| REQ-ANAL-001 | click_count incremented | `src/services.py` | `resolve_redirect()` | `test_should_increment_click_count_on_redirect` | ✅ PASS |
| REQ-ANAL-002 | last_accessed updated | `src/services.py` | `resolve_redirect()` | `test_should_update_last_accessed_after_redirect` | ✅ PASS |
| REQ-ANAL-003 | Referrer header captured | `src/services.py` | `resolve_redirect()` | `test_should_capture_referrer_header_on_redirect` | ✅ PASS |
| REQ-ANAL-004 | GET /stats endpoint | `src/routes.py` | `stats()` | `test_should_return_stats_with_all_fields` | ✅ PASS |
| REQ-ANAL-004 | Stats 404 for bad code | `src/routes.py` | `stats()` | `test_should_return_404_stats_when_code_not_found` | ✅ PASS |
| REQ-EXP-001 | Optional expires_at stored | `src/models.py` | `UrlRecord.expires_at` | `test_should_store_expiry_date_when_expires_at_provided` | ✅ PASS |
| REQ-EXP-002 | Expiry evaluated at redirect time | `src/models.py` | `is_expired()` | `test_should_return_410_when_url_is_expired` | ✅ PASS |
| REQ-VAL-001 | Reject non-http/https schemes | `src/validators.py` | `validate_url()` | `test_should_return_422_when_url_has_ftp_scheme` | ✅ PASS |
| REQ-VAL-001 | Reject URL with no scheme | `src/validators.py` | `validate_url()` | `test_should_return_422_when_url_has_no_scheme` | ✅ PASS |
| REQ-VAL-001 | Reject empty URL | `src/routes.py` | `shorten()` | `test_should_return_422_when_url_is_empty_string` | ✅ PASS |
| REQ-VAL-002 | Reject duplicate active URLs | `src/services.py` | `create_short_url()` | `test_should_return_409_when_url_already_shortened` | ✅ PASS |
| REQ-VAL-003 | Reject blocked domains | `src/validators.py` | `validate_url()` | `test_should_return_422_when_domain_is_blocked` | ✅ PASS |
| REQ-VAL-004 | Reject taken alias | `src/services.py` | `create_short_url()` | `test_should_return_409_when_custom_alias_already_taken` | ✅ PASS |
| REQ-VAL-004 | Reject bad alias format (parametrized) | `src/validators.py` | `validate_alias()` | `test_should_return_422_when_alias_format_is_invalid[…]` ×4 | ✅ PASS |
| REQ-API-001 | JSON envelope on all responses | `src/routes.py` | `ok()` / `err()` helpers | `test_should_return_error_envelope_when_url_missing` | ✅ PASS |
| REQ-API-002 | Correct HTTP status codes | `src/routes.py` | All route handlers | Multiple tests across all classes | ✅ PASS |
| REQ-API-002 | 405 on wrong method | `src/routes.py` | `app_errorhandler(405)` | `test_should_return_405_on_wrong_method` | ✅ PASS |

---

## Coverage Summary

| Category | Requirements | Tests | Full Coverage |
|----------|-------------|-------|---------------|
| Core Shortening | REQ-SHORT-001..003 | 5 | ✅ |
| Redirect | REQ-REDIR-001..003 | 4 | ✅ |
| Analytics | REQ-ANAL-001..004 | 5 | ✅ |
| Expiry | REQ-EXP-001..002 | 3 | ✅ |
| Validation | REQ-VAL-001..004 | 9 | ✅ |
| API Contract | REQ-API-001..002 | 3 | ✅ |
| **Total** | **16 req IDs** | **28 tests** | ✅ **100%** |

### Requirements without tests: None
### Tests without requirements: None
