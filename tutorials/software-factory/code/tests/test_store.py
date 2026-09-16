from unittest.mock import Mock
from store import IncidentStore


def test_old_open_incident_survives_recent_history_limit():
    db = IncidentStore.__new__(IncidentStore)
    db.collection = Mock()
    old_open = {'id': 'older-but-active', 'state': 'open', 'started_at': '2026-01-01'}
    recent_closed = [{'id': str(i), 'state': 'closed', 'started_at': '2026-09-16'} for i in range(30)]
    db.collection.where.return_value.stream.return_value = [Mock(to_dict=lambda: old_open)]
    db.collection.order_by.return_value.limit.return_value.stream.return_value = [
        Mock(to_dict=lambda item=item: item) for item in recent_closed]
    result = db.list()
    assert len(result) == 31
    assert old_open in result


def test_active_record_is_not_duplicated_when_also_recent():
    db = IncidentStore.__new__(IncidentStore)
    db.collection = Mock()
    record = {'id': 'open', 'state': 'open', 'started_at': '2026-09-16'}
    db.collection.where.return_value.stream.return_value = [Mock(to_dict=lambda: record)]
    db.collection.order_by.return_value.limit.return_value.stream.return_value = [Mock(to_dict=lambda: record)]
    assert db.list() == [record]
