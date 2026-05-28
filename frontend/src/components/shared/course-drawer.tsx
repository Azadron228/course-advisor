'use client';

import { X, Loader2, BookOpen } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiClient } from '@/lib/api-client';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';

interface CourseMaterial {
  content: string;
}

interface Course {
  subject_name: string;
  description: string;
  materials: CourseMaterial[];
}

interface CourseDrawerProps {
  courseId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function CourseDrawer({ courseId, isOpen, onClose }: CourseDrawerProps) {
  const t = useTranslations('Plan');
  const { data: course, isLoading, isError } = useQuery({
    queryKey: ['courses', courseId],
    queryFn: () => apiClient.get<Course>(`/courses/${courseId}`),
    enabled: isOpen && !!courseId,
  });

  if (!isOpen) return null;

  const aggregatedMaterials = course?.materials?.map(m => m.content).join('\n\n---\n\n') || '';

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 bg-background/80 backdrop-blur-sm transition-opacity" onClick={onClose} />
      
      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-2xl transform transition-all animate-in slide-in-from-right duration-300">
          <div className="flex h-full flex-col bg-surface shadow-2xl border-l border-border">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border bg-surface/50">
              <div className="flex items-center gap-3">
                <div className="bg-primary/10 p-2 rounded-lg text-primary">
                  <BookOpen className="w-5 h-5" />
                </div>
                <h2 className="text-xl font-bold text-foreground">{t('materials')}</h2>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-muted rounded-full text-muted transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-8">
              {isLoading ? (
                <div className="h-full flex flex-col items-center justify-center text-muted gap-3">
                  <Loader2 className="w-8 h-8 animate-spin" />
                  <p className="font-medium">{t('loadingMaterials')}</p>
                </div>
              ) : isError ? (
                <div className="p-4 bg-destructive/10 text-destructive rounded-xl border border-destructive/20">
                  {t('loadError')}
                </div>
              ) : course && (
                <div className="space-y-8">
                  <div>
                    <h1 className="text-3xl font-extrabold text-foreground mb-4">{course.subject_name}</h1>
                    <p className="text-lg text-muted leading-relaxed">{course.description}</p>
                  </div>

                  <div className="prose dark:prose-invert max-w-none border-t border-border pt-8 text-foreground">
                    {aggregatedMaterials ? (
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeRaw]}
                        components={{
                          code({ node, inline, className, children, ...props }: any) {
                            const match = /language-(\w+)/.exec(className || '');
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={vscDarkPlus}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            );
                          },
                        }}
                      >
                        {aggregatedMaterials}
                      </ReactMarkdown>
                    ) : (
                      <p className="italic text-muted">{t('noMaterials')}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
