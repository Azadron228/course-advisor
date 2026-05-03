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

  const handleCreate = async (data: Parameters<typeof createCourse>[0]) => {
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
          className="p-2 rounded-full hover:bg-input transition-colors"
        >
          <ChevronLeft className="w-6 h-6 text-muted" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground font-lexend">
            {t('addNewCourse')}
          </h1>
          <p className="text-muted">
            {t('backToCourses')}
          </p>
        </div>
      </div>

      <div className="bg-surface rounded-[2rem] shadow-sm border border-border p-8">
        <CourseForm 
          onSubmit={handleCreate} 
          isSubmitting={isSubmitting} 
        />
      </div>
    </div>
  );
}
