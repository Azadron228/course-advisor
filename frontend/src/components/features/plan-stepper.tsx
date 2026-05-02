'use client';

import { useState, useTransition } from 'react';
import { CheckCircle, Circle, Play, ExternalLink, Loader2, BookOpen } from 'lucide-react';
import { updateStepStatus } from '@/app/[locale]/plan/actions';
import { cn } from '@/lib/utils';
import { CourseDrawer } from '@/components/shared/course-drawer';
import { useTranslations } from 'next-intl';

export interface LearningMaterial {
  title: string;
  description: string;
  url?: string;
  type: string;
}

export interface LearningPathStep {
  order: number;
  title: string;
  description: string;
  resource_id: string | null;
  is_external: boolean;
  status: 'completed' | 'current' | 'upcoming';
  materials: LearningMaterial[];
}

export interface LearningPlan {
  id: number | null;
  goal: string;
  steps: LearningPathStep[];
  is_active: boolean;
  skill_level: string;
  learning_style: string;
  study_time: number;
  interests: string[];
}

interface PlanStepperProps {
  plan: LearningPlan;
}

export function PlanStepper({ plan }: PlanStepperProps) {
  const t = useTranslations('Plan');
  const tCommon = useTranslations('Common');
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleMarkComplete = async (order: number) => {
    if (!plan.id) return;
    setError(null);
    startTransition(async () => {
      try {
        await updateStepStatus(plan.id!, order, 'completed');
      } catch (err) {
        setError(err instanceof Error ? err.message : tCommon('error'));
      }
    });
  };

  const handleViewResource = (step: LearningPathStep) => {
    if (step.is_external && step.resource_id) {
       window.open(step.resource_id, '_blank');
    } else if (step.resource_id) {
       setSelectedCourseId(step.resource_id);
       setIsDrawerOpen(true);
    }
  };

  if (!plan || !plan.steps || plan.steps.length === 0) {
    return (
      <div className="p-8 text-center bg-surface dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <p className="text-slate-500 dark:text-slate-400">{t('notFound')}</p>
      </div>
    );
  }

  // Sort steps by order
  const sortedSteps = [...plan.steps].sort((a, b) => a.order - b.order);

  return (
    <>
      <div className="space-y-6">
      <div className="bg-surface dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">{t('myPlan')}</h1>
        <p className="text-slate-600 dark:text-slate-400">{t('goalValue', { goal: plan.goal })}</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      <div className="relative">
        {/* Vertical line connecting steps */}
        <div 
          className="absolute left-6 top-4 bottom-4 w-0.5 bg-slate-200 dark:bg-slate-800" 
          aria-hidden="true"
        />

        <div className="space-y-8">
          {sortedSteps.map((step, index) => {
            const isCompleted = step.status === 'completed';
            const isCurrent = step.status === 'current';

            return (
              <div key={step.order} className="relative flex gap-6">
                <div className="flex-shrink-0 z-10">
                  {isCompleted ? (
                    <div className="bg-secondary/10 dark:bg-secondary/20 rounded-full p-2 text-secondary dark:text-secondary ring-4 ring-white dark:ring-slate-950">
                      <CheckCircle className="w-8 h-8" />
                    </div>
                  ) : isCurrent ? (
                    <div className="bg-indigo-100 dark:bg-indigo-900/30 rounded-full p-2 text-indigo-600 dark:text-indigo-400 ring-4 ring-white dark:ring-slate-950 animate-pulse">
                      <Play className="w-8 h-8 fill-current" />
                    </div>
                  ) : (
                    <div className="bg-surface dark:bg-slate-900 rounded-full p-2 text-slate-300 dark:text-slate-700 ring-4 ring-white dark:ring-slate-950 border-2 border-slate-200 dark:border-slate-800">
                      <Circle className="w-8 h-8" />
                    </div>
                  )}
                </div>

                <div className={cn(
                  "flex-1 p-6 rounded-xl border transition-all",
                  isCompleted ? "bg-secondary/5 dark:bg-secondary/10 border-secondary/20 dark:border-secondary/30" : 
                  isCurrent ? "bg-surface dark:bg-slate-900 border-indigo-200 dark:border-indigo-800 shadow-md ring-1 ring-indigo-50 dark:ring-indigo-900/20" : 
                  "bg-surface/50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-800 opacity-70"
                )}>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={cn(
                          "text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full",
                          isCompleted ? "bg-secondary/10 dark:bg-secondary/20 text-secondary" :
                          isCurrent ? "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400" :
                          "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                        )}>
                          {t('stepLabel', { index: index + 1 })}
                        </span>
                        {step.is_external && (
                          <span className="flex items-center gap-1 text-xs text-slate-400 dark:text-slate-500">
                            <ExternalLink className="w-3 h-3" /> {t('external')}
                          </span>
                        )}
                      </div>
                      <h3 className={cn(
                        "text-lg font-bold",
                        isCompleted ? "text-slate-900 dark:text-slate-100" :
                        isCurrent ? "text-indigo-900 dark:text-indigo-300" :
                        "text-slate-700 dark:text-slate-400"
                      )}>
                        {step.title}
                      </h3>
                    </div>
                    
                    {isCurrent && (
                      <button
                        onClick={() => handleMarkComplete(step.order)}
                        disabled={isPending}
                        className="inline-flex items-center justify-center px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer shadow-lg shadow-indigo-200 dark:shadow-none"
                      >
                        {isPending ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            {t('updating')}
                          </>
                        ) : (
                          t('markComplete')
                        )}
                      </button>
                    )}
                  </div>
                  
                  <p className={cn(
                    "mt-3 text-sm leading-relaxed",
                    isCompleted ? "text-slate-600 dark:text-slate-300" :
                    isCurrent ? "text-slate-600 dark:text-slate-300" :
                    "text-slate-500 dark:text-slate-400"
                  )}>
                    {step.description}
                  </p>

                  {step.materials && step.materials.length > 0 && (
                    <div className="mt-4 space-y-3">
                      <h4 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{t('materials')}</h4>
                      {step.materials.map((mat, midx) => (
                        <div key={midx} className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{mat.title}</span>
                            {mat.url && (
                              <a href={mat.url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500">
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                          <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{mat.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {step.resource_id && (
                    <div className="mt-4 flex items-center gap-2">
                      <button 
                        onClick={() => handleViewResource(step)}
                        className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 hover:underline inline-flex items-center gap-1 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
                      >
                        {step.is_external ? t('openExternal') : t('viewMaterials')} 
                        {step.is_external ? (
                          <ExternalLink className="w-3 h-3 ml-1" />
                        ) : (
                          <BookOpen className="w-3 h-3 ml-1" />
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>

    <CourseDrawer 
      courseId={selectedCourseId} 
      isOpen={isDrawerOpen} 
      onClose={() => setIsDrawerOpen(false)} 
    />
  </>
);
}
