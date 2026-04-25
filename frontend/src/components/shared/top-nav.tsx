'use client';

import { useState, useRef, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { 
  Menu, 
  Bell, 
  Search, 
  LogOut, 
  User as UserIcon, 
  Settings,
  ChevronDown
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/use-auth';
import { useLayoutStore } from '@/hooks/use-layout-store';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/plan': 'Learning Plan',
  '/map': 'Learning Roadmap',
  '/chat': 'AI Advisor',
  '/profile': 'My Profile',
};

export function TopNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { toggleMobileDrawer } = useLayoutStore();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const title = pageTitles[pathname] || 'EduPath AI';

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
    <header className="sticky top-0 z-40 flex items-center justify-between h-16 px-4 bg-white/80 backdrop-blur-md border-b border-slate-200 lg:px-6">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleMobileDrawer}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100"
        >
          <Menu size={20} />
        </button>
        <h1 className="text-lg font-lexend font-semibold text-slate-900 lg:text-xl">
          {title}
        </h1>
      </div>

      <div className="flex items-center gap-2 lg:gap-4">
        <div className="hidden md:flex relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search courses, skills..."
            className="w-64 pl-10 pr-4 py-2 bg-slate-100 border-transparent rounded-lg text-sm focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
          />
        </div>

        <button className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 relative">
          <Bell size={20} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
        </button>

        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className="flex items-center gap-2 p-1 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-xs">
              {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-sm font-medium text-slate-900 leading-none">
                {user?.full_name || 'User'}
              </p>
            </div>
            <ChevronDown size={16} className={cn("text-slate-400 transition-transform", isProfileOpen && "rotate-180")} />
          </button>

          {isProfileOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-lg py-1 z-50 animate-in fade-in zoom-in duration-200">
              <div className="px-4 py-2 border-b border-slate-100">
                <p className="text-sm font-medium text-slate-900 truncate">{user?.full_name || 'User'}</p>
                <p className="text-xs text-slate-500 truncate">{user?.email}</p>
              </div>
              <div className="p-1">
                <button className="flex w-full items-center gap-3 px-3 py-2 text-sm text-slate-600 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors">
                  <UserIcon size={18} />
                  My Profile
                </button>
                <button className="flex w-full items-center gap-3 px-3 py-2 text-sm text-slate-600 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors">
                  <Settings size={18} />
                  Settings
                </button>
              </div>
              <div className="p-1 border-t border-slate-100">
                <button
                  onClick={() => logout()}
                  className="flex w-full items-center gap-3 px-3 py-2 text-sm text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
                >
                  <LogOut size={18} />
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
