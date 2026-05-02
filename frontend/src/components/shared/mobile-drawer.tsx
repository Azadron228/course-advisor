'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { X, GraduationCap } from 'lucide-react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { 
  LayoutDashboard, 
  BookOpen, 
  MessageSquare, 
  User
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLayoutStore } from '@/hooks/use-layout-store';

export function MobileDrawer() {
  const t = useTranslations('Navigation');
  const tCommon = useTranslations('Common');
  const pathname = usePathname();
  const { isMobileDrawerOpen, setMobileDrawerOpen } = useLayoutStore();

  const navItems = [
    { name: t('dashboard'), href: '/dashboard', icon: LayoutDashboard },
    { name: t('learningPlan'), href: '/plan', icon: BookOpen },
    { name: t('aiAdvisor'), href: '/chat', icon: MessageSquare },
    { name: t('profile'), href: '/profile', icon: User },
  ];

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
      <div className="fixed inset-y-0 left-0 w-full max-w-xs bg-surface shadow-2xl animate-in slide-in-from-left duration-300 border-r border-border">
        <div className="flex items-center justify-between h-16 px-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/20 dark:shadow-none">
              <GraduationCap size={20} />
            </div>
            <span className="font-lexend font-bold text-foreground">
              {tCommon('title')}
            </span>
          </div>
          <button
            onClick={() => setMobileDrawerOpen(false)}
            className="p-2 rounded-lg text-muted hover:bg-muted/10 transition-colors"
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
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-4 px-4 py-3 rounded-xl transition-all group",
                  isActive 
                    ? "bg-primary/10 text-primary" 
                    : "text-muted hover:bg-muted/10 hover:text-foreground"
                )}
              >
                <Icon 
                  size={22} 
                  className={cn(
                    "transition-colors",
                    isActive ? "text-primary" : "text-muted group-hover:text-foreground"
                  )} 
                />
                <span className="font-semibold">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
