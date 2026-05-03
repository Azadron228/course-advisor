import React from 'react';
import { cookies } from 'next/headers';
import Link from 'next/link';
import { getTranslations } from 'next-intl/server';
import { 
  ClipboardList, 
  MessageSquare, 
  ArrowRight
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
      color: "bg-primary/10 text-primary"
    },
    {
      title: tNav('aiAdvisor'),
      description: t('aiAdvisorDesc'),
      href: "/chat",
      icon: MessageSquare,
      color: "bg-secondary/10 text-secondary"
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
        <h2 className="text-xl font-bold text-foreground">{tCommon('navHub')}</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {navCards.map((card) => (
            <Link 
              key={card.title} 
              href={card.href}
              className="group relative flex flex-col rounded-xl border border-border bg-surface p-6 shadow-sm transition-all hover:border-primary/50 hover:shadow-md"
            >
              <div className={`mb-4 flex h-12 w-12 items-center justify-center rounded-lg ${card.color}`}>
                <card.icon className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-lg font-bold text-foreground group-hover:text-primary transition-colors">
                {card.title}
              </h3>
              <p className="text-sm text-muted mb-4 flex-1">
                {card.description}
              </p>
              <div className="flex items-center text-sm font-semibold text-primary">
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
