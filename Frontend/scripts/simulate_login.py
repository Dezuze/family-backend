#!/usr/bin/env python3
"""Simulate frontend login: GET /api/csrf/ then POST /api/auth/login/ with cookies and X-CSRFToken."""
import os
import sys
try:
    import requests
except Exception:
    print('requests library missing; please run: pip install requests')
    sys.exit(2)

BASE = os.environ.get('API_BASE', 'http://localhost:8000')
EMAIL = os.environ.get('TEST_EMAIL', 'test@example.com')
PASSWORD = os.environ.get('TEST_PASSWORD', 'password')

def main():
    s = requests.Session()
    try:
        r = s.get(BASE + '/api/csrf/', timeout=5)
    except Exception as e:
        print('Error calling /api/csrf/:', e)
        return 1

    print('/api/csrf/ ->', r.status_code)
    csrftoken = s.cookies.get('csrftoken')
    print('cookie csrftoken:', csrftoken)

    headers = {'Content-Type': 'application/json'}
    if csrftoken:
        headers['X-CSRFToken'] = csrftoken

    payload = {'identifier': EMAIL, 'password': PASSWORD}
    try:
        r2 = s.post(BASE + '/api/auth/login/', json=payload, headers=headers, timeout=5)
    except Exception as e:
        print('Error posting /api/auth/login/:', e)
        return 1

    print('/api/auth/login/ ->', r2.status_code)
    try:
        print('response JSON:', r2.json())
    except Exception:
        print('response text:', r2.text)
    # If login failed due to credentials, try signing up and retrying
    if r2.status_code != 200:
        print('Attempting to sign up a test user and retry login...')
        signup_payload = {
            'username': 'simtest',
            'email': 'simtest@example.com',
            'member_id': 'simtest',
            'password': 'simpass123',
        }
        try:
            r3 = s.post(BASE + '/api/auth/signup/', json=signup_payload, headers=headers, timeout=5)
            print('/api/auth/signup/ ->', r3.status_code)
            try:
                print('signup response:', r3.json())
            except Exception:
                print('signup text:', r3.text)
        except Exception as e:
            print('Error posting /api/auth/signup/:', e)
            return 1

        # retry login with new user
        payload = {'identifier': signup_payload['username'], 'password': signup_payload['password']}
        try:
            r4 = s.post(BASE + '/api/auth/login/', json=payload, headers=headers, timeout=5)
            print('/api/auth/login/ (retry) ->', r4.status_code)
            try:
                print('retry response JSON:', r4.json())
            except Exception:
                print('retry response text:', r4.text)
        except Exception as e:
            print('Error retrying login:', e)
            return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
