#!/usr/bin/env python3
"""Introduce a bad revision, send synthetic requests, or recover the demo API."""
import argparse
import json
import subprocess
import time
import urllib.request
import urllib.error


def run(args, *command):
    return subprocess.check_output(['gcloud', *command, '--project', args.project,
                                    '--region', args.region, '--quiet', '--format=json'], text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['break', 'recover', 'traffic', 'info'])
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', default='europe-west2')
    parser.add_argument('--seconds', type=int, default=300)
    args = parser.parse_args()
    service = 'software-factory-api'
    if args.action in ('break', 'recover'):
        failure = 'true' if args.action == 'break' else 'false'
        run(args, 'run', 'services', 'update', service, '--update-env-vars', 'DEMO_FAILURE=' + failure)
        # Explicitly route to the new revision, including after a manual traffic rollback.
        run(args, 'run', 'services', 'update-traffic', service, '--to-latest')
    description = json.loads(run(args, 'run', 'services', 'describe', service))
    url = description['status']['url']
    print(url, flush=True)
    if args.action == 'traffic':
        token = subprocess.check_output(['gcloud', 'auth', 'print-identity-token'], text=True).strip()
        end = time.monotonic() + max(1, min(args.seconds, 1800))
        counts = {}
        while time.monotonic() < end:
            request = urllib.request.Request(url + '/api/checkout', data=b'{"product_id":"course","quantity":1}',
                                            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status = response.status
            except urllib.error.HTTPError as error:
                status = error.code
            counts[status] = counts.get(status, 0) + 1
            print(json.dumps({'status': status, 'counts': counts}), flush=True)
            time.sleep(1)


if __name__ == '__main__':
    main()
