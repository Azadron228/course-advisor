'use client';

import React, { useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAdminCourses } from '@/hooks/use-admin-courses';
import { CourseForm } from '@/components/admin/course-form';
import { useTranslations } from 'next-intl';
import { useRouter } from '@/i18n/routing';
import { 
  ArrowLeft, 
  FileText, 
  Upload, 
  CheckCircle2, 
  AlertCircle,
  Loader2
} from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function EditCoursePage() {
  const params = useParams();
  const id = params.id as string;
  const { courses, isLoading, updateCourse, uploadMaterials } = useAdminCourses();
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const course = courses.find((c) => c.id === id);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="p-8 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-900">{t('noCoursesFound')}</h2>
        <Link href="/admin/courses" className="text-primary hover:underline mt-4 inline-block">
          {t('backToCourses')}
        </Link>
      </div>
    );
  }

  const handleUpdate = async (data: any) => {
    setIsUpdating(true);
    try {
      await updateCourse({ id, data });
      alert(t('updateSuccess'));
      router.push('/admin/courses');
    } catch (error) {
      console.error('Failed to update course:', error);
      alert(tCommon('error'));
    } finally {
      setIsUpdating(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      await uploadMaterials({ id, file });
      alert(t('uploadSuccess'));
    } catch (error) {
      console.error('Failed to upload materials:', error);
      alert(tCommon('error'));
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href="/admin/courses"
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-slate-900 font-lexend">
              {t('editCourse')}
            </h1>
            <p className="text-slate-500 mt-1">{course.subject_name} ({course.id})</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8">
            <CourseForm 
              initialData={course} 
              onSubmit={handleUpdate} 
              isSubmitting={isUpdating}
              isEdit={true}
            />
          </div>
        </div>

        <div className="space-y-8">
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 font-lexend">
                {t('eduMaterials')}
              </h3>
            </div>

            <div className="space-y-6">
              {course.materials_content ? (
                <div className="flex items-start gap-3 p-4 bg-emerald-50 text-emerald-700 rounded-xl border border-emerald-100">
                  <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <p className="text-sm font-medium">
                    {t('syllabusAnalyzed')}
                  </p>
                </div>
              ) : (
                <div className="flex items-start gap-3 p-4 bg-slate-50 text-slate-600 rounded-xl border border-slate-100">
                  <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <p className="text-sm">
                    {t('uploadPrompt')}
                  </p>
                </div>
              )}

              <div className="pt-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".pdf,.txt"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 transition-all font-semibold"
                >
                  {isUploading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Upload className="w-5 h-5" />
                  )}
                  {isUploading ? t('uploading') : t('uploadFile')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
