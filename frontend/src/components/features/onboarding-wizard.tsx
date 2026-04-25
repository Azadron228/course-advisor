'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/hooks/use-auth';
import { Loader2, CheckCircle2, ArrowRight, ArrowLeft, Tag, X } from 'lucide-react';

const step1Schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  career_goal: z.string().min(5, 'Career goal must be at least 5 characters'),
});

type Step1Values = z.infer<typeof step1Schema>;

export function OnboardingWizard() {
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [interests, setInterests] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const { user, fetchUser } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<Step1Values>({
    resolver: zodResolver(step1Schema),
    defaultValues: {
      full_name: user?.full_name || '',
      career_goal: user?.career_goal || '',
    },
  });

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

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

  const handleFinalize = async () => {
    setIsSubmitting(true);
    try {
      const data = {
        ...getValues(),
        interests,
        onboarding_completed: true,
      };
      await apiClient.patch('/users/me', data);
      await fetchUser(); // Refresh user data to hide wizard
      window.location.reload(); // Force a full reload to ensure all Server Components are updated
    } catch (error) {
      console.error('Onboarding failed:', error);
      alert('Failed to complete onboarding. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-surface rounded-2xl shadow-2xl w-full max-w-xl overflow-hidden transition-all border border-slate-200 dark:border-slate-800">
        {/* Progress Bar */}
        <div className="h-2 w-full bg-slate-100 dark:bg-slate-800">
          <div 
            className="h-full bg-blue-600 transition-all duration-500 ease-out"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        <div className="p-8">
          {step === 1 && (
            <div className="space-y-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-foreground">Welcome to EduPath AI!</h2>
                <p className="text-slate-500 dark:text-slate-400">Let&apos;s start by getting to know you better.</p>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Full Name</label>
                  <input
                    {...register('full_name')}
                    className={`block w-full px-4 py-2 bg-white dark:bg-slate-900 text-slate-900 dark:text-white border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none ${
                      errors.full_name ? 'border-red-300' : 'border-slate-300 dark:border-slate-700'
                    }`}
                    placeholder="Enter your full name"
                  />
                  {errors.full_name && <p className="text-sm text-red-600">{errors.full_name.message}</p>}
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Career Goal</label>
                  <textarea
                    {...register('career_goal')}
                    rows={3}
                    className={`block w-full px-4 py-2 bg-white dark:bg-slate-900 text-slate-900 dark:text-white border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none ${
                      errors.career_goal ? 'border-red-300' : 'border-slate-300 dark:border-slate-700'
                    }`}
                    placeholder="What are you hoping to achieve? (e.g., Become a Data Scientist)"
                  />
                  {errors.career_goal && <p className="text-sm text-red-600">{errors.career_goal.message}</p>}
                </div>
              </div>

              <button
                onClick={handleSubmit(nextStep)}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-blue-200 dark:shadow-none"
              >
                Next Step
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-foreground">What are you interested in?</h2>
                <p className="text-slate-500 dark:text-slate-400">Add tags for skills or topics you want to learn.</p>
              </div>

              <div className="space-y-4">
                <div className="relative">
                  <Tag className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    value={currentTag}
                    onChange={(e) => setCurrentTag(e.target.value)}
                    onKeyDown={handleAddInterest}
                    className="block w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-900 text-slate-900 dark:text-white border border-slate-300 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="Type and press Enter (e.g., Python, UI Design)"
                  />
                </div>

                <div className="flex flex-wrap gap-2 min-h-[100px] p-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
                  {interests.length === 0 ? (
                    <p className="text-sm text-slate-400 italic">No interests added yet...</p>
                  ) : (
                    interests.map((tag) => (
                      <span
                        key={tag}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium border border-blue-200 dark:border-blue-800"
                      >
                        {tag}
                        <button onClick={() => removeInterest(tag)} className="hover:text-blue-900 dark:hover:text-blue-100">
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={prevStep}
                  className="flex-1 flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 font-semibold py-3 rounded-xl transition-all"
                >
                  <ArrowLeft className="w-5 h-5" />
                  Back
                </button>
                <button
                  onClick={nextStep}
                  className="flex-[2] flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-blue-200 dark:shadow-none"
                >
                  Next Step
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6 text-center">
              <div className="flex justify-center">
                <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded-full">
                  <CheckCircle2 className="w-16 h-16 text-green-600 dark:text-green-400" />
                </div>
              </div>

              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-foreground">You&apos;re all set!</h2>
                <p className="text-slate-500 dark:text-slate-400">
                  We&apos;re ready to create your personalized learning journey.
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-2xl text-left space-y-3 border border-slate-100 dark:border-slate-800">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-500 dark:text-slate-400">Name</span>
                  <span className="text-sm font-semibold text-foreground">{getValues().full_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-500 dark:text-slate-400">Goal</span>
                  <span className="text-sm font-semibold truncate max-w-[200px] text-foreground">{getValues().career_goal}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-500 dark:text-slate-400">Interests</span>
                  <span className="text-sm font-semibold text-foreground">{interests.length} topics</span>
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  disabled={isSubmitting}
                  onClick={prevStep}
                  className="flex-1 flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 font-semibold py-3 rounded-xl transition-all disabled:opacity-50"
                >
                  Back
                </button>
                <button
                  disabled={isSubmitting}
                  onClick={handleFinalize}
                  className="flex-[2] flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-green-200 dark:shadow-none disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    'Get Started!'
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
