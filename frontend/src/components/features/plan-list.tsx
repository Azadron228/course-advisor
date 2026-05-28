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
  completed_steps: number;
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

  const activePlan = plans.find((p) => p.is_active);
  const otherPlans = plans.filter((p) => !p.is_active);

  return (
    <div className="space-y-10">
      {/* Title Header */}
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

      {/* Main Content Area */}
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
        <div className="space-y-10">
          {/* Featured Active Journey Card */}
          {activePlan && (
            <div className="relative overflow-hidden rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/10 via-primary/5 to-surface p-8 shadow-xl shadow-primary/5 group">
              <div className="relative z-10 space-y-6">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-primary text-white text-[10px] font-black uppercase tracking-widest rounded-full animate-pulse">
                    {t('activeJourney')}
                  </span>
                </div>

                <div>
                  <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-foreground group-hover:text-primary transition-colors">
                    {activePlan.goal}
                  </h2>
                </div>

                {(() => {
                  const completed = activePlan.completed_steps || 0;
                  const total = activePlan.step_count || 0;
                  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
                  return (
                    <div className="space-y-3">
                      <div className="flex justify-between text-xs font-bold text-muted">
                        <span>{t('completedSteps', { completed, total, percent })}</span>
                      </div>
                      <div className="w-full h-3 bg-muted/20 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-primary to-emerald-500 rounded-full transition-all duration-1000 ease-out" 
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  );
                })()}

                <div className="flex flex-wrap gap-4 items-center justify-between pt-2">
                  <Link
                    href={`/plan/${activePlan.id}`}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white text-xs font-black uppercase tracking-wider rounded-xl hover:bg-primary/90 hover:shadow-lg hover:shadow-primary/20 transition-all active:scale-95 shadow-md"
                  >
                    {t('resumeJourney')}
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                  
                  <DeleteButton planId={activePlan.id} />
                </div>
              </div>
            </div>
          )}

          {/* List of other plans */}
          {otherPlans.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xs font-black text-muted uppercase tracking-[0.2em]">{activePlan ? t('otherPaths') : t('allPaths')}</h2>
              <div className="grid gap-4">
                {otherPlans.map((plan) => (
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
                        {plan.step_count > 0 && (
                          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                            {(() => {
                              const completed = plan.completed_steps || 0;
                              const total = plan.step_count || 0;
                              return total > 0 ? Math.round((completed / total) * 100) : 0;
                            })()}% {t('progress').toLowerCase()}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-6 flex items-center gap-2 z-10">
                      <DeleteButton planId={plan.id} />
                      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-input group-hover:bg-primary/10 text-muted group-hover:text-primary transition-all pointer-events-none">
                        <ChevronRight className="w-6 h-6 group-hover:translate-x-0.5 transition-transform" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
