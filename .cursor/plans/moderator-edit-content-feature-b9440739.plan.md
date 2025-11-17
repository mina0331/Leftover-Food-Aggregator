<!-- b9440739-bd35-4af0-b607-6ae6d208fad6 1e9de6f4-c950-4fba-adf0-272bba045bd8 -->
# User Suspension and Reinstatement Feature

## Overview

Allow moderators to suspend users for repeated violations and reinstate them. Suspended users are blocked from accessing platform features. Suspensions are tracked with reasons and linked to violations.

## Implementation Steps

### 1. Create UserSuspension Model

**New File:** `moderation/models.py` (add to existing file)

- Fields: `user` (ForeignKey to User), `suspended_by` (ForeignKey to User), `reason` (TextField), `suspended_at` (DateTimeField), `reinstated_at` (DateTimeField, nullable), `reinstated_by` (ForeignKey, nullable), `reinstatement_notes` (TextField, blank)
- Methods: `is_active()` returns True if not reinstated, `reinstate(moderator, notes)` method
- Meta: ordering by `-suspended_at`, indexes on user and suspended_at

### 2. Add Suspension Status Helper

**File:** `userprivileges/roles.py` (or create if doesn't exist)

- Add `is_suspended(user)` function that checks if user has active suspension
- Add `get_active_suspension(user)` function to get current suspension record

### 3. Create Suspension Views

**File:** `moderation/views.py`

- Add `suspend_user(request, user_id)` view:
- Check moderator permissions
- Get user to suspend
- Handle GET (show form) and POST (create suspension)
- Set user.is_active = False
- Create UserSuspension record
- Optionally link to flagged content violations
- Add `reinstate_user(request, suspension_id)` view:
- Check moderator permissions
- Get suspension record
- Set user.is_active = True
- Update suspension with reinstatement info
- Add `user_management(request)` view:
- List all users with suspension status
- Show violation counts per user
- Allow quick suspend/reinstate actions

### 4. Create Suspension Forms

**File:** `moderation/forms.py` (add to existing)

- Add `SuspendUserForm` with reason field (Textarea) and optional link to flag IDs
- Add `ReinstateUserForm` with notes field

### 5. Create Suspension Templates

**New File:** `moderation/templates/moderation/suspend_user.html`

- Form to suspend user with reason field
- Show user info and violation history
- Link to related flagged content

**New File:** `moderation/templates/moderation/user_management.html`

- Table/list of users with suspension status
- Show violation counts (deleted/edited flags)
- Quick action buttons (Suspend/Reinstate)
- Search and filter functionality

### 6. Add Suspension Middleware/Decorator

**New File:** `moderation/middleware.py` (optional, or add to views)

- Create `check_suspension` decorator that:
- Checks if user is suspended
- Redirects to suspension notice page if suspended
- Allows moderators/staff to bypass
- Apply to key views (chat, posting, profile editing)

### 7. Create Suspension Notice Page

**New File:** `moderation/templates/moderation/suspended.html`

- Inform user they are suspended
- Show suspension reason and date
- Contact information for appeals

### 8. Update Moderator Dashboard

**File:** `userprivileges/templates/userprivileges/moderator_home.html`

- Add "User Management" section with link to user management page
- Show suspended user count
- Quick access to suspend/reinstate

### 9. Add URL Routes

**File:** `moderation/urls.py`

- Add `path('users/', views.user_management, name='user_management')`
- Add `path('suspend/<int:user_id>/', views.suspend_user, name='suspend_user')`
- Add `path('reinstate/<int:suspension_id>/', views.reinstate_user, name='reinstate_user')`
- Add `path('suspended/', views.suspended_notice, name='suspended_notice')` (for suspended users)

### 10. Update Admin Interface

**File:** `moderation/admin.py`

- Register `UserSuspension` model
- Add filters for active suspensions, suspended users
- Add search by user, reason

### 11. Add Suspension Checks to Views

**Files:** `chat/views.py`, `posting/views.py`, `profiles/views.py`

- Add `@check_suspension` decorator or inline checks to key views
- Prevent suspended users from creating content, sending messages, etc.

### 12. Link Suspensions to Violations

**File:** `moderation/views.py`

- In `suspend_user`, optionally count violations (deleted/edited flags)
- Show violation history when suspending
- Store violation summary in suspension reason

## Key Implementation Details

- **Suspension Method:** Use Django's `user.is_active = False` to block login, plus custom checks for already-logged-in users
- **Violation Tracking:** Count flags where status is DELETED or EDITED to identify repeat offenders
- **Permission Checks:** All suspension views must verify moderator/staff/superuser status
- **Audit Trail:** UserSuspension model provides complete history of suspensions/reinstatements
- **User Experience:** Suspended users see clear message explaining why and how to appeal
- **Moderator Workflow:** Easy access from user management page, can see violation history before suspending

## Files to Modify

1. `moderation/models.py` - Add UserSuspension model
2. `moderation/views.py` - Add suspension/reinstatement views
3. `moderation/forms.py` - Add suspension forms
4. `moderation/urls.py` - Add suspension routes
5. `moderation/admin.py` - Register UserSuspension
6. `userprivileges/templates/userprivileges/moderator_home.html` - Add user management link
7. `userprivileges/roles.py` - Add suspension helper functions
8. `chat/views.py`, `posting/views.py`, `profiles/views.py` - Add suspension checks

## Files to Create

1. `moderation/templates/moderation/suspend_user.html` - Suspend form
2. `moderation/templates/moderation/user_management.html` - User list with suspension status
3. `moderation/templates/moderation/suspended.html` - Suspension notice page
4. `moderation/middleware.py` - Suspension check decorator (optional)

## Database Changes

- New `moderation_usersuspension` table with user, suspension details, reinstatement info

### To-dos

- [ ] Update FlaggedContent model: Add EDITED status and edit_content() method
- [ ] Create moderation/forms.py with ModeratorPostEditForm and ModeratorMessageEditForm
- [ ] Add edit_flagged_content() view in moderation/views.py
- [ ] Create edit_content.html template for moderator content editing
- [ ] Update review_flagged.html: Add Edit button and EDITED status stats
- [ ] Add edit URL route in moderation/urls.py
- [ ] Update moderation/admin.py to include EDITED in filters