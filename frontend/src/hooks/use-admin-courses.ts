import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface CourseMaterial {
  id: number;
  course_id: number;
  filename: string;
  status: string;
  created_at: string;
}

export interface Course {
  id: number;
  subject_name: string;
  description: string;
  skills_taught: string[];
  materials: CourseMaterial[];
}

export function useAdminCourses() {
  const queryClient = useQueryClient();

  const coursesQuery = useQuery({
    queryKey: ['admin', 'courses'],
    queryFn: () => apiClient.get<Course[]>('/admin/courses'),
  });

  const createCourseMutation = useMutation({
    mutationFn: (data: Omit<Course, 'id' | 'materials'>) => 
      apiClient.post<Course>('/admin/courses', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const updateCourseMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Omit<Course, 'id' | 'materials'>> }) =>
      apiClient.put<Course>(`/admin/courses/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const deleteCourseMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/admin/courses/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const uploadMaterialsMutation = useMutation({
    mutationFn: ({ id, file }: { id: number; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post<CourseMaterial>(`/admin/courses/${id}/materials`, formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const deleteMaterialMutation = useMutation({
    mutationFn: ({ courseId, materialId }: { courseId: number; materialId: number }) =>
      apiClient.delete(`/admin/courses/${courseId}/materials/${materialId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  return {
    courses: coursesQuery.data || [],
    isLoading: coursesQuery.isLoading,
    error: coursesQuery.error,
    createCourse: createCourseMutation.mutateAsync,
    updateCourse: updateCourseMutation.mutateAsync,
    deleteCourse: deleteCourseMutation.mutateAsync,
    uploadMaterials: uploadMaterialsMutation.mutateAsync,
    deleteMaterial: deleteMaterialMutation.mutateAsync,
  };
}
