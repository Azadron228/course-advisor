'use server';

import { revalidatePath } from 'next/cache';
import { cookies } from 'next/headers';
import { API_BASE_URL } from '@/lib/config';

export async function updateStepStatus(order: number, status: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/learning-plan/steps/${order}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ status }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to update step status');
  }

  revalidatePath('/plan');
  return { success: true };
}

export async function generatePlanAction(data: {
  full_name: string;
  career_goal: string;
  interests: string[];
}) {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) {
    throw new Error('Authentication required');
  }

  // 1. Update user profile
  const profileResponse = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      full_name: data.full_name,
      career_goal: data.career_goal,
      onboarding_completed: true,
    }),
  });

  if (!profileResponse.ok) {
    throw new Error('Failed to update profile');
  }

  // 2. Generate learning plan
  const planResponse = await fetch(`${API_BASE_URL}/learning-plan/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!planResponse.ok) {
    throw new Error('Failed to generate learning plan');
  }

  revalidatePath('/plan');
  revalidatePath('/dashboard');
  return { success: true };
}
