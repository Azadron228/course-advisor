'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslations } from 'next-intl';
import { Course } from '@/hooks/use-admin-courses';

const courseSchema = z.object({
  id: z.string().min(1, 'Required'),
  subject_name: z.string().min(1, 'Required'),
  credits: z.number().min(0),
  description: z.string().min(1, 'Required'),
  skills_taught: z.string(),
  difficulty: z.number().min(0).max(1),
  workload: z.number().min(0).max(1),
});

type CourseFormValues = z.infer<typeof courseSchema>;

interface CourseFormProps {
  initialData?: Partial<Course>;
  onSubmit: (data: any) => void;
  isSubmitting: boolean;
  isEdit?: boolean;
}

export function CourseForm({ initialData, onSubmit, isSubmitting, isEdit }: CourseFormProps) {
  const t = useTranslations('Admin');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<CourseFormValues>({
    resolver: zodResolver(courseSchema),
    defaultValues: {
      id: initialData?.id || '',
      subject_name: initialData?.subject_name || '',
      credits: initialData?.credits || 0,
      description: initialData?.description || '',
      skills_taught: initialData?.skills_taught?.join(', ') || '',
      difficulty: initialData?.difficulty ?? 0.5,
      workload: initialData?.workload ?? 0.5,
    },
  });

  const difficulty = watch('difficulty');
  const workload = watch('workload');

  const onFormSubmit = (values: CourseFormValues) => {
    const formattedData = {
      ...values,
      skills_taught: values.skills_taught
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s !== ''),
    };
    onSubmit(formattedData);
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Column: General Information */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-foreground border-b border-slate-200 dark:border-slate-800 pb-2">
            {t('generalInfo')}
          </h3>
          
          <div className="space-y-2">
            <label htmlFor="id" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              {t('courseId')}
            </label>
            <input
              {...register('id')}
              id="id"
              disabled={isEdit}
              className="block w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 px-4 py-2.5 text-slate-900 dark:text-white placeholder-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-primary/10 sm:text-sm transition-all disabled:opacity-50"
              placeholder="CS101"
            />
            {errors.id && <p className="text-sm text-red-500">{errors.id.message}</p>}
          </div>

          <div className="space-y-2">
            <label htmlFor="subject_name" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              {t('subjectName')}
            </label>
            <input
              {...register('subject_name')}
              id="subject_name"
              className="block w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 px-4 py-2.5 text-slate-900 dark:text-white placeholder-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-primary/10 sm:text-sm transition-all"
              placeholder="Introduction to Computer Science"
            />
            {errors.subject_name && <p className="text-sm text-red-500">{errors.subject_name.message}</p>}
          </div>

          <div className="space-y-2">
            <label htmlFor="credits" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Credits
            </label>
            <input
              {...register('credits', { valueAsNumber: true })}
              id="credits"
              type="number"
              className="block w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 px-4 py-2.5 text-slate-900 dark:text-white placeholder-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-primary/10 sm:text-sm transition-all"
            />
            {errors.credits && <p className="text-sm text-red-500">{errors.credits.message}</p>}
          </div>

          <div className="space-y-2">
            <label htmlFor="description" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              {t('description')}
            </label>
            <textarea
              {...register('description')}
              id="description"
              rows={5}
              className="block w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 px-4 py-2.5 text-slate-900 dark:text-white placeholder-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-primary/10 sm:text-sm transition-all"
            />
            {errors.description && <p className="text-sm text-red-500">{errors.description.message}</p>}
          </div>
        </div>

        {/* Right Column: Metadata & Skills */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-foreground border-b border-slate-200 dark:border-slate-800 pb-2">
            {t('metadataSkills')}
          </h3>

          <div className="space-y-2">
            <label htmlFor="skills_taught" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              {t('skillsTaught')}
            </label>
            <input
              {...register('skills_taught')}
              id="skills_taught"
              className="block w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 px-4 py-2.5 text-slate-900 dark:text-white placeholder-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-primary/10 sm:text-sm transition-all"
              placeholder={t('skillsPlaceholder')}
            />
          </div>

          <div className="space-y-6 pt-2">
            <div className="space-y-3">
              <div className="flex justify-between">
                <label htmlFor="difficulty" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                  {t('difficulty')}
                </label>
                <span className="text-sm font-mono font-bold text-primary">{Math.round((difficulty || 0) * 100)}%</span>
              </div>
              <input
                {...register('difficulty', { valueAsNumber: true })}
                id="difficulty"
                type="range"
                min="0"
                max="1"
                step="0.01"
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            <div className="space-y-3">
              <div className="flex justify-between">
                <label htmlFor="workload" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                  {t('workload')}
                </label>
                <span className="text-sm font-mono font-bold text-primary">{Math.round((workload || 0) * 100)}%</span>
              </div>
              <input
                {...register('workload', { valueAsNumber: true })}
                id="workload"
                type="range"
                min="0"
                max="1"
                step="0.01"
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="pt-6 border-t border-slate-200 dark:border-slate-800 flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-xl bg-primary px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/20 hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 transition-all active:scale-[0.98]"
        >
          {isSubmitting ? '...' : isEdit ? t('updateCourse') : t('createCourse')}
        </button>
      </div>
    </form>
  );
}
