'use client';

import { useState, useRef, useEffect } from 'react';
import { usePathname, useRouter } from '@/i18n/routing';
import { useLocale, useTranslations } from 'next-intl';
import { 
  Menu, 
  Bell, 
  Search, 
  LogOut, 
  User as UserIcon, 
  Settings,
  ChevronDown,
  Globe,
  Shield
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/use-auth';
import { useLayoutStore } from '@/hooks/use-layout-store';
import { ThemeToggle } from './theme-toggle';
import { LanguageSwitcher } from './language-switcher';

export function TopNav() {
  const t = useTranslations('Common');
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  
  const { user, logout, isAuthenticated } = useAuth();
  const { toggleMobileDrawer } = useLayoutStore();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const toggleLanguage = () => {
    const nextLocale = locale === 'en' ? 'ru' : 'en';
    router.replace(pathname, { locale: nextLocale });
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-40 flex items-center justify-between h-16 px-4 bg-surface/80 backdrop-blur-md border-b border-border lg:px-6">
      <div className="flex items-center gap-4">
        {isAuthenticated && (
          <button
            onClick={toggleMobileDrawer}
            className="lg:hidden p-2 rounded-lg text-muted hover:bg-muted/10 transition-colors"
          >
            <Menu size={20} />
          </button>
        )}
        <h1 className="text-lg font-lexend font-semibold text-foreground lg:text-xl">
          {t('title')}
        </h1>
      </div>

      <div className="flex items-center gap-2 lg:gap-4">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Language Switcher */}
        <LanguageSwitcher />

        {isAuthenticated && (
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className="flex items-center gap-2 p-1 rounded-lg hover:bg-muted/10 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </div>
              <div className="hidden lg:block text-left">
                <p className="text-sm font-medium text-foreground leading-none">
                  {user?.full_name || 'User'}
                </p>
              </div>
              <ChevronDown size={16} className={cn("text-muted transition-transform", isProfileOpen && "rotate-180")} />
            </button>

            {isProfileOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-surface border border-border rounded-xl shadow-lg py-1 z-50 animate-in fade-in zoom-in duration-200">
                <div className="px-4 py-2 border-b border-border">
                  <p className="text-sm font-medium text-foreground truncate">{user?.full_name || 'User'}</p>
                  <p className="text-xs text-muted truncate">{user?.email}</p>
                </div>
                <div className="p-1">
                  {user?.is_admin && (
                    <button 
                      onClick={() => {
                        setIsProfileOpen(false);
                        router.push('/admin/users');
                      }}
                      className="flex w-full items-center gap-3 px-3 py-2 text-sm text-primary font-medium rounded-lg hover:bg-primary/10 transition-colors"
                    >
                      <Shield size={18} />
                      {t('adminPortal')}
                    </button>
                  )}
                  <button className="flex w-full items-center gap-3 px-3 py-2 text-sm text-muted rounded-lg hover:bg-muted/10 hover:text-foreground transition-colors">
                    <UserIcon size={18} />
                    {t('profile')}
                  </button>
                  <button className="flex w-full items-center gap-3 px-3 py-2 text-sm text-muted rounded-lg hover:bg-muted/10 hover:text-foreground transition-colors">
                    <Settings size={18} />
                    {t('settings')}
                  </button>
                </div>
                <div className="p-1 border-t border-border">
                  <button
                    onClick={() => logout()}
                    className="flex w-full items-center gap-3 px-3 py-2 text-sm text-rose-600 dark:text-rose-400 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-colors"
                  >
                    <LogOut size={18} />
                    {t('logout')}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
