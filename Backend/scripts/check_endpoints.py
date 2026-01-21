import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')
django.setup()

from django.test import Client

def main():
    c = Client()
    r = c.get('/api/profiles/gallery/')
    print('/api/profiles/gallery/ ->', r.status_code)
    try:
        print('gallery payload sample keys:', list(r.json().keys()) if isinstance(r.json(), dict) else 'list')
    except Exception as e:
        print('gallery json error', e)

    r2 = c.get('/api/families/')
    print('/api/families/ ->', r2.status_code)
    try:
        print('families payload sample keys:', list(r2.json().keys()) if isinstance(r2.json(), dict) else 'list')
    except Exception as e:
        print('families json error', e)

if __name__ == '__main__':
    main()
