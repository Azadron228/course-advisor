import { cookies } from 'next/headers';
import { PlanStepper, LearningPlan } from '@/components/features/plan-stepper';
import { PlanList } from '@/components/features/plan-list';
import { LearningPlanGenerator } from '@/components/features/learning-plan-generator';
import { redirect } from 'next/navigation';
import { API_BASE_URL } from '@/lib/config';

async function getLearningPlans(token: string): Promise<LearningPlan[]> {
  const response = await fetch(`${API_BASE_URL}/learning-plan/`, {
    headers: { 'Authorization': `Bearer ${token}` },
    next: { revalidate: 0 }
  });
  if (!response.ok) return [];
  return response.json();
}

async function getLearningPlanById(token: string, id: string): Promise<LearningPlan | null> {
  const response = await fetch(`${API_BASE_URL}/learning-plan/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` },
    next: { revalidate: 0 }
  });
  if (!response.ok) return null;
  return response.json();
}

export default async function PlanPage({ searchParams }: { searchParams: Promise<{ id?: string, view?: string }> }) {
  const { id, view } = await searchParams;
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) redirect('/login');

  if (view === 'new') return <LearningPlanGenerator />;

  if (id) {
    const plan = await getLearningPlanById(token, id);
    if (!plan) redirect('/plan');
    return <PlanStepper plan={plan} />;
  }

  const plans = await getLearningPlans(token);
  return <PlanList plans={plans} />;
}
