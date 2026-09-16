#!/usr/bin/env python3
"""Deploy the demo with gcloud. No Terraform state or embedded credentials."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import urllib.error

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


def ensure_account(name):
    email = f'{name}@{PROJECT}.iam.gserviceaccount.com'
    accounts = cli('iam', 'service-accounts', 'list', json_output=True)
    if not any(a['email'] == email for a in accounts):
        cli('iam', 'service-accounts', 'create', name, '--display-name', name)
    return email


def role(email, name):
    cli('projects', 'add-iam-policy-binding', PROJECT, '--member', 'serviceAccount:' + email,
        '--role', name, '--condition=None')


def deploy():
    cli('services', 'enable', 'run.googleapis.com', 'cloudbuild.googleapis.com',
        'artifactregistry.googleapis.com', 'monitoring.googleapis.com', 'logging.googleapis.com',
        'pubsub.googleapis.com', 'firestore.googleapis.com', 'aiplatform.googleapis.com', 'iam.googleapis.com')
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
    repositories = cli('artifacts', 'repositories', 'list', '--location', REGION, json_output=True)
    if not any(r['name'].endswith('/' + PREFIX) for r in repositories):
        cli('artifacts', 'repositories', 'create', PREFIX, '--location', REGION, '--repository-format', 'docker')
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
        urls[mode] = cli('run', 'services', 'describe', name, '--region', REGION, json_output=True)['status']['url']
    cli('run', 'services', 'add-iam-policy-binding', PREFIX + '-triage', '--region', REGION,
        '--member', 'serviceAccount:' + push_sa, '--role', 'roles/run.invoker')
    topics = cli('pubsub', 'topics', 'list', json_output=True)
    if not any(t['name'].endswith('/' + PREFIX + '-alerts') for t in topics):
        cli('pubsub', 'topics', 'create', PREFIX + '-alerts')
    topic = f'projects/{PROJECT}/topics/{PREFIX}-alerts'
    channels = api('GET', 'notificationChannels').get('notificationChannels', [])
    channel = next((c for c in channels if c.get('displayName') == PREFIX), None)
    if channel is None:
        channel = api('POST', 'notificationChannels', {'type': 'pubsub', 'displayName': PREFIX,
                                                      'labels': {'topic': topic}})
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
    policies = api('GET', 'alertPolicies').get('alertPolicies', [])
    existing = next((p for p in policies if p['displayName'] == policy['displayName']), None)
    if existing:
        policy['name'] = existing['name']
        policy = api('PATCH', 'alertPolicies/' + existing['name'].split('/')[-1], policy)
    else:
        policy = api('POST', 'alertPolicies', policy)
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
