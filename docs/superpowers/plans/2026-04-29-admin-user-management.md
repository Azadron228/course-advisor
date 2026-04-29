# Admin User Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a dedicated Admin Portal starting with User Management, allowing admins to view, edit roles, and toggle status of all users.

**Architecture:**
- **Route Group:** `/admin/` for all administrative features.
- **Layout:** Dedicated `AdminLayout` with role-based redirection and an `AdminSidebar`.
- **User Management:** A centralized page with a searchable table and an edit modal.

**Tech Stack:** Next.js (App Router), React Query, Lucide Icons, Tailwind CSS.

---

### Task 1: Update User Interface & Auth Hook

**Files:**
- Modify: `frontend/src/hooks/use-auth.ts`

- [ ] **Step 1: Update `User` interface to match backend**
Update the `User` interface in `use-auth.ts` to include `is_admin` instead of `is_superuser`, and add missing fields.

```typescript
export interface User {
  id: number;
  email: string;
  full_name?: string;
  career_goal?: string;
  interests?: string[];
  onboarding_completed?: boolean;
  is_active: boolean;
  is_admin: boolean;
  disabled?: boolean;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/use-auth.ts
git commit -m "refactor: update User interface to match backend schema"
```

### Task 2: Create Admin Sidebar Component

**Files:**
- Create: `frontend/src/components/admin/admin-sidebar.tsx`

- [ ] **Step 1: Implement `AdminSidebar`**
Create a sidebar specifically for the admin portal.

```tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Users, LayoutDashboard, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Dashboard', href: '/admin', icon: LayoutDashboard },
  { name: 'Users', href: '/admin/users', icon: Users },
  { name: 'Settings', href: '/admin/settings', icon: Settings },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r border-slate-200 h-full hidden md:flex flex-col">
      <div className="p-6">
        <h2 className="text-xl font-bold text-primary font-lexend">Admin Portal</h2>
      </div>
      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.includes(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors",
                isActive 
                  ? "bg-primary/10 text-primary" 
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/admin/admin-sidebar.tsx
git commit -m "feat: add AdminSidebar component"
```

### Task 3: Implement Admin Layout

**Files:**
- Create: `frontend/src/app/[locale]/admin/layout.tsx`

- [ ] **Step 1: Implement `AdminLayout` with access control**
Create the layout for the admin route group. It should check if the user is an admin and redirect if not.

```tsx
'use client';

import { useAuth } from '@/hooks/use-auth';
import { useRouter } from '@/i18n/routing';
import { useEffect } from 'react';
import { AdminSidebar } from '@/components/admin/admin-sidebar';
import { Loader2 } from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push('/login');
      } else if (!user?.is_admin) {
        router.push('/dashboard');
      }
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading || !user?.is_admin) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-slate-50">
      <AdminSidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/admin/layout.tsx
git commit -m "feat: add AdminLayout with access control"
```

### Task 4: User Data Hook

**Files:**
- Create: `frontend/src/hooks/use-users.ts`

- [ ] **Step 1: Implement `useUsers` hook**
Create a hook for fetching and managing users using React Query.

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { User } from './use-auth';

export function useUsers() {
  const queryClient = useQueryClient();

  const usersQuery = useQuery({
    queryKey: ['users'],
    queryFn: () => apiClient.get<User[]>('/users/'),
  });

  const updateUserMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<User> }) =>
      apiClient.put<User>(`/users/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/users/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  return {
    users: usersQuery.data || [],
    isLoading: usersQuery.isLoading,
    error: usersQuery.error,
    updateUser: updateUserMutation.mutateAsync,
    deleteUser: deleteUserMutation.mutateAsync,
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/use-users.ts
git commit -m "feat: add useUsers hook for admin data fetching"
```

### Task 5: User Table Component

**Files:**
- Create: `frontend/src/components/admin/user-table.tsx`

- [ ] **Step 1: Implement `UserTable`**
Create a table component to display and manage users.

```tsx
'use client';

import { useState } from 'react';
import { User } from '@/hooks/use-auth';
import { Edit2, Trash2, Shield, User as UserIcon } from 'lucide-react';

interface UserTableProps {
  users: User[];
  onEdit: (user: User) => void;
  onDelete: (id: number) => void;
}

export function UserTable({ users, onEdit, onDelete }: UserTableProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredUsers = users.filter(user => 
    user.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="p-4 border-b border-slate-200">
        <input
          type="text"
          placeholder="Search users..."
          className="w-full max-w-sm px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
            <tr>
              <th className="px-6 py-4">User</th>
              <th className="px-6 py-4">Role</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredUsers.map((user) => (
              <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                      {user.full_name?.[0] || user.email[0].toUpperCase()}
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-slate-900">{user.full_name || 'No Name'}</div>
                      <div className="text-sm text-slate-500">{user.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    user.is_admin ? 'bg-indigo-100 text-indigo-800' : 'bg-slate-100 text-slate-800'
                  }`}>
                    {user.is_admin ? <Shield className="w-3 h-3 mr-1" /> : <UserIcon className="w-3 h-3 mr-1" />}
                    {user.is_admin ? 'Admin' : 'Student'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    !user.disabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {!user.disabled ? 'Active' : 'Disabled'}
                  </span>
                </td>
                <td className="px-6 py-4 text-right space-x-2">
                  <button 
                    onClick={() => onEdit(user)}
                    className="p-2 text-slate-400 hover:text-primary transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => {
                      if (confirm('Are you sure you want to delete this user?')) {
                        onDelete(user.id);
                      }
                    }}
                    className="p-2 text-slate-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/admin/user-table.tsx
