# Frontend Localization and TopNav Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement full localization (Russian default, English support) using `next-intl` and refactor the TopNav to handle authenticated states and language switching.

**Architecture:** Use `next-intl` App Router pattern with `[locale]` dynamic segment. Unified middleware for i18n and auth. Localized navigation hooks.

**Tech Stack:** Next.js 15, `next-intl`, Tailwind CSS, Lucide React.

---

### Task 1: Setup next-intl and Messages

**Files:**
- Create: `frontend/messages/ru.json`
- Create: `frontend/messages/en.json`
- Create: `frontend/src/i18n/routing.ts`
- Create: `frontend/src/i18n/request.ts`

- [ ] **Step 1: Install `next-intl`**

Run: `cd frontend && npm install next-intl`

- [ ] **Step 2: Create Russian messages**

```json
{
  "Common": {
    "title": "EduPath AI",
    "searchPlaceholder": "Поиск курсов, навыков...",
    "logout": "Выйти",
    "profile": "Мой профиль",
    "settings": "Настройки"
  },
  "Auth": {
    "login": "Вход",
    "register": "Регистрация"
  }
}
```

- [ ] **Step 3: Create English messages**

```json
{
  "Common": {
    "title": "EduPath AI",
    "searchPlaceholder": "Search courses, skills...",
    "logout": "Logout",
    "profile": "My Profile",
    "settings": "Settings"
  },
  "Auth": {
    "login": "Login",
    "register": "Register"
  }
}
```

- [ ] **Step 4: Create routing configuration**

```typescript
import {defineRouting} from 'next-intl/routing';
import {createNavigation} from 'next-intl/navigation';

export const routing = defineRouting({
  locales: ['en', 'ru'],
  defaultLocale: 'ru'
});

export const {Link, redirect, usePathname, useRouter, getPathname} =
  createNavigation(routing);
```

- [ ] **Step 5: Create request configuration**

```typescript
import {getRequestConfig} from 'next-intl/server';
import {routing} from './routing';

export default getRequestConfig(async ({requestLocale}) => {
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default
  };
});
```

- [ ] **Step 6: Commit setup**

```bash
git add frontend/package.json frontend/package-lock.json frontend/messages frontend/src/i18n
git commit -m "feat: setup next-intl and messages"
```

---

### Task 2: Refactor App Structure for [locale]

**Files:**
- Create: `frontend/src/app/[locale]/layout.tsx` (Copy/Move from `src/app/layout.tsx`)
- Create: `frontend/src/app/[locale]/page.tsx` (Copy/Move from `src/app/page.tsx`)
- Move: `frontend/src/app/chat`, `dashboard`, `login`, `map`, `plan`, `profile`, `register` to `frontend/src/app/[locale]/`
- Modify: `frontend/next.config.ts`

- [ ] **Step 1: Create localized root layout**

Wrap the existing layout logic with `NextIntlClientProvider`.

```tsx
import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import {routing} from '@/i18n/routing';
import {notFound} from 'next/navigation';

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 2: Move directories**

Run:
```bash
mkdir -p frontend/src/app/[locale]
mv frontend/src/app/chat frontend/src/app/[locale]/
mv frontend/src/app/dashboard frontend/src/app/[locale]/
mv frontend/src/app/login frontend/src/app/[locale]/
mv frontend/src/app/map frontend/src/app/[locale]/
mv frontend/src/app/plan frontend/src/app/[locale]/
mv frontend/src/app/profile frontend/src/app/[locale]/
mv frontend/src/app/register frontend/src/app/[locale]/
mv frontend/src/app/page.tsx frontend/src/app/[locale]/
# Keep globals.css and favicon.ico in src/app/
```

- [ ] **Step 3: Update next.config.ts**

```typescript
import createNextIntlPlugin from 'next-intl/plugin';
const withNextIntl = createNextIntlPlugin();

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ['37.151.21.4', 'localhost'],
};

