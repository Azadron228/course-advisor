'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { X, GraduationCap } from 'lucide-react';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  BookOpen, 
  MessageSquare, 
  User
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLayoutStore } from '@/hooks/use-layout-store';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Learning Plan', href: '/plan', icon: BookOpen },
  { name: 'AI Advisor', href: '/chat', icon: MessageSquare },
  { name: 'Profile', href: '/profile', icon: User },
];

export function MobileDrawer() {
  const pathname = usePathname();
  const { isMobileDrawerOpen, setMobileDrawerOpen } = useLayoutStore();

  // Close drawer when route changes
  useEffect(() => {
    setMobileDrawerOpen(false);
  }, [pathname, setMobileDrawerOpen]);

  if (!isMobileDrawerOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] lg:hidden">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"
        onClick={() => setMobileDrawerOpen(false)}
      />
      
      {/* Drawer */}
      <div className="fixed inset-y-0 left-0 w-full max-w-xs bg-surface shadow-2xl animate-in slide-in-from-left duration-300 border-r border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-200 dark:shadow-none">
              <GraduationCap size={20} />
            </div>
            <span className="font-lexend font-bold text-slate-900 dark:text-white">
              EduPath AI
            </span>
          </div>
          <button
            onClick={() => setMobileDrawerOpen(false)}
            className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="px-4 py-6 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-4 px-4 py-3 rounded-xl transition-all",
                  isActive 
                    ? "bg-indigo-600 text-white shadow-lg shadow-indigo-200 dark:shadow-none" 
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white"
                )}
              >
                <Icon size={22} className={cn(isActive ? "text-white" : "text-slate-400 dark:text-slate-500")} />
                <span className="font-semibold">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
