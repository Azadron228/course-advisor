'use client';

import { useAdminCourses } from '@/hooks/use-admin-courses';
import { Link } from '@/i18n/routing';
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

  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to delete the course "${name}"?`)) {
      try {
        await deleteCourse(id);
      } catch (error) {
        console.error('Failed to delete course:', error);
        alert('Failed to delete course. Please try again.');
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
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 font-lexend flex items-center">
            <BookOpen className="mr-3 h-8 w-8 text-primary" />
            Course Management
          </h1>
          <p className="text-slate-500 mt-1">Create, edit, and manage courses in the catalog.</p>
        </div>
        <Link 
          href="/admin/courses/new"
          className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium shadow-sm w-fit"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add New Course
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {courses.map((course) => (
          <div 
            key={course.id}
            className="bg-white rounded-[1rem] border border-slate-200 shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col h-full"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-slate-50 rounded-lg text-primary">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div className="flex space-x-1">
                <Link 
                  href={`/admin/courses/${course.id}`}
                  className="p-2 text-slate-400 hover:text-primary hover:bg-slate-50 rounded-lg transition-colors"
                  title="Edit Course"
                >
                  <Edit2 className="w-4 h-4" />
                </Link>
                <button 
                  onClick={() => handleDelete(course.id, course.subject_name)}
                  className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete Course"
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
                <span className="px-2 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded-md uppercase">
                  {course.credits} Credits
                </span>
              </div>
              <h3 className="text-xl font-bold text-slate-900 font-lexend mb-2 line-clamp-1">
                {course.subject_name}
              </h3>
              <p className="text-slate-600 text-sm line-clamp-3 mb-6">
                {course.description}
              </p>
            </div>

            <div className="mt-auto pt-6 border-t border-slate-100">
              <div className="flex justify-between items-center mb-2 text-sm font-medium">
                <span className="text-slate-500">Difficulty</span>
                <span className="text-slate-900 font-bold">{course.difficulty}%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-primary h-full rounded-full transition-all duration-500" 
                  style={{ width: `${course.difficulty}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {courses.length === 0 && (
        <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-slate-300">
          <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-900 font-lexend">No courses found</h3>
          <p className="text-slate-500 mt-1">Get started by creating your first course.</p>
        </div>
      )}
    </div>
  );
}
