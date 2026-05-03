'use client';

import { useState, useTransition } from 'react';
import { CheckCircle, Circle, Play, ExternalLink, Loader2, BookOpen } from 'lucide-react';
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
    if (step.is_external && step.resource_id) {
       window.open(step.resource_id, '_blank');
    } else if (step.resource_id && plan.id) {
       router.push(`/${locale}/plan/${plan.id}/lessons/${step.resource_id}`);
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
    <div className="space-y-6">
      <div className="bg-surface p-6 rounded-xl border border-border shadow-sm">
        <h1 className="text-2xl font-bold text-foreground mb-2">{t('myPlan')}</h1>
        <p className="text-muted">{t('goalValue', { goal: plan.goal })}</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      <div className="relative">
        {/* Vertical line connecting steps */}
        <div 
          className="absolute left-6 top-4 bottom-4 w-0.5 bg-border " 
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
                    <div className="bg-success/10 rounded-full p-2 text-success ring-4 ring-background">
                      <CheckCircle className="w-8 h-8" />
                    </div>
                  ) : isCurrent ? (
                    <div className="bg-primary/10 rounded-full p-2 text-primary ring-4 ring-background animate-pulse">
                      <Play className="w-8 h-8 fill-current" />
                    </div>
                  ) : (
                    <div className="bg-surface rounded-full p-2 text-muted/30 ring-4 ring-background border-2 border-border">
                      <Circle className="w-8 h-8" />
                    </div>
                  )}
                </div>

                <div className={cn(
                  "flex-1 p-6 rounded-xl border transition-all",
                  isCompleted ? "bg-success/5 border-success/20" : 
                  isCurrent ? "bg-surface border-primary/20 shadow-md ring-1 ring-primary/5" : 
                  "bg-surface/50 border-border opacity-70"
                )}>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={cn(
                          "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full",
                          isCompleted ? "bg-success/10 text-success" :
                          isCurrent ? "bg-primary/10 text-primary" :
                          "bg-muted/10 text-muted"
                        )}>
                          {t('stepLabel', { index: index + 1 })}
                        </span>
                        {step.is_external && (
                          <span className="flex items-center gap-1 text-xs text-muted">
                            <ExternalLink className="w-3 h-3" /> {t('external')}
                          </span>
                        )}
                      </div>
                      <h3 className={cn(
                        "text-lg font-bold",
                        isCompleted ? "text-foreground" :
                        isCurrent ? "text-primary" :
                        "text-muted"
                      )}>
                        {step.title}
                      </h3>
                    </div>
                    
                    {isCurrent && (
                      <button
                        onClick={() => handleMarkComplete(step.order)}
                        disabled={isPending}
                        className="inline-flex items-center justify-center px-4 py-2 bg-primary text-white text-sm font-semibold rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer shadow-lg shadow-primary/20 dark:shadow-none"
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
                    isCompleted ? "text-muted" :
                    isCurrent ? "text-muted" :
                    "text-muted"
                  )}>
                    {step.description}
                  </p>

                  {step.materials && step.materials.length > 0 && (
                    <div className="mt-4 space-y-3">
                      <h4 className="text-xs font-bold text-muted uppercase tracking-wider">{t('materials')}</h4>
                      {step.materials.map((mat, midx) => (
                        <div key={midx} className="p-3 bg-input/50 rounded-lg border border-border">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-bold text-foreground">{mat.title}</span>
                            {mat.url && (
                              <a href={mat.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:text-primary/80">
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                          <p className="text-xs text-muted leading-relaxed">{mat.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {step.resource_id && (
                    <div className="mt-4 flex items-center gap-2">
                      <button 
                        onClick={() => handleViewResource(step)}
                        className="text-xs font-bold text-primary hover:text-primary/80 hover:underline inline-flex items-center gap-1 bg-primary/10 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
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
  );
}