git commit -m "feat: add UserTable component"
```

### Task 6: Edit User Modal Component

**Files:**
- Create: `frontend/src/components/admin/edit-user-modal.tsx`

- [ ] **Step 1: Implement `EditUserModal`**
Create a modal to edit user details.

```tsx
'use client';

import { useState, useEffect } from 'react';
import { User } from '@/hooks/use-auth';
import { X } from 'lucide-react';

interface EditUserModalProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: number, data: Partial<User>) => Promise<void>;
}

export function EditUserModal({ user, isOpen, onClose, onSave }: EditUserModalProps) {
  const [formData, setFormData] = useState<Partial<User>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name,
        email: user.email,
        is_admin: user.is_admin,
        disabled: user.disabled,
      });
    }
  }, [user]);

  if (!isOpen || !user) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSave(user.id, formData);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="flex items-center justify-between p-6 border-b border-slate-100">
          <h3 className="text-xl font-bold text-slate-900 font-lexend">Edit User</h3>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              value={formData.full_name || ''}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-500 cursor-not-allowed outline-none"
              value={formData.email || ''}
              disabled
            />
          </div>
          <div className="flex items-center justify-between py-2">
            <div>
              <div className="text-sm font-medium text-slate-900">Administrator</div>
              <div className="text-xs text-slate-500">Grant admin privileges</div>
            </div>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, is_admin: !formData.is_admin })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                formData.is_admin ? 'bg-primary' : 'bg-slate-200'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                formData.is_admin ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>
          <div className="flex items-center justify-between py-2 border-t border-slate-100 pt-4">
            <div>
              <div className="text-sm font-medium text-slate-900">Disabled</div>
              <div className="text-xs text-slate-500">Disable user account</div>
            </div>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, disabled: !formData.disabled })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                formData.disabled ? 'bg-red-500' : 'bg-slate-200'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                formData.disabled ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>
          <div className="pt-6">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-primary hover:bg-primary-dark text-white font-semibold py-3 rounded-xl shadow-lg shadow-primary/20 transition-all disabled:opacity-50 flex items-center justify-center"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/admin/edit-user-modal.tsx
git commit -m "feat: add EditUserModal component"
```

### Task 7: Implement Admin Users Page

**Files:**
- Create: `frontend/src/app/[locale]/admin/users/page.tsx`

- [ ] **Step 1: Implement Admin Users Page**
Create the page that brings together the table and modal.

```tsx
'use client';

import { useState } from 'react';
import { UserTable } from '@/components/admin/user-table';
import { EditUserModal } from '@/components/admin/edit-user-modal';
import { useUsers } from '@/hooks/use-users';
import { User } from '@/hooks/use-auth';
import { Users as UsersIcon, Loader2 } from 'lucide-react';

export default function AdminUsersPage() {
  const { users, isLoading, updateUser, deleteUser } = useUsers();
  const [editingUser, setEditingUser] = useState<User | null>(null);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 font-lexend flex items-center">
            <UsersIcon className="mr-3 h-8 w-8 text-primary" />
            User Management
          </h1>
          <p className="text-slate-500 mt-1">Manage system users, roles, and permissions.</p>
        </div>
        <div className="text-sm text-slate-500 font-medium bg-white px-4 py-2 rounded-lg border border-slate-200">
          Total Users: {users.length}
        </div>
      </div>

      <UserTable 
        users={users} 
        onEdit={setEditingUser} 
        onDelete={deleteUser} 
      />

      <EditUserModal 
        user={editingUser}
        isOpen={!!editingUser}
        onClose={() => setEditingUser(null)}
        onSave={async (id, data) => {
          await updateUser({ id, data });
        }}
      />
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/admin/users/page.tsx
git commit -m "feat: add admin users management page"
```

### Task 8: Add Admin Link to Navigation

**Files:**
- Modify: `frontend/src/components/shared/top-nav.tsx`

- [ ] **Step 1: Add Admin Portal link to `TopNav`**
Add a conditional link to the Admin Portal for admin users.

```tsx
// Inside TopNav component, near user profile or navigation links
{user?.is_admin && (
  <Link
    href="/admin/users"
    className="text-sm font-medium text-slate-600 hover:text-primary transition-colors flex items-center"
  >
    <Shield className="w-4 h-4 mr-1" />
    Admin Portal
  </Link>
)}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/shared/top-nav.tsx
git commit -m "feat: add Admin Portal link to TopNav for admins"
```
