import { cookies } from 'next/headers';
import { LearningPlanGenerator } from '@/components/features/learning-plan-generator';
import { redirect } from 'next/navigation';

export default async function NewPlanPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) redirect('/login');

  return <LearningPlanGenerator />;
}
