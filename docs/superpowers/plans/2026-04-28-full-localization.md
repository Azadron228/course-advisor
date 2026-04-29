# Full Localization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully translate the frontend application by moving all hardcoded strings to i18n JSON files and updating components to use the `next-intl` library.

**Architecture:** Systematic replacement of hardcoded strings with `t('key')` calls using `useTranslations` (client-side) and `getTranslations` (server-side).

**Tech Stack:** Next.js, next-intl, TypeScript.

---

### Task 1: Update Translation Files

**Files:**
- Modify: `frontend/messages/en.json`
- Modify: `frontend/messages/ru.json`

- [ ] **Step 1: Update en.json with all identified strings**

```json
{
  "Common": {
    "title": "EduPath AI",
    "searchPlaceholder": "Search courses, skills...",
    "logout": "Logout",
    "profile": "My Profile",
    "settings": "Settings",
    "loading": "Loading...",
    "saveChanges": "Save Changes",
    "savingChanges": "Saving Changes...",
    "beta": "Beta",
    "aiPowered": "AI Powered",
    "navHub": "Navigation Hub",
    "backToDashboard": "Back to Dashboard",
    "go": "Go",
    "thinking": "Thinking..."
  },
  "Auth": {
    "login": "Login",
    "register": "Register",
    "signIn": "Sign In",
    "signUp": "Sign Up",
    "createAccount": "Create Account",
    "welcomeBack": "Welcome Back",
    "continueJourney": "Continue your learning journey",
    "emailAddress": "Email Address",
    "password": "Password",
    "forgotPassword": "Forgot password?",
    "dontHaveAccount": "Don't have an account?",
    "alreadyHaveAccount": "Already have an account?",
    "signingIn": "Signing in...",
    "creatingAccount": "Creating account...",
    "userProfile": "User Profile",
    "manageProfile": "Manage your personal information and career goals",
    "fullName": "Full Name",
    "careerGoal": "Career Goal",
    "profileUpdated": "Profile updated successfully!",
    "loginError": "Invalid email or password. Please try again.",
    "nameMinLength": "Name must be at least 2 characters",
    "invalidEmail": "Invalid email address",
    "goalMinLength": "Career goal must be at least 5 characters"
  },
  "Dashboard": {
    "activePlan": "Active Learning Plan",
    "progress": "Progress",
    "achievementLevel": "Achievement Level",
    "risingStar": "Rising Star",
    "insightsSoon": "Skill Insights coming soon",
    "insightsDesc": "Advanced analytics for your learning journey.",
    "leaderboards": "Leaderboards",
    "leaderboardsDesc": "Compete with other learners in your field.",
    "quickActions": "Quick Actions",
    "quickActionsDesc": "Resume your last lesson with one click."
  },
  "Chat": {
    "title": "AI Advisor",
    "subtitle": "Get personalized advice and course recommendations",
    "companion": "Your personalized learning companion",
    "howCanIHelp": "How can I help you today?",
    "intro": "Ask me about course recommendations, skill development, or how to reach your career goals.",
    "suggestPython": "Recommend Python courses",
    "suggestWebDev": "What skills for Web Dev?",
    "suggestPlan": "Explain my learning plan",
    "suggestDataScience": "How to start in Data Science?",
    "placeholder": "Ask your advisor anything...",
    "aiPoweredNote": "AI-powered suggestions based on your profile and goals."
  },
  "Plan": {
    "myPaths": "My Paths",
    "noPaths": "No paths yet",
    "startGenerating": "Start by generating your first personalized learning path.",
    "createNew": "Create New Path",
    "defineGoals": "Define your goals and learning preferences.",
    "goalLabel": "What is your goal?",
    "interestsLabel": "Interests & Specific Topics",
    "skillLevelLabel": "Current Skill Level",
    "beginner": "Beginner - Just starting out",
    "intermediate": "Intermediate - Some experience",
    "advanced": "Advanced - Looking for depth",
    "visual": "Visual - Videos and Diagrams",
    "practical": "Practical - Labs and Projects",
    "theoretical": "Theoretical - Books and Docs",
    "transcriptNote": "Upload your transcript (.html) to help the AI skip courses you've already completed.",
    "clickToUpload": "Click to upload your transcript",
    "supportsHtml": "Supports .HTML",
    "myPlan": "My Learning Plan",
    "notFound": "No learning plan found. Go to the dashboard to generate one.",
    "materials": "Course Materials",
    "noMaterials": "No specific materials provided for this course yet."
  },
  "Navigation": {
    "dashboard": "Dashboard",
    "learningPlan": "Learning Plan",
    "aiAdvisor": "AI Advisor",
    "profile": "Profile"
  }
}
```

