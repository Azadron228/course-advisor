'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { 
  LayoutDashboard, 
  BookOpen, 
  MessageSquare, 
  User,
  ChevronLeft,
  ChevronRight,
  GraduationCap
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLayoutStore } from '@/hooks/use-layout-store';

export function Sidebar() {
  const t = useTranslations('Navigation');
  const tCommon = useTranslations('Common');
  const pathname = usePathname();
  const { isCollapsed, toggleSidebar } = useLayoutStore();

  const navItems = [
    { name: t('dashboard'), href: '/dashboard', icon: LayoutDashboard },
    { name: t('learningPlan'), href: '/plan', icon: BookOpen },
    { name: t('aiAdvisor'), href: '/chat', icon: MessageSquare },
  ];

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex flex-col bg-surface border-r border-border transition-all duration-300 ease-in-out lg:static",
        isCollapsed ? "w-20" : "w-64"
      )}
    >
      <div className="flex items-center justify-between h-16 px-4 border-b border-border">
        <Link href="/dashboard" className="flex items-center gap-3 overflow-hidden">
          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/20 dark:shadow-none">
            <GraduationCap size={20} />
          </div>
          {!isCollapsed && (
            <span className="font-lexend font-bold text-foreground truncate">
              {tCommon('title')}
            </span>
          )}
        </Link>
        <button
          onClick={toggleSidebar}
          className="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg text-muted hover:bg-muted/10 transition-colors"
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
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
                  {item.name}
                </span>
              )}
              {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-surface text-foreground text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 shadow-lg border border-border">
                  {item.name}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

    </aside>
  );
}
