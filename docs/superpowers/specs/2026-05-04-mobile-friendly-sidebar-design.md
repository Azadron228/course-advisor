# Design Spec: Mobile-Friendly Unified Navigation

## Problem Statement
The current sidebar implementation has two major issues:
1. **Overlap on Mobile:** The student `Sidebar` is `fixed` but not hidden on mobile, causing it to overlap content.
2. **Missing Admin Mobile Nav:** The `AdminSidebar` is hidden on mobile, leaving admin users with no navigation.
3. **Code Duplication:** Navigation items and logic are duplicated between `Sidebar`, `AdminSidebar`, and `MobileDrawer`.

## Goals
- Fix sidebar overlapping on mobile.
- Provide full navigation support for Admins on mobile.
- Unify navigation logic and styling into a single source of truth.
- Ensure consistent "Active Link" behavior across all navigation components.

## Proposed Changes

### 1. Navigation Configuration (`frontend/src/lib/navigation.ts`)
Extract navigation item definitions into a shared configuration file.

```typescript
export interface NavItem {
  nameKey?: string; // For i18n
  name?: string;     // Literal name (for admin)
  href: string;
  icon: any;
}

export const STUDENT_NAV_ITEMS: NavItem[] = [
  { nameKey: 'dashboard', href: '/dashboard', icon: LayoutDashboard },
  { nameKey: 'learningPlan', href: '/plan', icon: BookOpen },
  { nameKey: 'aiAdvisor', href: '/chat', icon: MessageSquare },
];

export const ADMIN_NAV_ITEMS: NavItem[] = [
  { name: 'Courses', href: '/admin/courses', icon: BookOpen },
  { name: 'Users', href: '/admin/users', icon: Users },
];
```

### 2. Reusable `NavItems` Component
Create a `NavItems` component that renders a list of `NavItem` objects. This component will handle:
- i18n translation (if `nameKey` is present).
- Active link detection.
- Consistent styling.
- Tooltips for collapsed desktop sidebar.
- Click callbacks (to close the mobile drawer).

### 3. Sidebar Refactoring
- **`Sidebar.tsx`**: Update Tailwind classes to hide on mobile (`hidden lg:flex`) and be static on desktop. Use the new `NavItems` component.
- **`AdminSidebar.tsx`**: Update Tailwind classes to hide on mobile (`hidden lg:flex`) and use the new `NavItems` component.

### 4. Mobile Drawer Enhancement
- **`MobileDrawer.tsx`**: Update to detect if the user is in the admin section and show `ADMIN_NAV_ITEMS` instead of `STUDENT_NAV_ITEMS`.
- Ensure `ChatSidebarHistory` is visible in the drawer when on the chat page, just like in the desktop sidebar.

### 5. Admin Layout Update
- Include `MobileDrawer` in `AdminLayout` to enable mobile navigation for admins.

## Success Criteria
- [ ] Sidebars do not overlap content on screens < 1024px.
- [ ] Admins can navigate via a mobile drawer on small screens.
- [ ] Navigation items are defined in a single location for each role.
- [ ] Chat history is accessible via the mobile drawer when on the chat page.
- [ ] Theme (Light/Dark) and Localization (EN/RU/KK) work correctly in the new navigation components.
