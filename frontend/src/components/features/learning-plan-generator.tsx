'use client';

import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslations } from 'next-intl';
import { generatePlanAction } from '@/app/[locale]/plan/actions';
import { Loader2, ArrowRight, Tag, X, Sparkles, Upload, FileText, Check, Clock, Brain } from 'lucide-react';
import { cn } from '@/lib/utils';

const formSchema = z.object({
  goal: z.string().min(5, 'Goal must be at least 5 characters'),
  skill_level: z.enum(['Beginner', 'Intermediate', 'Advanced']),
  learning_style: z.enum(['Visual', 'Practical', 'Theoretical']),
  study_time: z.number().min(1).max(100),
});

type FormValues = z.infer<typeof formSchema>;

export function LearningPlanGenerator() {
  const t = useTranslations('Plan');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [interests, setInterests] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { skill_level: 'Beginner', learning_style: 'Practical', study_time: 10 }
  });

  const handleAddInterest = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && currentTag.trim()) {
      e.preventDefault();
      if (!interests.includes(currentTag.trim())) {
        setInterests([...interests, currentTag.trim()]);
      }
      setCurrentTag('');
    }
  };

  const removeInterest = (tag: string) => {
    setInterests(interests.filter((t) => t !== tag));
  };

  const onSubmit = async (data: FormValues) => {
    setIsSubmitting(true);
    const formData = new FormData();
    formData.append('goal', data.goal);
    formData.append('skill_level', data.skill_level);
    formData.append('learning_style', data.learning_style);
    formData.append('study_time', data.study_time.toString());
    formData.append('interests', JSON.stringify(interests));
    if (file) formData.append('transcript', file);

    try {
      await generatePlanAction(formData);
    } catch (err) {
      console.error(err);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white">{t('createNew')}</h1>
        <p className="text-slate-500 dark:text-slate-400 text-lg">{t('defineGoals')}</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8 bg-surface dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl shadow-slate-100/50 dark:shadow-none">
        <div className="grid gap-8 md:grid-cols-2">
          {/* Goal & Interests Section */}
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">{t('goalLabel')}</label>
              <textarea
                {...register('goal')}
                rows={3}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900 dark:text-white resize-none"
                placeholder={t('goalPlaceholder')}
              />
              {errors.goal && <p className="text-xs text-red-500 font-medium">{errors.goal.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">{t('interestsLabel')}</label>
              <div className="relative">
                <Tag className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                <input
                  value={currentTag}
                  onChange={(e) => setCurrentTag(e.target.value)}
                  onKeyDown={handleAddInterest}
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900 dark:text-white"
                  placeholder={t('typeAndPressEnter')}
                />
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {interests.map((tag) => (
                  <span key={tag} className="flex items-center gap-1.5 px-3 py-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded-full text-xs font-bold border border-indigo-100 dark:border-indigo-800 animate-in zoom-in-95 duration-200">
                    {tag}
                    <button type="button" onClick={() => removeInterest(tag)} className="hover:text-indigo-900 dark:hover:text-indigo-200 p-0.5 rounded-full hover:bg-indigo-100 dark:hover:bg-indigo-900 transition-colors">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Preferences Section */}
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">{t('skillLevelLabel')}</label>
              <select
                {...register('skill_level')}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900 dark:text-white appearance-none"
              >
                <option value="Beginner">{t('beginner')}</option>
                <option value="Intermediate">{t('intermediate')}</option>
                <option value="Advanced">{t('advanced')}</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Brain className="w-4 h-4 text-indigo-500" /> {t('learningStyle')}
              </label>
              <select
                {...register('learning_style')}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900 dark:text-white appearance-none"
              >
                <option value="Visual">{t('visual')}</option>
                <option value="Practical">{t('practical')}</option>
                <option value="Theoretical">{t('theoretical')}</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Clock className="w-4 h-4 text-indigo-500" /> {t('studyTime')}
              </label>
              <input
                type="number"
                {...register('study_time', { valueAsNumber: true })}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900 dark:text-white"
              />
              {errors.study_time && <p className="text-xs text-red-500 font-medium">{errors.study_time.message}</p>}
            </div>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="pt-6 border-t border-slate-100 dark:border-slate-800">
          <div className="space-y-2">
            <label className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-500" /> {t('academicTranscript')}
            </label>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">{t('transcriptNote')}</p>
            
            <div 
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "group relative border-2 border-dashed rounded-2xl p-8 transition-all cursor-pointer flex flex-col items-center justify-center text-center",
                file ? "border-green-300 bg-green-50 dark:bg-green-900/10" : "border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:border-indigo-300 dark:hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
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
                <div className="flex flex-col items-center gap-2 text-green-700 dark:text-green-400">
                  <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-2">
                    <Check className="w-6 h-6" />
                  </div>
                  <p className="font-bold">{file.name}</p>
                  <button 
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    className="text-xs font-bold text-red-600 dark:text-red-400 hover:underline mt-2"
                  >
                    {t('removeFile')}
                  </button>
                </div>
              ) : (
                <>
                  <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-700 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-900 flex items-center justify-center mb-4 transition-colors">
                    <Upload className="w-6 h-6 text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" />
                  </div>
                  <p className="font-bold text-slate-700 dark:text-slate-300 group-hover:text-indigo-900 dark:group-hover:text-white transition-colors">{t('clickToUpload')}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-500 mt-1 uppercase font-bold tracking-widest">{t('supportsHtml')}</p>
                </>
              )}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full flex items-center justify-center gap-3 bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold py-5 rounded-2xl transition-all shadow-xl shadow-indigo-200 disabled:opacity-50"
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