export default withNextIntl(nextConfig);
```

- [ ] **Step 4: Commit refactor**

```bash
git add frontend/src/app frontend/next.config.ts
git commit -m "refactor: move app routes to [locale] segment"
```

---

### Task 3: Unified i18n and Auth Middleware

**Files:**
- Modify: `frontend/src/middleware.ts`

- [ ] **Step 1: Update middleware to combine next-intl and auth**

```typescript
import createMiddleware from 'next-intl/middleware';
import {NextResponse} from 'next/server';
import type {NextRequest} from 'next/server';
import {routing} from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

const protectedRoutes = ['/dashboard', '/plan', '/map', '/chat'];
const authRoutes = ['/login', '/register'];

export default function middleware(request: NextRequest) {
  const {pathname} = request.nextUrl;
  const token = request.cookies.get('token')?.value;

  // 1. Run intl middleware first to handle locale redirection
  const response = intlMiddleware(request);

  // 2. Auth logic
  // Strip locale from pathname for route checking
  const pathnameWithoutLocale = pathname.replace(/^\/(en|ru)/, '') || '/';

  const isProtectedRoute = protectedRoutes.some((route) => 
    pathnameWithoutLocale === route || pathnameWithoutLocale.startsWith(`${route}/`)
  );
  
  const isAuthRoute = authRoutes.some((route) => 
    pathnameWithoutLocale === route || pathnameWithoutLocale.startsWith(`${route}/`)
  );

  const currentLocale = pathname.split('/')[1] || routing.defaultLocale;

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL(`/${currentLocale}/login`, request.url));
  }

  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL(`/${currentLocale}/dashboard`, request.url));
  }

  return response;
}

export const config = {
  matcher: ['/', '/(ru|en)/:path*', '/((?!api|_next/static|_next/image|favicon.ico).*)']
};
```

- [ ] **Step 2: Commit middleware**

```bash
git add frontend/src/middleware.ts
git commit -m "feat: unified i18n and auth middleware"
```

---

### Task 4: Refactor TopNav with Language Switcher

**Files:**
- Modify: `frontend/src/components/shared/top-nav.tsx`

- [ ] **Step 1: Update TopNav with conditional rendering and language switcher**

```tsx
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
  Globe
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/use-auth';
import { useLayoutStore } from '@/hooks/use-layout-store';

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
    const nextLocale = locale === 'ru' ? 'en' : 'ru';
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
    <header className="sticky top-0 z-40 flex items-center justify-between h-16 px-4 bg-white/80 backdrop-blur-md border-b border-slate-200 lg:px-6">
      <div className="flex items-center gap-4">
        {isAuthenticated && (
          <button
            onClick={toggleMobileDrawer}
            className="lg:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100"
          >
            <Menu size={20} />
          </button>
        )}
        <h1 className="text-lg font-lexend font-semibold text-slate-900 lg:text-xl">
          {t('title')}
        </h1>
      </div>

      <div className="flex items-center gap-2 lg:gap-4">
        {isAuthenticated && (
          <>
            <div className="hidden md:flex relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="text"
                placeholder={t('searchPlaceholder')}
                className="w-64 pl-10 pr-4 py-2 bg-slate-100 border-transparent rounded-lg text-sm focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
            </div>

            <button className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
            </button>
          </>
        )}

        <button 
          onClick={toggleLanguage}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition-colors"
        >
          <Globe size={16} />
          <span className={cn(locale === 'ru' ? "text-indigo-600 font-bold" : "")}>RU</span>
          <span className="text-slate-300">|</span>
          <span className={cn(locale === 'en' ? "text-indigo-600 font-bold" : "")}>EN</span>
        </button>

        {isAuthenticated && (
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
                    {t('profile')}
                  </button>
                  <button className="flex w-full items-center gap-3 px-3 py-2 text-sm text-slate-600 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors">
                    <Settings size={18} />
                    {t('settings')}
                  </button>
                </div>
                <div className="p-1 border-t border-slate-100">
                  <button
                    onClick={() => logout()}
                    className="flex w-full items-center gap-3 px-3 py-2 text-sm text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
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
```

- [ ] **Step 2: Commit TopNav**

```bash
git add frontend/src/components/shared/top-nav.tsx
git commit -m "feat: update TopNav with language switcher and conditional rendering"
```
