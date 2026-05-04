# Mobile-Friendly Unified Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix sidebar overlapping on mobile and enable mobile navigation for admins by unifying navigation logic.

**Architecture:** Extract navigation configuration into a central file and create a reusable `NavItems` component for both desktop sidebars and the mobile drawer.

**Tech Stack:** React, Next.js, Tailwind CSS, Lucide React, next-intl.

---

### Task 1: Create Central Navigation Configuration

**Files:**
- Create: `frontend/src/lib/navigation.ts`

- [ ] **Step 1: Define navigation items and interfaces**

```typescript
import { 
  LayoutDashboard, 
  BookOpen, 
  MessageSquare,
  Users
} from 'lucide-react';

export interface NavItem {
  nameKey?: string;
  name?: string;
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

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/lib/navigation.ts
git commit -m "feat: add central navigation configuration"
```

---

### Task 2: Create Reusable NavItems Component

**Files:**
- Create: `frontend/src/components/shared/nav-items.tsx`

- [ ] **Step 1: Implement NavItems component**

```tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { cn } from '@/lib/utils';
import { NavItem } from '@/lib/navigation';

interface NavItemsProps {
  items: NavItem[];
  isCollapsed?: boolean;
  onItemClick?: () => void;
  translationNamespace?: string;
}

export function NavItems({ items, isCollapsed, onItemClick, translationNamespace = 'Navigation' }: NavItemsProps) {
  const t = useTranslations(translationNamespace);
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {items.map((item) => {
        const isActive = pathname.includes(item.href);
        const Icon = item.icon;
        const label = item.nameKey ? t(item.nameKey) : item.name;

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onItemClick}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all group relative",
              isActive 
                ? "bg-primary/10 text-primary" 
                : "text-muted hover:bg-muted/10 hover:text-foreground"
            )}
          >
            <Icon 
              size={20} 
              className={cn(
                "flex-shrink-0 transition-colors",
                isActive ? "text-primary" : "text-muted group-hover:text-foreground"
              )} 
            />
            {!isCollapsed && (
              <span className="text-sm font-semibold whitespace-nowrap">
                {label}
              </span>
            )}
            {isCollapsed && (
              <div className="absolute left-full ml-2 px-2 py-1 bg-surface text-foreground text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 shadow-lg border border-border">
                {label}
              </div>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
```

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/components/shared/nav-items.tsx
git commit -m "feat: add reusable NavItems component"
```

---

### Task 3: Refactor Student Sidebar

**Files:**
- Modify: `frontend/src/components/shared/sidebar.tsx`

- [ ] **Step 1: Update sidebar to use NavItems and fix mobile visibility**

```tsx
// Change the container classes and use NavItems
// Remove navItems definition from Sidebar component
// Import NavItems from './nav-items'
// Import STUDENT_NAV_ITEMS from '@/lib/navigation'

// In the JSX:
<aside
  className={cn(
    "hidden lg:flex lg:flex-col bg-surface border-r border-border transition-all duration-300 ease-in-out lg:static lg:inset-y-0",
    isCollapsed ? "w-20" : "w-64"
  )}
>
  {/* ... header ... */}
  <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
    <div className="px-3 py-4">
      <NavItems items={STUDENT_NAV_ITEMS} isCollapsed={isCollapsed} />
    </div>
    {/* ... chat history ... */}
  </div>
</aside>
```

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/components/shared/sidebar.tsx
git commit -m "refactor: use unified NavItems in Student Sidebar and fix mobile overlap"
```

---

### Task 4: Refactor Admin Sidebar

**Files:**
- Modify: `frontend/src/components/admin/admin-sidebar.tsx`

- [ ] **Step 1: Update AdminSidebar to use NavItems and hide on mobile**

```tsx
// Update to hidden lg:flex
// Use NavItems with ADMIN_NAV_ITEMS
// Remove local navItems definition

import { NavItems } from '../shared/nav-items';
import { ADMIN_NAV_ITEMS } from '@/lib/navigation';

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex lg:flex-col w-64 bg-surface border-r border-border h-full">
      <div className="p-6 border-b border-border h-16 flex items-center">
        <h2 className="text-xl font-bold text-primary font-lexend">Admin Portal</h2>
      </div>
      <div className="flex-1 px-4 py-6">
        <NavItems items={ADMIN_NAV_ITEMS} />
      </div>
    </aside>
  );
}
```

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/components/admin/admin-sidebar.tsx
git commit -m "refactor: use unified NavItems in Admin Sidebar and fix mobile visibility"
```

---

### Task 5: Enhance Mobile Drawer for Admin and Chat History

**Files:**
- Modify: `frontend/src/components/shared/mobile-drawer.tsx`

- [ ] **Step 1: Support Admin nav and Chat history in MobileDrawer**

```tsx
import { STUDENT_NAV_ITEMS, ADMIN_NAV_ITEMS } from '@/lib/navigation';
import { NavItems } from './nav-items';
import { ChatSidebarHistory } from '../features/chat-sidebar-history';

export function MobileDrawer() {
  // ... existing hooks ...
  const isAdmin = pathname.includes('/admin');
  const isChatPage = pathname.includes('/chat');
  
  return (
    // ... Backdrop ...
    <div className="fixed inset-y-0 left-0 w-full max-w-xs bg-surface shadow-2xl animate-in slide-in-from-left duration-300 border-r border-border flex flex-col">
      {/* ... Header ... */}
      
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <NavItems 
          items={isAdmin ? ADMIN_NAV_ITEMS : STUDENT_NAV_ITEMS} 
          onItemClick={() => setMobileDrawerOpen(false)}
        />
        
        {isChatPage && (
          <div className="mt-8 pt-8 border-t border-border">
            <h3 className="px-4 text-xs font-semibold text-muted uppercase tracking-wider mb-4">
              Chat History
            </h3>
            <ChatSidebarHistory isCollapsed={false} />
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/components/shared/mobile-drawer.tsx
git commit -m "feat: enhance MobileDrawer with Admin support and Chat history"
```

---

### Task 6: Enable Mobile Navigation in Admin Layout

**Files:**
- Modify: `frontend/src/app/[locale]/admin/layout.tsx`

- [ ] **Step 1: Add MobileDrawer to AdminLayout**

```tsx
import { MobileDrawer } from '@/components/shared/mobile-drawer';

// ... in return ...
<div className="flex h-screen bg-background">
  <AdminSidebar />
  <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
    <TopNav />
    <main className="flex-1 overflow-y-auto p-8">
      {/* ... */}
    </main>
  </div>
  <MobileDrawer />
</div>
```

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/app/[locale]/admin/layout.tsx
git commit -m "feat: enable mobile navigation in Admin Portal"
```
