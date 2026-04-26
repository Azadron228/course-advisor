# Design Spec: Frontend Localization and TopNav Refactor

This document outlines the design for implementing internationalization (i18n) in the Course Advisor frontend using `next-intl` and refactoring the `TopNav` component to handle authenticated/unauthenticated states with a language switcher.

## 1. Internationalization (i18n)

### 1.1 Goals
- Support Russian (`ru`) and English (`en`) languages.
- Default language: Russian (`ru`).
- Locale must always be present in the URL (e.g., `/ru/dashboard`).
- Localized UI strings for common components (Navigation, Auth, Profile).

### 1.2 Architecture
- **Framework**: `next-intl` for Next.js App Router.
- **Directory Structure**:
  - `frontend/messages/ru.json`: Russian translations.
  - `frontend/messages/en.json`: English translations.
  - `frontend/src/i18n/routing.ts`: Configuration for locales and localized navigation hooks.
  - `frontend/src/i18n/request.ts`: Message loading configuration for server components.
  - `frontend/src/app/[locale]/`: Root layout and pages moved here to support path-based localization.

### 1.3 Routing & Middleware
- **Middleware**: `src/middleware.ts` will be updated to:
  1. Use `next-intl` middleware for locale redirection.
  2. Maintain existing authentication logic (protecting routes like `/dashboard`, `/plan`, etc.).
  3. Support pathnames with locale prefixes (e.g., checking `/ru/dashboard`).
- **Navigation Hooks**: All components will use localized `Link`, `useRouter`, and `usePathname` from `src/i18n/routing.ts` to ensure the locale is preserved during navigation.

## 2. TopNav Component Refactor

### 2.1 Authenticated State
- **Visibility**: All existing elements remain visible.
- **Components**:
  - Mobile Menu Button (Hamburger)
  - Logo ("EduPath AI" text)
  - Search Bar
  - Notifications Button
  - Profile Dropdown
  - **New**: Language Switcher (RU | EN).

### 2.2 Unauthenticated State
- **Visibility**: Minimal view.
- **Components**:
  - Logo ("EduPath AI" text)
  - **New**: Language Switcher (RU | EN).
- **Hidden**: Mobile Menu Button, Search Bar, Notifications, Profile Dropdown.

### 2.3 Language Switcher
- **Implementation**: A simple text-based toggle.
- **Behavior**: Clicking the inactive locale will switch the current URL path to that locale (e.g., `/ru/login` -> `/en/login`).

## 3. Implementation Steps
1. Install `next-intl`.
2. Create message files and i18n configuration.
3. Move `src/app/` content to `src/app/[locale]/`.
4. Update `src/middleware.ts` to handle both i18n and auth.
5. Refactor `TopNav.tsx` for conditional rendering and language switching.
6. Localize initial batch of strings (Login, Register, Dashboard).

## 4. Testing Criteria
- Navigating to `/` redirects to `/ru/`.
- Switching language updates the URL path and UI text.
- Unauthorized users on `/ru/` or `/ru/login` only see Logo and Language Switcher.
- Authorized users see the full TopNav.
- Protected routes remain protected even with locale prefix.
