'use client';

import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useState } from 'react';
import { CheckCircle2, XCircle, ArrowRight, RefreshCcw, Loader2, ChevronLeft, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { API_BASE_URL } from '@/lib/config';
import Cookies from 'js-cookie';

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

export function PracticeTestUI({ 
  planId, 
  stepOrder, 
  locale, 
  testData,
  nextStepOrder
}: { 
  planId: string, 
  stepOrder: string, 
  locale: string, 
  testData: TestData,
  nextStepOrder?: string
}) {
  const questions = testData.questions || [];
  const [viewMode, setViewMode] = useState<'test' | 'summary' | 'review'>(
    testData.last_attempt ? 'summary' : 'test'
  );
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [textAnswer, setTextAnswer] = useState<string>('');
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(testData.last_attempt?.score || 0);
  const [results, setResults] = useState<TestResult[]>(testData.last_attempt?.results || []);
  const [userAnswers, setUserAnswers] = useState<(number | string)[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const currentQuestion = questions[currentIndex];

  const handleSelect = (index: number) => {
    if (isAnswered) return;
    setSelectedOption(index);
  };

  const handleCheck = () => {
    const qType = currentQuestion.type || 'multiple_choice';

    if (qType === 'multiple_choice' || qType === 'true_false') {
      if (selectedOption === null || isAnswered) return;

      setIsAnswered(true);
      setUserAnswers(prev => [...prev, selectedOption]);
      if (selectedOption === currentQuestion.correct_answer_index) {
        setScore(prev => prev + 1);
      }
    } else {
      if (!textAnswer.trim() || isAnswered) return;

      setIsAnswered(true);
      setUserAnswers(prev => [...prev, textAnswer]);
      if (textAnswer.trim().toLowerCase() === currentQuestion.correct_answer_text?.trim().toLowerCase()) {
        setScore(prev => prev + 1);
      }
    }
  };

  const handleNext = async () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setSelectedOption(null);
      setTextAnswer('');
      setIsAnswered(false);
    } else {
      // Finished
      setIsSubmitting(true);
      try {
        const token = Cookies.get('token');

        const res = await fetch(`${API_BASE_URL}/learning-plan/${planId}/lessons/${stepOrder}/test/submit`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ answers: userAnswers })
        });

        if (res.ok) {
          const data = await res.json();
          setResults(data.results);
          setScore(data.score);
          setViewMode('summary');
        }
      } catch (e) {
        console.error("Failed to submit score", e);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  if (!questions || questions.length === 0) {
    return <div>No questions available.</div>;
  }

  if (viewMode === 'summary') {
    const percentage = Math.round((score / questions.length) * 100);
    return (
      <div className="text-center space-y-6 py-8">
        <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-primary/10 text-primary mb-4">
          <span className="text-3xl font-black">{percentage}%</span>
        </div>
        <h2 className="text-2xl font-bold">Test Completed!</h2>
        <p className="text-muted">You answered {score} out of {questions.length} questions correctly.</p>

        <div className="pt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={() => setViewMode('review')}
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 bg-surface border border-border text-foreground rounded-xl font-medium hover:bg-muted/10 transition-colors"
          >
            <Eye size={18} /> Review Answers
          </button>
          <button
            onClick={() => {
              setCurrentIndex(0);
              setSelectedOption(null);
              setTextAnswer('');
              setIsAnswered(false);
              setScore(0);
              setUserAnswers([]);
              setViewMode('test');
            }}
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 bg-surface border border-border text-foreground rounded-xl font-medium hover:bg-muted/10 transition-colors"
          >
            <RefreshCcw size={18} /> Retake Test
          </button>
          <Link
            href={nextStepOrder ? `/${locale}/plan/${planId}/lessons/${nextStepOrder}` : `/${locale}/plan/${planId}`}
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 bg-primary text-white rounded-xl font-medium shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
          >
            {nextStepOrder ? 'Next Lesson' : 'Back to Plan'}
          </Link>
        </div>
      </div>
    );
  }

  if (viewMode === 'review') {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <button 
            onClick={() => setViewMode('summary')}
            className="flex items-center gap-2 text-sm font-medium text-muted hover:text-foreground transition-colors"
          >
            <ChevronLeft size={16} /> Back to Summary
          </button>
          <h2 className="text-xl font-bold">Review Answers</h2>
        </div>

        <div className="space-y-8">
          {results.map((result: TestResult, idx: number) => {
            const question = questions[result.question_index];
            if (!question) return null;

            const isMultipleChoice = question.type === 'multiple_choice' || question.type === 'true_false';
            
            let userAnsDisplay = result.user_answer;
            let correctAnsDisplay = result.correct_answer_text;
            
            if (isMultipleChoice && typeof result.user_answer === 'number' && question.options) {
              userAnsDisplay = question.options[result.user_answer];
            }
            if (isMultipleChoice && question.correct_answer_index !== undefined && question.options) {
              correctAnsDisplay = question.options[question.correct_answer_index];
            }

            return (
              <div key={idx} className="p-6 border border-border rounded-2xl bg-surface/50 space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-muted/60">
                      Question {idx + 1}
                    </span>
                    <h3 className="font-bold leading-tight">
                      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                        {question.question}
                      </ReactMarkdown>
                    </h3>
                  </div>
                  {result.is_correct ? (
                    <span className="flex items-center gap-1 text-success text-sm font-bold shrink-0">
                      <CheckCircle2 size={16} /> Correct
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-destructive text-sm font-bold shrink-0">
                      <XCircle size={16} /> Incorrect
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-3 rounded-xl bg-muted/5 border border-border/50">
                    <span className="text-[10px] font-bold uppercase text-muted block mb-1">Your Answer</span>
                    <div className={cn("text-sm font-medium", result.is_correct ? "text-success" : "text-destructive")}>
                      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                        {String(userAnsDisplay || 'No answer')}
                      </ReactMarkdown>
                    </div>
                  </div>
                  {!result.is_correct && (
                    <div className="p-3 rounded-xl bg-success/5 border border-success/20">
                      <span className="text-[10px] font-bold uppercase text-success block mb-1">Correct Answer</span>
                      <div className="text-sm font-bold text-success">
                        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                          {String(correctAnsDisplay || result.correct_answer_text || 'Unknown')}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-4 bg-muted/10 rounded-xl">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider mb-2 text-muted">Explanation</h4>
                  <div className="text-sm text-muted leading-relaxed">
                    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                      {result.explanation}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        <div className="pt-4 flex justify-center">
          <button
            onClick={() => setViewMode('summary')}
            className="px-8 py-3 bg-primary text-white rounded-xl font-medium shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
          >
            Back to Summary
          </button>
        </div>
      </div>
    );
  }

  const renderQuestion = () => {
    const qType = currentQuestion.type || 'multiple_choice';

    if (qType === 'multiple_choice' || qType === 'true_false') {
      return (
        <div className="space-y-3">
          {currentQuestion.options?.map((option, idx) => {
            const isSelected = selectedOption === idx;
            const isCorrect = idx === currentQuestion.correct_answer_index;

            let stateClasses = "border-border bg-surface hover:border-primary/50 cursor-pointer";
            if (isAnswered) {
              if (isCorrect) {
                stateClasses = "border-success bg-success/10 text-success cursor-default";
              } else if (isSelected && !isCorrect) {
                stateClasses = "border-destructive bg-destructive/10 text-destructive cursor-default";
              } else {
                stateClasses = "border-border bg-surface/50 opacity-50 cursor-default";
              }
            } else if (isSelected) {
              stateClasses = "border-primary ring-1 ring-primary bg-primary/5 text-primary";
            }

            return (
              <button
                key={idx}
                onClick={() => handleSelect(idx)}
                disabled={isAnswered}
                className={cn(
                  "w-full text-left p-4 rounded-xl border transition-all duration-200 flex items-center justify-between group",
                  stateClasses
                )}
              >
                <span className="font-medium">
                  <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                    {option}
                  </ReactMarkdown>
                </span>
                {isAnswered && isCorrect && <CheckCircle2 className="w-5 h-5 text-success" />}
                {isAnswered && isSelected && !isCorrect && <XCircle className="w-5 h-5 text-destructive" />}
              </button>
            );
          })}
        </div>
      );
    } else {
      // short_answer or fill_in_the_blank
      const isCorrect = textAnswer.trim().toLowerCase() === currentQuestion.correct_answer_text?.trim().toLowerCase();

      return (
        <div className="space-y-4">
          <input
            type="text"
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
            disabled={isAnswered}
            placeholder="Type your answer here..."
            className={cn(
              "w-full p-4 rounded-xl border bg-surface transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/20",
              isAnswered
                ? isCorrect
                  ? "border-success bg-success/10 text-success"
                  : "border-destructive bg-destructive/10 text-destructive"
                : "border-border focus:border-primary"
            )}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !isAnswered && textAnswer.trim()) {
                handleCheck();
              }
            }}
          />
          {isAnswered && !isCorrect && (
            <div className="text-sm font-medium text-success">
              Correct answer: <span className="font-bold">{currentQuestion.correct_answer_text}</span>
            </div>
          )}
        </div>
      );
    }
  };

  return (
    <div className="space-y-8">
      {/* Progress */}
      <div className="flex items-center gap-4">
        <div className="flex-1 h-2 bg-surface rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-500 ease-out"
            style={{ width: `${((currentIndex + (isAnswered ? 1 : 0)) / questions.length) * 100}%` }}
          />
        </div>
        <span className="text-sm font-medium text-muted">
          Question {currentIndex + 1} of {questions.length}
        </span>
      </div>

      {/* Question */}
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-muted/20 text-muted text-[10px] font-black uppercase tracking-wider rounded">
            {currentQuestion.type?.replace('_', ' ') || 'multiple choice'}
          </span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold leading-tight">
          <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
            {currentQuestion.question}
          </ReactMarkdown>
        </h2>

        {renderQuestion()}
      </div>

      {/* Explanation */}
      {isAnswered && (
        <div className="p-5 bg-muted/10 rounded-xl border border-border animate-in fade-in slide-in-from-bottom-2">
          <h4 className="text-sm font-bold uppercase tracking-wider mb-2 flex items-center gap-2">
            {(currentQuestion.type === 'multiple_choice' || currentQuestion.type === 'true_false') ? (
              selectedOption === currentQuestion.correct_answer_index ? (
                <span className="text-success flex items-center gap-1"><CheckCircle2 size={16} /> Correct</span>
              ) : (
                <span className="text-destructive flex items-center gap-1"><XCircle size={16} /> Incorrect</span>
              )
            ) : (
              textAnswer.trim().toLowerCase() === currentQuestion.correct_answer_text?.trim().toLowerCase() ? (
                <span className="text-success flex items-center gap-1"><CheckCircle2 size={16} /> Correct</span>
              ) : (
                <span className="text-destructive flex items-center gap-1"><XCircle size={16} /> Incorrect</span>
              )
            )}
          </h4>
          <p className="text-muted leading-relaxed text-sm">
            <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
              {currentQuestion.explanation}
            </ReactMarkdown>
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="pt-4 flex justify-end">
        {!isAnswered ? (
          <button
            onClick={handleCheck}
            disabled={
              (currentQuestion.type === 'multiple_choice' || currentQuestion.type === 'true_false')
                ? selectedOption === null
                : !textAnswer.trim()
            }
            className="px-8 py-3 bg-primary text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
          >
            Check Answer
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={isSubmitting}
            className="px-8 py-3 bg-primary text-white rounded-xl font-medium flex items-center gap-2 shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all"
          >
            {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : (
              <>
                {currentIndex === questions.length - 1 ? 'Finish Test' : 'Next Question'}
                <ArrowRight size={18} />
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
