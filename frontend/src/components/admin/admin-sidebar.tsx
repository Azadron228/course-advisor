'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Users, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Courses', href: '/admin/courses', icon: BookOpen },
  { name: 'Users', href: '/admin/users', icon: Users },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-surface border-r border-border h-full hidden md:flex flex-col">
      <div className="p-6 border-b border-border h-16 flex items-center">
        <h2 className="text-xl font-bold text-primary font-lexend">Admin Portal</h2>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.includes(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all",
                isActive 
                  ? "bg-primary/10 text-primary shadow-sm" 
                  : "text-muted hover:bg-input hover:text-foreground"
              )}
            >
              <item.icon className={cn(
                "mr-3 h-5 w-5 transition-colors",
                isActive ? "text-primary" : "text-muted"
              )} />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

