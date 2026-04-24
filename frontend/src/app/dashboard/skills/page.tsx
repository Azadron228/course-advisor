'use client';
import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Card } from '@/components/ui/Card';

interface SkillNode {
  id: string;
  label: string;
  mastery_level: number;
  category: string;
}

export default function SkillMapPage() {
  const [skills, setSkills] = useState<SkillNode[]>([]);

  useEffect(() => {
    api.get('/api/v1/skills/map').then(res => setSkills(res.data.nodes)).catch(console.error);
  }, []);

  return (
    <div className="p-8 max-w-[1280px] mx-auto">
      <h1 className="text-4xl font-bold mb-8">Interactive Skill Map</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {skills.map(skill => (
          <Card key={skill.id} className="flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-semibold tracking-wider uppercase text-[var(--text-muted)]">{skill.category}</span>
              <span className="text-sm font-medium text-[var(--primary)]">{skill.mastery_level}%</span>
            </div>
            <h3 className="text-xl font-semibold">{skill.label}</h3>
            <div className="h-2 w-full bg-[var(--border-light)] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[var(--secondary)] rounded-full transition-all" 
                style={{ width: `${skill.mastery_level}%` }}
              />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
