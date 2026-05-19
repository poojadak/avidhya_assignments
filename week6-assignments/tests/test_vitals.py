"""
tests/test_vitals.py
Existing tests — sparse. Students will use the Test Agent to find gaps.
"""
import pytest
from unittest.mock import patch
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.vitals import record_vitals, get_patient_vitals, calculate_alert_threshold


class TestRecordVitals:

    @patch("app.vitals._execute_write", return_value="reading_001")
    @patch("app.vitals._execute_read", return_value=[])
    def test_happy_path(self, mock_read, mock_write):
        result = record_vitals("p001", "heart_rate", 72.0, "nurse_01")
        assert result["success"] is True
        assert result["reading_id"] == "reading_001"
        assert result["alert"] is False

    @patch("app.vitals._execute_write", return_value="reading_002")
    @patch("app.vitals._execute_read", return_value=[])
    def test_high_heart_rate_triggers_alert(self, mock_read, mock_write):
        result = record_vitals("p001", "heart_rate", 160.0, "nurse_01")
        assert result["alert"] is True

    # MISSING: test negative value accepted without error
    # MISSING: test unknown vital_type accepted without error
    # MISSING: test patient_id that doesn't exist — no integrity check
    # MISSING: test value=None (should raise, currently crashes)
    # MISSING: test SQL injection in patient_id


class TestCalculateAlertThreshold:

    def test_adult_heart_rate(self):
        t = calculate_alert_threshold("heart_rate", 45)
        assert t["low"] == 60
        assert t["high"] == 100

    # MISSING: test age > 65 adjustments
    # MISSING: test age < 18 adjustments
    # MISSING: test has_condition=True
    # MISSING: test unknown vital_type raises KeyError (unhandled edge case)
    # MISSING: test age=0 (newborn)
    # MISSING: test age=None (should raise TypeError, currently crashes)
