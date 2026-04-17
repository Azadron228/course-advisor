'use client';

import React from 'react';
import { RecommendationResponse } from '@/lib/types';
import { Card, CardContent, CardHeader } from '@/components/ui-base';
import {
  Zap,
  Map,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { motion } from 'framer-motion';

interface RoadmapViewProps {
  results: RecommendationResponse;
  difficulty: number;
}

export const RoadmapView: React.FC<RoadmapViewProps> = ({ results, difficulty }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-12 pb-20"
    >
      {/* Header */}
      <div className="flex items-end justify-between border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Your Academic Roadmap</h1>
          <p className="text-slate-500 mt-2">Personalized strategy based on your {results.results.length} course recommendations.</p>
        </div>
        <div className="bg-green-50 text-green-700 px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2 border border-green-100">
          <CheckCircle2 size={16} />
          Plan Ready
        </div>
      </div>

      {/* Analysis Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center gap-2 font-bold text-slate-900 bg-slate-50/50">
            <AlertCircle size={20} className="text-orange-500" />
            Skill Gap Analysis
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="p-4 bg-orange-50 rounded-2xl border border-orange-100">
                  <span className="text-xs text-orange-600 font-bold uppercase tracking-wider">Overall Gap Score</span>
                  <div className="text-4xl font-black text-orange-700 mt-1">{((results.skill_gap_analysis?.overall_gap_score || 0) * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 mb-3">Critical Skills to Acquire</h3>
                  <div className="flex flex-wrap gap-2">
                    {results.skill_gap_analysis?.critical_skills.map((skill, i) => (
                      <span key={i} className="px-3 py-1 bg-red-50 text-red-600 rounded-full text-xs font-semibold border border-red-100">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-900">Gaps by Domain</h3>
                <div className="space-y-4">
                  {results.skill_gap_analysis?.domain_breakdown.map((domain, i) => (
                    <div key={i} className="space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-700">{domain.domain}</span>
                        <span className="text-slate-400">{(domain.gap_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-orange-500 rounded-full"
                          style={{ width: `${domain.gap_score * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Learning Path */}
      <section className="space-y-6">
        <div className="flex items-center gap-2 text-2xl font-bold text-slate-900">
          <Map size={24} className="text-blue-600" />
          <h2>Learning Path</h2>
        </div>
        <div className="relative space-y-8 before:absolute before:left-6 before:top-4 before:bottom-4 before:w-0.5 before:bg-blue-100">
          {results.learning_path.sort((a, b) => a.order - b.order).map((step, i) => (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              key={i}
              className="relative pl-16"
            >
              <div className="absolute left-0 w-12 h-12 rounded-full bg-white border-4 border-blue-50 flex items-center justify-center z-10 shadow-sm">
                <span className="text-blue-600 font-black">{step.order}</span>
              </div>
              <Card>
                <CardContent className="p-6 flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="text-lg font-bold text-slate-900">{step.title}</h3>
                    <p className="text-slate-500 text-sm">{step.description}</p>
                    {step.resource_id && (
                      <div className="mt-4 pt-4 border-t border-slate-100 flex items-center gap-4">
                        {step.is_external ? (
                          <a
                            href={step.resource_id} target="_blank" rel="noopener noreferrer"
                            className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1 uppercase tracking-widest"
                          >
                            View Resource <ExternalLink size={12} />
                          </a>
                        ) : (
                          <span className="text-xs font-bold text-slate-400 flex items-center gap-1 uppercase tracking-widest">
                            Internal Course ID: {step.resource_id}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  <ChevronRight size={20} className="text-slate-300" />
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Course Catalog */}
      <section className="space-y-6">
        <div className="flex items-center gap-2 text-2xl font-bold text-slate-900">
          <CheckCircle2 size={24} className="text-green-600" />
          <h2>Recommended Courses</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {results.results.map((rec, i) => (
            <Card key={i} className="hover:shadow-md transition-shadow">
              <CardHeader className="bg-slate-50/50">
                <div className="flex justify-between items-start">
                  <h3 className="font-bold text-slate-900 leading-tight pr-4">{rec.subject_name}</h3>
                  <div className="bg-blue-50 text-blue-600 px-2 py-1 rounded text-xs font-black">
                    {(rec.score * 100).toFixed(0)}%
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-slate-600 line-clamp-3">
                  {rec.reasoning}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {rec.reason_tags.map((tag, j) => (
                    <span key={j} className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="pt-4 grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">Alignment</span>
                    <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: `${rec.breakdown.content_sim * 100}%` }} />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">Skill Gap</span>
                    <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${rec.breakdown.skill_gap * 100}%` }} />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </motion.div>
  );
};
