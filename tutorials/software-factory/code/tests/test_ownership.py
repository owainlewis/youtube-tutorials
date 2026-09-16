import json
from unittest.mock import Mock

import pytest

import cleanup
import deploy


@pytest.fixture
def state(tmp_path, monkeypatch):
    monkeypatch.setattr(deploy, 'PROJECT', 'demo-project', raising=False)
    monkeypatch.setattr(deploy, 'REGION', 'europe-west2', raising=False)
    monkeypatch.setattr(deploy, 'STATE_PATH', tmp_path / '.software-factory-state.json')
    return deploy.load_state()


def empty_inventory():
    return {kind: [] for kind in ('accounts', 'databases', 'repositories', 'services',
                                 'topics', 'subscriptions', 'notificationChannels', 'alertPolicies')}


@pytest.mark.parametrize('kind,resource', [
    ('accounts', 'software-factory-api@demo-project.iam.gserviceaccount.com'),
    ('databases', 'projects/demo-project/databases/software-factory'),
    ('repositories', 'projects/demo-project/locations/europe-west2/repositories/software-factory'),
    ('services', 'software-factory-api'),
    ('topics', 'projects/demo-project/topics/software-factory-alerts'),
    ('subscriptions', 'projects/demo-project/subscriptions/software-factory-triage'),
    ('notificationChannels', {'name': 'projects/demo-project/notificationChannels/123', 'displayName': 'software-factory'}),
    ('alertPolicies', {'name': 'projects/demo-project/alertPolicies/123', 'displayName': 'software-factory / Checkout errors'}),
])
def test_collision_requires_ownership(state, kind, resource):
    existing = empty_inventory()
    existing[kind] = [resource]
    with pytest.raises(RuntimeError, match='Unowned'):
        deploy.preflight(state, existing)
    state['resources'][kind] = [resource['name'] if isinstance(resource, dict) else resource]
    deploy.preflight(state, existing)


def test_cleanup_requires_manifest_before_cloud_calls(state, monkeypatch):
    cloud = Mock()
    monkeypatch.setattr(deploy, 'inventory', cloud)
    with pytest.raises(RuntimeError, match='missing'):
        cleanup.cleanup()
    cloud.assert_not_called()


@pytest.mark.parametrize('field,value', [('project', 'other-project'), ('region', 'us-central1')])
def test_manifest_scope_is_checked(state, field, value):
    state[field] = value
    deploy.save_state(state)
    with pytest.raises(RuntimeError, match='does not match'):
        deploy.load_state()


def test_cleanup_does_not_delete_matching_unowned_resources(state, monkeypatch):
    owned = 'projects/demo-project/alertPolicies/123'
    state['resources'] = {'alertPolicies': [owned], 'services': ['software-factory-api']}
    deploy.save_state(state)
    existing = empty_inventory()
    existing['alertPolicies'] = [
        {'name': owned, 'displayName': 'renamed'},
        {'name': 'projects/demo-project/alertPolicies/456', 'displayName': 'software-factory / Checkout errors'},
    ]
    existing['services'] = ['software-factory-api', 'software-factory-dashboard']
    monkeypatch.setattr(deploy, 'inventory', lambda: existing)
    cli, api = Mock(), Mock()
    monkeypatch.setattr(deploy, 'cli', cli)
    monkeypatch.setattr(deploy, 'api', api)
    cleanup.cleanup()
    api.assert_called_once_with('DELETE', 'alertPolicies/123')
    cli.assert_called_once_with('run', 'services', 'delete', 'software-factory-api', '--region', 'europe-west2')
    assert json.loads(deploy.STATE_PATH.read_text())['resources'] == {'alertPolicies': [], 'services': []}


def test_creation_is_saved_immediately(state, monkeypatch):
    monkeypatch.setattr(deploy, 'STATE', state, raising=False)
    deploy.remember('services', 'software-factory-api')
    assert deploy.load_state()['resources']['services'] == ['software-factory-api']


def test_page_two_collision_is_not_adopted(state, monkeypatch):
    api = Mock(side_effect=[{'alertPolicies': [], 'nextPageToken': 'page two'},
        {'alertPolicies': [{'name': 'projects/demo-project/alertPolicies/later',
                            'displayName': 'software-factory / Checkout errors'}]}])
    monkeypatch.setattr(deploy, 'api', api)
    inventory = empty_inventory()
    inventory['alertPolicies'] = deploy.monitoring_list('alertPolicies')
    with pytest.raises(RuntimeError, match='Unowned'):
        deploy.preflight(state, inventory)
    assert api.call_args.args == ('GET', 'alertPolicies?pageToken=page+two')


def test_cleanup_finds_owned_resource_on_page_two(state, monkeypatch):
    owned = 'projects/demo-project/alertPolicies/later'
    state['resources'] = {'alertPolicies': [owned]}
    deploy.save_state(state)
    responses = [{'alertPolicies': [], 'nextPageToken': 'later'},
                 {'alertPolicies': [{'name': owned}]}, {}]
    api = Mock(side_effect=responses)
    monkeypatch.setattr(deploy, 'api', api)
    inventory = empty_inventory()
    inventory['alertPolicies'] = deploy.monitoring_list('alertPolicies')
    monkeypatch.setattr(deploy, 'inventory', lambda: inventory)
    cleanup.cleanup()
    assert api.call_args.args == ('DELETE', 'alertPolicies/later')
    assert deploy.load_state()['resources']['alertPolicies'] == []
