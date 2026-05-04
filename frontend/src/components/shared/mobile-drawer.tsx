'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { X, GraduationCap } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useLayoutStore } from '@/hooks/use-layout-store';
import { STUDENT_NAV_ITEMS, ADMIN_NAV_ITEMS } from '@/lib/navigation';
import { NavItems } from './nav-items';
import { ChatSidebarHistory } from '../features/chat-sidebar-history';

export function MobileDrawer() {
  const tCommon = useTranslations('Common');
  const tNav = useTranslations('Navigation');
  const pathname = usePathname();
  const { isMobileDrawerOpen, setMobileDrawerOpen } = useLayoutStore();

  const isAdmin = pathname.includes('/admin');
  const isChatPage = pathname.includes('/chat');

  // Close drawer when route changes
  useEffect(() => {
    setMobileDrawerOpen(false);
  }, [pathname, setMobileDrawerOpen]);

  if (!isMobileDrawerOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] lg:hidden">
      {/* Backdrop */}
      <button 
        type="button"
        className="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity w-full h-full border-none cursor-default"
        onClick={() => setMobileDrawerOpen(false)}
        aria-label="Close drawer"
      />
      
      {/* Drawer container */}
      <div 
        role="dialog"
        aria-modal="true"
        aria-label={tCommon('title')}
        className="fixed inset-y-0 left-0 w-full max-w-xs bg-surface shadow-2xl animate-in slide-in-from-left duration-300 border-r border-border flex flex-col"
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-border flex-shrink-0">
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
            className="p-2 rounded-lg text-muted hover:bg-input transition-colors"
            aria-label="Close drawer"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6">
          <NavItems 
            items={isAdmin ? ADMIN_NAV_ITEMS : STUDENT_NAV_ITEMS} 
            onItemClick={() => setMobileDrawerOpen(false)}
          />
          
          {isChatPage && (
            <div className="mt-8 pt-8 border-t border-border">
              <h3 className="px-4 text-xs font-semibold text-muted uppercase tracking-wider mb-4">
                {tNav('chatHistory')}
              </h3>
              <ChatSidebarHistory isCollapsed={false} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
