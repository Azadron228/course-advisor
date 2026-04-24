'use client';
import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Card } from '@/components/ui/Card';

interface PlanStep {
  title: string;
  description: string;
  status: string;
}

export default function ProfilePlanPage() {
  const [goal, setGoal] = useState('');
  const [steps, setSteps] = useState<PlanStep[]>([]);

  useEffect(() => {
    api.get('/api/v1/learning-plan').then(res => {
      setGoal(res.data.career_goal);
      setSteps(res.data.steps);
    });
  }, []);

  return (
    <div className="p-8 max-w-[1280px] mx-auto">
      <h1 className="text-4xl font-bold mb-2">Learning Plan</h1>
      <p className="text-[var(--text-muted)] mb-8 text-lg">Goal: {goal}</p>
      
      <div className="space-y-4">
        {steps.map((step, idx) => (
          <Card key={idx} className={step.status === 'current' ? 'border-[var(--primary)] shadow-md' : ''}>
            <div className="flex items-start gap-4">
              <div className={`w-3 h-3 mt-2 rounded-full ${step.status === 'completed' ? 'bg-[var(--secondary)]' : step.status === 'current' ? 'bg-[var(--primary)]' : 'bg-gray-300'}`} />
              <div>
                <h3 className="text-xl font-semibold">{step.title}</h3>
                <p className="text-[var(--text-muted)]">{step.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
