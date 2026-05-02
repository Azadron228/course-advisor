# Design Spec: Natural Deep Slate Theme Refactor

## 1. Goal
Fix the "unnatural" feel of the dark theme by refining backgrounds, borders, inputs, and shadows. Ensure the white theme remains unchanged while creating a cohesive, professional dark mode experience using a Variable-Driven Architecture.

## 2. Palette Refinement (Deep Slate)
We will move to a deeper, more cohesive Slate palette for dark mode to provide better contrast and a more "natural" feel of elevation.

| Variable | Light Mode | Dark Mode (Refined) | Purpose |
| :--- | :--- | :--- | :--- |
| `--background` | `#f8f9ff` | `#020617` (Slate 950) | Primary app background |
| `--surface` | `#ffffff` | `#0f172a` (Slate 900) | Cards, sidebars, modals |
| `--foreground` | `#111827` | `#f8fafc` | Primary text |
| `--muted` | `#64748b` | `#94a3b8` | Secondary/Muted text |
| `--border` | `#e2e8f0` | `#1e293b` (Slate 800) | Standard UI borders |
| `--input` | `#f1f5f9` | `#1e293b` (Slate 800) | Input field backgrounds |
| `--ring` | `#4f46e5` | `#6366f1` | Focus rings |

## 3. Key Changes

### 3.1 CSS Variable Architecture
Move from hardcoded Tailwind classes to logical CSS variables in `globals.css`. This allows components to automatically adapt to theme changes without needing explicit `dark:` overrides everywhere.

### 3.2 Border & Shadow Refinement
- **Borders:** Replace harsh or inconsistent borders with a unified `--border` variable.
- **Shadows:** In dark mode, shadows will be significantly reduced or replaced by subtle borders. Since shadows aren't physically "natural" on dark backgrounds, we will rely on surface color shifts (`--surface` vs `--background`) to show elevation.

### 3.3 Input & Form Fields
- Fix "jarring" focus states.
- Ensure inputs use `--input` for background and `--border` for boundaries.
- Standardize focus rings using `--ring`.

### 3.4 Dashboard & Navigation Cards
- Fix hardcoded light backgrounds (e.g., `bg-blue-50`) by introducing "tinted" variables or using opacity-based backgrounds (e.g., `bg-primary/10`) that work across both themes.

## 4. Implementation Strategy
1. **Update `globals.css`:** Define the expanded variable set.
2. **Tailwind Config Update:** Map the new variables to Tailwind theme utilities (using the Tailwind 4 `@theme` block).
3. **Surgical Refactoring:** 
    - Update `layout.tsx` and `MainLayout`.
    - Fix `DashboardSummary` and `DashboardPage` (priority).
    - Refactor `TopNav` and `Sidebar`.
    - Audit and fix inputs in `Login`, `Register`, and `Admin` forms.
4. **Verification:** Test toggle transitions and verify contrast ratios in both modes.

## 5. Success Criteria
- Dark theme feels "premium" and natural (no jarring whites or unnatural shadows).
- White theme is visually identical to current state.
- No hardcoded `bg-white` or `bg-slate-50` without dark overrides.
- Form inputs have consistent, accessible focus states.
