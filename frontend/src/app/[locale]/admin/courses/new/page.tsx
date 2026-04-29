'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter, Link } from '@/i18n/routing';
import { ChevronLeft } from 'lucide-react';
import { CourseForm } from '@/components/admin/course-form';
import { useAdminCourses } from '@/hooks/use-admin-courses';

export default function NewCoursePage() {
  const t = useTranslations('Admin');
  const router = useRouter();
  const { createCourse } = useAdminCourses();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (data: any) => {
    setIsSubmitting(true);
    try {
      await createCourse(data);
      alert(t('createSuccess'));
      router.push('/admin/courses');
    } catch (error) {
      console.error('Failed to create course:', error);
      alert('Error creating course');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center gap-4">
        <Link
          href="/admin/courses"
          className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <ChevronLeft className="w-6 h-6 text-slate-500" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white font-lexend">
            {t('addNewCourse')}
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            {t('backToCourses')}
          </p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-[2rem] shadow-sm border border-slate-100 dark:border-slate-800 p-8">
        <CourseForm 
          onSubmit={handleCreate} 
          isSubmitting={isSubmitting} 
        />
      </div>
    </div>
  );
}
