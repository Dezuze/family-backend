import time
import requests

POSSIBLE_FRONT = ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002']
BACK_URL = 'http://localhost:8000'

# pick first frontend that responds
FRONT_URL = None
for u in POSSIBLE_FRONT:
    try:
        r = requests.get(u, timeout=1)
        if r.status_code < 500:
            FRONT_URL = u
            break
    except Exception:
        continue
if not FRONT_URL:
    FRONT_URL = POSSIBLE_FRONT[0]
    print('No frontend responding on common ports; will try', FRONT_URL)

# wait for frontend
for i in range(30):
    try:
        r = requests.get(FRONT_URL, timeout=2)
        if r.status_code < 500:
            print('Frontend up')
            break
    except Exception:
        pass
    time.sleep(1)
else:
    print('Frontend did not start within timeout')
    exit(2)

# Check pages
paths = ['/gallery', '/members', '/familytree']
for p in paths:
    try:
        r = requests.get(FRONT_URL + p, timeout=5)
        print(f'GET {p} ->', r.status_code)
        print(' Title in HTML:', ('Gallery' in r.text) if p=='/gallery' else ('Members' in r.text) if p=='/members' else ('Family' in r.text))
    except Exception as e:
        print(f'Error fetching {p}:', e)

# Check backend APIs
api_paths = ['/api/profiles/gallery/', '/api/families/']
for ap in api_paths:
    try:
        r = requests.get(BACK_URL + ap, timeout=5)
        print(f'API {ap} ->', r.status_code)
        try:
            js = r.json()
            if isinstance(js, dict):
                keys = list(js.keys())
            else:
                keys = ['list']
            print('  payload keys:', keys[:5])
        except Exception as e:
            print('  json parse error', e)
    except Exception as e:
        print(f'Error fetching API {ap}:', e)
