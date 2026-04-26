'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  BookOpen, 
  Map, 
  MessageSquare, 
  User,
  ChevronLeft,
  ChevronRight,
  GraduationCap
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLayoutStore } from '@/hooks/use-layout-store';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Learning Plan', href: '/plan', icon: BookOpen },
  { name: 'Roadmap', href: '/map', icon: Map },
  { name: 'AI Advisor', href: '/chat', icon: MessageSquare },
  { name: 'Profile', href: '/profile', icon: User },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isCollapsed, toggleSidebar } = useLayoutStore();

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex flex-col bg-white border-r border-slate-200 transition-all duration-300 ease-in-out lg:static",
        isCollapsed ? "w-20" : "w-64"
      )}
    >
      <div className={cn(
        "flex items-center h-16 border-b border-slate-200 transition-all duration-300",
        isCollapsed ? "justify-center px-2" : "justify-between px-4"
      )}>
        <Link 
          href="/dashboard" 
          className={cn(
            "flex items-center gap-3 overflow-hidden",
            isCollapsed && "justify-center"
          )}
        >
          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
            <GraduationCap size={20} />
          </div>
          {!isCollapsed && (
            <span className="font-lexend font-bold text-slate-900 truncate">
              EduPath AI
            </span>
          )}
        </Link>
        {!isCollapsed && (
          <button
            onClick={toggleSidebar}
            className="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg text-slate-500 hover:bg-slate-100"
          >
            <ChevronLeft size={20} />
          </button>
        )}
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
                "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group relative",
                isActive 
                  ? "bg-indigo-50 text-indigo-700" 
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <Icon 
                size={20} 
                className={cn(
                  "flex-shrink-0",
                  isActive ? "text-indigo-600" : "text-slate-400 group-hover:text-slate-600"
                )} 
              />
              {!isCollapsed && (
                <span className="text-sm font-medium whitespace-nowrap">
                  {item.name}
                </span>
              )}
              {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-slate-900 text-white text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50">
                  {item.name}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-200">
        {isCollapsed ? (
          <button
            onClick={toggleSidebar}
            className="flex items-center justify-center w-full h-10 rounded-lg text-slate-500 hover:bg-slate-100"
            title="Expand Sidebar"
          >
            <ChevronRight size={20} />
          </button>
        ) : (
          <div className="p-3 rounded-lg bg-slate-50">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
              Need help?
            </p>
            <p className="text-xs text-slate-400">
              Check out our documentation or contact support.
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
