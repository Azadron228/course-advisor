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
  Loader2,
  Trash2,
  FileCode,
  FilePen
} from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function EditCoursePage() {
  const params = useParams();
  const id = parseInt(params.id as string, 10);
  const { courses, isLoading, updateCourse, uploadMaterials, deleteMaterial } = useAdminCourses();
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
      // alert(t('uploadSuccess')); // Removed alert for smoother flow
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

  const handleDeleteMaterial = async (materialId: number) => {
    if (confirm('Are you sure you want to delete this material?')) {
      try {
        await deleteMaterial({ courseId: id, materialId });
      } catch (error) {
        console.error('Failed to delete material:', error);
        alert(tCommon('error'));
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 p-8">
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
            <p className="text-slate-500 mt-1">{course.subject_name} (ID: {course.id})</p>
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
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 flex flex-col h-fit">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-50 rounded-lg text-[#4F46E5]">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 font-lexend">
                {t('eduMaterials')}
              </h3>
            </div>

            <div className="space-y-6">
              {/* Materials List */}
              <div className="space-y-3">
                {course.materials && course.materials.length > 0 ? (
                  course.materials.map((material) => (
                    <div 
                      key={material.id} 
                      className="group flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:border-indigo-100 hover:bg-indigo-50/30 transition-all"
                    >
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className="p-2 bg-white rounded-lg shadow-sm border border-slate-100 text-slate-400 group-hover:text-indigo-500 transition-colors">
                          {material.filename.endsWith('.pdf') ? <FileText className="w-4 h-4" /> : <FileCode className="w-4 h-4" />}
                        </div>
                        <div className="overflow-hidden">
                          <p className="text-sm font-semibold text-slate-700 truncate group-hover:text-slate-900 transition-colors">
                            {material.filename}
                          </p>
                          <div className="flex items-center gap-2">
                             <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-md ${
                               material.status === 'analyzed' ? 'bg-emerald-50 text-emerald-600' : 
                               material.status === 'pending' ? 'bg-amber-50 text-orange-600' : 
                               'bg-red-50 text-red-600'
                             }`}>
                               {material.status}
                             </span>
                             <span className="text-[10px] text-slate-400">
                               {new Date(material.created_at).toLocaleDateString()}
                             </span>
                          </div>
                        </div>
                      </div>
                      <button 
                        onClick={() => handleDeleteMaterial(material.id)}
                        className="p-2 text-slate-300 hover:text-red-500 hover:bg-white rounded-lg transition-all opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                ) : (
                   <div className="text-center py-8 px-4 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                      <FilePen className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                      <p className="text-sm text-slate-500 font-medium">No materials yet</p>
                      <p className="text-xs text-slate-400 mt-1">Upload files to help AI understand your course</p>
                   </div>
                )}
              </div>

              {/* Upload Zone */}
              <div className="pt-4 border-t border-slate-50">
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
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-[#4F46E5] text-white rounded-xl hover:bg-[#4338CA] disabled:opacity-50 transition-all font-semibold shadow-lg shadow-indigo-500/20 active:scale-[0.98]"
                >
                  {isUploading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Upload className="w-5 h-5" />
                  )}
                  {isUploading ? t('uploading') : t('uploadFile')}
                </button>
                <p className="text-[10px] text-center text-slate-400 mt-3 font-medium uppercase tracking-widest">
                  PDF or TXT only
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
