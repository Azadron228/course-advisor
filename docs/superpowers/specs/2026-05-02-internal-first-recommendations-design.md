# Design Spec: Internal-First Recommendation & Supplementary Materials

## 1. Goal
Refactor the AI Academic Strategist to prioritize the university's internal course catalog. The system should only recommend internal courses as primary learning steps. External materials (documentation, videos, articles) should be used strictly as supplementary resources for internal courses or as gap-fillers when no internal course is available. No external "courses" (e.g., Coursera, Udemy) should be recommended.

## 2. Core Logic Changes

### 2.1. AI Agent Constraints (`analysis_agent.py`)
Update the `generate_global_analysis` prompt with strict instructions:
1.  **Internal Priority:** Every learning step MUST prioritize an internal course if it covers the required skills.
2.  **No External Courses:** The agent is forbidden from recommending external "courses" (e.g., from other platforms like Coursera or edX).
3.  **Supplementary Materials:** For every internal course recommended, the agent MUST include 1-2 high-quality external **materials** (official documentation, specific YouTube tutorials, or technical articles) to support the student.
4.  **Gap Filling:** If a critical skill gap exists (e.g., a prerequisite like "Python") and no internal course is available, the agent should create a step using ONLY external **materials** (docs/videos) to fill that gap.

### 2.2. Entity Mapping
Ensure the `LearningPathStep` and `LearningMaterial` entities are used as follows:
- **`is_external` (Step level):** 
    - `False` if the step is centered around a university course.
    - `True` ONLY if no internal course exists for a mandatory prerequisite.
- **`materials` (Material level):**
    - For internal steps: First material is the course details; subsequent materials are external supplements.
    - For gap steps: All materials are external (docs, videos, etc.).

## 3. Implementation Plan
1.  **Prompt Update:** Revise the `prompt_template_str` in `backend/app/infrastructure/ai/analysis_agent.py`.
2.  **Verification:** Test with a scenario where a prerequisite is missing (e.g., "Math for AI") that isn't in the internal catalog to ensure it uses materials instead of an external course.
3.  **Refinement:** Ensure "internal course" materials in the JSON output match the `Course` ID and metadata provided in the context.

## 4. Success Criteria
- Learning paths consist primarily of internal courses.
- No "Coursera", "Udemy", or "edX" mentions in the output.
- Internal course steps include helpful documentation/video links.
- Missing prerequisites are filled with documentation/videos rather than being skipped.
