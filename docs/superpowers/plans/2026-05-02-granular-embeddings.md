# Granular Material-Level Embeddings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement granular chunking and storage for course material embeddings to handle large files and improve search precision.

**Architecture:** Introduce a `course_material_chunks` table to store fragmented content and embeddings. Update the recommendation engine to use the "best-matching chunk" for similarity scoring.

**Tech Stack:** Python, FastAPI, SQLAlchemy (pgvector), llama-index (TokenTextSplitter).

---

### Task 1: Database Migration and Models

**Files:**
- Create: `backend/alembic/versions/2026_05_02_add_course_material_chunks.py`
- Modify: `backend/app/infrastructure/db/models.py`

- [ ] **Step 1: Update models.py**

Add the `CourseMaterialChunkORM` and update `CourseMaterialORM`.

```python
# backend/app/infrastructure/db/models.py

# ... existing imports ...
from pgvector.sqlalchemy import Vector

class CourseMaterialORM(Base):
    __tablename__ = "course_materials"
    # ... existing fields ...
    chunks: Mapped[List["CourseMaterialChunkORM"]] = relationship(
        back_populates="material", cascade="all, delete-orphan"
    )

class CourseMaterialChunkORM(Base):
    __tablename__ = "course_material_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("course_materials.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[List[float]] = mapped_column(Vector(1536), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    material: Mapped["CourseMaterialORM"] = relationship(back_populates="chunks")
```

- [ ] **Step 2: Create migration file**

Since database connection might be restricted, create the migration file manually in `backend/alembic/versions/`. (Note: Rev ID should be unique, using `20260502_chunks` as a placeholder or following local pattern).

```python
"""add course material chunks

Revision ID: 20260502_chunks
Revises: 1a68ae6f82ce
Create Date: 2026-05-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '20260502_chunks'
down_revision = '1a68ae6f82ce' # Need to verify latest revision
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'course_material_chunks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['material_id'], ['course_materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('course_material_chunks')
```

- [ ] **Step 3: Run migration**

Run: `./.venv/bin/alembic upgrade head`
Expected: Success (Ensure `down_revision` is correct before running).

- [ ] **Step 4: Commit**

```bash
git add backend/app/infrastructure/db/models.py backend/alembic/versions/
git commit -m "feat: add course_material_chunks table and ORM model"
```

---

### Task 2: Domain Entities and Chunking Utility

**Files:**
- Modify: `backend/app/domain/catalog/entities.py`
- Modify: `backend/app/infrastructure/ai/embeddings.py`

- [ ] **Step 1: Update CourseMaterialChunk entity**

```python
# backend/app/domain/catalog/entities.py

@dataclass
class CourseMaterialChunk:
    id: Optional[int]
    material_id: int
    content: str
    embedding: List[float]
    chunk_index: int
```

- [ ] **Step 2: Add chunking utility**

```python
# backend/app/infrastructure/ai/embeddings.py

from llama_index.core.node_parser import TokenTextSplitter

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[str]:
    """Splits text into overlapping chunks using llama-index TokenTextSplitter."""
    splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/domain/catalog/entities.py backend/app/infrastructure/ai/embeddings.py
git commit -m "feat: add chunking utility and domain entity"
```

---

### Task 3: Repository Enhancements

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/course_repository.py`

- [ ] **Step 1: Add chunk management methods**

Add `add_material_chunks` and `get_best_material_similarity`.

```python
# backend/app/infrastructure/db/repositories/course_repository.py
from sqlalchemy import func
from app.infrastructure.db.models import CourseMaterialChunkORM, CourseMaterialORM
from app.domain.catalog.entities import CourseMaterialChunk

