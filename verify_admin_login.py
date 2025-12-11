#!/usr/bin/env python
"""
Verify Django admin login works
This script tests if you can actually log in to the admin panel
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.contrib.auth import authenticate

def test_login(username, password):
    """Test if a username/password combination works"""
    user = authenticate(username=username, password=password)
    if user:
        print(f"✅ Login SUCCESS for '{username}'")
        print(f"   - Superuser: {user.is_superuser}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Active: {user.is_active}")
        return True
    else:
        print(f"❌ Login FAILED for '{username}'")
        print(f"   - Password is incorrect or user doesn't exist")
        return False

def main():
    print("\n" + "="*60)
    print("Django Admin Login Verification")
    print("="*60 + "\n")
    
    # Get all admin users
    admin_users = User.objects.filter(
        models.Q(is_superuser=True) | models.Q(is_staff=True)
    ).filter(is_active=True)
    
    if not admin_users.exists():
        print("❌ No active admin users found!")
        return
    
    print("Available admin users:\n")
    for i, user in enumerate(admin_users, 1):
        print(f"{i}. {user.username} ({user.email or 'no email'})")
        print(f"   Superuser: {user.is_superuser}, Staff: {user.is_staff}")
    
    print("\n" + "-"*60)
    print("To test login, you have two options:")
    print("-"*60)
    print("\nOption 1: Test in Browser (Recommended)")
    print("  1. Start server: python manage.py runserver")
    print("  2. Go to: http://127.0.0.1:8000/admin/")
    print("  3. Try logging in with one of the usernames above")
    print("  4. If it works, you'll see the admin dashboard")
    print("  5. If it fails, you'll see an error message")
    
    print("\nOption 2: Test Password (if you know it)")
    print("  Run: python verify_admin_login.py <username> <password>")
    print("  Example: python verify_admin_login.py superuser mypassword")
    
    print("\nOption 3: Reset Password")
    print("  If you forgot the password, reset it:")
    print("  python manage.py shell")
    print("  >>> from django.contrib.auth.models import User")
    print("  >>> user = User.objects.get(username='your_username')")
    print("  >>> user.set_password('new_password')")
    print("  >>> user.save()")
    print("  >>> exit()")
    
    # If username and password provided as arguments, test them
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
        print(f"\n{'='*60}")
        print(f"Testing login for: {username}")
        print(f"{'='*60}\n")
        test_login(username, password)
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    from django.db import models
    main()

