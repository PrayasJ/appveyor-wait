#!/usr/bin/env python3
"""
Wait for appveyor to complete
Attempts to fetch statuses from
- status API https://developer.github.com/v3/repos/statuses/
- checks API https://developer.github.com/v3/checks/
"""

# importing libraries
import os
from re import search
import requests
from requests.auth import HTTPBasicAuth
from subprocess import check_output
import sys
from time import sleep

# Getting  important urls
GITHUB_API = 'https://api.github.com'
check_runs_api = '/repos/{userrepo}/commits/{ref}/check-runs'
status_api = '/repos/{userrepo}/commits/{ref}/status'


def api_get(path, *args, **kwargs):
    url = GITHUB_API + path
    tokens = os.getenv('GITHUB_TOKEN')
    if 'auth' not in kwargs and tokens:
        kwargs['auth'] = HTTPBasicAuth('', tokens)
    headers = kwargs.get('headers', {})
    if 'Accept' not in headers:
        headers['Accept'] = (
            'application/json, '
            # Custom header for checks API
            # https://developer.github.com/v3/checks/runs/#list-check-runs-for-a-specific-ref
            'application/vnd.github.antiope-preview+json;q=0.9, '
            '*/*;q=0.8'
        )
    kwargs['headers'] = headers
    r = requests.get(url, *args, **kwargs)
    r.raise_for_status()
    return r

# gets the status of the build 
# returns pending success failure
def get_status(userrepo, ref):
    r_checkruns = api_get(
        check_runs_api.format(userrepo=userrepo, ref=ref)).json()
    r_status = api_get(status_api.format(userrepo=userrepo, ref=ref)).json()
    results = []
    if 'check_runs' in r_checkruns:
        for run in r_checkruns['check_runs']:
            status = run['status']
            conclusion = run['conclusion']
            app = run['app']['name']
            if app == 'appveyor CI':
                # status: queued in_progress completed
                # conclusion: success failure None
                print('appveyor CI check status:{} conclusion:{}'.format(
                    status, conclusion))
                if status == 'completed':
                    state = conclusion
                else:
                    state = 'pending'
                results.append(state)

        try:
            state = r_status['state']
            # state=pending if there are no statuses
            if r_status['statuses']:
                print('status state:{}'.format(state))
                results.append(state)
        except KeyError:
            pass

    return results


if len(sys.argv) == 1:
    g_url = check_output(
        ['git', 'remote', 'get-url', 'origin']).decode().strip()
    try:
        m = search(
            r'.+[^\w]github.com[:/](?P<userrepo>[^/]+/[^/]+?)(\.git)?$',
            g_url).groupdict()
        print(m)
    except AttributeError:
        raise ValueError('Unable to get user/repository: {}'.format(g_url))
    userrepo = m['userrepo']
    ref = check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    if len(ref) != 40:
        raise ValueError('Unable to get HEAD commit: {}'.format(ref))
elif len(sys.argv) == 3:
    userrepo, ref = sys.argv[1:3]
else:
    raise ValueError('Expected 0 or 2 arguments (user/repository, commit-ref)')

print('Getting appveyor status for {}@{}'.format(userrepo, ref))

# Retry for 4m in case appveyor is slow to trigger
results = get_status(userrepo, ref)
for n in range(4):
    if not results:
        print('No CI status found, retrying in 30s')
        sleep(60)
        results = get_status(userrepo, ref)
if not results:
    raise Exception('No CI status found for {}@{}'.format(userrepo, ref))

while 'pending' in results and 'failure' not in results:
    sleep(30)
    results = get_status(userrepo, ref)
    if 'failure' in results:
        sys.exit(1)

if 'failure' in results:
    sys.exit(1)

if set(results) != {'success'}:
    raise RuntimeError('Unexpected status: {}'.format(results))
