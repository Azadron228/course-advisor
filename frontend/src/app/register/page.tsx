'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { apiClient } from '@/lib/api-client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

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
      
      // router.push('/dashboard') is handled by login() in useAuth
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f8f9ff] px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-sm border border-[#F1F5F9]">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-[#0b1c30] font-[family-name:var(--font-lexend)]">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-[#464555] font-[family-name:var(--font-inter)]">
            Or{' '}
            <Link href="/login" className="font-medium text-[#4F46E5] hover:text-[#3525cd]">
              sign in to your existing account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700 border border-red-200">
              {error}
            </div>
          )}
          <div className="space-y-4 rounded-md shadow-sm">
            <div>
              <label htmlFor="full-name" className="block text-sm font-medium text-[#464555] mb-1">
                Full Name
              </label>
              <input
                id="full-name"
                name="name"
                type="text"
                required
                className="relative block w-full rounded-lg border border-[#c7c4d8] px-3 py-2 text-[#0b1c30] placeholder-[#777587] focus:border-[#4F46E5] focus:outline-none focus:ring-[#4F46E5] sm:text-sm transition-all"
                placeholder="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="email-address" className="block text-sm font-medium text-[#464555] mb-1">
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="relative block w-full rounded-lg border border-[#c7c4d8] px-3 py-2 text-[#0b1c30] placeholder-[#777587] focus:border-[#4F46E5] focus:outline-none focus:ring-[#4F46E5] sm:text-sm transition-all"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" name="password" className="block text-sm font-medium text-[#464555] mb-1">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="relative block w-full rounded-lg border border-[#c7c4d8] px-3 py-2 text-[#0b1c30] placeholder-[#777587] focus:border-[#4F46E5] focus:outline-none focus:ring-[#4F46E5] sm:text-sm transition-all"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative flex w-full justify-center rounded-lg bg-[#10B981] px-4 py-2 text-sm font-semibold text-white hover:bg-[#008f5d] focus:outline-none focus:ring-2 focus:ring-[#10B981] focus:ring-offset-2 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
