# Design Spec: Granular Material-Level Embeddings and Chunking

Currently, the Course Advisor platform aggregates all course materials into a single text string to generate a "course embedding." This approach fails when the total content exceeds the 8,191-token limit of the `text-embedding-3-small` model. This design introduces granular chunking and a separate storage layer for material-level embeddings to ensure scalability and better search precision.

## 1. Objectives
- **Scalability:** Handle arbitrarily large course materials (PDFs, long text) without hitting LLM token limits.
- **Precision:** Improve recommendation quality by matching student profiles against specific chunks of course content rather than a diluted aggregate.
- **Maintainability:** Keep the user-facing material list clean while managing fragments internally.

## 2. Proposed Architecture

### 2.1 Database Schema Change
A new table `course_material_chunks` will be added to store fragments of uploaded materials.

**Table: `course_material_chunks`**
- `id` (Primary Key, Integer)
- `material_id` (Foreign Key -> `course_materials.id`, ON DELETE CASCADE)
- `content` (Text): The actual text content of the chunk.
- `embedding` (Vector(1536)): The embedding vector for this specific chunk.
- `chunk_index` (Integer): The order of the chunk within the parent material.

### 2.2 Chunking Strategy
- **Library:** `llama-index`'s `TokenTextSplitter`.
- **Chunk Size:** 800 tokens.
- **Chunk Overlap:** 100 tokens (approx. 12.5%).
- **Model:** `text-embedding-3-small` (1536 dimensions).

### 2.3 Updated Recommendation Logic
The `AdvisorService` currently calculates `content_sim` based on the `CourseORM.embedding` (which reflects the description + all materials). We will refactor this to:
1. Calculate `description_similarity` using `CourseORM.embedding` (which will now represent *only* the course description).
2. Calculate `chunk_similarity` by finding the **maximum** cosine similarity across all `course_material_chunks` associated with that course.
3. Set `final_content_sim = max(description_similarity, chunk_similarity)`.

## 3. Implementation Plan

### Phase 1: Infrastructure & DB
- Create and run an Alembic migration for the `course_material_chunks` table.
- Update `backend/app/infrastructure/db/models.py` to include the new ORM model.
- Update `backend/app/domain/catalog/entities.py` with the `CourseMaterialChunk` dataclass.

### Phase 2: Core Logic
- Add `chunk_text` utility to `backend/app/infrastructure/ai/embeddings.py`.
- Update `CourseRepository` to support:
    - Batch saving of chunks.
    - `get_best_material_similarity` query using `func.max` and `cosine_distance`.

### Phase 3: Integration
- Update `Admin API` (`/courses/{id}/materials` POST) to perform chunking and embedding generation on upload.
- Update `AdvisorService.recommend` to use the new "Max Similarity" scoring logic.
- Update `seed.py` to ensure initial course materials are also chunked and embedded.

## 4. Testing Strategy
- **Unit Tests:** Verify the `chunk_text` utility correctly creates overlapping fragments.
- **Integration Tests:** Upload a large PDF (>10k tokens) and verify multiple chunks are created and searchable.
- **Regression:** Ensure the recommendation score remains coherent for existing courses with short descriptions.

## 5. Alternatives Considered
- **Averaging Vectors:** Transparently chunk and average vectors in `get_embedding`. This was rejected because averaging across diverse topics (e.g., a syllabus covering 10 different weeks) dilutes the search signal.
- **Direct Material Embedding:** Adding an embedding to the `course_materials` table directly. This was rejected because a single file can still exceed the token limit; a child `chunks` table is more robust.
