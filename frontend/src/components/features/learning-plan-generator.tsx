'use client';

import { useState, useRef, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslations, useLocale } from 'next-intl';
import { generatePlanAction } from '@/app/[locale]/plan/actions';
import { Loader2, ArrowRight, Tag, Sparkles, Upload, FileText, Check, CheckCircle2, Plus, X } from 'lucide-react';
import { cn } from '@/lib/utils';

const PREDEFINED_INTERESTS = [
  'AI & Machine Learning',
  'UX Design',
  'Data Science',
  'Marketing',
  'Web Development',
  'Cybersecurity',
  'Business Strategy',
  'Digital Art'
];

export function LearningPlanGenerator() {
  const t = useTranslations('Plan');
  const locale = useLocale();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [interests, setInterests] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const [isAddingInterest, setIsAddingInterest] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const interestInputRef = useRef<HTMLInputElement>(null);

  // Simulated progress bar effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSubmitting) {
      interval = setInterval(() => {
        setLoadingProgress((prev) => {
          if (prev >= 95) return prev;
          return prev + (prev < 50 ? 5 : prev < 80 ? 2 : 0.5);
        });
      }, 200);
    }
    return () => clearInterval(interval);
  }, [isSubmitting]);

  // Focus interest input when toggled
  useEffect(() => {
    if (isAddingInterest && interestInputRef.current) {
      interestInputRef.current.focus();
    }
  }, [isAddingInterest]);

  const formSchema = z.object({
    goal: z.string().min(5, t('validation.goalMinLength')),
    skill_level: z.enum(['Beginner', 'Intermediate', 'Advanced']),
    learning_style: z.enum(['Visual', 'Practical', 'Theoretical']),
    study_time: z.number().min(1).max(100),
  });

  type FormValues = z.infer<typeof formSchema>;

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { skill_level: 'Beginner', learning_style: 'Practical', study_time: 10 }
  });

  const handleAddInterest = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && currentTag.trim()) {
      e.preventDefault();
      toggleInterest(currentTag.trim());
      setCurrentTag('');
      setIsAddingInterest(false);
    } else if (e.key === 'Escape') {
      setIsAddingInterest(false);
      setCurrentTag('');
    }
  };

  const toggleInterest = (tag: string) => {
    if (interests.includes(tag)) {
      setInterests(interests.filter((t) => t !== tag));
    } else {
      setInterests([...interests, tag]);
    }
  };

  const onSubmit = async (data: FormValues) => {
    setLoadingProgress(0);
    setIsSubmitting(true);
    const formData = new FormData();
    formData.append('goal', data.goal);
    formData.append('skill_level', data.skill_level);
    formData.append('learning_style', data.learning_style);
    formData.append('study_time', data.study_time.toString());
    formData.append('interests', JSON.stringify(interests));
    formData.append('language', locale);
    if (file) formData.append('transcript', file);

    try {
      await generatePlanAction(formData);
    } catch (err) {
      console.error(err);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-extrabold text-foreground tracking-tight">{t('createNew')}</h1>
        <p className="text-muted-foreground text-xl">{t('defineGoals')}</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-10 bg-surface p-8 md:p-12 rounded-[2rem] border border-border shadow-2xl shadow-primary/5 dark:shadow-none">
        {isSubmitting && (
          <div className="space-y-3 animate-in fade-in duration-300">
            <div className="flex justify-between items-end">
              <p className="text-sm font-bold text-primary animate-pulse flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                {t('drafting')}
              </p>
              <span className="text-xs font-bold text-muted-foreground tracking-widest uppercase">{Math.round(loadingProgress)}%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
              <div 
                className="bg-primary h-full rounded-full transition-all duration-300 ease-out shadow-[0_0_10px_rgba(var(--primary),0.5)]"
                style={{ width: `${loadingProgress}%` }}
              />
            </div>
          </div>
        )}

        <div className="space-y-10">
          {/* Goal Section */}
          <div className="space-y-3">
            <label className="text-sm font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" /> {t('goalLabel')}
            </label>
            <textarea
              {...register('goal')}
              rows={4}
              className="w-full px-5 py-4 bg-input border border-border rounded-2xl focus:ring-2 focus:ring-primary outline-none transition-all text-foreground resize-none text-lg shadow-sm"
              placeholder={t('goalPlaceholder')}
            />
            {errors.goal && <p className="text-sm text-destructive font-medium">{errors.goal.message}</p>}
          </div>

          {/* Interests Section */}
          <div className="space-y-3">
            <label className="text-sm font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
              <Tag className="w-4 h-4 text-primary" /> {t('interestsLabel')}
            </label>
            
            <div className="flex flex-wrap gap-2 pt-1">
              {interests.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleInterest(tag)}
                  className="px-4 py-2 rounded-full text-xs font-bold border transition-all flex items-center gap-1.5 bg-primary text-white border-primary shadow-lg shadow-primary/20 animate-in zoom-in-95 duration-200"
                >
                  {tag}
                  {PREDEFINED_INTERESTS.includes(tag) ? <CheckCircle2 className="w-3 h-3" /> : <X className="w-3 h-3" />}
                </button>
              ))}
              
              {PREDEFINED_INTERESTS.filter(t => !interests.includes(t)).map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleInterest(tag)}
                  className="px-4 py-2 rounded-full text-xs font-bold border transition-all flex items-center gap-1.5 bg-surface border-border text-foreground hover:border-primary/50"
                >
                  {tag}
                </button>
              ))}

              {isAddingInterest ? (
                <div className="flex items-center gap-2 bg-surface border border-primary/50 rounded-full pl-4 pr-1 py-1 ring-2 ring-primary/20 animate-in zoom-in-95 duration-200">
                  <input
                    ref={interestInputRef}
                    value={currentTag}
                    onChange={(e) => setCurrentTag(e.target.value)}
                    onKeyDown={handleAddInterest}
                    onBlur={() => {
                      if (!currentTag.trim()) setIsAddingInterest(false);
                    }}
                    className="bg-transparent border-none outline-none text-xs font-bold w-24 placeholder:text-muted-foreground placeholder:font-medium"
                    placeholder="Topic..."
                  />
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => {
                        if (currentTag.trim()) {
                          toggleInterest(currentTag.trim());
                          setCurrentTag('');
                          setIsAddingInterest(false);
                        }
                      }}
                      className="p-1.5 bg-primary text-white rounded-full hover:bg-primary/90 transition-colors"
                    >
                      <Check className="w-3 h-3" />
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setIsAddingInterest(false);
                        setCurrentTag('');
                      }}
                      className="p-1.5 hover:bg-secondary/50 rounded-full transition-colors text-muted-foreground"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setIsAddingInterest(true)}
                  className="px-4 py-2 rounded-full text-xs font-bold border border-dashed border-primary/30 text-primary hover:bg-primary/5 hover:border-primary/50 transition-all flex items-center gap-1.5"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Add Topic
                </button>
              )}
            </div>
          </div>

          {/* Transcript Upload Section */}
          <div className="space-y-3 pt-4 border-t border-border/50">
            <label className="text-sm font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-primary" /> {t('academicTranscript')}
            </label>
            
            <div 
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "group relative border-2 border-dashed rounded-2xl p-10 transition-all cursor-pointer flex flex-col items-center justify-center text-center",
                file ? "border-primary bg-primary/5" : "border-border bg-input hover:border-primary hover:bg-primary/5"
              )}
            >
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".html"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              
              {file ? (
                <div className="flex flex-col items-center gap-2 text-primary">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                    <Check className="w-6 h-6" />
                  </div>
                  <p className="font-bold text-sm truncate max-w-sm">{file.name}</p>
                  <button 
                    type="button"
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    className="text-xs font-bold text-destructive hover:underline mt-2"
                  >
                    {t('removeFile')}
                  </button>
                </div>
              ) : (
                <>
                  <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center mb-4 transition-colors">
                    <Upload className="w-6 h-6 text-muted-foreground group-hover:text-primary" />
                  </div>
                  <p className="font-bold text-foreground group-hover:text-primary transition-colors">{t('clickToUpload')}</p>
                  <p className="text-[10px] text-muted-foreground mt-1 uppercase font-bold tracking-widest">{t('supportsHtml')}</p>
                </>
              )}
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed italic">{t('transcriptNote')}</p>
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full flex items-center justify-center gap-3 bg-primary hover:bg-primary/90 text-white font-extrabold py-5 rounded-2xl transition-all shadow-xl shadow-primary/20 disabled:opacity-50 hover:scale-[1.01] active:scale-[0.99]"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              {t('drafting')}
            </>
          ) : (
            <>
              <Sparkles className="w-6 h-6" />
              {t('generateButton')}
              <ArrowRight className="w-6 h-6" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
