# Natural Deep Slate Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the "unnatural" dark theme by implementing a Variable-Driven Architecture with refined Deep Slate tones, focusing on borders, shadows, and inputs.

**Architecture:** Use CSS variables for logical theme tokens (background, surface, border, input, ring) mapped to Tailwind 4's `@theme` system. This allows components to be theme-aware without excessive `dark:` overrides.

**Tech Stack:** React, Next.js, Tailwind CSS 4, next-themes.

---

### Task 1: Update Global CSS Variables

**Files:**
- Modify: `frontend/src/app/globals.css`

- [ ] **Step 1: Define expanded CSS variables**

Update `:root` and `.dark` blocks with the refined palette.

```css
:root {
  --background: #f8f9ff;
  --foreground: #111827;
  --primary: #4f46e5;
  --secondary: #10b981;
  --tertiary: #f59e0b;
  --surface: #ffffff;
  --radius: 0.5rem;
  
  /* Added/Refined Variables */
  --muted: #64748b;
  --border: #e2e8f0;
  --input: #f1f5f9;
  --ring: #4f46e5;
}

.dark {
  --background: #020617; /* Slate 950 */
  --foreground: #f8fafc;
  --surface: #0f172a;    /* Slate 900 */
  --muted: #94a3b8;
  --border: #1e293b;     /* Slate 800 */
  --input: #1e293b;
  --ring: #6366f1;
}
```

- [ ] **Step 2: Map variables to Tailwind @theme**

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-secondary: var(--secondary);
  --color-tertiary: var(--tertiary);
  --color-surface: var(--surface);
  --color-muted: var(--muted);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  
  --radius-md: var(--radius);
  --font-lexend: var(--font-lexend);
  --font-inter: var(--font-inter);
}
```

- [ ] **Step 3: Update body styles**

Ensure the body uses the new background and foreground variables.

```css
body {
  background-color: var(--background);
  color: var(--foreground);
  font-family: var(--font-inter), ui-sans-serif, system-ui, sans-serif;
  transition: background-color 0.3s, color 0.3s;
}
```

- [ ] **Step 4: Commit changes**

```bash
git add frontend/src/app/globals.css
git commit -m "theme: update global css variables and tailwind mapping"
```

---

### Task 2: Refactor Layout Components

**Files:**
- Modify: `frontend/src/components/shared/main-layout.tsx`
- Modify: `frontend/src/components/shared/top-nav.tsx`
- Modify: `frontend/src/components/shared/sidebar.tsx`

- [ ] **Step 1: Update MainLayout**

Ensure the wrapper uses the standard background.

```tsx
// frontend/src/components/shared/main-layout.tsx
// Change: <div className="flex h-screen overflow-hidden bg-background">
// To: <div className="flex h-screen overflow-hidden bg-background text-foreground">
```

- [ ] **Step 2: Refactor TopNav**

Replace hardcoded slate borders with the `border-border` utility.

```tsx
// frontend/src/components/shared/top-nav.tsx
// Change: border-b border-slate-200 dark:border-slate-800
// To: border-b border-border
```

- [ ] **Step 3: Refactor Sidebar**

Update container and item styles to use logical variables.

```tsx
// frontend/src/components/shared/sidebar.tsx
// Change: bg-surface border-r border-slate-200 dark:border-slate-800
// To: bg-surface border-r border-border

// Change: isActive ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300"
// To: isActive ? "bg-primary/10 text-primary"
```

- [ ] **Step 4: Commit changes**

```bash
git add frontend/src/components/shared/main-layout.tsx frontend/src/components/shared/top-nav.tsx frontend/src/components/shared/sidebar.tsx
git commit -m "theme: refactor layout components to use logical variables"
```

---

### Task 3: Fix Dashboard and Feature Components

**Files:**
- Modify: `frontend/src/app/[locale]/dashboard/page.tsx`
- Modify: `frontend/src/components/features/dashboard-summary.tsx`

- [ ] **Step 1: Refactor Dashboard Summary Cards**

Remove hardcoded backgrounds and use surface + border variables.

```tsx
// frontend/src/components/features/dashboard-summary.tsx
// Ensure cards use: rounded-xl border border-border bg-surface p-6
```

- [ ] **Step 2: Fix Dashboard Navigation Cards**

Replace hardcoded tints (like `bg-blue-50`) with opacity-based colors.

```tsx
// frontend/src/app/[locale]/dashboard/page.tsx
// Change: color: "bg-blue-50 text-blue-600", borderColor: "border-blue-100"
// To: color: "bg-primary/10 text-primary", borderColor: "border-primary/20"
```

- [ ] **Step 3: Commit changes**

```bash
git add frontend/src/app/[locale]/dashboard/page.tsx frontend/src/components/features/dashboard-summary.tsx
git commit -m "theme: fix dashboard components backgrounds and borders"
```

---

### Task 4: Standardize Inputs and Form Fields

**Files:**
- Modify: `frontend/src/app/[locale]/login/page.tsx`
- Modify: `frontend/src/app/[locale]/register/page.tsx`
- Modify: `frontend/src/components/admin/user-table.tsx`

- [ ] **Step 1: Refactor Login/Register Inputs**

Use the new `--input` and `--border` variables for consistent form fields.

```tsx
// frontend/src/app/[locale]/login/page.tsx
// Change: border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800
// To: border-border bg-input
```

- [ ] **Step 2: Standardize Focus States**

Ensure all inputs use the unified focus ring.

```tsx
// Change: focus:ring-primary/10
// To: focus:ring-ring/20 focus:border-ring
```

- [ ] **Step 3: Commit changes**

```bash
git add frontend/src/app/[locale]/login/page.tsx frontend/src/app/[locale]/register/page.tsx frontend/src/components/admin/user-table.tsx
git commit -m "theme: standardize inputs and form fields"
```

---

### Task 5: Final Audit and Verification

- [ ] **Step 1: Search and replace remaining hardcoded slate borders**

Search for `border-slate-200` or `dark:border-slate-800` and replace with `border-border`.

- [ ] **Step 2: Verify Contrast and Shadows**

Manually check that dark mode uses subtle borders instead of heavy shadows. Ensure `shadow-sm` and `shadow-md` are either removed or overridden in dark mode for a more natural look.

- [ ] **Step 3: Final Build check**

Run `npm run build` in the frontend to ensure no styling errors were introduced.

- [ ] **Step 4: Commit final fixes**

```bash
git commit -m "theme: final audit and cleanup of hardcoded colors"
```
