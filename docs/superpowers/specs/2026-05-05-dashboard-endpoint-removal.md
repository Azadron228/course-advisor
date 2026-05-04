# Design Spec: Dashboard Endpoint Removal

This document outlines the removal of the dedicated dashboard API endpoint and the refactoring of the frontend to use existing services for dashboard data.

## 1. Objectives
- Eliminate the redundant `GET /api/v1/dashboard` endpoint.
- Refactor the frontend Dashboard page to fetch data from `/users/me` and `/learning-plan/`.
- Maintain the current Dashboard UI and user experience.

## 2. Backend Changes

### 2.1 File Removals
- `backend/app/api/v1/endpoints/dashboard.py`: Delete the entire file.
- `backend/app/api/v1/schemas/dashboard.py`: Delete the entire file.

### 2.2 Router Update
- `backend/app/api/router.py`: Remove the `dashboard` import and the `api_router.include_router(dashboard.router, ...)` call.

## 3. Frontend Changes

### 3.1 `DashboardPage` Refactor (`frontend/src/app/[locale]/dashboard/page.tsx`)
The `getDashboardData` function will be updated to:
1. Fetch `GET /api/v1/users/me` for user profile (full name, onboarding status).
2. Fetch `GET /api/v1/learning-plan/` for the list of learning plans.
3. Identify the active plan (`is_active: true`).
4. Return an object compatible with the existing `DashboardResponse` interface:
   ```typescript
   {
     active_plan_title: string | null;
     progress_percentage: number;
     welcome_message: string;
     onboarding_completed: boolean;
   }
   ```

### 3.2 Data Mapping
- `active_plan_title`: From the first plan in `/learning-plan/` where `is_active === true`.
- `progress_percentage`: Set to 0 (preserving existing mocked behavior).
- `welcome_message`: `Welcome back, {user.full_name || 'Student'}!`
- `onboarding_completed`: From `user.onboarding_completed`.

## 4. Verification Plan

### 4.1 Backend
- Ensure the server starts without errors after removing the router inclusion.
- Verify `GET /api/v1/dashboard/` returns 404.

### 4.2 Frontend
- Navigate to `/dashboard` and verify:
    - Welcome message correctly displays the user's name.
    - Active plan title matches the one marked active in the plan list.
    - Navigation cards still function correctly.
- Verify no console errors during data fetching.
