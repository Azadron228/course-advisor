import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface Course {
  id: string;
  subject_name: string;
  credits: number;
  description: string;
  skills_taught: string[];
  difficulty: number;
  workload: number;
  materials_content?: string;
}

export function useAdminCourses() {
  const queryClient = useQueryClient();

  const coursesQuery = useQuery({
    queryKey: ['admin', 'courses'],
    queryFn: () => apiClient.get<Course[]>('/admin/courses'),
  });

  const createCourseMutation = useMutation({
    mutationFn: (data: Omit<Course, 'materials_content'>) => 
      apiClient.post<Course>('/admin/courses', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const updateCourseMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Course> }) =>
      apiClient.put<Course>(`/admin/courses/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const deleteCourseMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/admin/courses/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const uploadMaterialsMutation = useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post<Course>(`/admin/courses/${id}/materials`, formData);
    },
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
  };
}
