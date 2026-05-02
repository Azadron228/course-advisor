'use client';

import { useState, useRef, useEffect, useTransition } from 'react';
import { useLocale } from 'next-intl';
import { usePathname, useRouter } from '@/i18n/routing';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

const LOCALES = [
  { code: 'en', label: 'English' },
  { code: 'ru', label: 'Русский' }
];

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  
  const [isOpen, setIsOpen] = useState(false);
  const [isPending, startTransition] = useTransition();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const switchLanguage = (nextLocale: string) => {
    startTransition(() => {
      router.replace(pathname, { locale: nextLocale });
    });
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isPending}
        className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-muted hover:bg-input transition-colors border border-border",
          isPending && "opacity-50 cursor-not-allowed"
        )}
      >
        <Globe size={16} />
        <span className="uppercase">{locale}</span>
        <ChevronDown 
          size={14} 
          className={cn("text-muted transition-transform", isOpen && "rotate-180")} 
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-36 bg-surface border border-border rounded-xl shadow-lg py-1 z-50 animate-in fade-in zoom-in duration-200">
          {LOCALES.map((l) => (
            <button
              key={l.code}
              onClick={() => switchLanguage(l.code)}
              className="flex items-center justify-between w-full px-4 py-2 text-sm text-left text-foreground hover:bg-input transition-colors"
            >
              <span>{l.label}</span>
              {locale === l.code && (
                <Check size={16} className="text-primary" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
