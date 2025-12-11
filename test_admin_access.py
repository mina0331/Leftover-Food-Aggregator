#!/usr/bin/env python
"""
Quick script to test Django admin access
Run this to verify your admin user works
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

def test_admin_user():
    print("\n" + "="*60)
    print("Testing Django Admin User Access")
    print("="*60 + "\n")
    
    # List all admin users
    admin_users = User.objects.filter(
        models.Q(is_superuser=True) | models.Q(is_staff=True)
    )
    
    if not admin_users.exists():
        print("❌ No admin users found!")
        print("\nCreate one with: python manage.py createsuperuser\n")
        return False
    
    print("Found admin users:\n")
    for user in admin_users:
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email or '(no email)'}")
        print(f"  Superuser: {user.is_superuser}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Active: {user.is_active}")
        print()
    
    # Test authentication for each user
    print("Testing authentication...\n")
    for user in admin_users:
        # Try to authenticate (we can't test password without knowing it)
        print(f"Testing user: {user.username}")
        print(f"  ✅ User exists in database")
        print(f"  ✅ User is {'active' if user.is_active else 'INACTIVE (cannot login)'}")
        print(f"  ✅ User has admin access: {user.is_superuser or user.is_staff}")
        
        if not user.is_active:
            print(f"  ⚠️  WARNING: User is inactive and cannot login!")
        
        if not (user.is_superuser or user.is_staff):
            print(f"  ⚠️  WARNING: User does not have admin access!")
        
        print()
    
    print("="*60)
    print("Manual Testing Steps:")
    print("="*60)
    print("\n1. Start the server:")
    print("   python manage.py runserver")
    print("\n2. Open in browser:")
    print("   http://127.0.0.1:8000/admin/")
    print("\n3. Try to login with:")
    for user in admin_users:
        print(f"   Username: {user.username}")
        if user.email:
            print(f"   Email: {user.email}")
    print("\n4. If login fails, reset password:")
    print("   python manage.py shell")
    print("   from django.contrib.auth.models import User")
    print("   user = User.objects.get(username='your_username')")
    print("   user.set_password('new_password')")
    print("   user.save()")
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == "__main__":
    from django.db import models
    test_admin_user()

