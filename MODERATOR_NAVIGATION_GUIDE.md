# Moderator Navigation Guide

## Overview
Moderators have **the same access as admin users**. This guide shows you exactly how to navigate and access all moderator features.

---

## 🔐 Access Levels

### Moderator Permissions
- ✅ **Full Django Admin Access** (`is_staff = True` automatically granted)
- ✅ Same permissions as superusers in the admin panel
- ✅ Can manage all users, profiles, and content
- ✅ Can appoint other moderators (via admin panel)
- ❌ Cannot delete their own account (security protection)

---

## 🚀 Navigation Flow

### 1. **Login Process**

**Step 1:** Go to login page
```
URL: http://127.0.0.1:8000/accounts/login/
```
- Sign in with your moderator credentials (email/password or Google OAuth)

**Step 2:** Automatic Redirect
- After login, you'll be automatically redirected to:
```
URL: http://127.0.0.1:8000/moderator/
```
This is your **Moderator Dashboard** - your home base for all moderation activities.

---

### 2. **Primary Access Points**

#### **A. Moderator Dashboard**
```
URL: http://127.0.0.1:8000/moderator/
```
**Purpose:** Central hub with quick links to all admin functions
- Visual dashboard with organized sections
- Direct links to all admin panel sections
- Information about your moderator status

**Key Sections:**
- 🚀 Quick Access - Django Admin Panel (prominent green button)
- 👥 User Management
- 📝 Account & Session Management
- 🔗 Social Accounts
- 📊 Admin Logs & Activity
- 🌍 Site Configuration

---

#### **B. Django Admin Panel (Main Admin Interface)**
```
URL: http://127.0.0.1:8000/admin/
```
**Purpose:** Full administrative control - this is where you do most of your work

**Access:** Click the green "🔑 Open Admin Panel" button from moderator dashboard, or navigate directly to `/admin/`

**Login:** Use the same credentials you used for regular site login

---

### 3. **Admin Panel Navigation - Essential Pages**

#### **👥 User Management Pages**

**All Users List**
```
URL: http://127.0.0.1:8000/admin/auth/user/
```
**What you can do:**
- View all registered users
- Edit user details (username, email, password)
- Activate/deactivate users
- Grant/revoke superuser status
- Search and filter users

**User Profiles Management** ⭐ **MOST IMPORTANT**
```
URL: http://127.0.0.1:8000/admin/profiles/profile/
```
**What you can do:**
- View all user profiles
- **Appoint moderators** - Change role dropdown to "Moderator"
- **Remove moderators** - Change role dropdown to "Student" or "club"
- See admin access status (Staff column)
- Use bulk actions:
  - 👑 **"Appoint as Moderator"** - Select multiple profiles → Actions dropdown → "Appoint as Moderator"
  - 🗑️ **"Remove Moderator Status"** - Select moderator profiles → Actions → "Remove Moderator Status"
  - 👨‍🎓 **"Set as Student"**
  - 🏢 **"Set as Organization"**
- Quick edit role directly in list view (Role column is editable)

**User Groups**
```
URL: http://127.0.0.1:8000/admin/auth/group/
```
- Create and manage permission groups
- Assign permissions to groups
- Assign users to groups

**Permissions**
```
URL: http://127.0.0.1:8000/admin/auth/permission/
```
- View all available permissions
- Rarely need to modify directly

---

#### **📝 Account Management Pages**

**Email Addresses**
```
URL: http://127.0.0.1:8000/admin/account/emailaddress/
```
**What you can do:**
- View all user email addresses
- See verification status
- Mark emails as verified/unverified

**Email Confirmations**
```
URL: http://127.0.0.1:8000/admin/account/emailconfirmation/
```
- View pending email confirmations
- Resend confirmation emails if needed

**Active Sessions**
```
URL: http://127.0.0.1:8000/admin/sessions/session/
```
- View all active user sessions
- Delete sessions to force logout
- Useful for security (force logout compromised accounts)

---

#### **🔗 Social Login Management**

**Social Accounts**
```
URL: http://127.0.0.1:8000/admin/socialaccount/socialaccount/
```
**What you can do:**
- View all Google OAuth connections
- See which users logged in via Google
- Disconnect social accounts

**Social Apps (OAuth Configuration)**
```
URL: http://127.0.0.1:8000/admin/socialaccount/socialapp/
```
- Configure OAuth providers (Google)
- Edit client IDs and secrets
- Site restrictions

