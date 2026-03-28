# Family App Backend

Django REST Framework backend for the Family Application.

## Prerequisites
- Python 3.10+
- PostgreSQL (or SQLite for local dev)

## Setup

1.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4.  **Run Development Server**
    ```bash
    python manage.py runserver
    ```

## 🧪 Testing
Run the full test suite with:
```bash
python manage.py test
```
To run specific apps:
```bash
python manage.py test families news
```
Targeted families test runs:
```bash
python manage.py test families --verbosity 2
python manage.py test families.tests.TreeEditEndpointsTests --verbosity 2
python manage.py test families.tests.ManagedMembersTests --verbosity 2
```
**Note**: Tests are configured to use a temporary media root for file uploads.

## Permission Model

Tree and managed-member actions are protected by member ownership checks.

- `member.user_account == request.user`: self-management allowed.
- `member.created_by == request.user` and member is non-independent and has no account: guardian management allowed.
- Otherwise management actions are rejected.

### `is_independent` Semantics
- `false`: member can be managed by guardian flows.
- `true`: member is autonomous and no longer managed by guardian-only edit flows.

## Relationship Constraints

Families tree-edit endpoints enforce shared relation rules:

- Max one spouse per member.
- Max one father and one mother per member.
- Max two total parents.
- Self-link is rejected.
- Duplicate relationship edges are rejected.

These validations are applied consistently in both create-new and link-existing relative paths.

## Families API Reference

### Search Members For Linking
- **Endpoint**: `GET /api/families/member-search/?q={query}&exclude_id={id}`
- **Auth**: required
- **Purpose**: return lightweight members for link-existing picker.

### Add Relative (Create New)
- **Endpoint**: `POST /api/families/tree-edit/{pk}/add-relative/`
- **Auth**: required
- **Purpose**: create a new member and link with `relation_type`.

### Link Existing Member
- **Endpoint**: `POST /api/families/tree-edit/{pk}/link-existing/`
- **Auth**: required
- **Purpose**: link an existing `target_member_id` to anchor with `relation_type`.

### Member Context
- **Endpoint**: `GET /api/families/member-context/{pk}/`
- **Auth**: required
- **Purpose**: ownership flags and allowed actions for editor UI gating.

## Security
- **Password Policy**: Enforced 12-character minimum with mixed case, numbers, and symbols.
- **Environment Variables**:
    - `DJANGO_SECRET_KEY`: Set in production.
    - `DEBUG`: Set to `False` in production.

## 💾 Backups
Run the management command to create a JSON dump of the database:
```bash
python manage.py backup_db
```
Backups are saved to the `backups/` directory with a timestamp.
