'use client';

import { LearningPlan } from '@/components/features/plan-stepper';
import { ChevronRight, Calendar, BookOpen, Clock, Zap } from 'lucide-react';
import { Link } from '@/i18n/routing';

export function PlanList({ plans }: { plans: LearningPlan[] }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-extrabold text-slate-900">My Paths</h1>
        <Link 
          href="/plan?view=new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100"
        >
          <Zap className="w-4 h-4" />
          Create New Plan
        </Link>
      </div>

      <div className="grid gap-4">
        {plans.length === 0 ? (
          <div className="bg-white p-12 rounded-2xl border-2 border-dashed border-slate-200 text-center">
            <BookOpen className="w-16 h-16 text-slate-200 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-slate-900">No paths yet</h3>
            <p className="text-slate-500 mb-6 max-w-xs mx-auto">Start by generating your first personalized learning path.</p>
            <Link 
              href="/plan?view=new"
              className="inline-flex items-center text-indigo-600 font-bold hover:underline"
            >
              Get started <ChevronRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
        ) : (
          plans.map((plan) => (
            <Link 
              key={plan.id}
              href={`/plan?id=${plan.id}`}
              className="group flex items-center justify-between p-6 bg-white rounded-2xl border border-slate-200 hover:border-indigo-300 hover:shadow-xl hover:shadow-indigo-50/50 transition-all"
            >
              <div className="flex-1 min-w-0">
                <h3 className="text-xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors truncate mb-2">
                  {plan.goal}
                </h3>
                <div className="flex flex-wrap gap-4 text-xs font-semibold text-slate-500">
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-100 rounded-md">
                    {plan.skill_level}
                  </span>
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-100 rounded-md">
                    <Clock className="w-3 h-3" /> {plan.study_time}h/week
                  </span>
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-100 rounded-md">
                    {plan.steps.length} Steps
                  </span>
                </div>
              </div>
              <div className="ml-6 flex items-center justify-center w-12 h-12 rounded-full bg-slate-50 group-hover:bg-indigo-50 text-slate-400 group-hover:text-indigo-600 transition-all">
                <ChevronRight className="w-6 h-6 group-hover:translate-x-0.5 transition-transform" />
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
