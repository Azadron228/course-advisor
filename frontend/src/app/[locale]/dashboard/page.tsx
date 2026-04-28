import React from 'react';
import { cookies } from 'next/headers';
import Link from 'next/link';
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

  const navCards = [
    {
      title: "Learning Plan",
      description: "Continue your structured learning path and track daily goals.",
      href: "/plan",
      icon: ClipboardList,
      color: "bg-blue-50 text-blue-600",
      borderColor: "border-blue-100"
    },
    {
      title: "AI Advisor",
      description: "Chat with your personal assistant for guidance and help.",
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
        <h2 className="text-xl font-bold text-slate-900">Navigation Hub</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {navCards.map((card) => (
            <Link 
              key={card.title} 
              href={card.href}
              className="group relative flex flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-indigo-300 hover:shadow-md"
            >
              <div className={`mb-4 flex h-12 w-12 items-center justify-center rounded-lg ${card.color}`}>
                <card.icon className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                {card.title}
              </h3>
              <p className="text-sm text-slate-500 mb-4 flex-1">
                {card.description}
              </p>
              <div className="flex items-center text-sm font-semibold text-indigo-600">
                Go to {card.title}
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Optional: Placeholder for additional dashboard content */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-xl border border-dashed border-slate-300 p-8 flex flex-col items-center justify-center text-center">
          <TrendingUp className="h-10 w-10 text-slate-300 mb-3" />
          <h4 className="font-medium text-slate-900">Skill Insights coming soon</h4>
          <p className="text-sm text-slate-500">Advanced analytics for your learning journey.</p>
        </div>
        <div className="rounded-xl border border-dashed border-slate-300 p-8 flex flex-col items-center justify-center text-center">
          <Award className="h-10 w-10 text-slate-300 mb-3" />
          <h4 className="font-medium text-slate-900">Leaderboards</h4>
          <p className="text-sm text-slate-500">Compete with other learners in your field.</p>
        </div>
        <div className="rounded-xl border border-dashed border-slate-300 p-8 flex flex-col items-center justify-center text-center">
          <Zap className="h-10 w-10 text-slate-300 mb-3" />
          <h4 className="font-medium text-slate-900">Quick Actions</h4>
          <p className="text-sm text-slate-500">Resume your last lesson with one click.</p>
        </div>
      </div>
    </div>
  );
}
