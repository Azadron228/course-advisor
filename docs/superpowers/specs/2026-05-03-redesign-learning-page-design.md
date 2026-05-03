# Design Spec: Redesigned Learning Page Experience

## 1. Overview
Redesign the core learning experience by transforming course materials into dedicated, interactive lesson pages. Each lesson will feature a high-readability reading environment, a persistent AI-powered study assistant anchored to the content, and AI-generated practice tests to verify mastery and track progress.

## 2. User Experience (UX)

### 2.1 Lesson Page (`/[locale]/lesson/[id]`)
- **Layout:** "Textbook Sidebar" (Approach 1).
  - **Main Content (65-70% width):** Focused Markdown reading area with a progress bar at the top.
  - **Right Sidebar (30-35% width):** Persistent AI Chat window.
- **AI Chat Behavior:**
  - Anchored to the current lesson content.
  - Initialized with a system prompt grounding it in the lesson text.
  - Provides quick actions like "Summarize" or "Explain this concept".
- **Navigation:**
  - Accessed via the Learning Plan dashboard steps.
  - Clicking a step navigates to the full lesson page instead of opening a drawer.

### 2.2 Practice Test Experience
- **Generation:** AI-generated in the background when the lesson page is first opened.
- **Access:** A "Knowledge Check" card at the bottom of the lesson text.
- **Separate Page (`/[locale]/lesson/[id]/test`):**
  - Immersive, distraction-free UI.
  - One question at a time or scrollable list.
  - Immediate feedback and score tracking.

## 3. Technical Architecture

### 3.1 Data Model Updates
- **`practice_tests` table:**
  - `id` (PK)
  - `material_id` (FK to `CourseMaterial.id`)
  - `content` (JSON: questions, options, correct_answers, explanations)
  - `created_at`
- **`user_test_scores` table:**
  - `id` (PK)
  - `user_id` (FK)
  - `material_id` (FK to `CourseMaterial.id`)
  - `score` (Integer)
  - `attempts` (Integer)
  - `completed_at`

*Note: The `LearningPathStep.resource_id` will be used as the link to the `CourseMaterial.id`.*

### 3.2 AI Integration
- **Background Generation:** 
  - Triggered on lesson load.
  - Backend task generates a test based on lesson content.
  - Stores in `practice_tests` if not already present.
- **Anchored Chat:**
  - System prompt includes the full lesson text (or summary if too long).
  - Scope is limited to the lesson material.

### 3.3 Components
- `LessonPage`: Parent container.
- `LessonMarkdown`: Content viewer with scroll tracking.
- `LessonSidebarChat`: Compact, anchored chat component.
- `PracticeTestUI`: Interactive test form.
- `TestResultSummary`: Score and AI feedback display.

## 4. Success Criteria
- [ ] Users can navigate from Plan -> Full Lesson Page.
- [ ] AI Chat effectively answers questions based *only* on the lesson content.
- [ ] Practice tests are generated and ready by the time a user finishes reading.
- [ ] Test scores are accurately recorded and visible in the user's progress.

## 5. Potential Risks & Mitigations
- **Token Limits:** For extremely long lessons, the AI chat will use a sliding window or summary of the content.
- **AI Hallucinations in Tests:** Tests will include "Reference Text" to explain why an answer is correct, pulled directly from the lesson.
- **Mobile Experience:** The sidebar will collapse into a bottom sheet or toggleable panel on mobile.
