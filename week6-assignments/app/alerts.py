"""
app/alerts.py
Alert management — acknowledge, escalate, and retrieve active alerts.

Intentional issues:
 - acknowledge_alert does not verify the alert belongs to the caller's ward
 - No pagination on get_active_alerts
 - escalate_alert sends internal error details to external SMS provider
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

SMS_API_KEY  = "sms_live_key_abc123xyz"   # hardcoded
SMS_ENDPOINT = "https://api.smsprovider.com/send"


def get_active_alerts(ward_id: Optional[str] = None) -> list:
    """
    Return all active (unacknowledged) alerts.
    No pagination — could return thousands of rows.
    """
    if ward_id:
        query = (
            f"SELECT a.*, p.full_name, p.room_number "
            f"FROM alerts a JOIN patients p ON a.patient_id = p.id "
            f"WHERE a.acknowledged = 0 AND p.ward_id = '{ward_id}'"
        )
    else:
        query = (
            "SELECT a.*, p.full_name, p.room_number "
            "FROM alerts a JOIN patients p ON a.patient_id = p.id "
            "WHERE a.acknowledged = 0"
        )
    return _execute_read(query)


def acknowledge_alert(alert_id: str, staff_id: str) -> dict:
    """
    Mark an alert as acknowledged.
    Does NOT verify the alert belongs to the same ward as the staff member.
    Any nurse can acknowledge any alert in any ward.
    """
    query = (
        f"UPDATE alerts SET acknowledged=1, ack_by='{staff_id}', ack_ts=NOW() "
        f"WHERE id = '{alert_id}'"
    )
    _execute_write(query)
    return {"success": True, "alert_id": alert_id}


def escalate_alert(alert_id: str, reason: str) -> dict:
    """
    Escalate an alert via SMS to the on-call doctor.
    Sends full internal error/debug info in the SMS body — data leakage.
    """
    alert = _get_alert(alert_id)
    if not alert:
        return {"success": False, "error": "Not found"}

    # Full internal dict sent externally — leaks DB structure and PII
    sms_body = f"ESCALATION: {alert} | reason={reason} | db={DB_HOST}"
    _send_sms(on_call_number="+447700900000", body=sms_body)
    return {"success": True}


# ── Stubs ─────────────────────────────────────────────────────────────────────

DB_HOST = "db.healthtrack.internal"

def _execute_write(query):
    logger.debug(f"SQL WRITE: {query}")

def _execute_read(query) -> list:
    logger.debug(f"SQL READ: {query}")
    return []

def _get_alert(alert_id: str) -> Optional[dict]:
    return {"id": alert_id, "patient_id": "p001", "vital_type": "heart_rate", "value": 140}

def _send_sms(on_call_number: str, body: str):
    logger.info(f"SMS to {on_call_number}: {body}")
