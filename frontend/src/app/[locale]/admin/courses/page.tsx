'use client';

import { useAdminCourses } from '@/hooks/use-admin-courses';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { 
  BookOpen, 
  Plus, 
  Edit2, 
  Trash2, 
  Loader2,
  GraduationCap
} from 'lucide-react';

export default function AdminCourseListPage() {
  const { courses, isLoading, deleteCourse } = useAdminCourses();
  const t = useTranslations('Admin');

  const handleDelete = async (id: string, name: string) => {
    if (confirm(t('confirmDelete', { name }))) {
      try {
        await deleteCourse(id);
      } catch (error) {
        console.error('Failed to delete course:', error);
        alert(t('deleteError'));
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 font-lexend flex items-center">
            <BookOpen className="mr-3 h-8 w-8 text-primary" />
            {t('courseManagement')}
          </h1>
          <p className="text-slate-500 mt-1">{t('manageCoursesDesc')}</p>
        </div>
        <Link 
          href="/admin/courses/new"
          className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-xl hover:bg-primary/90 transition-all font-semibold shadow-lg shadow-primary/20 w-fit"
        >
          <Plus className="w-5 h-5 mr-2" />
          {t('addNewCourse')}
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {courses.map((course) => (
          <div 
            key={course.id}
            className="bg-white rounded-[1rem] border border-slate-100 shadow-sm hover:shadow-md transition-all p-6 flex flex-col h-full group"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-primary/5 rounded-xl text-primary">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Link 
                  href={`/admin/courses/${course.id}`}
                  className="p-2 text-slate-400 hover:text-primary hover:bg-slate-50 rounded-lg transition-colors"
                  title={t('editCourse')}
                >
                  <Edit2 className="w-4 h-4" />
                </Link>
                <button 
                  onClick={() => handleDelete(course.id, course.subject_name)}
                  className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title={t('deleteCourse')}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-grow">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  ID: {course.id}
                </span>
                <span className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs font-bold rounded-md uppercase">
                  {t('credits', { count: course.credits })}
                </span>
              </div>
              <h3 className="text-xl font-bold text-slate-900 font-lexend mb-2 line-clamp-1">
                {course.subject_name}
              </h3>
              <p className="text-slate-600 text-sm line-clamp-3 mb-6">
                {course.description}
              </p>
            </div>

            <div className="mt-auto pt-6 border-t border-slate-50">
              <div className="flex justify-between items-center mb-2 text-sm font-medium">
                <span className="text-slate-500">{t('difficulty')}</span>
                <span className="text-slate-900 font-bold">{Math.round(course.difficulty * 100)}%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-primary h-full rounded-full transition-all duration-700 ease-out" 
                  style={{ width: `${course.difficulty * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {courses.length === 0 && (
        <div className="text-center py-20 bg-white rounded-[2rem] border border-dashed border-slate-200 shadow-sm">
          <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <BookOpen className="w-10 h-10 text-slate-300" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 font-lexend">{t('noCoursesFound')}</h3>
          <p className="text-slate-500 mt-2 max-w-sm mx-auto">{t('startFirstCourse')}</p>
          <Link 
            href="/admin/courses/new"
            className="mt-8 inline-flex items-center px-8 py-3 bg-primary text-white rounded-xl hover:bg-primary/90 transition-all font-semibold shadow-lg shadow-primary/20"
          >
            <Plus className="w-5 h-5 mr-2" />
            {t('addNewCourse')}
          </Link>
        </div>
      )}
    </div>
  );
}
