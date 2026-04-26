'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { generatePlanAction } from '@/app/[locale]/plan/actions';
import { Loader2, ArrowRight, Tag, X, Sparkles } from 'lucide-react';

const formSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  career_goal: z.string().min(5, 'Career goal must be at least 5 characters'),
});

type FormValues = z.infer<typeof formSchema>;

export function CreatePlanForm({ initialName = '' }: { initialName?: string }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [interests, setInterests] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      full_name: initialName,
      career_goal: '',
    },
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
    setError(null);
    try {
      await generatePlanAction({
        ...data,
        interests,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate plan');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">Start Your Learning Journey</h1>
        <p className="text-slate-500 text-lg">Tell us your goals, and our AI will draft a personalized path for you.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xl space-y-6">
        {error && (
          <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Full Name</label>
            <input
              {...register('full_name')}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900"
              placeholder="e.g. Alex Johnson"
            />
            {errors.full_name && <p className="text-xs text-red-500">{errors.full_name.message}</p>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">What is your career goal?</label>
            <textarea
              {...register('career_goal')}
              rows={3}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900"
              placeholder="e.g. I want to become a Senior Frontend Engineer focusing on React and AI."
            />
            {errors.career_goal && <p className="text-xs text-red-500">{errors.career_goal.message}</p>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Interests & Topics</label>
            <div className="relative">
              <Tag className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
              <input
                value={currentTag}
                onChange={(e) => setCurrentTag(e.target.value)}
                onKeyDown={handleAddInterest}
                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900"
                placeholder="Type and press Enter (e.g. TypeScript, UI Design)"
              />
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {interests.map((tag) => (
                <span key={tag} className="flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold border border-indigo-100">
                  {tag}
                  <button type="button" onClick={() => removeInterest(tag)} className="hover:text-indigo-900">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-indigo-200 disabled:opacity-50"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Drafting Your Plan...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Generate My Learning Path
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