- [ ] **Step 2: Update ru.json with Russian translations**

```json
{
  "Common": {
    "title": "EduPath AI",
    "searchPlaceholder": "Поиск курсов, навыков...",
    "logout": "Выйти",
    "profile": "Мой профиль",
    "settings": "Настройки",
    "loading": "Загрузка...",
    "saveChanges": "Сохранить изменения",
    "savingChanges": "Сохранение...",
    "beta": "Бета",
    "aiPowered": "На базе ИИ",
    "navHub": "Навигация",
    "backToDashboard": "Вернуться к панели",
    "go": "Перейти",
    "thinking": "Думаю..."
  },
  "Auth": {
    "login": "Вход",
    "register": "Регистрация",
    "signIn": "Войти",
    "signUp": "Зарегистрироваться",
    "createAccount": "Создать аккаунт",
    "welcomeBack": "С возвращением",
    "continueJourney": "Продолжите свой путь обучения",
    "emailAddress": "Электронная почта",
    "password": "Пароль",
    "forgotPassword": "Забыли пароль?",
    "dontHaveAccount": "Нет аккаунта?",
    "alreadyHaveAccount": "Уже есть аккаунт?",
    "signingIn": "Вход...",
    "creatingAccount": "Создание аккаунта...",
    "userProfile": "Профиль пользователя",
    "manageProfile": "Управляйте личной информацией и целями",
    "fullName": "Полное имя",
    "careerGoal": "Карьерная цель",
    "profileUpdated": "Профиль успешно обновлен!",
    "loginError": "Неверный email или пароль. Попробуйте еще раз.",
    "nameMinLength": "Имя должно содержать не менее 2 символов",
    "invalidEmail": "Некорректный адрес электронной почты",
    "goalMinLength": "Цель должна содержать не менее 5 символов"
  },
  "Dashboard": {
    "activePlan": "Активный план обучения",
    "progress": "Прогресс",
    "achievementLevel": "Уровень достижений",
    "risingStar": "Восходящая звезда",
    "insightsSoon": "Аналитика навыков скоро появится",
    "insightsDesc": "Расширенная аналитика вашего процесса обучения.",
    "leaderboards": "Таблицы лидеров",
    "leaderboardsDesc": "Соревнуйтесь с другими учениками в вашей области.",
    "quickActions": "Быстрые действия",
    "quickActionsDesc": "Возобновите последний урок одним кликом."
  },
  "Chat": {
    "title": "ИИ Советник",
    "subtitle": "Получите персональные советы и рекомендации по курсам",
    "companion": "Ваш персональный помощник в обучении",
    "howCanIHelp": "Чем я могу помочь сегодня?",
    "intro": "Спросите меня о рекомендациях курсов, развитии навыков или о том, как достичь ваших карьерных целей.",
    "suggestPython": "Порекомендуй курсы по Python",
    "suggestWebDev": "Какие навыки нужны для Web-разработки?",
    "suggestPlan": "Объясни мой план обучения",
    "suggestDataScience": "С чего начать в Data Science?",
    "placeholder": "Спросите о чем угодно...",
    "aiPoweredNote": "Рекомендации ИИ на основе вашего профиля и целей."
  },
  "Plan": {
    "myPaths": "Мои пути",
    "noPaths": "Путей пока нет",
    "startGenerating": "Начните с создания вашего первого персонального пути обучения.",
    "createNew": "Создать новый путь",
    "defineGoals": "Определите свои цели и предпочтения в обучении.",
    "goalLabel": "Какова ваша цель?",
    "interestsLabel": "Интересы и конкретные темы",
    "skillLevelLabel": "Текущий уровень навыков",
    "beginner": "Новичок — только начинаю",
    "intermediate": "Средний — есть некоторый опыт",
    "advanced": "Продвинутый — ищу глубины",
    "visual": "Визуальный — видео и диаграммы",
    "practical": "Практический — лаборатории и проекты",
    "theoretical": "Теоретический — книги и документация",
    "transcriptNote": "Загрузите свою транскрипцию (.html), чтобы ИИ мог пропустить уже пройденные курсы.",
    "clickToUpload": "Нажмите, чтобы загрузить транскрипцию",
    "supportsHtml": "Поддерживается .HTML",
    "myPlan": "Мой план обучения",
    "notFound": "План обучения не найден. Перейдите в панель управления, чтобы создать его.",
    "materials": "Материалы курса",
    "noMaterials": "Для этого курса пока нет специфических материалов."
  },
  "Navigation": {
    "dashboard": "Панель управления",
    "learningPlan": "План обучения",
    "aiAdvisor": "ИИ Советник",
    "profile": "Профиль"
  }
}
```

