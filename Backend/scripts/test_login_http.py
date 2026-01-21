import requests

BACK = 'http://localhost:8000'

def test_login(username, password):
    s = requests.Session()
    try:
        r = s.get(BACK + '/api/csrf/', timeout=5)
        print('/api/csrf/ ->', r.status_code)
    except Exception as e:
        print('csrf request failed', e)
        return
    csrftoken = s.cookies.get('csrftoken') or s.cookies.get('csrf') or None
    print('csrf cookie:', csrftoken)
    headers = {'X-CSRFToken': csrftoken} if csrftoken else {}
    payload = {'identifier': username, 'password': password}
    r = s.post(BACK + '/api/auth/login/', json=payload, headers=headers, timeout=5)
    print('/api/auth/login/ ->', r.status_code)
    try:
        print('response json:', r.json())
    except Exception:
        print('response text:', r.text[:500])

if __name__ == '__main__':
    import sys
    u = sys.argv[1] if len(sys.argv) > 1 else 'wesly'
    p = sys.argv[2] if len(sys.argv) > 2 else 'wesly'
    test_login(u, p)
