# Full Localization and Kazakh Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Achieve full localization by adding Kazakh support, updating Russian/English translations, removing obsolete keys, and localizing hardcoded validation messages.

**Architecture:** Update `next-intl` configuration (routing/middleware), add a new translation file (`kk.json`), and refactor the `LearningPlanGenerator` component to use translations for validation.

**Tech Stack:** React (Next.js), `next-intl`, Zod, Tailwind CSS.

---

### Task 1: Clean Up and Update Existing Translations

**Files:**
- Modify: `frontend/messages/en.json`
- Modify: `frontend/messages/ru.json`

- [ ] **Step 1: Update `en.json`**
  - Remove obsolete `Plan` keys: `beginner`, `intermediate`, `advanced`, `learningStyle`, `studyTime`, `beginnerLevel`, `intermediateLevel`, `advancedLevel`, `visual`, `practical`, `theoretical`.
  - Add `Plan.validation.goalMinLength`: "Goal must be at least 5 characters".

- [ ] **Step 2: Update `ru.json`**
  - Update `Plan.myPaths` to `"Мои планы обучения"`.
  - Add `Plan.validation.goalMinLength`: "Цель должна содержать не менее 5 символов".
  - Remove the same obsolete keys as in `en.json`.

- [ ] **Step 3: Commit**
```bash
git add frontend/messages/en.json frontend/messages/ru.json
git commit -m "intl: update EN and RU translations, remove obsolete keys"
```

### Task 2: Create Kazakh Translation File

**Files:**
- Create: `frontend/messages/kk.json`

- [ ] **Step 1: Create `kk.json` with full translations**
  - Use the content provided in the design doc.

- [ ] **Step 2: Commit**
```bash
git add frontend/messages/kk.json
git commit -m "intl: add Kazakh (kk) translation file"
```

### Task 3: Enable Kazakh Locale in Routing and Middleware

**Files:**
- Modify: `frontend/src/i18n/routing.ts`
- Modify: `frontend/src/middleware.ts`

- [ ] **Step 1: Update `routing.ts`**
  - Add `'kk'` to `locales`.
```typescript
export const routing = defineRouting({
  locales: ['en', 'ru', 'kk'],
  defaultLocale: 'ru'
});
```

- [ ] **Step 2: Update `middleware.ts`**
  - Update the locale extraction regex to include `kk`.
```typescript
const pathnameWithoutLocale = pathname.replace(/^\/(en|ru|kk)/, '') || '/';
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/i18n/routing.ts frontend/src/middleware.ts
git commit -m "intl: enable Kazakh locale in routing and middleware"
```

### Task 4: Update Language Switcher UI

**Files:**
- Modify: `frontend/src/components/shared/language-switcher.tsx`

- [ ] **Step 1: Add Kazakh to `LOCALES`**
```typescript
const LOCALES = [
  { code: 'en', label: 'English' },
  { code: 'ru', label: 'Русский' },
  { code: 'kk', label: 'Қазақша' }
];
```

- [ ] **Step 2: Commit**
```bash
git add frontend/src/components/shared/language-switcher.tsx
git commit -m "ui: add Kazakh to language switcher"
```

### Task 5: Localize Validation Messages in LearningPlanGenerator

**Files:**
- Modify: `frontend/src/components/features/learning-plan-generator.tsx`

- [ ] **Step 1: Refactor Zod schema to use dynamic translations**
  - Move the schema inside the component or use a function that accepts `t`.

```typescript
export function LearningPlanGenerator() {
  const t = useTranslations('Plan');
  
  const formSchema = z.object({
    goal: z.string().min(5, t('validation.goalMinLength')),
    // ...
  });
  // ...
}
```

- [ ] **Step 2: Commit**
```bash
git add frontend/src/components/features/learning-plan-generator.tsx
git commit -m "intl: localize goal validation message"
```

### Task 6: Final Verification

- [ ] **Step 1: Verify all locales**
  - Switch between EN, RU, and KK.
  - Check the "Learning Plan" page heading in each.
  - Trigger validation in each.

- [ ] **Step 2: Final Commit (if needed)**
```bash
git commit --allow-empty -m "chore: localization verification complete"
```
