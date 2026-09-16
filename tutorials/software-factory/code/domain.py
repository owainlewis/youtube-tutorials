"""Incident lifecycle, independent of Google Cloud for offline verification."""
from datetime import datetime, timezone
import hashlib


def now():
    return datetime.now(timezone.utc).isoformat()


def incident_key(incident_id):
    return hashlib.sha256(incident_id.encode()).hexdigest()


def iso_timestamp(value):
    return datetime.fromtimestamp(float(value), timezone.utc).isoformat()


def begin_incident(previous, incident, clock=None):
    """Closed is terminal. Retry failed or expired work, never duplicate completed work."""
    clock = clock or now()
    record = dict(previous or {})
    if incident['state'] == 'closed':
        record.update(id=incident['incident_id'], state='closed', status='recovered',
                      updated_at=clock, ended_at=iso_timestamp(incident['ended_at'])
                      if incident.get('ended_at') else clock)
        record.setdefault('started_at', iso_timestamp(incident['started_at']))
        record.setdefault('title', incident.get('policy_name', 'API incident'))
        record.setdefault('report', None)
        record.setdefault('steps', [])
        return record, False
    if record.get('state') == 'closed' or record.get('status') == 'triaged':
        return record, False
    if record.get('status') == 'investigating':
        age = (datetime.fromisoformat(clock) - datetime.fromisoformat(record['updated_at'])).total_seconds()
        if age < 240:
            return record, False
    record.update(id=incident['incident_id'], title=incident.get('policy_name', 'API incident'),
                  summary=incident.get('summary', ''), state='open', status='investigating',
                  started_at=iso_timestamp(incident['started_at']), updated_at=clock,
                  ended_at=None, report=None, steps=[], error=None)
    # Reconstruct this link rather than accepting a URL supplied in the message.
    return record, True


def finish_incident(record, report=None, error=None):
    if record.get('state') == 'closed':
        # Keep a late investigation, but never reopen an incident closed by Monitoring.
        if report:
            record['report'] = report
        return record
    record.update(status='failed' if error else 'triaged', report=report,
                  error=error, updated_at=now())
    return record
