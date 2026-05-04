'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { 
  ChevronLeft,
  ChevronRight,
  GraduationCap
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLayoutStore } from '@/hooks/use-layout-store';
import { ChatSidebarHistory } from '../features/chat-sidebar-history';
import { NavItems } from './nav-items';
import { STUDENT_NAV_ITEMS } from '@/lib/navigation';

export function Sidebar() {
  const tCommon = useTranslations('Common');
  const pathname = usePathname();
  const { isCollapsed, toggleSidebar } = useLayoutStore();

  const isChatPage = pathname.includes('/chat');

  return (
    <aside
      className={cn(
        "hidden lg:flex lg:flex-col bg-surface border-r border-border transition-all duration-300 ease-in-out lg:static lg:inset-y-0",
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

      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <div className="px-3 py-4">
          <NavItems items={STUDENT_NAV_ITEMS} isCollapsed={isCollapsed} />
        </div>

        {isChatPage && !isCollapsed && (
          <div className="flex-1 flex flex-col min-h-0 border-t border-border pt-4 overflow-hidden">
            <ChatSidebarHistory isCollapsed={isCollapsed} />
          </div>
        )}
      </div>
    </aside>
  );
}
