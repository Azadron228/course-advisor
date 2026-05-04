'use client';

import { NavItems } from '../shared/nav-items';
import { ADMIN_NAV_ITEMS } from '@/lib/navigation';

export function AdminSidebar() {
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
