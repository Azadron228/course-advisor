import { cookies } from 'next/headers';
import { PlanStepper, LearningPlan } from '@/components/features/plan-stepper';
import { CreatePlanForm } from '@/components/features/create-plan-form';
import { redirect } from 'next/navigation';
import { API_BASE_URL } from '@/lib/config';

async function getLearningPlan(): Promise<LearningPlan | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) {
    redirect('/login');
  }

  try {
    const response = await fetch(`${API_BASE_URL}/learning-plan/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Cache-Control': 'no-cache',
      },
    });

    if (response.status === 401) {
      redirect('/login');
    }

    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error('Failed to fetch learning plan');
    }

    return response.json();
  } catch (error) {
    console.error('Error fetching learning plan:', error);
    return null;
  }
}

async function getUser() {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) return null;

  const response = await fetch(`${API_BASE_URL}/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) return null;
  return response.json();
}

export default async function PlanPage() {
  const [plan, user] = await Promise.all([getLearningPlan(), getUser()]);

  return (
    <div className="py-4">
      {plan ? (
        <PlanStepper plan={plan} />
      ) : (
        <CreatePlanForm initialName={user?.full_name} />
      )}
    </div>
  );
}
