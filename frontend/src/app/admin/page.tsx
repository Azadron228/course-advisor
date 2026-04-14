'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import api from '@/lib/api';
import { Card, CardContent, CardHeader } from '@/components/ui-base';
import { Loader2, Plus, Pencil, Trash2, X, Check } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Course {
  id: string;
  subject_name: string;
  credits: number;
  description: string;
  skills_taught: string[];
  difficulty: number;
  workload: number;
}

export default function AdminPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<Course>>({});
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && (!user || !user.is_admin)) {
      router.push('/dashboard');
      return;
    }
    if (user?.is_admin) {
      fetchCourses();
    }
  }, [user, authLoading]);

  const fetchCourses = async () => {
    try {
      const resp = await api.get('/api/v1/admin/courses');
      setCourses(resp.data);
    } catch (err) {
      console.error('Failed to fetch courses', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (course: Course) => {
    setIsEditing(course.id);
    setEditForm(course);
  };

  const handleCancelEdit = () => {
    setIsEditing(null);
    setEditForm({});
  };

  const handleSave = async (courseId: string) => {
    try {
      await api.put(`/api/v1/admin/courses/${courseId}`, editForm);
      setIsEditing(null);
      fetchCourses();
    } catch (err) {
      console.error('Failed to update course', err);
      alert('Failed to update course');
    }
  };

  const handleDelete = async (courseId: string) => {
    if (!confirm('Are you sure you want to delete this course?')) return;
    try {
      await api.delete(`/api/v1/admin/courses/${courseId}`);
      fetchCourses();
    } catch (err) {
      console.error('Failed to delete course', err);
      alert('Failed to delete course');
    }
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Admin Dashboard</h1>
            <p className="text-slate-500">Manage Course Inventory</p>
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700">
            <Plus size={20} /> Add Course
          </button>
        </div>

        <div className="space-y-4">
          {courses.map(course => (
            <Card key={course.id}>
              <CardContent className="p-6">
                {isEditing === course.id ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Subject Name</label>
                        <input
                          className="w-full p-2 border rounded"
                          value={editForm.subject_name || ''}
                          onChange={e => setEditForm({...editForm, subject_name: e.target.value})}
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Credits</label>
                        <input
                          type="number"
                          className="w-full p-2 border rounded"
                          value={editForm.credits || 0}
                          onChange={e => setEditForm({...editForm, credits: parseFloat(e.target.value)})}
                        />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-500 uppercase">Description</label>
                      <textarea
                        className="w-full p-2 border rounded h-24"
                        value={editForm.description || ''}
                        onChange={e => setEditForm({...editForm, description: e.target.value})}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Difficulty (0-1)</label>
                        <input
                          type="number" step="0.1" min="0" max="1"
                          className="w-full p-2 border rounded"
                          value={editForm.difficulty || 0}
                          onChange={e => setEditForm({...editForm, difficulty: parseFloat(e.target.value)})}
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase">Workload (0-1)</label>
                        <input
                          type="number" step="0.1" min="0" max="1"
                          className="w-full p-2 border rounded"
                          value={editForm.workload || 0}
                          onChange={e => setEditForm({...editForm, workload: parseFloat(e.target.value)})}
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-4">
                      <button onClick={handleCancelEdit} className="p-2 text-slate-500 hover:bg-slate-100 rounded">
                        <X size={20} />
                      </button>
                      <button onClick={() => handleSave(course.id)} className="p-2 text-green-600 hover:bg-green-50 rounded">
                        <Check size={20} />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2">
                        <h2 className="text-xl font-bold text-slate-900">{course.subject_name}</h2>
                        <span className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded font-mono">
                          {course.id}
                        </span>
                      </div>
                      <p className="text-slate-600 mt-2 text-sm line-clamp-2">{course.description}</p>
                      <div className="flex gap-4 mt-4 text-sm">
                        <span className="text-slate-500">Credits: <strong className="text-slate-900">{course.credits}</strong></span>
                        <span className="text-slate-500">Difficulty: <strong className="text-slate-900">{course.difficulty}</strong></span>
                        <span className="text-slate-500">Workload: <strong className="text-slate-900">{course.workload}</strong></span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => handleEdit(course)} className="p-2 text-slate-500 hover:bg-slate-100 rounded">
                        <Pencil size={18} />
                      </button>
                      <button onClick={() => handleDelete(course.id)} className="p-2 text-red-500 hover:bg-red-50 rounded">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
