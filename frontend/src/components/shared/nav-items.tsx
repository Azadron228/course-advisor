'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { cn } from '@/lib/utils';
import { NavItem } from '@/lib/navigation';

interface NavItemsProps {
  items: NavItem[];
  isCollapsed?: boolean;
  onItemClick?: () => void;
  translationNamespace?: string;
}

export function NavItems({ items, isCollapsed, onItemClick, translationNamespace = 'Navigation' }: NavItemsProps) {
  const t = useTranslations(translationNamespace);
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {items.map((item) => {
        const isActive = pathname.includes(item.href);
        const Icon = item.icon;
        const label = item.nameKey ? t(item.nameKey) : item.name;

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onItemClick}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all group relative",
              isActive 
                ? "bg-primary/10 text-primary" 
                : "text-muted hover:bg-muted/10 hover:text-foreground"
            )}
          >
            <Icon 
              size={20} 
              className={cn(
                "flex-shrink-0 transition-colors",
                isActive ? "text-primary" : "text-muted group-hover:text-foreground"
              )} 
            />
            {!isCollapsed && (
              <span className="text-sm font-semibold whitespace-nowrap">
                {label}
              </span>
            )}
            {isCollapsed && (
              <div className="absolute left-full ml-2 px-2 py-1 bg-surface text-foreground text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 shadow-lg border border-border">
                {label}
              </div>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