# Inside CourseRepository:

    def add_material_chunks(self, chunks: list[CourseMaterialChunk]) -> None:
        for chunk in chunks:
            orm = CourseMaterialChunkORM(
                material_id=chunk.material_id,
                content=chunk.content,
                embedding=chunk.embedding,
                chunk_index=chunk.chunk_index
            )
            self.db.add(orm)
        self.db.commit()

    def get_best_material_similarity(self, course_id: int, student_embedding: list[float]) -> float:
        """Finds the maximum similarity score among all chunks of a course."""
        query = (
            select(func.max(1 - CourseMaterialChunkORM.embedding.cosine_distance(student_embedding)))
            .join(CourseMaterialORM)
            .where(CourseMaterialORM.course_id == course_id)
        )
        result = self.db.scalar(query)
        return float(result) if result is not None else 0.0
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/infrastructure/db/repositories/course_repository.py
git commit -m "feat: add chunking support to CourseRepository"
```

---

### Task 4: Integration - Admin API

**Files:**
- Modify: `backend/app/api/v1/endpoints/admin.py`

- [ ] **Step 1: Update upload_course_materials**

Modify the endpoint to chunk the content and save embeddings for each chunk.

```python
# backend/app/api/v1/endpoints/admin.py
from app.infrastructure.ai.embeddings import get_embedding, chunk_text
from app.domain.catalog.entities import CourseMaterialChunk

# Inside upload_course_materials:

    # ... after saved_material = course_repo.add_material(material) ...

    # Chunk and Embed
    text_chunks = chunk_text(content)
    chunks_to_save = []
    for i, chunk_txt in enumerate(text_chunks):
        emb = get_embedding(chunk_txt)
        chunks_to_save.append(CourseMaterialChunk(
            id=None, 
            material_id=saved_material.id, 
            content=chunk_txt, 
            embedding=emb, 
            chunk_index=i
        ))
    
    course_repo.add_material_chunks(chunks_to_save)

    # Trigger course embedding update (NOW ONLY USES DESCRIPTION)
    new_embedding = get_embedding(course.description)
    from dataclasses import replace
    updated_course = replace(course, embedding=new_embedding)
    course_repo.save(updated_course)

    return saved_material
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/endpoints/admin.py
git commit -m "feat: integrate chunking into admin material upload"
```

---

### Task 5: Integration - Scoring Refactor

**Files:**
- Modify: `backend/app/services/advisor_service.py`

- [ ] **Step 1: Update recommendation scoring**

Refactor `recommend` to use the best of description and material chunk similarities.

```python
# backend/app/services/advisor_service.py

# Inside recommend method:

        for course in courses:
            # 1. Broad match (Description)
            desc_sim = self.course_repo.get_content_similarity(course.id, student_embedding)
            
            # 2. Granular match (Best Material Chunk)
            chunk_sim = self.course_repo.get_best_material_similarity(course.id, student_embedding)
            
            # Final content similarity is the best match found
            content_sim = max(desc_sim, chunk_sim)

            skill_gap = self.scoring_service.calculate_skill_gap(student, course)
            # ... rest of scoring remains the same ...
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/advisor_service.py
git commit -m "refactor: use max similarity across chunks for recommendation scoring"
```

---

### Task 6: Cleanup & Seed Script

**Files:**
- Modify: `backend/seed.py`

- [ ] **Step 1: Update seed script**

Ensure materials in `seed.py` are also chunked.

```python
# backend/seed.py
from app.infrastructure.ai.embeddings import chunk_text
from app.domain.catalog.entities import CourseMaterialChunk

# Inside seed() loop:

            # After session.add(material) and session.flush():
            text_chunks = chunk_text(c["materials_content"])
            for i, chunk_txt in enumerate(text_chunks):
                emb = get_embedding(chunk_txt)
                chunk_orm = CourseMaterialChunkORM(
                    material_id=material.id,
                    content=chunk_txt,
                    embedding=emb,
                    chunk_index=i
                )
                session.add(chunk_orm)
```

- [ ] **Step 2: Run seed script**

Run: `python backend/seed.py`
Expected: Database seeded with chunks.

- [ ] **Step 3: Final Commit**

```bash
git add backend/seed.py
git commit -m "chore: update seed script to support chunked materials"
```
