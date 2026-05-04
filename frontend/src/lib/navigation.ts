import { 
  LayoutDashboard, 
  BookOpen, 
  MessageSquare,
  Users
} from 'lucide-react';

export interface NavItem {
  nameKey?: string;
  name?: string;
  href: string;
  icon: any;
}

export const STUDENT_NAV_ITEMS: NavItem[] = [
  { nameKey: 'dashboard', href: '/dashboard', icon: LayoutDashboard },
  { nameKey: 'learningPlan', href: '/plan', icon: BookOpen },
  { nameKey: 'aiAdvisor', href: '/chat', icon: MessageSquare },
];

export const ADMIN_NAV_ITEMS: NavItem[] = [
  { name: 'Courses', href: '/admin/courses', icon: BookOpen },
  { name: 'Users', href: '/admin/users', icon: Users },
];
