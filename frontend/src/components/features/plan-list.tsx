'use client';

import { ChevronRight, BookOpen, Zap, Trash2, Loader2 } from 'lucide-react';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { useTransition } from 'react';
import { deletePlanAction } from '@/app/[locale]/plan/actions';

export interface LearningPlanSummary {
  id: number;
  goal: string;
  is_active: boolean;
  last_interacted_at: string;
  step_count: number;
}

function DeleteButton({ planId }: { planId: number }) {
  const [isPending, startTransition] = useTransition();

  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this learning plan?')) {
      startTransition(async () => {
        try {
          await deletePlanAction(planId);
        } catch (error) {
          console.error(error);
          alert('Failed to delete plan.');
        }
      });
    }
  };

  return (
    <button 
      onClick={handleDelete}
      disabled={isPending}
      className="p-3 rounded-full hover:bg-destructive/10 text-muted hover:text-destructive transition-colors disabled:opacity-50"
      aria-label="Delete Plan"
    >
      {isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Trash2 className="w-5 h-5" />}
    </button>
  );
}

export function PlanList({ plans }: { plans: LearningPlanSummary[] }) {
  const t = useTranslations('Plan');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-extrabold text-foreground">{t('myPaths')}</h1>
        <Link 
          href="/plan/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-white font-bold rounded-xl hover:bg-primary/90 transition-all shadow-lg shadow-primary/10 dark:shadow-none"
        >
          <Zap className="w-4 h-4" />
          {t('createNew')}
        </Link>
      </div>

      <div className="grid gap-4">
        {plans.length === 0 ? (
          <div className="bg-surface p-12 rounded-2xl border-2 border-dashed border-border text-center">
            <BookOpen className="w-16 h-16 text-muted/30 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-foreground">{t('noPaths')}</h3>
            <p className="text-muted mb-6 max-w-xs mx-auto">{t('startGenerating')}</p>
            <Link 
              href="/plan/new"
              className="inline-flex items-center text-primary font-bold hover:underline"
            >
              {t('getStarted')} <ChevronRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
        ) : (
          plans.map((plan) => (
            <div 
              key={plan.id}
              className="group relative flex items-center justify-between p-6 bg-surface rounded-2xl border border-border hover:border-primary hover:shadow-xl hover:shadow-primary/5 dark:hover:shadow-none transition-all overflow-hidden"
            >
              <Link 
                href={`/plan/${plan.id}`}
                className="absolute inset-0 z-0 rounded-2xl focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                aria-label={`View plan: ${plan.goal}`}
              />
              <div className="flex-1 min-w-0 z-10 pointer-events-none">
                <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors truncate mb-2">
                  {plan.goal}
                </h3>
                <div className="flex flex-wrap gap-4 text-xs font-semibold text-muted">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-muted/10 text-muted">
                    {t('stepsCount', { count: plan.step_count })}
                  </span>
                </div>
              </div>
              <div className="ml-6 flex items-center gap-2 z-10">
                <DeleteButton planId={plan.id} />
                <div className="flex items-center justify-center w-12 h-12 rounded-full bg-input group-hover:bg-primary/10 text-muted group-hover:text-primary transition-all pointer-events-none">
                  <ChevronRight className="w-6 h-6 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
