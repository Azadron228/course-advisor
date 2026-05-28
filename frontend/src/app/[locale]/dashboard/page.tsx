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

interface LearningPlanSummary {
  id: number;
  goal: string;
  is_active: boolean;
  last_interacted_at: string;
  step_count: number;
}

interface UserProfile {
  full_name: string | null;
  onboarding_completed: boolean;
}

async function getDashboardData() {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  try {
    const [plansRes, userRes] = await Promise.all([
      fetch(`${API_BASE_URL}/learning-plan/`, {
        headers: { 'Authorization': `Bearer ${token}` },
        next: { revalidate: 0 }
      }),
      fetch(`${API_BASE_URL}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` },
        cache: 'no-store'
      })
    ]);

    const plans: LearningPlanSummary[] = plansRes.ok ? await plansRes.json() : [];
    const user: UserProfile = userRes.ok ? await userRes.json() : { full_name: null, onboarding_completed: true };
    
    const activePlan = plans.find(p => p.is_active);

    return {
      active_plan_title: activePlan?.goal || null,
      progress_percentage: 0, // Mocked for now as it was in backend
      full_name: user.full_name,
      onboarding_completed: user.onboarding_completed
    };
  } catch (error) {
    console.error('Dashboard data fetch error:', error);
    return {
      active_plan_title: null,
      progress_percentage: 0,
      full_name: null,
      onboarding_completed: true
    };
  }
}

export default async function DashboardPage() {
  const data = await getDashboardData();
  const t = await getTranslations('Dashboard');
  const tNav = await getTranslations('Navigation');
  const tCommon = await getTranslations('Common');

  const welcomeMessage = t('welcomeBackUser', { name: data.full_name || t('student') });

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
        welcomeMessage={welcomeMessage}
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
