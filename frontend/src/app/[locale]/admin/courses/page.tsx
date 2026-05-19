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

  const handleDelete = async (id: number, name: string) => {
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
          <h1 className="text-3xl font-bold text-foreground font-lexend flex items-center">
            <BookOpen className="mr-3 h-8 w-8 text-primary" />
            {t('courseManagement')}
          </h1>
          <p className="text-muted mt-1">{t('manageCoursesDesc')}</p>
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
            className="bg-surface rounded-[1rem] border border-border shadow-sm hover:shadow-md transition-all p-6 flex flex-col h-full group"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-primary/5 dark:bg-primary/10 rounded-xl text-primary">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Link 
                  href={`/admin/courses/${course.id}`}
                  className="p-2 text-muted hover:text-primary hover:bg-input rounded-lg transition-colors"
                  title={t('editCourse')}
                >
                  <Edit2 className="w-4 h-4" />
                </Link>
                <button 
                  onClick={() => handleDelete(course.id, course.subject_name)}
                  className="p-2 text-muted hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  title={t('deleteCourse')}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-grow">
              <div className="flex items-center justify-between mb-2">
              </div>
              <h3 className="text-xl font-bold text-foreground font-lexend mb-2 line-clamp-1">
                {course.subject_name}
              </h3>
              <p className="text-muted text-sm line-clamp-3 mb-6">
                {course.description}
              </p>
            </div>

            <div className="mt-auto pt-4 border-t border-border">
               <div className="flex flex-wrap gap-2">
                {course.skills_taught.slice(0, 3).map((skill, index) => (
                  <span key={index} className="px-2 py-1 bg-input text-muted text-[10px] font-bold rounded-md uppercase">
                    {skill}
                  </span>
                ))}
                {course.skills_taught.length > 3 && (
                  <span className="px-2 py-1 bg-input text-muted text-[10px] font-bold rounded-md uppercase">
                    +{course.skills_taught.length - 3}
                  </span>
                )}
               </div>
            </div>
          </div>
        ))}
      </div>

      {courses.length === 0 && (
        <div className="text-center py-20 bg-surface rounded-[2rem] border border-dashed border-border shadow-sm">
          <div className="w-20 h-20 bg-input rounded-full flex items-center justify-center mx-auto mb-6">
            <BookOpen className="w-10 h-10 text-muted/50" />
          </div>
          <h3 className="text-xl font-bold text-foreground font-lexend">{t('noCoursesFound')}</h3>
          <p className="text-muted mt-2 max-w-sm mx-auto">{t('startFirstCourse')}</p>
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
