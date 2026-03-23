#!/usr/bin/env python3
"""
X List Manager — Create and manage X (Twitter) Lists via official API.
Uses OAuth 1.0a (User Context) for list operations.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from requests_oauthlib import OAuth1Session

# Load env
ENV_FILE = Path('/root/.openclaw/.env')
for line in ENV_FILE.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        key, _, val = line.partition('=')
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key.startswith('export '):
            key = key[7:]
        os.environ.setdefault(key, val)

CONSUMER_KEY = os.environ['X_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['X_CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['X_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['X_ACCESS_TOKEN_SECRET']

BASE = 'https://api.x.com/2'


def get_session():
    return OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET,
    )


def get_me(session):
    """Get authenticated user info."""
    r = session.get(f'{BASE}/users/me')
    r.raise_for_status()
    return r.json()['data']


def create_list(session, name, description='', private=False):
    """Create a new list."""
    payload = {'name': name, 'private': private}
    if description:
        payload['description'] = description
    r = session.post(f'{BASE}/lists', json=payload)
    if r.status_code == 403:
        print(f'ERROR 403: {r.text}')
        print('This likely means you need pay-per-use credits loaded.')
        sys.exit(1)
    r.raise_for_status()
    data = r.json()['data']
    print(f'List created: {data["name"]} (ID: {data["id"]})')
    return data


def add_member(session, list_id, user_id):
    """Add a member to a list by user ID."""
    for attempt in range(3):
        r = session.post(f'{BASE}/lists/{list_id}/members', json={'user_id': user_id})
        if _handle_rate_limit(r):
            continue
        r.raise_for_status()
        return r.json()
    raise Exception('Rate limit exhausted for add_member')


def _handle_rate_limit(r):
    """Wait if rate limited, return True if we should retry."""
    if r.status_code == 429:
        reset = r.headers.get('x-rate-limit-reset')
        if reset:
            wait = max(int(reset) - int(time.time()), 1) + 2
        else:
            wait = 65
        print(f'  Rate limited, waiting {wait}s...')
        time.sleep(wait)
        return True
    return False


def lookup_user(session, username):
    """Look up a user by username to get their ID."""
    username = username.lstrip('@')
    for attempt in range(3):
        r = session.get(f'{BASE}/users/by/username/{username}')
        if _handle_rate_limit(r):
            continue
        if r.status_code == 404 or (r.status_code == 200 and 'errors' in r.json()):
            print(f'  User @{username} not found, skipping')
            return None
        r.raise_for_status()
        return r.json()['data']
    print(f'  @{username}: rate limit exhausted, skipping')
    return None


def get_lists(session, user_id):
    """Get owned lists."""
    r = session.get(f'{BASE}/users/{user_id}/owned_lists')
    r.raise_for_status()
    return r.json().get('data', [])


# Default reply targets list
REPLY_TARGETS = [
    # Builders & Creators
    'levelsio', 'gregisenberg', 'LinusEkenstam', 'LiamOttley',
    'mattshumer_', 'mckaywrigley', 'swyx', 'bentossell',
    'dannypostmaa', 'AlexFinn', 'dickiebush', 'svpino',
    'matt_gray_', 'marc_louvion', 'skirank',
    # AI Leaders & Researchers
    'karpathy', 'sama', 'ylecun', 'fchollet', 'DrJimFan', 'lexfridman',
    # AI News
    'rowancheung', 'TheRundownAI', 'bensbites', '_akhaliq',
    'theneuron', 'theresanaiforthat',
    # High engagement
    'venturetwins', 'nonmayorpete', 'ankurnagpal', 'aakashgupta',
]


def cmd_create(args):
    session = get_session()
    me = get_me(session)
    print(f'Authenticated as @{me["username"]} (ID: {me["id"]})')

    list_data = create_list(
        session, args.name, description=args.description, private=args.private
    )

    if args.add_defaults:
        print(f'\nAdding {len(REPLY_TARGETS)} accounts...')
        added, failed = 0, 0
        for username in REPLY_TARGETS:
            user = lookup_user(session, username)
            if user:
                try:
                    add_member(session, list_data['id'], user['id'])
                    print(f'  + @{username}')
                    added += 1
                except Exception as e:
                    print(f'  x @{username}: {e}')
                    failed += 1
        print(f'\nDone! Added {added}, failed {failed}')

    return list_data


def cmd_add(args):
    session = get_session()
    user = lookup_user(session, args.username)
    if user:
        add_member(session, args.list_id, user['id'])
        print(f'Added @{args.username} to list {args.list_id}')


def cmd_show(args):
    session = get_session()
    me = get_me(session)
    print(f'Authenticated as @{me["username"]}')
    lists = get_lists(session, me['id'])
    if not lists:
        print('No lists found.')
    for lst in lists:
        print(f'  {lst["name"]} (ID: {lst["id"]})')


def cmd_test(args):
    session = get_session()
    me = get_me(session)
    print(f'API connection OK! Authenticated as @{me["username"]} (ID: {me["id"]})')


def main():
    p = argparse.ArgumentParser(description='X List Manager')
    sub = p.add_subparsers(dest='cmd', required=True)

    # test
    sub.add_parser('test', help='Test API connection')

    # show
    sub.add_parser('show', help='Show your lists')

    # create
    pc = sub.add_parser('create', help='Create a new list')
    pc.add_argument('name', help='List name')
    pc.add_argument('--description', default='', help='List description')
    pc.add_argument('--private', action='store_true', help='Make list private')
    pc.add_argument('--add-defaults', action='store_true',
                    help='Add default reply target accounts')

    # add
    pa = sub.add_parser('add', help='Add a user to a list')
    pa.add_argument('list_id', help='List ID')
    pa.add_argument('username', help='Username to add')

    args = p.parse_args()
    if args.cmd == 'test':
        cmd_test(args)
    elif args.cmd == 'show':
        cmd_show(args)
    elif args.cmd == 'create':
        cmd_create(args)
    elif args.cmd == 'add':
        cmd_add(args)


if __name__ == '__main__':
    main()
