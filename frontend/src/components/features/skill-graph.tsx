'use client';

import { useMemo, useState } from 'react';
import { LearningPlan } from './plan-stepper';

export interface SkillNode {
  id: string;
  label: string;
  mastery_level: number;
  category: string;
}

interface SkillGraphProps {
  skills: SkillNode[];
  plan: LearningPlan | null;
}

export function SkillGraph({ skills, plan }: SkillGraphProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const { nodes, edges } = useMemo(() => {
    // Basic Layout: grid-like arrangement
    const cols = Math.max(1, Math.ceil(Math.sqrt(skills.length)));
    const spacingX = 220;
    const spacingY = 150;
    const marginX = 120;
    const marginY = 120;

    const mappedNodes = skills.map((skill, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      return {
        ...skill,
        x: marginX + col * spacingX,
        // Stagger rows slightly for a more organic look
        y: marginY + row * spacingY + (col % 2 === 0 ? 30 : 0),
      };
    });

    const edges = [];
    if (plan && plan.steps) {
      const sortedSteps = [...plan.steps].sort((a, b) => a.order - b.order);
      
      // Try to find matching skills for each step
      const stepToSkillIds = sortedSteps.map(step => {
        const titleLower = step.title.toLowerCase();
        const descLower = step.description.toLowerCase();
        
        // Find the best matching skill
        const matchedSkill = skills.find(s => 
          titleLower.includes(s.label.toLowerCase()) || 
          descLower.includes(s.label.toLowerCase())
        );
        return matchedSkill ? matchedSkill.id : null;
      });

      // Create edges between consecutive matched skills
      for (let i = 0; i < stepToSkillIds.length - 1; i++) {
        const sourceId = stepToSkillIds[i];
        if (!sourceId) continue;
        
        // Find next step that has a matching skill
        for (let j = i + 1; j < stepToSkillIds.length; j++) {
          const targetId = stepToSkillIds[j];
          if (targetId && targetId !== sourceId) {
            edges.push({ source: sourceId, target: targetId });
            break; // Only connect to the immediate next skill
          }
        }
      }
    }

    return { nodes: mappedNodes, edges };
  }, [skills, plan]);

  if (!skills || skills.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        No skills data available to display.
      </div>
    );
  }

  // Calculate SVG dimensions to ensure all nodes fit
  const maxX = Math.max(...nodes.map(n => n.x), 0) + 200;
  const maxY = Math.max(...nodes.map(n => n.y), 0) + 200;

  return (
    <div className="w-full overflow-x-auto bg-white rounded-xl border border-slate-200 shadow-sm p-4 custom-scrollbar">
      <svg width={Math.max(maxX, 800)} height={Math.max(maxY, 400)} className="min-w-full">
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="25" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
          </marker>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Draw Edges */}
        {edges.map((edge, i) => {
          const sourceNode = nodes.find(n => n.id === edge.source);
          const targetNode = nodes.find(n => n.id === edge.target);
          if (!sourceNode || !targetNode) return null;

          return (
            <line
              key={`edge-${i}-${edge.source}-${edge.target}`}
              x1={sourceNode.x}
              y1={sourceNode.y}
              x2={targetNode.x}
              y2={targetNode.y}
              stroke="#cbd5e1"
              strokeWidth="2"
              markerEnd="url(#arrowhead)"
              strokeDasharray="6 4"
              className="transition-all duration-500 ease-in-out"
            />
          );
        })}

        {/* Draw Nodes */}
        {nodes.map(node => {
          const isHovered = hoveredNode === node.id;
          // mastery_level is likely 0-1 or 0-100. Handle both gracefully.
          const masteryPercent = node.mastery_level <= 1 ? node.mastery_level * 100 : node.mastery_level;
          const radius = 35 + (masteryPercent / 100) * 10;
          const strokeColor = isHovered ? '#4f46e5' : '#818cf8'; // Indigo 600 / 400
          
          return (
            <g 
              key={node.id}
              className="cursor-pointer transition-transform duration-300"
              onMouseEnter={() => setHoveredNode(node.id)}
              onMouseLeave={() => setHoveredNode(null)}
              style={{ transform: isHovered ? 'scale(1.05)' : 'scale(1)', transformOrigin: `${node.x}px ${node.y}px` }}
            >
              {/* Base Circle */}
              <circle
                cx={node.x}
                cy={node.y}
                r={radius}
                fill="#ffffff"
                stroke={strokeColor}
                strokeWidth={isHovered ? 4 : 2}
                filter={isHovered ? 'url(#glow)' : undefined}
                className="transition-all duration-300"
              />
              
              {/* Background for Progress */}
              <circle
                cx={node.x}
                cy={node.y}
                r={radius - 6}
                fill="transparent"
                stroke="#e0e7ff"
                strokeWidth="6"
              />
              
              {/* Mastery Progress Ring */}
              {masteryPercent > 0 && (
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={radius - 6}
                  fill="transparent"
                  stroke="#6366f1"
                  strokeWidth="6"
                  strokeDasharray={`${(masteryPercent / 100) * 2 * Math.PI * (radius - 6)} ${2 * Math.PI * (radius - 6)}`}
                  transform={`rotate(-90 ${node.x} ${node.y})`}
                  className="transition-all duration-700 ease-out"
                />
              )}
              
              {/* Inner Circle (Optional styling) */}
              <circle
                cx={node.x}
                cy={node.y}
                r={radius - 12}
                fill={isHovered ? '#eef2ff' : '#ffffff'}
                className="transition-colors duration-300"
              />
              
              {/* Text Label */}
              <text
                x={node.x}
                y={node.y + radius + 24}
                textAnchor="middle"
                className={`text-sm font-medium select-none transition-colors duration-300 ${isHovered ? 'fill-indigo-900 font-bold' : 'fill-slate-700'}`}
              >
                {node.label}
              </text>
              
              {/* Hover Tooltip SVG Elements */}
              {isHovered && (
                <g className="pointer-events-none">
                  <rect 
                    x={node.x - 75} 
                    y={node.y - radius - 65} 
                    width="150" 
                    height="50" 
                    rx="8" 
                    fill="#1e293b" 
                    opacity="0.95" 
                  />
                  <text x={node.x} y={node.y - radius - 43} textAnchor="middle" className="fill-white text-xs font-semibold">
                    {node.category || 'Skill Category'}
                  </text>
                  <text x={node.x} y={node.y - radius - 25} textAnchor="middle" className="fill-indigo-200 text-[11px]">
                    Mastery Level: {masteryPercent.toFixed(0)}%
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