**Social Tokens**
```
URL: http://127.0.0.1:8000/admin/socialaccount/socialtoken/
```
- View OAuth access tokens
- Usually empty unless actively using tokens

---

#### **📊 Admin Logs**

**Admin Action Log**
```
URL: http://127.0.0.1:8000/admin/admin/logentry/
```
**What you can do:**
- View all admin actions (who did what, when)
- Track changes made by moderators/admins
- Audit trail for platform changes
- See user additions, deletions, modifications

---

#### **🌍 Site Configuration**

**Sites**
```
URL: http://127.0.0.1:8000/admin/sites/site/
```
**What you can do:**
- Configure site domain (for django-allauth)
- Currently set to `example.com` (Site ID: 1)
- Usually doesn't need modification

---

## 📋 Common Moderator Tasks & How to Complete Them

### **Task 1: Appoint a New Moderator**

**Method A: Via Admin Panel (Recommended)**
1. Navigate to: `http://127.0.0.1:8000/admin/profiles/profile/`
2. Find the user you want to make a moderator
3. Click on their profile
4. In the "Role" dropdown, select **"Moderator"**
5. Click **"Save"**
6. ✅ Done! They now have admin access automatically

**Method B: Bulk Action (Multiple Users)**
1. Navigate to: `http://127.0.0.1:8000/admin/profiles/profile/`
2. Check the boxes next to users you want to make moderators
3. In the "Action" dropdown at the top, select **"👑 Appoint as Moderator (grants admin access)"**
4. Click **"Go"**
5. ✅ All selected users are now moderators

---

### **Task 2: Remove Moderator Status**

**Steps:**
1. Navigate to: `http://127.0.0.1:8000/admin/profiles/profile/`
2. Filter by "Role: Moderator" if needed
3. Select the moderator(s) you want to demote
4. In "Action" dropdown, select **"🗑️ Remove Moderator Status"**
5. Click **"Go"**
6. ✅ Their admin access is automatically revoked

---

### **Task 3: View All Moderators**

**Steps:**
1. Navigate to: `http://127.0.0.1:8000/admin/profiles/profile/`
2. In the right sidebar, under "Filters", click **"Role: Moderator"**
3. ✅ You'll see all current moderators
4. Check the "Admin Access" column - all should show "✓ Staff"

---

### **Task 4: Manage User Accounts**

**Edit a User:**
1. Navigate to: `http://127.0.0.1:8000/admin/auth/user/`
2. Click on the username you want to edit
3. Modify fields (email, password, active status, staff status, superuser)
4. Click **"Save"**

**Deactivate a User:**
1. Navigate to: `http://127.0.0.1:8000/admin/auth/user/`
2. Click on the user
3. Uncheck **"Active"**
4. Click **"Save"**
5. ✅ User can no longer log in

**Force Logout (Delete Session):**
1. Navigate to: `http://127.0.0.1:8000/admin/sessions/session/`
2. Find the user's session (search by user ID or username)
3. Select it and click **"Delete"**
4. ✅ User is immediately logged out

---

### **Task 5: View Platform Activity**

**Steps:**
1. Navigate to: `http://127.0.0.1:8000/admin/admin/logentry/`
2. ✅ See all admin actions:
   - Who made changes
   - What they changed
   - When it happened
   - What the old/new values were

---

## 🗺️ Complete Navigation Map

```
Login Page
    ↓
/moderator/ (Moderator Dashboard)
    ├─→ /admin/ (Django Admin Panel)
    │   ├─→ /admin/auth/user/ (All Users)
    │   ├─→ /admin/profiles/profile/ ⭐ (Manage Roles - APPOINT MODERATORS HERE)
    │   ├─→ /admin/auth/group/ (User Groups)
    │   ├─→ /admin/auth/permission/ (Permissions)
    │   ├─→ /admin/account/emailaddress/ (Email Addresses)
    │   ├─→ /admin/account/emailconfirmation/ (Email Confirmations)
    │   ├─→ /admin/sessions/session/ (Active Sessions)
    │   ├─→ /admin/socialaccount/socialaccount/ (Social Accounts)
    │   ├─→ /admin/socialaccount/socialapp/ (OAuth Apps)
    │   ├─→ /admin/admin/logentry/ (Admin Logs)
    │   └─→ /admin/sites/site/ (Site Settings)
    │
    ├─→ /student/ (Student View - if you want to see student experience)
    ├─→ /provider/ (Provider View - if you want to see org experience)
    └─→ / (Home/Landing Page)
```

