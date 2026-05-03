import { notFound } from 'next/navigation';
import { PracticeTestUI } from '@/components/features/practice-test-ui';
import Link from 'next/link';
import { API_BASE_URL } from '@/lib/config';

async function getPracticeTest(lessonId: string) {
  const res = await fetch(`${API_BASE_URL}/lessons/${lessonId}/test`, {
    cache: 'no-store'
  });
  if (!res.ok) {
    if (res.status === 404) return null; // Test not generated yet
    throw new Error('Failed to fetch test');
  }
  return res.json();
}

export default async function PracticeTestPage({
  params
}: {
  params: { locale: string; id: string; lessonId: string }
}) {
  const { locale, id, lessonId } = await params;
  const testData = await getPracticeTest(lessonId);

  if (!testData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-background p-8 text-center space-y-6">
        <h1 className="text-3xl font-bold">Generating Practice Test...</h1>
        <p className="text-muted max-w-md">Your practice test is being created in the background. Please wait a moment and try again.</p>
        <Link 
          href={`/${locale}/plan/${id}/lessons/${lessonId}`}
          className="text-primary font-medium hover:underline"
        >
          Return to Lesson
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-2xl bg-background rounded-3xl shadow-xl border border-border p-6 sm:p-10">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold">Knowledge Check</h1>
          <Link 
            href={`/${locale}/plan/${id}/lessons/${lessonId}`}
            className="text-sm font-medium text-muted hover:text-foreground transition-colors"
          >
            Exit Test
          </Link>
        </div>
        
        <PracticeTestUI 
          planId={id}
          lessonId={lessonId} 
          locale={locale}
          testData={testData.content} 
        />
      </div>
    </div>
  );
}
