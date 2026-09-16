from google.cloud.logging_v2.types import LogEntry
from agent import log_payload, evidence_window


def test_structured_error_is_evidence_not_object_address():
    entry = LogEntry(json_payload={'message': 'Price lookup returned None',
                                   'details': {'error_type': 'PriceLookupError'}})
    result = log_payload(entry)
    assert 'Price lookup returned None' in result
    assert 'PriceLookupError' in result
    assert 'MapComposite object' not in result


def test_request_log_preserves_status():
    entry = LogEntry(http_request={'status': 500})
    assert '500' in log_payload(entry)


def test_text_logs_and_size_bound():
    assert 'failure' in log_payload(LogEntry(text_payload='failure'))
    assert len(log_payload(LogEntry(text_payload='x' * 5000))) <= 1200


def test_retry_window_includes_recent_failure_after_ten_minutes():
    start, end = evidence_window(10000, current_time=13000)
    assert end == 13000
    assert start == 11200
    assert end - start == 1800


def test_first_attempt_includes_preincident_context():
    assert evidence_window(10000, current_time=10030) == (9100, 10030)
