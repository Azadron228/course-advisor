import createMiddleware from 'next-intl/middleware';
import {NextResponse} from 'next/server';
import type {NextRequest} from 'next/server';
import {routing} from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

const protectedRoutes = ['/dashboard', '/plan', '/chat'];
const authRoutes = ['/login', '/register'];

export default function proxy(request: NextRequest) {
  const {pathname} = request.nextUrl;
  const token = request.cookies.get('token')?.value;

  // 1. Run intl middleware first to handle locale redirection
  const response = intlMiddleware(request);

  // 2. Auth logic
  // Strip locale from pathname for route checking (e.g. /ru/dashboard -> /dashboard)
  const pathnameWithoutLocale = pathname.replace(/^\/(en|ru|kk)/, '') || '/';

  const isProtectedRoute = protectedRoutes.some((route) => 
    pathnameWithoutLocale === route || pathnameWithoutLocale.startsWith(`${route}/`)
  );
  
  const isAuthRoute = authRoutes.some((route) => 
    pathnameWithoutLocale === route || pathnameWithoutLocale.startsWith(`${route}/`)
  );

  const segments = pathname.split('/');
  const firstSegment = segments[1];
  const locales = routing.locales as readonly string[];
  const currentLocale = locales.includes(firstSegment) ? firstSegment : routing.defaultLocale;

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL(`/${currentLocale}/login`, request.url));
  }

  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL(`/${currentLocale}/dashboard`, request.url));
  }

  return response;
}

export const config = {
  matcher: ['/', '/(ru|en|kk)/:path*', '/((?!api|_next/static|_next/image|favicon.ico).*)']
};
