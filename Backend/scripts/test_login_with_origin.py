import requests

BACK = 'http://localhost:8000'
ORIGIN = 'http://localhost:3001'

def test():
    s = requests.Session()
    headers = {'Origin': ORIGIN}
    r = s.get(BACK + '/api/csrf/', headers=headers)
    print('/api/csrf/ ->', r.status_code)
    print('response headers:', {k:v for k,v in r.headers.items() if k.lower().startswith('access-control')})
    print('set-cookie:', r.headers.get('set-cookie'))
    # try login
    csrftoken = s.cookies.get('csrftoken') or s.cookies.get('csrf')
    print('cookie csrftoken:', csrftoken)
    payload = {'identifier': 'wesly', 'password': 'wesly'}
    headers2 = {'Origin': ORIGIN}
    if csrftoken:
        headers2['X-CSRFToken'] = csrftoken
    r2 = s.post(BACK + '/api/auth/login/', json=payload, headers=headers2)
    print('/api/auth/login/ ->', r2.status_code)
    print('response headers:', {k:v for k,v in r2.headers.items() if k.lower().startswith('access-control')})
    print('set-cookie after login:', r2.headers.get('set-cookie'))
    try:
        print('json:', r2.json())
    except Exception:
        print('text:', r2.text[:500])

if __name__ == '__main__':
    test()
