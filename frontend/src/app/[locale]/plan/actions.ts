'use server';

import { revalidatePath } from 'next/cache';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { API_BASE_URL } from '@/lib/config';

export async function updateStepStatus(planId: number, order: number, status: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/learning-plan/${planId}/steps/${order}`, {
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

export async function generatePlanAction(formData: FormData) {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) throw new Error('Authentication required');

  // 1. If file, call parser
  const file = formData.get('transcript') as File | null;
  let parsedTranscript = null;
  if (file && file.size > 0) {
    const parserFormData = new FormData();
    parserFormData.append('file', file);
    try {
      const parseResponse = await fetch(`${API_BASE_URL}/parser/parse-transcript`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: parserFormData
      });
      
      if (parseResponse.ok) {
        parsedTranscript = await parseResponse.json();
      } else {
        console.warn('Transcript parsing failed, continuing without it');
      }
    } catch (e) {
      console.error('Transcript parsing error:', e);
    }
  }

  // 2. Generate learning plan with specific params
  const goal = formData.get('goal') as string;
  const skill_level = formData.get('skill_level') as string;
  const learning_style = formData.get('learning_style') as string;
  const study_time = Number(formData.get('study_time'));
  const interests = JSON.parse(formData.get('interests') as string);
  const language = formData.get('language') as string || 'en';

  const generateResponse = await fetch(`${API_BASE_URL}/learning-plan/generate`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json' 
    },
    body: JSON.stringify({
      goal,
      skill_level,
      learning_style,
      study_time,
      interests,
      transcript: parsedTranscript,
      language
    })
  });

  if (!generateResponse.ok) {
    const error = await generateResponse.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to generate plan');
  }

  const newPlan = await generateResponse.json();
  
  revalidatePath('/plan');
  revalidatePath('/dashboard');
  
  // Redirect to the new plan view
  redirect(`/plan/${newPlan.id}`);
}
