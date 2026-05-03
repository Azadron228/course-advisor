import { notFound } from 'next/navigation';
import { LessonSidebarChat } from '@/components/features/lesson-sidebar-chat';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';

// Simple fetch function for server components
async function getLesson(id: string) {
  const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
  const res = await fetch(`${backendUrl}/api/v1/lessons/${id}`, {
    cache: 'no-store'
  });
  if (!res.ok) return null;
  return res.json();
}

export default async function LessonPage({
  params
}: {
  params: { locale: string; id: string }
}) {
  // Await the params object before accessing properties
  const { locale, id } = await params;
  
  const lesson = await getLesson(id);

  if (!lesson) {
    notFound();
  }

  // Background trigger for test generation is handled by the backend when fetching the lesson
  // But actually the endpoint is /lessons/{id}/test. Let's call it just to trigger it asynchronously
  fetch(`${process.env.BACKEND_URL || 'http://backend:8000'}/api/v1/lessons/${id}/test`, {
    cache: 'no-store'
  }).catch(() => {});

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      {/* Main Content (70%) */}
      <div className="w-[70%] h-full overflow-y-auto p-8 border-r border-border scroll-smooth">
        <div className="max-w-3xl mx-auto space-y-8">
          <div className="space-y-4 pb-8 border-b border-border">
            <h1 className="text-4xl font-extrabold tracking-tight">{lesson.filename}</h1>
            <div className="flex items-center gap-4 text-sm text-muted">
              <span>Status: {lesson.status}</span>
            </div>
          </div>
          
          <div className="prose dark:prose-invert max-w-none text-foreground leading-relaxed">
            <ReactMarkdown>{lesson.content}</ReactMarkdown>
          </div>

          <div className="mt-16 p-8 bg-surface rounded-2xl border border-border shadow-sm flex flex-col items-center justify-center text-center space-y-6">
            <h2 className="text-2xl font-bold">Knowledge Check</h2>
            <p className="text-muted">Test your understanding of this material with a quick AI-generated practice test.</p>
            <Link 
              href={`/${locale}/lesson/${id}/test`}
              className="px-8 py-3 bg-primary text-white rounded-xl font-semibold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
            >
              Start Practice Test
            </Link>
          </div>
        </div>
      </div>

      {/* Sidebar Chat (30%) */}
      <div className="w-[30%] h-full bg-surface/50">
        <LessonSidebarChat lessonId={id} lessonContent={lesson.content} />
      </div>
    </div>
  );
}
