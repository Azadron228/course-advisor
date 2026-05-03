import { cookies } from 'next/headers';
import { PlanStepper, LearningPlan } from '@/components/features/plan-stepper';
import { redirect } from 'next/navigation';
import { API_BASE_URL } from '@/lib/config';

async function getLearningPlanById(token: string, id: string): Promise<LearningPlan | null> {
  const response = await fetch(`${API_BASE_URL}/learning-plan/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` },
    next: { revalidate: 0 }
  });
  if (!response.ok) return null;
  return response.json();
}

export default async function PlanDetailPage({ 
  params 
}: { 
  params: { id: string } 
}) {
  const { id } = await params;
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) redirect('/login');

  const plan = await getLearningPlanById(token, id);
  if (!plan) redirect('/plan');

  return <PlanStepper plan={plan} />;
}
