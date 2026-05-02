# Light Theme Regression Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix light theme regressions by adjusting the `--input` variable and standardizing its usage in admin components.

**Architecture:** Surgical updates to CSS variables and component class names to align with the original design while maintaining the new variable-based system.

**Tech Stack:** React, Tailwind CSS, CSS Variables.

---

### Task 1: Update globals.css

**Files:**
- Modify: `frontend/src/app/globals.css`

- [ ] **Step 1: Change --input variable in :root**

```css
  --border: #e2e8f0;
  --input: #f8fafc;
  --ring: #4f46e5;
```

- [ ] **Step 2: Commit globals.css change**

```bash
git add frontend/src/app/globals.css
git commit -m "theme: update --input variable to Slate 50 for light theme"
```

### Task 2: Update UserTable Component

**Files:**
- Modify: `frontend/src/components/admin/user-table.tsx`

- [ ] **Step 1: Update table header background**
Replace `bg-muted/50` with `bg-input/50`.

- [ ] **Step 2: Update row hover background**
Replace `hover:bg-muted/30` with `hover:bg-input/30`.

- [ ] **Step 3: Commit UserTable changes**

```bash
git add frontend/src/components/admin/user-table.tsx
git commit -m "theme: use bg-input for UserTable headers and row hover"
```

### Task 3: Update EditUserModal Component

**Files:**
- Modify: `frontend/src/components/admin/edit-user-modal.tsx`

- [ ] **Step 1: Update input background**
Ensure inputs use `bg-input`.

- [ ] **Step 2: Commit EditUserModal changes**

```bash
git add frontend/src/components/admin/edit-user-modal.tsx
git commit -m "theme: standardize inputs to use bg-input in EditUserModal"
```

### Task 4: Final Verification

- [ ] **Step 1: Verify build**
Run: `npm run build` in `frontend` directory.

- [ ] **Step 2: Report STATUS**
