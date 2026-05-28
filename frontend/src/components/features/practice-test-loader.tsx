
'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Loader2 } from 'lucide-react';
import { API_BASE_URL } from '@/lib/config';
import Cookies from 'js-cookie';
import { PracticeTestUI } from './practice-test-ui';

type QuestionType = 'multiple_choice' | 'short_answer' | 'true_false' | 'fill_in_the_blank';

interface Question {
  type: QuestionType;
  question: string;
  options?: string[];
  correct_answer_index?: number;
  correct_answer_text?: string;
  explanation: string;
}

interface TestResult {
  question_index: number;
  user_answer: number | string;
  is_correct: boolean;
  correct_answer_text?: string;
  explanation?: string;
}

interface TestData {
  questions: Question[];
  last_attempt?: {
    score: number;
    results: TestResult[];
  };
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
  const t = useTranslations('Plan');
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
        <p className="text-sm text-muted font-medium">{t('generatingPracticeTest')}</p>
      </div>
    );
  }

  if (error || !testData) {
    return (
      <div className="p-6 border border-red-500/20 bg-red-500/5 rounded-xl text-center">
        <p className="text-sm text-red-500 font-medium">{t('failedToLoadPracticeTest')}</p>
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