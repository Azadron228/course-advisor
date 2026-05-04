import { notFound, redirect } from 'next/navigation';
import { LessonSidebarChat } from '@/components/features/lesson-sidebar-chat';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';
import { API_BASE_URL } from '@/lib/config';
import { cookies } from 'next/headers';
import { Award, RefreshCcw, ExternalLink, Video, BookOpen, Globe, ArrowLeft } from 'lucide-react';
import { LearningPlan } from '@/components/features/plan-stepper';

// Simple fetch function for server components
async function getLesson(token: string, lessonId: string) {
  const res = await fetch(`${API_BASE_URL}/lessons/${lessonId}`, {
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
  params,
  searchParams
}: {
  params: { locale: string; id: string; lessonId: string };
  searchParams: { order?: string };
}) {
  // Await the params object before accessing properties
  const { locale, id, lessonId } = await params;
  const { order } = await searchParams;
  
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) redirect('/login');

  // Fetch both lesson and plan in parallel
  const [lesson, plan] = await Promise.all([
    getLesson(token, lessonId),
    getLearningPlan(token, id)
  ]);

  if (!lesson) {
    notFound();
  }

  // Find the specific step in the plan for this lesson using the lesson's unique ID
  const currentStep = plan?.steps.find(s => 
    s.id === parseInt(lessonId) || 
    (order && s.order === parseInt(order))
  );

  // Background trigger for test generation
  fetch(`${API_BASE_URL}/lessons/${lessonId}/test`, {
    headers: { 'Authorization': `Bearer ${token}` },
    cache: 'no-store'
  }).catch(() => {});

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      {/* Main Content (70%) */}
      <div className="w-[70%] h-full overflow-y-auto p-8 border-r border-border scroll-smooth">
        <div className="max-w-3xl mx-auto space-y-12">
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
          
          {/* Main Lesson Content */}
          <div className="bg-surface/30 rounded-3xl p-8 border border-border/50">
            <div className="flex items-center gap-2 mb-8 text-muted/60">
              <BookOpen className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-tighter">Internal University Resource: {lesson.filename}</span>
            </div>
            <div className="prose dark:prose-invert max-w-none text-foreground leading-relaxed">
              <ReactMarkdown>{lesson.content}</ReactMarkdown>
            </div>
          </div>

          {/* AI-Generated Supplementary Materials */}
          {currentStep?.materials && currentStep.materials.length > 0 && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="h-px flex-1 bg-border" />
                <h3 className="text-xs font-black text-muted uppercase tracking-[0.2em] whitespace-nowrap">Supplementary Materials</h3>
                <div className="h-px flex-1 bg-border" />
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {currentStep.materials.map((material, idx) => (
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

          {/* Knowledge Check */}
          {!lesson.is_external && (
            <div className="mt-16 p-8 bg-surface rounded-2xl border border-border shadow-sm flex flex-col items-center justify-center text-center space-y-6">
              <h2 className="text-2xl font-bold">Knowledge Check</h2>
              
              {lesson.score !== null && lesson.score !== undefined ? (
                <div className="space-y-6 w-full max-w-md mx-auto">
                  <div className="flex flex-col items-center gap-4 p-6 bg-success/5 rounded-3xl border border-success/20">
                    <div className="w-20 h-20 rounded-full bg-success/10 flex items-center justify-center text-success shadow-inner">
                      <Award className="w-10 h-10" />
                    </div>
                    <div>
                      <div className="text-3xl font-black text-success">{lesson.score}%</div>
                      <div className="text-sm font-bold text-success/60 uppercase tracking-widest">Mastery Score</div>
                    </div>
                  </div>
                  <p className="text-muted font-medium">You&apos;ve successfully completed this lesson&apos;s knowledge check!</p>
                  <Link 
                    href={`/${locale}/plan/${id}/lessons/${lessonId}/test`}
                    className="inline-flex items-center gap-2 px-8 py-3 bg-surface border border-border text-foreground rounded-xl font-bold hover:bg-muted/10 transition-all shadow-sm"
                  >
                    <RefreshCcw className="w-4 h-4" /> Retake Practice Test
                  </Link>
                </div>
              ) : (
                <>
                  <p className="text-muted max-w-sm mx-auto">Test your understanding of this material with a quick AI-generated practice test.</p>
                  <Link 
                    href={`/${locale}/plan/[id]/lessons/${lessonId}/test`}
                    className="px-8 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
                  >
                    Start Practice Test
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Sidebar Chat (30%) */}
      <div className="w-[30%] h-full bg-surface/50">
        <LessonSidebarChat lessonId={lessonId} lessonContent={lesson.content} />
      </div>
    </div>
  );
}
