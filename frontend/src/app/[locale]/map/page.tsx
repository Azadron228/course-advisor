'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { SkillGraph, SkillNode } from '@/components/features/skill-graph';
import { LearningPlan } from '@/components/features/plan-stepper';
import { Loader2, Map as MapIcon, AlertCircle } from 'lucide-react';

export default function MapPage() {
  const { data: skillsData, isLoading: isLoadingSkills, error: skillsError } = useQuery<{ nodes: SkillNode[] }>({
    queryKey: ['skills-map'],
    queryFn: () => apiClient.get('/skills/map/'),
  });

  const { data: planData, isLoading: isLoadingPlan } = useQuery<LearningPlan>({
    queryKey: ['learning-plan'],
    queryFn: () => apiClient.get('/learning-plan/'),
  });

  const isLoading = isLoadingSkills || isLoadingPlan;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-600 animate-spin" />
        <span className="text-slate-600 font-medium animate-pulse">Loading interactive skill map...</span>
      </div>
    );
  }

  if (skillsError) {
    return (
      <div className="p-8 mt-4 bg-red-50 rounded-xl border border-red-100 shadow-sm flex flex-col items-center justify-center text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mb-3" />
        <h2 className="text-xl font-bold text-red-800 mb-2">Error Loading Skill Map</h2>
        <p className="text-red-600 max-w-md">
          We could not load your skill graph. Please check your connection and try again later.
        </p>
      </div>
    );
  }

  const skills = skillsData?.nodes || [];

  return (
    <div className="py-4 space-y-6">
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-start gap-4">
        <div className="p-3 bg-indigo-50 rounded-lg text-indigo-600 shrink-0">
          <MapIcon size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-1">Interactive Skill Map</h1>
          <p className="text-slate-600">
            Visualize your current skills, mastery levels, and how they connect to your active learning path.
          </p>
        </div>
      </div>

      <SkillGraph skills={skills} plan={planData || null} />
    </div>
  );
}
