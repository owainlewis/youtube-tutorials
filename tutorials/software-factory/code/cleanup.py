#!/usr/bin/env python3
"""Remove only this tutorial's named demo resources. Requires explicit --confirm."""
import argparse
import deploy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', default='europe-west2')
    parser.add_argument('--confirm', action='store_true')
    args = parser.parse_args()
    if not args.confirm:
        parser.error('--confirm is required; this deletes demo history and container images')
    deploy.PROJECT = args.project
    cli, api = deploy.cli, deploy.api
    prefix = deploy.PREFIX
    for item in api('GET', 'alertPolicies').get('alertPolicies', []):
        if item['displayName'] == prefix + ' / Checkout errors':
            api('DELETE', 'alertPolicies/' + item['name'].split('/')[-1])
    for item in api('GET', 'notificationChannels').get('notificationChannels', []):
        if item.get('displayName') == prefix:
            api('DELETE', 'notificationChannels/' + item['name'].split('/')[-1])
    for kind, name in [('subscriptions', prefix + '-triage'), ('topics', prefix + '-alerts')]:
        items = cli('pubsub', kind, 'list', json_output=True)
        if any(item['name'].endswith('/' + name) for item in items):
            cli('pubsub', kind, 'delete', name)
    services = cli('run', 'services', 'list', '--region', args.region, json_output=True)
    for name in [prefix + '-api', prefix + '-triage', prefix + '-dashboard']:
        if any(item['metadata']['name'] == name for item in services):
            cli('run', 'services', 'delete', name, '--region', args.region)
    for database in cli('firestore', 'databases', 'list', json_output=True):
        if database['name'].endswith('/' + prefix):
            cli('firestore', 'databases', 'delete', '--database', prefix)
    for repository in cli('artifacts', 'repositories', 'list', '--location', args.region, json_output=True):
        if repository['name'].endswith('/' + prefix):
            cli('artifacts', 'repositories', 'delete', prefix, '--location', args.region)
    accounts = cli('iam', 'service-accounts', 'list', json_output=True)
    for suffix in ['api', 'triage', 'dashboard', 'push', 'build']:
        email = f'{prefix}-{suffix}@{args.project}.iam.gserviceaccount.com'
        member = 'serviceAccount:' + email
        policy = cli('projects', 'get-iam-policy', args.project, json_output=True)
        for binding in policy.get('bindings', []):
            if member in binding['members'] and not binding.get('condition'):
                cli('projects', 'remove-iam-policy-binding', args.project,
                    '--member', member, '--role', binding['role'], '--condition=None')
        if suffix == 'build' and any(item['email'] == email for item in accounts):
            cli('storage', 'buckets', 'remove-iam-policy-binding', f'gs://{args.project}_cloudbuild',
                '--member', member, '--role', 'roles/storage.objectViewer')
        if any(item['email'] == email for item in accounts):
            cli('iam', 'service-accounts', 'delete', email)
    print('Demo removed. Shared APIs, build history and project billing remain unchanged.')


if __name__ == '__main__':
    main()
