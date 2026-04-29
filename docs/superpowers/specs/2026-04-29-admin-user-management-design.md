# Design Spec: Admin User Management Portal

This document outlines the implementation of a dedicated administrative portal for managing users within the Course Advisor platform, based on the EduPath AI Navigator design system.

## 1. Overview
The Admin Portal provides a secure area for system administrators to manage the user base. The initial release focuses on User Management, providing visibility into the registered users and tools to manage their access and roles.

## 2. Architecture

### Frontend
- **Route Grouping:** All admin features will live under `frontend/src/app/[locale]/admin/`.
- **Layout:** `admin/layout.tsx` will provide the structural shell, including a specialized `AdminSidebar`.
- **State Management:** Uses `use-auth.ts` to verify admin privileges.
- **Data Fetching:** TanStack Query for efficient fetching and mutation of user data.

### Backend
- **Endpoints:** 
    - `GET /api/v1/users/`: List all users (Admin only).
    - `GET /api/v1/users/{user_id}`: Get specific user details.
    - `PUT /api/v1/users/{user_id}`: Update user info/roles.
    - `DELETE /api/v1/users/{user_id}`: Remove a user.
- **Security:** Managed via `get_current_admin_user` dependency in FastAPI.

## 3. Components

### AdminSidebar
- Navigation links for admin sections.
- For Phase 1, it will only contain "Users".
- Distinct styling to differentiate from the student sidebar.

### UserTable
- **Search:** Client-side filtering by name or email.
- **Columns:**
    - User (Avatar + Name + Email)
    - Role (Badge: "Admin" or "Student")
    - Status (Badge: "Active" or "Disabled")
    - Actions (Edit button, Toggle Status button)

### EditUserModal
- A slide-over or center-aligned modal.
- Fields:
    - Full Name (Text)
    - Email (Email, read-only or editable)
    - Password (Optional reset field)
    - Role (Switch: "Is Administrator")
    - Status (Switch: "Account Active")

## 4. User Flow
1. Admin logs in.
2. A "Admin Portal" link appears in the main navigation or user menu.
3. Admin clicks the link and is navigated to `/admin/users`.
4. Admin views the list of all users.
5. Admin clicks "Edit" on a user to modify their role or basic information.
6. Admin can toggle "Active" status directly from the table to quickly disable accounts.

## 5. Security & Access Control
- **Backend Protection:** Every admin endpoint is protected by the `get_current_admin_user` dependency which verifies the `is_admin` flag in the JWT.
- **Frontend Protection:** The `admin/layout.tsx` will redirect to `/dashboard` if the authenticated user's `is_admin` field is false.

## 6. Success Criteria
- Admins can successfully see a list of all registered users.
- Admins can promote a student to an admin role.
- Admins can disable a user account, preventing that user from logging in.
- Non-admin users cannot access the `/admin` routes.