---

## 🔑 Key URLs Reference

| Purpose | URL | When to Use |
|---------|-----|-------------|
| **Moderator Dashboard** | `/moderator/` | Your home page after login |
| **Admin Panel Home** | `/admin/` | Full admin access - main work area |
| **Appoint Moderators** | `/admin/profiles/profile/` | ⭐ **MOST IMPORTANT** - Change roles here |
| **Manage Users** | `/admin/auth/user/` | Edit user accounts, activate/deactivate |
| **View All Moderators** | `/admin/profiles/profile/?role__exact=moderator` | See who has moderator access |
| **Admin Activity Log** | `/admin/admin/logentry/` | Audit trail of all changes |
| **Force Logout** | `/admin/sessions/session/` | Delete user sessions |

---

## ⚠️ Important Notes

### Security Features
1. **Auto Staff Assignment:** When you appoint someone as moderator, `is_staff = True` is automatically set (via signal in `profiles/signals.py`)
2. **Auto Staff Removal:** When you remove moderator status, `is_staff = False` is automatically removed (unless they're also a superuser)
3. **Role Protection:** Regular users cannot select "Moderator" during signup - only admins can assign this role
4. **Account Protection:** Moderators cannot delete their own accounts (security feature)

### Multiple Moderators
- ✅ **Multiple moderators are fully supported**
- ✅ Each moderator has independent admin access
- ✅ All moderators have the same permissions
- ✅ No limit on number of moderators

### Appointing New Moderators
**Who can appoint moderators?**
- Existing moderators (they have admin access)
- Superusers (they have admin access)
- Anyone with admin panel access

**Process:**
1. You must have admin access (moderator or superuser)
2. Go to `/admin/profiles/profile/`
3. Change role to "Moderator"
4. Save
5. ✅ Done - they now have admin access

---

## 🎯 Quick Start Checklist for New Moderators

- [ ] Log in at `/accounts/login/`
- [ ] Verify you're redirected to `/moderator/`
- [ ] Click "🔑 Open Admin Panel" button
- [ ] Verify you can access `/admin/`
- [ ] Go to `/admin/profiles/profile/` and see all profiles
- [ ] Test appointing a test user as moderator (then remove it)
- [ ] Review `/admin/admin/logentry/` to see activity history
- [ ] Bookmark `/admin/` and `/moderator/` for quick access

---

## 💡 Pro Tips

1. **Bookmark These Pages:**
   - `/admin/` - Your main work area
   - `/admin/profiles/profile/` - For role management
   - `/moderator/` - Quick dashboard with links

2. **Use Bulk Actions:**
   - Select multiple profiles at once
   - Use Actions dropdown for bulk role changes
   - Much faster than changing one at a time

3. **Check Admin Logs Regularly:**
   - `/admin/admin/logentry/`
   - Helps track what other moderators are doing
   - Good for security auditing

4. **Quick Role Check:**
   - Filter by "Role: Moderator" to see all moderators
   - Check "Admin Access" column to verify staff status

5. **Session Management:**
   - If a user reports security issues, delete their session
   - Forces immediate logout
   - Located at `/admin/sessions/session/`

---

## 🆘 Troubleshooting

**Problem:** "I can't access `/admin/`"
- **Solution:** Verify your profile role is "Moderator" at `/admin/profiles/profile/`
- Check that your user's `is_staff` is True (should be automatic)
- Try logging out and back in

**Problem:** "I can't see the Admin Panel button"
- **Solution:** Make sure you're logged in as a moderator
- Verify you're on `/moderator/` dashboard
- Check browser console for errors

**Problem:** "I can't appoint moderators"
- **Solution:** You need admin access first - ask an existing moderator/superuser to appoint you
- Verify you can access `/admin/` before trying to appoint others

**Problem:** "Changes aren't saving"
- **Solution:** Make sure you have the correct permissions
- Check if you're looking at the right user/profile
- Verify you clicked "Save" button

---

## 📞 Summary

**Primary Workflow:**
1. **Login** → Auto-redirected to `/moderator/`
2. **Click Admin Panel** → Go to `/admin/`
3. **Navigate to Profiles** → `/admin/profiles/profile/`
4. **Manage Roles** → Appoint/remove moderators as needed
5. **Use Other Admin Sections** → User management, logs, sessions, etc.

**Remember:** Moderators = Admins. You have full access to everything in the Django admin panel!

