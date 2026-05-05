'use client';

import { usePathname } from '@/i18n/routing';
import { Sidebar } from './sidebar';
import { TopNav } from './top-nav';
import { MobileDrawer } from './mobile-drawer';
import { cn } from '@/lib/utils';

const PUBLIC_ROUTES = ['/login', '/register', '/'];

export function MainLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  // pathname from @/i18n/routing doesn't include the locale prefix
  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
  const isAdminRoute = pathname.startsWith('/admin');

  if (isPublicRoute || isAdminRoute) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopNav />
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <div className={cn("mx-auto h-full", "max-w-screen-20xl")}>
            {children}
          </div>
        </main>
      </div>
      <MobileDrawer />
    </div>
  );
}