- [ ] **Step 3: Commit translation files**

```bash
git add frontend/messages/en.json frontend/messages/ru.json
git commit -m "i18n: update translation strings for all components"
```

### Task 2: Translate Navigation Components

**Files:**
- Modify: `frontend/src/components/shared/sidebar.tsx`
- Modify: `frontend/src/components/shared/top-nav.tsx` (ensure title/placeholder use translations)

- [ ] **Step 1: Update sidebar.tsx to use translations**

```tsx
import { useTranslations } from 'next-intl';
// ...
export function Sidebar() {
  const t = useTranslations('Navigation');
  const navItems = [
    { name: t('dashboard'), href: '/dashboard', icon: LayoutDashboard },
    { name: t('learningPlan'), href: '/plan', icon: BookOpen },
    { name: t('aiAdvisor'), href: '/chat', icon: MessageSquare },
    { name: t('profile'), href: '/profile', icon: User },
  ];
  // ...
}
```

- [ ] **Step 2: Update top-nav.tsx (if needed)**
Check if `title` and `searchPlaceholder` already use `t('title')` and `t('searchPlaceholder')`.

- [ ] **Step 3: Commit navigation changes**

```bash
git add frontend/src/components/shared/sidebar.tsx frontend/src/components/shared/top-nav.tsx
git commit -m "i18n: translate navigation components"
```

### Task 3: Translate Auth and Profile Pages

**Files:**
- Modify: `frontend/src/app/[locale]/login/page.tsx`
- Modify: `frontend/src/app/[locale]/register/page.tsx`
- Modify: `frontend/src/app/[locale]/profile/page.tsx`

- [ ] **Step 1: Update login/page.tsx**
Use `useTranslations('Auth')` and `useTranslations('Common')`.

- [ ] **Step 2: Update register/page.tsx**
Use `useTranslations('Auth')` and `useTranslations('Common')`.

- [ ] **Step 3: Update profile/page.tsx**
Use `useTranslations('Auth')`, `useTranslations('Common')`.

- [ ] **Step 4: Commit auth changes**

```bash
git add frontend/src/app/[locale]/login/page.tsx frontend/src/app/[locale]/register/page.tsx frontend/src/app/[locale]/profile/page.tsx
git commit -m "i18n: translate auth and profile pages"
```

### Task 4: Translate Dashboard

**Files:**
- Modify: `frontend/src/app/[locale]/dashboard/page.tsx`
- Modify: `frontend/src/components/features/dashboard-summary.tsx`

- [ ] **Step 1: Update dashboard/page.tsx (Server Component)**
Use `getTranslations` from `next-intl/server`.

- [ ] **Step 2: Update dashboard-summary.tsx**
Use `useTranslations('Dashboard')`.

- [ ] **Step 3: Commit dashboard changes**

```bash
git add frontend/src/app/[locale]/dashboard/page.tsx frontend/src/components/features/dashboard-summary.tsx
git commit -m "i18n: translate dashboard"
```

### Task 5: Translate Chat

**Files:**
- Modify: `frontend/src/app/[locale]/chat/page.tsx`
- Modify: `frontend/src/components/features/chat-window.tsx`

- [ ] **Step 1: Update chat/page.tsx**
Use `useTranslations('Chat')`.

- [ ] **Step 2: Update chat-window.tsx**
Use `useTranslations('Chat')` and `useTranslations('Common')`.

- [ ] **Step 3: Commit chat changes**

```bash
git add frontend/src/app/[locale]/chat/page.tsx frontend/src/components/features/chat-window.tsx
git commit -m "i18n: translate chat interface"
```

### Task 6: Translate Learning Plan Components

**Files:**
- Modify: `frontend/src/components/features/learning-plan-generator.tsx`
- Modify: `frontend/src/components/features/plan-list.tsx`
- Modify: `frontend/src/components/features/plan-stepper.tsx`
- Modify: `frontend/src/components/shared/course-drawer.tsx`

- [ ] **Step 1: Update learning-plan-generator.tsx**
Use `useTranslations('Plan')`.

- [ ] **Step 2: Update plan-list.tsx**
Use `useTranslations('Plan')`.

- [ ] **Step 3: Update plan-stepper.tsx**
Use `useTranslations('Plan')`.

- [ ] **Step 4: Update course-drawer.tsx**
Use `useTranslations('Plan')`.

- [ ] **Step 5: Commit plan changes**

```bash
git add frontend/src/components/features/learning-plan-generator.tsx frontend/src/components/features/plan-list.tsx frontend/src/components/features/plan-stepper.tsx frontend/src/components/shared/course-drawer.tsx
git commit -m "i18n: translate learning plan components"
```

---
