'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';

export default function LoginPage() {
  const t = useTranslations('Auth');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
    } catch {
      setError(t('loginError'));
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-surface p-8 shadow-sm border border-slate-200 dark:border-slate-800 transition-all">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground font-[family-name:var(--font-lexend)]">
            {t('welcomeBack')}
          </h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 font-[family-name:var(--font-inter)]">
            {t('continueJourney')}
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
              <label htmlFor="email-address" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                {t('emailAddress')}
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="block w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 px-4 py-2.5 text-slate-900 dark:text-white placeholder-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-primary/10 sm:text-sm transition-all"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" title="password" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                  {t('password')}
                </label>
                <Link href="#" className="text-xs font-medium text-primary hover:underline">
                  {t('forgotPassword')}
                </Link>
              </div>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="block w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 px-4 py-2.5 text-slate-900 dark:text-white placeholder-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-primary/10 sm:text-sm transition-all"
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
              className="group relative flex w-full justify-center rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/20 hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 transition-all active:scale-[0.98]"
            >
              {isLoading ? t('signingIn') : t('signIn')}
            </button>

            <p className="text-center text-sm text-slate-500 dark:text-slate-400">
              {t('dontHaveAccount')}{' '}
              <Link href="/register" className="font-semibold text-primary hover:underline">
                {t('signUp')}
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
