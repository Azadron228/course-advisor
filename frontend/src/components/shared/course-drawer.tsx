'use client';

import { X, Loader2, BookOpen } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '@/lib/api-client';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';

interface Course {
  subject_name: string;
  description: string;
  materials_content: string | null;
}

interface CourseDrawerProps {
  courseId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function CourseDrawer({ courseId, isOpen, onClose }: CourseDrawerProps) {
  const t = useTranslations('Plan');
  const { data: course, isLoading, isError } = useQuery({
    queryKey: ['courses', courseId],
    queryFn: () => apiClient.get<Course>(`/courses/${courseId}`),
    enabled: isOpen && !!courseId,
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" onClick={onClose} />
      
      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-2xl transform transition-all animate-in slide-in-from-right duration-300">
          <div className="flex h-full flex-col bg-white shadow-2xl border-l border-slate-200">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-100 bg-slate-50/50">
              <div className="flex items-center gap-3">
                <div className="bg-indigo-100 p-2 rounded-lg text-indigo-600">
                  <BookOpen className="w-5 h-5" />
                </div>
                <h2 className="text-xl font-bold text-slate-900">{t('materials')}</h2>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full text-slate-500 transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-8">
              {isLoading ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-3">
                  <Loader2 className="w-8 h-8 animate-spin" />
                  <p className="font-medium">{t('loadingMaterials')}</p>
                </div>
              ) : isError ? (
                <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-100">
                  {t('loadError')}
                </div>
              ) : course && (
                <div className="space-y-8">
                  <div>
                    <h1 className="text-3xl font-extrabold text-slate-900 mb-4">{course.subject_name}</h1>
                    <p className="text-lg text-slate-600 leading-relaxed">{course.description}</p>
                  </div>

                  <div className="prose prose-slate max-w-none border-t border-slate-100 pt-8 text-slate-900">
                    {course.materials_content ? (
                      <ReactMarkdown>{course.materials_content}</ReactMarkdown>
                    ) : (
                      <p className="italic text-slate-400">{t('noMaterials')}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
