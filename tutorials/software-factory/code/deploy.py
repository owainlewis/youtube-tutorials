#!/usr/bin/env python3
"""Deploy the demo with gcloud. No Terraform state or embedded credentials."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import urllib.error
from urllib.parse import urlencode

PREFIX = 'software-factory'


def cli(*args, json_output=False):
    command = ['gcloud', *args, '--project', PROJECT, '--quiet']
    if json_output:
        command += ['--format=json']
    result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
    return json.loads(result.stdout) if json_output and result.stdout.strip() else result.stdout.strip()


def api(method, path, body=None):
    token = subprocess.check_output(['gcloud', 'auth', 'print-access-token'], text=True).strip()
    request = urllib.request.Request('https://monitoring.googleapis.com/v3/projects/' + PROJECT + '/' + path,
        data=json.dumps(body).encode() if body is not None else None, method=method,
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
        return json.loads(data) if data else {}


def monitoring_list(kind):
    """Read every page before making ownership or deletion decisions."""
    items, token, seen = [], None, set()
    while True:
        path = kind + ('?' + urlencode({'pageToken': token}) if token else '')
        page = api('GET', path)
        items.extend(page.get(kind, []))
        token = page.get('nextPageToken')
        if not token:
            return items
        if token in seen:
            raise RuntimeError('Monitoring returned a repeated pagination token')
        seen.add(token)


STATE_PATH = Path(__file__).with_name('.software-factory-state.json')


def load_state(required=False):
    if not STATE_PATH.exists():
        if required:
            raise RuntimeError('Ownership manifest missing; refusing cleanup.')
        return {'version': 1, 'project': PROJECT, 'region': REGION, 'resources': {}}
    state = json.loads(STATE_PATH.read_text())
    if (state.get('version'), state.get('project'), state.get('region')) != (1, PROJECT, REGION):
        raise RuntimeError('Ownership manifest does not match this project and region.')
    return state


def save_state(state):
    temporary = STATE_PATH.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.replace(STATE_PATH)


def remember(kind, resource):
    resources = STATE['resources'].setdefault(kind, [])
    if resource not in resources:
        resources.append(resource)
        save_state(STATE)


def inventory():
    return {
        'accounts': [a['email'] for a in cli('iam', 'service-accounts', 'list', json_output=True)],
        'databases': [d['name'] for d in cli('firestore', 'databases', 'list', json_output=True)],
        'repositories': [r['name'] for r in cli('artifacts', 'repositories', 'list', '--location', REGION, json_output=True)],
        'services': [s['metadata']['name'] for s in cli('run', 'services', 'list', '--region', REGION, json_output=True)],
        'topics': [t['name'] for t in cli('pubsub', 'topics', 'list', json_output=True)],
        'subscriptions': [s['name'] for s in cli('pubsub', 'subscriptions', 'list', json_output=True)],
        'notificationChannels': monitoring_list('notificationChannels'),
        'alertPolicies': monitoring_list('alertPolicies'),
    }


def preflight(state, existing):
    expected = {
        'accounts': [f'{PREFIX}-{suffix}@{PROJECT}.iam.gserviceaccount.com'
                     for suffix in ('api', 'triage', 'dashboard', 'push', 'build')],
        'databases': [f'projects/{PROJECT}/databases/{PREFIX}'],
        'repositories': [f'projects/{PROJECT}/locations/{REGION}/repositories/{PREFIX}'],
        'services': [PREFIX + '-' + suffix for suffix in ('api', 'triage', 'dashboard')],
        'topics': [f'projects/{PROJECT}/topics/{PREFIX}-alerts'],
        'subscriptions': [f'projects/{PROJECT}/subscriptions/{PREFIX}-triage'],
    }
    for kind, names in expected.items():
        for name in names:
            if name in existing[kind] and name not in state['resources'].get(kind, []):
                raise RuntimeError(f'Unowned {kind} collision: {name}. Refusing deployment.')
    for kind, display in [('notificationChannels', PREFIX), ('alertPolicies', PREFIX + ' / Checkout errors')]:
        for item in existing[kind]:
            if item.get('displayName') == display and item['name'] not in state['resources'].get(kind, []):
                raise RuntimeError(f"Unowned {kind} collision: {item['name']}. Refusing deployment.")


def ensure_account(name):
    email = f'{name}@{PROJECT}.iam.gserviceaccount.com'
    accounts = cli('iam', 'service-accounts', 'list', json_output=True)
    if not any(a['email'] == email for a in accounts):
        cli('iam', 'service-accounts', 'create', name, '--display-name', name)
        remember('accounts', email)
    return email


def role(email, name):
    cli('projects', 'add-iam-policy-binding', PROJECT, '--member', 'serviceAccount:' + email,
        '--role', name, '--condition=None')


def deploy():
    global STATE
    STATE = load_state()
    cli('services', 'enable', 'run.googleapis.com', 'cloudbuild.googleapis.com',
        'artifactregistry.googleapis.com', 'monitoring.googleapis.com', 'logging.googleapis.com',
        'pubsub.googleapis.com', 'firestore.googleapis.com', 'aiplatform.googleapis.com', 'iam.googleapis.com')
    preflight(STATE, inventory())
    save_state(STATE)
    number = str(cli('projects', 'describe', PROJECT, json_output=True)['projectNumber'])
    api_sa = ensure_account(PREFIX + '-api')
    worker_sa = ensure_account(PREFIX + '-triage')
    dashboard_sa = ensure_account(PREFIX + '-dashboard')
    push_sa = ensure_account(PREFIX + '-push')
    for permission in ('roles/logging.viewer', 'roles/monitoring.viewer', 'roles/run.viewer',
                       'roles/aiplatform.user', 'roles/datastore.user'):
        role(worker_sa, permission)
    role(dashboard_sa, 'roles/datastore.viewer')
    databases = cli('firestore', 'databases', 'list', json_output=True)
    if not any(d['name'].endswith('/' + PREFIX) for d in databases):
        cli('firestore', 'databases', 'create', '--database', PREFIX, '--location', REGION, '--type', 'firestore-native')
        remember('databases', f'projects/{PROJECT}/databases/{PREFIX}')
    repositories = cli('artifacts', 'repositories', 'list', '--location', REGION, json_output=True)
    if not any(r['name'].endswith('/' + PREFIX) for r in repositories):
        cli('artifacts', 'repositories', 'create', PREFIX, '--location', REGION, '--repository-format', 'docker')
        remember('repositories', f'projects/{PROJECT}/locations/{REGION}/repositories/{PREFIX}')
    image = f'{REGION}-docker.pkg.dev/{PROJECT}/{PREFIX}/demo:latest'
    build_sa = ensure_account(PREFIX + '-build')
    role(build_sa, 'roles/logging.logWriter')
    buckets = cli('storage', 'buckets', 'list', json_output=True)
    if not any(b.get('name') == PROJECT + '_cloudbuild' for b in buckets):
        cli('storage', 'buckets', 'create', f'gs://{PROJECT}_cloudbuild', '--location', REGION, '--uniform-bucket-level-access')
    cli('storage', 'buckets', 'add-iam-policy-binding', f'gs://{PROJECT}_cloudbuild',
        '--member', 'serviceAccount:' + build_sa, '--role', 'roles/storage.objectViewer')
    cli('artifacts', 'repositories', 'add-iam-policy-binding', PREFIX, '--location', REGION,
        '--member', 'serviceAccount:' + build_sa, '--role', 'roles/artifactregistry.writer')
    build = {'steps': [{'name': 'gcr.io/cloud-builders/docker', 'args': ['build', '-t', image, '.']}],
             'images': [image], 'options': {'logging': 'CLOUD_LOGGING_ONLY'}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as config:
        json.dump(build, config)
        config.flush()
        cli('builds', 'submit', str(Path(__file__).parent), '--config', config.name,
            '--service-account', f'projects/{PROJECT}/serviceAccounts/{build_sa}')
    urls = {}
    common_env = f'GOOGLE_CLOUD_PROJECT={PROJECT},FIRESTORE_DATABASE={PREFIX},TARGET_SERVICE={PREFIX}-api,CLOUD_RUN_REGION={REGION}'
    for mode, sa in [('api', api_sa), ('worker', worker_sa), ('dashboard', dashboard_sa)]:
        name = PREFIX + '-' + ('triage' if mode == 'worker' else mode)
        env = common_env + f',APP_MODE={mode}'
        if mode == 'worker':
            env += f',GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_LOCATION=global,GEMINI_MODEL={MODEL}'
        if mode == 'api':
            env += ',DEMO_FAILURE=false'
        cli('run', 'deploy', name, '--image', image, '--region', REGION, '--service-account', sa,
            '--set-env-vars', env, '--memory', '1Gi' if mode == 'worker' else '256Mi',
            '--cpu', '1', '--min-instances', '0', '--max-instances', '2',
            '--concurrency', '4' if mode == 'worker' else '40', '--timeout', '240',
            '--no-allow-unauthenticated')
        remember('services', name)
        urls[mode] = cli('run', 'services', 'describe', name, '--region', REGION, json_output=True)['status']['url']
    cli('run', 'services', 'add-iam-policy-binding', PREFIX + '-triage', '--region', REGION,
        '--member', 'serviceAccount:' + push_sa, '--role', 'roles/run.invoker')
    topics = cli('pubsub', 'topics', 'list', json_output=True)
    if not any(t['name'].endswith('/' + PREFIX + '-alerts') for t in topics):
        cli('pubsub', 'topics', 'create', PREFIX + '-alerts')
        remember('topics', f'projects/{PROJECT}/topics/{PREFIX}-alerts')
    topic = f'projects/{PROJECT}/topics/{PREFIX}-alerts'
    channels = monitoring_list('notificationChannels')
    channel = next((c for c in channels if c['name'] in STATE['resources'].get('notificationChannels', [])), None)
    if channel is None:
        channel = api('POST', 'notificationChannels', {'type': 'pubsub', 'displayName': PREFIX,
                                                      'labels': {'topic': topic}})
        remember('notificationChannels', channel['name'])
    cli('pubsub', 'topics', 'add-iam-policy-binding', PREFIX + '-alerts',
        '--member', f'serviceAccount:service-{number}@gcp-sa-monitoring-notification.iam.gserviceaccount.com',
        '--role', 'roles/pubsub.publisher')
    # Only the Pub/Sub service agent can mint the push identity used by this subscription.
    cli('iam', 'service-accounts', 'add-iam-policy-binding', push_sa,
        '--member', f'serviceAccount:service-{number}@gcp-sa-pubsub.iam.gserviceaccount.com',
        '--role', 'roles/iam.serviceAccountTokenCreator')
    subscriptions = cli('pubsub', 'subscriptions', 'list', json_output=True)
    exists = any(s['name'].endswith('/' + PREFIX + '-triage') for s in subscriptions)
    sub_args = ['pubsub', 'subscriptions', 'update' if exists else 'create', PREFIX + '-triage']
    if not exists:
        sub_args += ['--topic', PREFIX + '-alerts']
    cli(*sub_args, '--push-endpoint', urls['worker'] + '/events', '--push-auth-service-account', push_sa,
        '--push-auth-token-audience', urls['worker'], '--ack-deadline', '240',
        '--min-retry-delay', '30s', '--max-retry-delay', '300s', '--message-retention-duration', '1h')
    remember('subscriptions', f'projects/{PROJECT}/subscriptions/{PREFIX}-triage')
    metric_filter = (f'resource.type="cloud_run_revision" AND resource.labels.service_name="{PREFIX}-api" '
                     'AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"')
    policy = {'displayName': PREFIX + ' / Checkout errors', 'combiner': 'OR', 'enabled': True,
        'notificationChannels': [channel['name']],
        'documentation': {'mimeType': 'text/markdown', 'content': 'Synthetic checkout demo. Triage only. A human restores the previous healthy Cloud Run revision.'},
        'alertStrategy': {'autoClose': '1800s', 'notificationPrompts': ['OPENED', 'CLOSED']},
        'conditions': [{'displayName': 'Checkout has server errors', 'conditionThreshold': {
            'filter': metric_filter, 'comparison': 'COMPARISON_GT', 'thresholdValue': 0,
            'duration': '60s', 'evaluationMissingData': 'EVALUATION_MISSING_DATA_INACTIVE',
            'aggregations': [{'alignmentPeriod': '60s', 'perSeriesAligner': 'ALIGN_SUM',
                'crossSeriesReducer': 'REDUCE_SUM',
                'groupByFields': ['resource.label.service_name', 'resource.label.project_id', 'resource.label.location']}]}}]}
    policies = monitoring_list('alertPolicies')
    existing = next((p for p in policies if p['name'] in STATE['resources'].get('alertPolicies', [])), None)
    if existing:
        policy['name'] = existing['name']
        policy = api('PATCH', 'alertPolicies/' + existing['name'].split('/')[-1], policy)
    else:
        policy = api('POST', 'alertPolicies', policy)
        remember('alertPolicies', policy['name'])
    print(json.dumps({'project': PROJECT, 'region': REGION, 'model': MODEL, 'urls': urls,
                      'policy': policy['name']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', default='europe-west2')
    parser.add_argument('--model', default='gemini-2.5-flash')
    args = parser.parse_args()
    PROJECT, REGION, MODEL = args.project, args.region, args.model
    deploy()
