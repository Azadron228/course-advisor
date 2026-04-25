import { cookies } from 'next/headers';
import { PlanStepper, LearningPlan } from '@/components/features/plan-stepper';
import { redirect } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

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

export default async function PlanPage() {
  const plan = await getLearningPlan();

  return (
    <div className="py-4">
      {plan ? (
        <PlanStepper plan={plan} />
      ) : (
        <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm text-center">
          <h2 className="text-xl font-bold text-slate-900 mb-4">No Active Learning Plan</h2>
          <p className="text-slate-600 mb-6">
            You haven&apos;t generated a learning plan yet. Tell us what you want to learn to get started.
          </p>
          <a
            href="/dashboard"
            className="inline-flex items-center justify-center px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Go to Dashboard
          </a>
        </div>
      )}
    </div>
  );
}
