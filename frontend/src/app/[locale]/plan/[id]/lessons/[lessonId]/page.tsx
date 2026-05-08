import { notFound, redirect } from 'next/navigation';
import { LessonSidebarChat } from '@/components/features/lesson-sidebar-chat';
import { PracticeTestLoader } from '@/components/features/practice-test-loader';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import Link from 'next/link';
import { API_BASE_URL } from '@/lib/config';
import { cookies } from 'next/headers';
import { ExternalLink, Video, BookOpen, Globe, ArrowLeft } from 'lucide-react';
import { LearningPlan } from '@/components/features/plan-stepper';

// Simple fetch function for server components
async function getLesson(token: string, planId: string, stepOrder: string) {
  const res = await fetch(`${API_BASE_URL}/learning-plan/${planId}/lessons/${stepOrder}`, {
    headers: { 'Authorization': `Bearer ${token}` },
    cache: 'no-store'
  });
  if (!res.ok) return null;
  return res.json();
}

async function getLearningPlan(token: string, planId: string): Promise<LearningPlan | null> {
  const res = await fetch(`${API_BASE_URL}/learning-plan/${planId}`, {
    headers: { 'Authorization': `Bearer ${token}` },
    cache: 'no-store'
  });
  if (!res.ok) return null;
  return res.json();
}

export default async function LessonPage({
  params
}: {
  params: { locale: string; id: string; lessonId: string };
}) {
  // Await the params object before accessing properties
  const { locale, id, lessonId } = await params;
  const stepOrder = lessonId; // lessonId in path is now stepOrder

  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) redirect('/login');

  // Fetch both lesson and plan in parallel
  const [lesson, plan] = await Promise.all([
    getLesson(token, id, stepOrder),
    getLearningPlan(token, id)
  ]);

  if (!lesson) {
    notFound();
  }

  // Use the fetched lesson directly
  const currentStep = lesson;
  const databaseLessonId = lesson.id.toString();

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      <div className="w-[70%] h-full overflow-y-auto p-8 border-r border-border scroll-smooth">
        <div className="max-w-7xl mx-auto space-y-12">
          {/* Back to Plan */}
          <Link
            href={`/${locale}/plan/${id}`}
            className="inline-flex items-center gap-2 text-sm font-bold text-muted hover:text-primary transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Learning Plan
          </Link>

          {/* Plan-Specific Header */}
          <div className="space-y-4">
            {currentStep && (
              <div className="flex items-center gap-3 mb-2">
                <span className="px-3 py-1 bg-primary/10 text-primary text-[10px] font-black uppercase tracking-widest rounded-full">
                  Step {currentStep.order} of Journey
                </span>
                <span className="text-muted text-[10px] font-bold uppercase tracking-widest italic truncate max-w-[200px]">
                  {plan?.goal}
                </span>
              </div>
            )}

            <h1 className="text-4xl font-black tracking-tight text-foreground">
              {currentStep?.title || lesson.filename}
            </h1>

            {currentStep?.description && (
              <p className="text-lg text-muted font-medium leading-relaxed border-l-4 border-primary/20 pl-6 py-2">
                {currentStep.description}
              </p>
            )}
          </div>

          {/* AI-Generated Supplementary Materials */}
          {lesson?.materials && lesson.materials.length > 0 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="h-px flex-1 bg-border" />
                <h3 className="text-xs font-black text-muted uppercase tracking-[0.2em] whitespace-nowrap">Материалы</h3>
                <div className="h-px flex-1 bg-border" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {lesson.materials.map((material, idx) => (
                  <a
                    key={idx}
                    href={material.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex flex-col p-5 bg-surface border border-border rounded-2xl hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 transition-all"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-2 bg-primary/10 text-primary rounded-lg">
                        {material.type === 'video' ? <Video className="w-4 h-4" /> :
                          material.type === 'documentation' ? <Globe className="w-4 h-4" /> :
                            <BookOpen className="w-4 h-4" />}
                      </div>
                      <ExternalLink className="w-4 h-4 text-muted group-hover:text-primary transition-colors" />
                    </div>
                    <h4 className="font-bold text-sm mb-1 group-hover:text-primary transition-colors">{material.title}</h4>
                    <p className="text-xs text-muted line-clamp-2 leading-relaxed">{material.description}</p>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Main Lesson Content */}

          <div className="prose prose-slate dark:prose-invert max-w-none 
                prose-headings:font-bold prose-h1:text-3xl 
                prose-p:text-foreground">
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeRaw, rehypeKatex]}
            >
              {lesson.content}
            </ReactMarkdown>
          </div>

          {/* Practice Test */}
          {lesson.content && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="h-px flex-1 bg-border" />
                <h3 className="text-xs font-black text-muted uppercase tracking-[0.2em] whitespace-nowrap">
                  Practice Test
                </h3>
                <div className="h-px flex-1 bg-border" />
              </div>

              <div className="bg-surface border border-border rounded-3xl p-8">
                <PracticeTestLoader planId={id} lessonId={databaseLessonId} stepOrder={stepOrder} locale={locale} />
              </div>
            </div>
          )}


        </div>
      </div>

      {/* Sidebar Chat (30%) */}
      <div className="w-[30%] h-full bg-surface/50">
        <LessonSidebarChat lessonId={databaseLessonId} lessonContent={lesson.content} />
      </div>
    </div>
  );
}