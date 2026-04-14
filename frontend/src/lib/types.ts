export interface TranscriptEntry {
  subject_name: string;
  credits: number;
  mark: number;
}

export interface DomainGap {
  domain: string;
  gap_score: number;
  missing_skills: string[];
}

export interface SkillGapAnalysis {
  overall_gap_score: number;
  domain_breakdown: DomainGap[];
  critical_skills: string[];
}

export interface LearningPathStep {
  order: number;
  title: string;
  description: string;
  resource_id?: string;
  is_external: boolean;
}

export interface ScoreBreakdown {
  skill_gap: number;
  content_sim: number;
  preference: number;
  rag_reasoning: number;
  difficulty: number;
  load: number;
}

export interface RecommendationResult {
  course_id: string;
  subject_name: string;
  score: number;
  breakdown: ScoreBreakdown;
  reasoning: string;
  reason_tags: string[];
  is_external: boolean;
  url?: string;
}

export interface RecommendationResponse {
  results: RecommendationResult[];
  skill_gap_analysis?: SkillGapAnalysis;
  learning_path: LearningPathStep[];
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_admin: boolean;
}
