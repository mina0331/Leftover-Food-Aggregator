# How to Create Django Admin User

## Quick Method: Create Superuser

Run this command to create a superuser account:

```bash
cd /Users/leolee/UVA/Year3-2526/SWE/project-b-27
source venv/bin/activate  # or activate your virtual environment
python manage.py createsuperuser
```

You'll be prompted to enter:
- Username
- Email (optional)
- Password (twice for confirmation)

## After Creating Superuser

1. **Access Django Admin:**
   ```
   http://127.0.0.1:8000/admin/
   ```

2. **Login with:**
   - Username: (the one you just created)
   - Password: (the one you just set)

## Alternative: Check Existing Users

If you want to check if there are already admin users:

```bash
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth.models import User
from profiles.models import Profile

# Check superusers
superusers = User.objects.filter(is_superuser=True)
for u in superusers:
    print(f"Superuser: {u.username} ({u.email})")

# Check staff users (can also access admin)
staff = User.objects.filter(is_staff=True)
for u in staff:
    is_mod = hasattr(u, 'profile') and u.profile.role == Profile.Role.MODERATOR
    print(f"Staff: {u.username} ({u.email}) - Moderator: {is_mod}")
```

## Reset Password for Existing User

If you have an existing user but forgot the password:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.get(username='your_username')
user.set_password('new_password')
user.save()
```

## Test Users (from test script)

If you ran the test script, these test users were created:
- **test_moderator** / **testpass123** (has admin access)
- **test_org** / **testpass123** (regular org user)
- **test_user** / **testpass123** (regular user)

Note: These may have been cleaned up if you ran with `--cleanup` flag.

