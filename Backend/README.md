# Family App Backend

Django REST Framework backend for the Family Application.

## 📋 Prerequisites
- Python 3.10+
- PostgreSQL (or SQLite for local dev)

## 🚀 Setup

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
**Note**: Tests are configured to use a temporary media root for file uploads.

## 🔒 Security
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
