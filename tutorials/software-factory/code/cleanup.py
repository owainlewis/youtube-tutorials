#!/usr/bin/env python3
"""Remove resources recorded by this deployment. Requires explicit --confirm."""
import argparse
import deploy


def cleanup():
    state = deploy.load_state(required=True)
    existing = deploy.inventory()
    cli, api = deploy.cli, deploy.api
    for kind in ['alertPolicies', 'notificationChannels', 'subscriptions', 'topics',
                 'services', 'databases', 'repositories', 'accounts']:
        for resource in list(state['resources'].get(kind, [])):
            present = (any(item['name'] == resource for item in existing[kind])
                       if kind in ('alertPolicies', 'notificationChannels')
                       else resource in existing[kind])
            if present:
                if kind in ('alertPolicies', 'notificationChannels'):
                    api('DELETE', kind + '/' + resource.split('/')[-1])
                elif kind in ('subscriptions', 'topics'):
                    cli('pubsub', kind, 'delete', resource)
                elif kind == 'services':
                    cli('run', 'services', 'delete', resource, '--region', deploy.REGION)
                elif kind == 'databases':
                    cli('firestore', 'databases', 'delete', '--database', resource.split('/')[-1])
                elif kind == 'repositories':
                    cli('artifacts', 'repositories', 'delete', resource, '--location', deploy.REGION)
                elif kind == 'accounts':
                    member = 'serviceAccount:' + resource
                    policy = cli('projects', 'get-iam-policy', deploy.PROJECT, json_output=True)
                    for binding in policy.get('bindings', []):
                        if member in binding.get('members', []) and not binding.get('condition'):
                            cli('projects', 'remove-iam-policy-binding', deploy.PROJECT,
                                '--member', member, '--role', binding['role'], '--condition=None')
                    if resource == f'{deploy.PREFIX}-build@{deploy.PROJECT}.iam.gserviceaccount.com':
                        bucket = f'gs://{deploy.PROJECT}_cloudbuild'
                        buckets = cli('storage', 'buckets', 'list', json_output=True)
                        if any(b['name'] == deploy.PROJECT + '_cloudbuild' for b in buckets):
                            policy = cli('storage', 'buckets', 'get-iam-policy', bucket, json_output=True)
                            if any(b['role'] == 'roles/storage.objectViewer' and member in b.get('members', [])
                                   for b in policy.get('bindings', [])):
                                cli('storage', 'buckets', 'remove-iam-policy-binding', bucket,
                                    '--member', member, '--role', 'roles/storage.objectViewer')
                    cli('iam', 'service-accounts', 'delete', resource)
            state['resources'][kind].remove(resource)
            deploy.save_state(state)
    print('Recorded demo resources removed. Shared APIs, build bucket, build history and billing remain unchanged.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', default='europe-west2')
    parser.add_argument('--confirm', action='store_true')
    args = parser.parse_args()
    if not args.confirm:
        parser.error('--confirm is required; this deletes demo history and container images')
    deploy.PROJECT, deploy.REGION = args.project, args.region
    cleanup()


if __name__ == '__main__':
    main()
