import { cookies } from 'next/headers';
import { PlanList, LearningPlanSummary } from '@/components/features/plan-list';
import { redirect } from 'next/navigation';
import { API_BASE_URL } from '@/lib/config';

async function getLearningPlans(token: string): Promise<LearningPlanSummary[]> {
  const response = await fetch(`${API_BASE_URL}/learning-plan/`, {
    headers: { 'Authorization': `Bearer ${token}` },
    next: { revalidate: 0 }
  });
  if (!response.ok) return [];
  return response.json();
}

export default async function PlanPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) redirect('/login');

  const plans = await getLearningPlans(token);
  return <PlanList plans={plans} />;
}
