'use client';

import { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/hooks/use-auth';
import { apiClient } from '@/lib/api-client';
import { Loader2, Save, User as UserIcon } from 'lucide-react';
import { useTranslations } from 'next-intl';

export default function ProfilePage() {
  const t = useTranslations('Auth');
  const tCommon = useTranslations('Common');
  const { user, isLoading: isUserLoading } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const profileSchema = useMemo(() => z.object({
    full_name: z.string().min(2, t('nameMinLength')),
    email: z.string().email(t('invalidEmail')),
    career_goal: z.string().min(5, t('goalMinLength')),
  }), [t]);

  type ProfileFormValues = z.infer<typeof profileSchema>;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    values: user ? {
      full_name: user.full_name || '',
      email: user.email || '',
      career_goal: user.career_goal || '',
    } : undefined,
  });

  const onSubmit = async (data: ProfileFormValues) => {
    setIsSaving(true);
    setMessage(null);
    try {
      await apiClient.patch('/users/me', data);
      setMessage({ type: 'success', text: t('profileUpdated') });
    } catch (error: unknown) {
      console.error('Failed to update profile:', error);
      const errorMessage = error instanceof Error ? error.message : (error as { message?: string })?.message || t('profileUpdateError');
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setIsSaving(false);
    }
  };

  if (isUserLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <div className="flex items-center gap-4 mb-8">
        <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-full">
          <UserIcon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-gray-900 ">{t('userProfile')}</h1>
          <p className="text-gray-500 dark:text-gray-400">{t('manageProfile')}</p>
        </div>
      </div>

      <div className="bg-surface rounded-xl shadow-sm border border-border overflow-hidden">
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {message && (
            <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800'}`}>
              {message.text}
            </div>
          )}

          <div className="space-y-2">
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('fullName')}
            </label>
            <input
              id="full_name"
              {...register('full_name')}
              className={`block w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all   ${
                errors.full_name ? 'border-red-300 dark:border-red-900' : 'border-border'
              }`}
              placeholder="John Doe"
            />
            {errors.full_name && (
              <p className="text-sm text-red-600 dark:text-red-400">{errors.full_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('emailAddress')}
            </label>
            <input
              id="email"
              type="email"
              {...register('email')}
              className={`block w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all   ${
                errors.email ? 'border-red-300 dark:border-red-900' : 'border-border'
              }`}
              placeholder="john@example.com"
            />
            {errors.email && (
              <p className="text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="career_goal" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('careerGoal')}
            </label>
            <textarea
              id="career_goal"
              rows={4}
              {...register('career_goal')}
              className={`block w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all   ${
                errors.career_goal ? 'border-red-300 dark:border-red-900' : 'border-border'
              }`}
              placeholder={t('careerGoalPlaceholder')}
            />
            {errors.career_goal && (
              <p className="text-sm text-red-600 dark:text-red-400">{errors.career_goal.message}</p>
            )}
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={isSaving}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {tCommon('savingChanges')}
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  {tCommon('saveChanges')}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
