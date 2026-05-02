'use client';

import React, { useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAdminCourses } from '@/hooks/use-admin-courses';
import { useQueryClient } from '@tanstack/react-query';
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
  const queryClient = useQueryClient();
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingMaterialId, setProcessingMaterialId] = useState<number | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  const course = courses.find((c) => c.id === id);

  // Polling for processing progress
  React.useEffect(() => {
    let interval: NodeJS.Timeout;
    if (processingMaterialId) {
      interval = setInterval(() => {
        queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [processingMaterialId, queryClient]);

  // If any material is currently in 'pending' or 'processing' status, and we are not already tracking it, track it
  React.useEffect(() => {
    const pendingMaterial = course?.materials?.find(
      (m) => m.status === 'pending' || m.status === 'processing'
    );
    if (pendingMaterial) {
      setProcessingMaterialId(pendingMaterial.id);
    } else {
      setProcessingMaterialId(null);
    }
  }, [course?.materials]);

  const processingProgress = React.useMemo(() => {
    if (!processingMaterialId || !course?.materials) return 0;
    const material = course.materials.find((m) => m.id === processingMaterialId);
    if (!material || !material.total_chunks) return 0;
    return Math.round((material.processed_chunks / material.total_chunks) * 100);
  }, [processingMaterialId, course?.materials]);

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
        <h2 className="text-2xl font-bold text-foreground">{t('noCoursesFound')}</h2>
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
    setUploadProgress(0);
    try {
      await uploadMaterials({ 
        id, 
        file, 
        onProgress: (progress) => setUploadProgress(progress) 
      });
      // alert(t('uploadSuccess')); // Removed alert for smoother flow
    } catch (error) {
      console.error('Failed to upload materials:', error);
      alert(tCommon('error'));
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
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
            className="p-2 text-muted hover:text-foreground hover:bg-input rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-foreground font-lexend">
              {t('editCourse')}
            </h1>
            <p className="text-muted mt-1">{course.subject_name} </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-surface rounded-2xl border border-border shadow-sm p-8">
            <CourseForm 
              initialData={course} 
              onSubmit={handleUpdate} 
              isSubmitting={isUpdating}
              isEdit={true}
            />
          </div>
        </div>

        <div className="space-y-8">
          <div className="bg-surface rounded-2xl border border-border shadow-sm p-8 flex flex-col h-fit">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg text-primary dark:text-indigo-400">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-foreground font-lexend">
                {t('eduMaterials')}
              </h3>
            </div>

            <div className="space-y-6">
              {/* Processing Notification */}
              {(processingMaterialId || isUploading) && (
                <div className="p-4 bg-primary/5 rounded-2xl border border-primary/20 space-y-3">
                  <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-primary">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      <span>
                        {isUploading 
                          ? (uploadProgress < 100 ? t('uploading') : t('processing'))
                          : t('processing')}
                      </span>
                    </div>
                    <span>{isUploading ? uploadProgress : processingProgress}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-input rounded-full overflow-hidden border border-border">
                    <div 
                      className="h-full bg-primary transition-all duration-300 ease-out rounded-full shadow-[0_0_8px_rgba(var(--primary-rgb),0.4)]"
                      style={{ width: `${isUploading ? uploadProgress : processingProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Materials List */}
              <div className="space-y-3">
                {course.materials && course.materials.length > 0 ? (
                  course.materials.map((material) => (
                    <div 
                      key={material.id} 
                      className="group flex items-center justify-between p-3 rounded-xl border border-border hover:border-primary/30 hover:bg-primary/5 transition-all"
                    >
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className="p-2 bg-surface  rounded-lg shadow-sm border border-border text-muted group-hover:text-primary transition-colors">
                          {material.filename.endsWith('.pdf') ? <FileText className="w-4 h-4" /> : <FileCode className="w-4 h-4" />}
                        </div>
                        <div className="overflow-hidden">
                          <p className="text-sm font-semibold text-foreground truncate group-hover:text-primary transition-colors">
                            {material.filename}
                          </p>
                          <div className="flex items-center gap-2">
                             <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-md ${
                               material.status === 'analyzed' ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400' : 
                               material.status === 'pending' ? 'bg-amber-50 dark:bg-amber-900/20 text-orange-600 dark:text-orange-400' : 
                               'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'
                             }`}>
                               {material.status}
                             </span>
                             <span className="text-[10px] text-muted">
                               {new Date(material.created_at).toLocaleDateString()}
                             </span>
                          </div>
                        </div>
                      </div>
                      <button 
                        onClick={() => handleDeleteMaterial(material.id)}
                        className="p-2 text-muted/40 hover:text-red-500 hover:bg-surface rounded-lg transition-all opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                ) : (
                   <div className="text-center py-8 px-4 bg-input  rounded-2xl border border-dashed border-border">
                      <FilePen className="w-8 h-8 text-muted/40 mx-auto mb-3" />
                      <p className="text-sm text-muted font-medium">No materials yet</p>
                      <p className="text-xs text-muted mt-1">Upload files to help AI understand your course</p>
                   </div>
                )}
              </div>

              {/* Upload Zone */}
              <div className="pt-4 border-t border-border">
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
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-primary text-white rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-all font-semibold shadow-lg shadow-primary/20 active:scale-[0.98]"
                >
                  {isUploading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Upload className="w-5 h-5" />
                  )}
                  {isUploading ? t('uploading') : t('uploadFile')}
                </button>
                <p className="text-[10px] text-center text-muted mt-3 font-medium uppercase tracking-widest">
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
