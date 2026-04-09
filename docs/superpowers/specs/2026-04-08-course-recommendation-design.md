# Design Spec: University Course Recommendation Backend

## 1. Overview
A decoupled university course recommendation system that uses a hybrid scoring engine (Skill Gap, RAG, Content/Cosine, and Preference) powered by PydanticAI and PostgreSQL/pgvector.

## 2. Architecture
The system consists of three services managed by Docker Compose:
- **Backend (FastAPI)**: Orchestrates the recommendation logic and LLM interaction.
- **Frontend (Streamlit)**: Provides the user interface for transcript entry and result visualization.
- **Database (PostgreSQL + pgvector)**: Stores course metadata and vector embeddings.
- **LLM Runner (Docker)**: Local LLM service (e.g., Ollama or LocalAI) for reasoning.

## 3. Data Models (Pydantic v2)

### 3.1. Core Entities
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class TranscriptEntry(BaseModel):
    subject_name: str
    credits: float
    mark: float = Field(ge=0, le=100)

class Student(BaseModel):
    id: str
    name: str
    transcript: List[TranscriptEntry]
    current_skills: List[str]

class Course(BaseModel):
    id: str
    subject_name: str
    credits: float
    description: str
    prerequisites: List[str]
    skills_taught: List[str]
    difficulty: float = Field(ge=0, le=1)
    workload: float = Field(ge=0, le=1)
```

### 3.2. Recommendation Models
```python
class UserPreference(BaseModel):
    interest_tags: List[str]
    target_difficulty: float
    max_workload: float

class ScoreBreakdown(BaseModel):
    skill_gap: float
    content_sim: float
    preference: float
    difficulty: float
    load: float

class RecommendationResult(BaseModel):
    course_id: str
    subject_name: str
    score: float
    breakdown: ScoreBreakdown
    reason_tags: List[str]
    is_external: bool = False
    url: Optional[str] = None

class RecommendationResponse(BaseModel):
    results: List[RecommendationResult]
```

## 4. Scoring Engine (Hybrid Scorer)
The final score is a weighted average of four components:

| Scorer | weight | Method |
| :--- | :--- | :--- |
| **Content Scorer** | 30% | Cosine similarity via `pgvector` comparing transcript subjects to course descriptions. |
| **Skill Gap Scorer**| 30% | Set difference analysis between `Course.skills_taught` and `Student.current_skills`. |
| **RAG Scorer** | 20% | PydanticAI agent reasoning over course syllabus vs student transcript/goals. |
| **Preference Scorer**| 20% | Heuristic matching of `interest_tags` and penalty for exceeding difficulty/workload limits. |

## 5. Implementation Details

### 5.1. Backend (FastAPI + PydanticAI)
- **Agent**: Uses `pydantic_ai.Agent` to parse student data and generate the "reasoning" part of the recommendation.
- **Vector Search**: SQL queries using `pgvector` operator (`<=>`) for cosine similarity.

### 5.2. Database Schema
- `courses` table: `id`, `subject_name`, `credits`, `description`, `skills_taught` (JSONB/Array), `difficulty`, `workload`, `embedding` (VECTOR(1536)).

### 5.3. Frontend (Streamlit)
- Forms for inputting transcript data (Subject Name, Credits, Mark).
- Slider inputs for `UserPreference`.
- Dynamic list or grid showing recommended courses with their score breakdowns.

## 6. Success Criteria
- [ ] Successfully parse a list of transcript entries from transctipt.html.
- [ ] Return structured JSON matching `RecommendationResponse`.
- [ ] Correctly rank courses based on hybrid logic.
- [ ] Run entirely locally via Docker Compose.
