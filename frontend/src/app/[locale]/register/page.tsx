'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { apiClient } from '@/lib/api-client';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';

export default function RegisterPage() {
  const t = useTranslations('Auth');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // 1. Register the user
      await apiClient.post('/auth/register', {
        email,
        password,
        full_name: fullName,
      });

      // 2. Automatically log them in
      await login(email, password);
      
    } catch (err: unknown) {
      const message = (err as { message?: string })?.message || t('loginError');
      setError(message);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-surface p-8 shadow-sm border border-border transition-all">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground font-[family-name:var(--font-lexend)]">
            {t('createAccount')}
          </h2>
          <p className="mt-2 text-sm text-muted font-[family-name:var(--font-inter)]">
            {t('registerSubtitle')}
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-lg bg-red-50 dark:bg-red-900/20 p-4 text-sm text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800 animate-in fade-in zoom-in duration-200">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="full-name" className="block text-sm font-medium text-foreground mb-1.5">
                {t('fullName')}
              </label>
              <input
                id="full-name"
                name="name"
                type="text"
                required
                className="block w-full rounded-lg border border-border bg-input px-4 py-2.5 text-foreground placeholder-muted focus:border-ring focus:ring-ring/20 focus:outline-none sm:text-sm transition-all"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="email-address" className="block text-sm font-medium text-foreground mb-1.5">
                {t('emailAddress')}
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="block w-full rounded-lg border border-border bg-input px-4 py-2.5 text-foreground placeholder-muted focus:border-ring focus:ring-ring/20 focus:outline-none sm:text-sm transition-all"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-1.5">
                {t('password')}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="block w-full rounded-lg border border-border bg-input px-4 py-2.5 text-foreground placeholder-muted focus:border-ring focus:ring-ring/20 focus:outline-none sm:text-sm transition-all"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-4">
            <button
              type="submit"
              disabled={isLoading}
              className="group relative flex w-full justify-center rounded-xl bg-secondary px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-secondary/20 hover:bg-secondary/90 focus:outline-none focus:ring-2 focus:ring-secondary focus:ring-offset-2 disabled:opacity-50 transition-all active:scale-[0.98]"
            >
              {isLoading ? t('creatingAccount') : t('createAccount')}
            </button>

            <p className="text-center text-sm text-muted">
              {t('alreadyHaveAccount')}{' '}
              <Link href="/login" className="font-semibold text-primary hover:underline">
                {t('signIn')}
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
