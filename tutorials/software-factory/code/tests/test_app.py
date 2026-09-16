import base64
import importlib
import json
import sys
import types
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


def client(monkeypatch, mode):
    monkeypatch.setenv('APP_MODE', mode)
    monkeypatch.setenv('GOOGLE_CLOUD_PROJECT', 'demo-project')
    import app
    importlib.reload(app)
    return app, TestClient(app.app)


def event(state='open', service='software-factory-api'):
    payload = {'incident': {'incident_id': 'test', 'state': state, 'started_at': 1700000000,
               'resource': {'labels': {'project_id': 'demo-project', 'service_name': service}}}}
    return {'message': {'data': base64.b64encode(json.dumps(payload).encode()).decode()}}


def test_healthy_and_broken_checkout(monkeypatch):
    _, http = client(monkeypatch, 'api')
    assert http.get('/api/products').status_code == 200
    response = http.post('/api/checkout', json={'quantity': 2})
    assert response.json()['total_gbp'] == 98
    assert http.post('/api/checkout', json={'quantity': 0}).status_code == 422
    assert http.post('/api/checkout', json={'product_id': 'missing'}).status_code == 404
    monkeypatch.setenv('DEMO_FAILURE', 'true')
    assert http.post('/api/checkout', json={}).status_code == 500
    assert http.get('/healthz').status_code == 200
    assert http.post('/events', json={}).status_code == 404


def test_worker_rejects_bad_or_unrelated_events(monkeypatch):
    app, http = client(monkeypatch, 'worker')
    db = Mock()
    monkeypatch.setattr(app, 'store', lambda: db)
    assert http.post('/events', json={}).status_code == 400
    assert http.post('/events', json=event(service='other')).json() == {'ignored': True}
    db.begin.assert_not_called()


def test_worker_does_not_ack_while_other_worker_runs(monkeypatch):
    app, http = client(monkeypatch, 'worker')
    db = Mock()
    db.begin.return_value = ({'status': 'investigating'}, False)
    monkeypatch.setattr(app, 'store', lambda: db)
    assert http.post('/events', json=event()).status_code == 503


def test_closed_event_does_not_call_model(monkeypatch):
    app, http = client(monkeypatch, 'worker')
    db = Mock()
    db.begin.return_value = ({'status': 'recovered'}, False)
    monkeypatch.setattr(app, 'store', lambda: db)
    assert http.post('/events', json=event('closed')).json()['status'] == 'recovered'
    db.finish.assert_not_called()


def test_worker_persists_report_before_ack(monkeypatch):
    app, http = client(monkeypatch, 'worker')
    db = Mock()
    db.begin.return_value = ({'status': 'investigating'}, True)
    monkeypatch.setattr(app, 'store', lambda: db)
    async def investigate(incident, store):
        return {'likely_cause': 'Regression'}
    monkeypatch.setitem(sys.modules, 'agent', types.SimpleNamespace(investigate=investigate))
    assert http.post('/events', json=event()).status_code == 200
    db.finish.assert_called_once_with('test', report={'likely_cause': 'Regression'})


def test_worker_model_failure_remains_visible_and_retries(monkeypatch):
    app, http = client(monkeypatch, 'worker')
    db = Mock()
    db.begin.return_value = ({'status': 'investigating'}, True)
    monkeypatch.setattr(app, 'store', lambda: db)
    async def investigate(incident, store):
        raise RuntimeError('private SDK details')
    monkeypatch.setitem(sys.modules, 'agent', types.SimpleNamespace(investigate=investigate))
    result = http.post('/events', json=event())
    assert result.status_code == 503
    assert 'private SDK details' not in result.text
    assert 'private SDK details' not in db.finish.call_args.kwargs['error']


def test_dashboard_cannot_receive_events(monkeypatch):
    app, http = client(monkeypatch, 'dashboard')
    db = Mock()
    db.list.return_value = []
    monkeypatch.setattr(app, 'store', lambda: db)
    assert http.get('/api/incidents').json()['incidents'] == []
    assert http.post('/events', json=event()).status_code == 404
    assert http.get('/').status_code == 200
