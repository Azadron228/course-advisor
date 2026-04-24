import React from 'react';

export function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-2xl border border-[var(--border-light)] shadow-[0px_4px_20px_rgba(0,0,0,0.04)] p-6 ${className}`}>
      {children}
    </div>
  );
}
