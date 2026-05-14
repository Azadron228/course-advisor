
'use client';

import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { API_BASE_URL } from '@/lib/config';
import Cookies from 'js-cookie';
import { PracticeTestUI } from './practice-test-ui';

interface Question {
  question: string;
  options: string[];
  correct_answer_index: number;
  explanation: string;
}

interface TestData {
  questions: Question[];
}

export function PracticeTestLoader({ 
  planId, 
  stepOrder, 
  locale,
  nextStepOrder
}: { 
  planId: string, 
  stepOrder: string, 
  locale: string,
  nextStepOrder?: string
}) {
  const [testData, setTestData] = useState<TestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function fetchTest() {
      try {
        const token = Cookies.get('token');
        const res = await fetch(`${API_BASE_URL}/learning-plan/${planId}/lessons/${stepOrder}/test`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!res.ok) {
          throw new Error('Failed to fetch test');
        }

        const data = await res.json();
        if (mounted) {
          setTestData(data);
          setLoading(false);
        }
      } catch (e) {
        console.error("Error fetching test:", e);
        if (mounted) {
          setError(true);
          setLoading(false);
        }
      }
    }

    fetchTest();

    return () => {
      mounted = false;
    };
  }, [planId, stepOrder]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 border border-border rounded-xl bg-surface/50">
        <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
        <p className="text-sm text-muted font-medium">Generating practice test...</p>
      </div>
    );
  }

  if (error || !testData) {
    return (
      <div className="p-6 border border-red-500/20 bg-red-500/5 rounded-xl text-center">
        <p className="text-sm text-red-500 font-medium">Failed to load practice test.</p>
      </div>
    );
  }

  return (
    <PracticeTestUI 
      planId={planId} 
      stepOrder={stepOrder} 
      locale={locale} 
      testData={testData}
      nextStepOrder={nextStepOrder}
    />
  );
}