import requests
import json
import random

API_BASE = 'http://127.0.0.1:8000/api'
session = requests.Session()

def main():
    print("--- 1. Login ---")
    login_data = {'identifier': 'testadmin', 'password': 'testadmin123'}
    r_login = session.post(f'{API_BASE}/auth/login/', json=login_data)
    print("Login status:", r_login.status_code)
    if r_login.status_code != 200:
        print("Login failed:", r_login.text)
        return

    csrftoken = session.cookies.get('csrftoken')
    session.headers.update({'X-CSRFToken': csrftoken, 'Referer': 'http://localhost:3000'})
    print("Logged in successfully.")

    print("\n--- 2. Create Root Member ---")
    create_data = {'first_name': 'TestRoot', 'last_name': 'Admin', 'gender': 'M'}
    r_create = session.post(f'{API_BASE}/families/managed/', data=create_data)
    print("Create root status:", r_create.status_code)
    if r_create.status_code != 201:
        print("Create root failed:", r_create.text)
        return
    test_member = r_create.json()
    member_id = test_member['id']
    print(f"Created member: {test_member['name']} (ID: {member_id})")

    print("\n--- 3. Test Editing (Quick Edit) ---")
    edit_url = f"{API_BASE}/families/managed/{member_id}/"
    edit_data = {'first_name': 'TestRootEdited', 'last_name': 'Admin', 'gender': 'M', 'nickname': 'TestEdit123'}
    r_edit = session.put(edit_url, data=edit_data)
    print("Edit status:", r_edit.status_code)
    if r_edit.status_code in [200, 204]:
        print("Edit successful!")
    else:
        print("Edit failed:", r_edit.text)
        
    print("\n--- 4. Test Adding Relative ---")
    add_rel_url = f"{API_BASE}/families/tree-edit/{member_id}/add-relative/"
    add_rel_data = {
        'first_name': 'Test',
        'last_name': 'Child',
        'gender': 'M',
        'relation_type': 'child'
    }
    r_add = session.post(add_rel_url, data=add_rel_data)
    print("Add relative status:", r_add.status_code)
    new_member_id = None
    if r_add.status_code == 201:
        print("Add relative successful!")
        new_member_id = r_add.json().get('member', {}).get('id')
    else:
        print("Add relative failed:", r_add.text)

    print("\n--- 5. Test Giving Access (Make Account) ---")
    if new_member_id:
        give_access_url = f"{API_BASE}/auth/give-access/"
        access_username = f"testuser_{random.randint(1000, 9999)}"
        access_data = {
            'profile_id': new_member_id,
            'username': access_username,
            'password': 'Password123!'
        }
        r_access = session.post(give_access_url, json=access_data)
        print("Give access status:", r_access.status_code)
        if r_access.status_code == 200:
            print("Give access successful! Created account for", access_username)
        else:
            print("Give access failed:", r_access.text)

if __name__ == '__main__':
    main()
