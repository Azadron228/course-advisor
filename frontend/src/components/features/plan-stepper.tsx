'use client';

import { useState, useTransition } from 'react';
import { CheckCircle, Circle, Play, ExternalLink, Loader2, GraduationCap, ArrowRight, Award } from 'lucide-react';
import { updateStepStatus } from '@/app/[locale]/plan/actions';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';
import { useRouter, useParams } from 'next/navigation';

export interface LearningMaterial {
  title: string;
  description: string;
  url?: string;
  type: string;
}

export interface LearningPathStep {
  id: number | null;
  order: number;
  title: string;
  description: string;
  resource_id: string | null;
  is_external: boolean;
  external_url?: string;
  status: 'completed' | 'current' | 'upcoming';
  materials: LearningMaterial[];
  score?: number | null;
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
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

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
    if (step.is_external && step.external_url) {
       window.open(step.external_url, '_blank');
    } else if (step.id && plan.id) {
       router.push(`/${locale}/plan/${plan.id}/lessons/${step.id}?order=${step.order}`);
    }
  };

  if (!plan || !plan.steps || plan.steps.length === 0) {
    return (
      <div className="p-8 text-center bg-surface rounded-xl border border-border shadow-sm">
        <p className="text-muted">{t('notFound')}</p>
      </div>
    );
  }

  // Sort steps by order
  const sortedSteps = [...plan.steps].sort((a, b) => a.order - b.order);

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="bg-surface p-8 rounded-3xl border border-border shadow-xl shadow-primary/5 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-primary font-bold text-sm uppercase tracking-wider">
            <GraduationCap className="w-5 h-5" />
            Learning Journey
          </div>
          <h1 className="text-3xl font-black text-foreground">{plan.goal}</h1>
          <p className="text-muted font-medium">Follow this sequence of lessons to master your goal.</p>
        </div>
        
        <div className="flex gap-4">
          <div className="px-5 py-3 bg-input rounded-2xl border border-border flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-[10px] font-bold text-muted uppercase">Level</span>
            <span className="text-lg font-black text-foreground">{plan.skill_level}</span>
          </div>
          <div className="px-5 py-3 bg-primary/10 rounded-2xl border border-primary/20 flex flex-col items-center justify-center min-w-[100px]">
            <span className="text-[10px] font-bold text-primary uppercase">Progress</span>
            <span className="text-lg font-black text-primary">
              {Math.round((sortedSteps.filter(s => s.status === 'completed').length / sortedSteps.length) * 100)}%
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      {/* Lesson List */}
      <div className="space-y-4">
        {sortedSteps.map((step, index) => {
          const isCompleted = step.status === 'completed';
          const isCurrent = step.status === 'current';
          const hasScore = step.score !== null && step.score !== undefined;

          return (
            <div 
              key={step.order} 
              className={cn(
                "group relative flex items-center gap-6 p-6 rounded-2xl border transition-all duration-300",
                isCompleted ? "bg-success/5 border-success/20 opacity-90" : 
                isCurrent ? "bg-surface border-primary shadow-lg scale-[1.02] ring-1 ring-primary/20" : 
                "bg-surface/50 border-border"
              )}
            >
              {/* Number/Icon Indicator */}
              <div className="hidden sm:flex flex-shrink-0 w-12 h-12 rounded-full items-center justify-center font-black text-lg shadow-inner">
                {isCompleted ? (
                  <div className="bg-success text-white rounded-full p-2">
                    <CheckCircle className="w-6 h-6" />
                  </div>
                ) : isCurrent ? (
                  <div className="bg-primary text-white rounded-full p-3 animate-pulse">
                    <Play className="w-5 h-5 fill-current" />
                  </div>
                ) : (
                  <div className="bg-input text-muted border-2 border-border rounded-full w-full h-full flex items-center justify-center">
                    {index + 1}
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                   <span className={cn(
                     "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full",
                     isCompleted ? "bg-success/10 text-success" :
                     isCurrent ? "bg-primary/10 text-primary" :
                     "bg-muted/10 text-muted"
                   )}>
                     Lesson {index + 1}
                   </span>
                   {step.is_external && (
                     <span className="flex items-center gap-1 text-[10px] font-bold text-muted uppercase">
                       <ExternalLink className="w-3 h-3" /> External
                     </span>
                   )}
                </div>
                
                <h3 className={cn(
                  "text-xl font-bold truncate",
                  isCompleted ? "text-foreground" :
                  isCurrent ? "text-primary" :
                  "text-muted/80"
                )}>
                  {step.title}
                </h3>
                
                <p className="text-sm text-muted line-clamp-1 mt-1 font-medium">
                  {step.description}
                </p>
              </div>

              {/* Mark/Score */}
              <div className="flex flex-col items-end gap-3">
                {hasScore && (
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-tertiary/10 text-tertiary rounded-xl border border-tertiary/20">
                    <Award className="w-4 h-4" />
                    <span className="text-sm font-black">{step.score}%</span>
                  </div>
                )}
                
                {!isCompleted && !isCurrent ? (
                   <div className="text-[10px] font-bold text-muted/40 uppercase tracking-widest">Locked</div>
                ) : (
                  <button
                    onClick={() => handleViewResource(step)}
                    disabled={(!step.id && !step.external_url) || !plan.id}
                    className={cn(
                      "inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-md",
                      isCompleted ? "bg-success/10 text-success hover:bg-success/20" :
                      "bg-primary text-white hover:bg-primary/90 hover:translate-x-1",
                      ((!step.id && !step.external_url) || !plan.id) && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    {isCompleted ? 'Review' : 'Start Lesson'}
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
