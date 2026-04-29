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
        key={editingUser?.id || 'none'}
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
