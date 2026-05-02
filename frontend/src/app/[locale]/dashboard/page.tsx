import React from 'react';
import { cookies } from 'next/headers';
import Link from 'next/link';
import { getTranslations } from 'next-intl/server';
import { 
  ClipboardList, 
  MessageSquare, 
  ArrowRight,
  TrendingUp,
  Award,
  Zap
} from 'lucide-react';
import { DashboardSummary } from '@/components/features/dashboard-summary';
import { API_BASE_URL } from '@/lib/config';

interface DashboardResponse {
  active_plan_title: string | null;
  progress_percentage: number;
  welcome_message: string;
  onboarding_completed: boolean;
}

async function getDashboardData(): Promise<DashboardResponse> {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      next: { revalidate: 0 } // Disable cache for dashboard to ensure real-time progress
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch dashboard: ${response.statusText}`);
    }

    return response.json();
  } catch (error) {
    console.error('Dashboard data fetch error:', error);
    // Return fallback data in case of error
    return {
      active_plan_title: null,
      progress_percentage: 0,
      welcome_message: "Welcome back!",
      onboarding_completed: true
    };
  }
}

export default async function DashboardPage() {
  const data = await getDashboardData();
  const t = await getTranslations('Dashboard');
  const tNav = await getTranslations('Navigation');
  const tCommon = await getTranslations('Common');

  const navCards = [
    {
      title: tNav('learningPlan'),
      description: t('learningPlanDesc'),
      href: "/plan",
      icon: ClipboardList,
      color: "bg-blue-50 text-blue-600",
      borderColor: "border-blue-100"
    },
    {
      title: tNav('aiAdvisor'),
      description: t('aiAdvisorDesc'),
      href: "/chat",
      icon: MessageSquare,
      color: "bg-purple-50 text-purple-600",
      borderColor: "border-purple-100"
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <DashboardSummary 
        welcomeMessage={data.welcome_message}
        activePlanTitle={data.active_plan_title}
        progressPercentage={data.progress_percentage}
      />

      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">{tCommon('navHub')}</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {navCards.map((card) => (
            <Link 
              key={card.title} 
              href={card.href}
              className="group relative flex flex-col rounded-xl border border-slate-200 dark:border-slate-800 bg-surface p-6 shadow-sm transition-all hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-md"
            >
              <div className={`mb-4 flex h-12 w-12 items-center justify-center rounded-lg ${card.color}`}>
                <card.icon className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-lg font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                {card.title}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4 flex-1">
                {card.description}
              </p>
              <div className="flex items-center text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                {t('goTo')} {card.title}
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
