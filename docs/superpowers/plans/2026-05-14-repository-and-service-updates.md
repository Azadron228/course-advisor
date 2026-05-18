# Repository and Service Updates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update PlanRepository and LessonService to support persisting user answers in practice tests and returning the last attempt's results.

**Architecture:** Update the repository layer to handle the new `answers` field and add a method to retrieve the last test score. Refactor the service layer to use a shared grading method and include the last attempt in the practice test response.

**Tech Stack:** Python, SQLAlchemy, FastAPI

---

### Task 1: Update PlanRepository

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`

- [ ] **Step 1: Update save_test_score to accept answers**

```python
<<<<
    def save_test_score(self, user_id: int, lesson_id: int, score: int):
        # 1. Check if user already has a score for this lesson
        existing_score = self.db.scalar(
            select(UserTestScoreORM)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )

        if existing_score:
            # 2. Update if higher or same
            if score > existing_score.score:
                existing_score.score = score
            existing_score.attempts += 1
            existing_score.completed_at = datetime.now(timezone.utc)
        else:
            # 3. Create new
            new_score = UserTestScoreORM(
                user_id=user_id,
                lesson_id=lesson_id,
                score=score,
                attempts=1,
            )
            self.db.add(new_score)

        self.db.commit()
====
    def save_test_score(self, user_id: int, lesson_id: int, score: int, answers: list) -> None:
        # 1. Check if user already has a score for this lesson
        existing_score = self.db.scalar(
            select(UserTestScoreORM)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )

        if existing_score:
            # 2. Always update score and answers for the latest attempt
            existing_score.score = score
            existing_score.answers = {"answers": answers}
            existing_score.attempts += 1
            existing_score.completed_at = datetime.now(timezone.utc)
        else:
            # 3. Create new
            new_score = UserTestScoreORM(
                user_id=user_id,
                lesson_id=lesson_id,
                score=score,
                answers={"answers": answers},
                attempts=1,
            )
            self.db.add(new_score)

        self.db.commit()
>>>>
```

- [ ] **Step 2: Add get_last_test_score**

```python
    def get_last_test_score(self, user_id: int, lesson_id: int) -> Optional[UserTestScoreORM]:
        return self.db.scalar(
            select(UserTestScoreORM)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py
git commit -m "feat: update PlanRepository to save answers and retrieve last score"
```

### Task 2: Refactor LessonService Grading Logic

**Files:**
- Modify: `backend/app/services/lesson_service.py`

- [ ] **Step 1: Add _grade_question private method**

```python
    def _grade_question(self, question: dict, submitted: Any) -> bool:
        q_type = question.get("type", "multiple_choice")
        if q_type in ["multiple_choice", "true_false"]:
            return submitted == question.get("correct_answer_index")
        elif q_type in ["short_answer", "fill_in_the_blank"]:
            if isinstance(submitted, str) and question.get("correct_answer_text"):
                return submitted.strip().lower() == question["correct_answer_text"].strip().lower()
        return False
```

- [ ] **Step 2: Update submit_test to use _grade_question and save answers**

```python
<<<<
        for i, q in enumerate(questions):
            submitted = submission.answers[i] if i < len(submission.answers) else None
            is_correct = False
            
            q_type = q.get("type", "multiple_choice")
            if q_type in ["multiple_choice", "true_false"]:
                is_correct = submitted == q.get("correct_answer_index")
            elif q_type in ["short_answer", "fill_in_the_blank"]:
                if isinstance(submitted, str) and q.get("correct_answer_text"):
                    is_correct = submitted.strip().lower() == q["correct_answer_text"].strip().lower()
            
            if is_correct:
                correct_count += 1

            results.append(
                TestSubmissionResultItem(
                    question_index=i,
                    is_correct=is_correct,
                    correct_answer_index=q.get("correct_answer_index"),
                    correct_answer_text=q.get("correct_answer_text"),
                    explanation=q["explanation"],
                )
            )

        # 3. Save score as percentage
        score_percentage = int((correct_count / len(questions)) * 100) if questions else 0
        self.plan_repo.save_test_score(user.id, lesson_id, score_percentage)
====
        for i, q in enumerate(questions):
            submitted = submission.answers[i] if i < len(submission.answers) else None
            is_correct = self._grade_question(q, submitted)
            
            if is_correct:
                correct_count += 1

            results.append(
                TestSubmissionResultItem(
                    question_index=i,
                    is_correct=is_correct,
                    user_answer=submitted,
                    correct_answer_index=q.get("correct_answer_index"),
                    correct_answer_text=q.get("correct_answer_text"),
                    explanation=q["explanation"],
                )
            )

        # 3. Save score as percentage
        score_percentage = int((correct_count / len(questions)) * 100) if questions else 0
        self.plan_repo.save_test_score(user.id, lesson_id, score_percentage, submission.answers)
>>>>
```

- [ ] **Step 3: Update get_practice_test to include last_attempt**

```python
<<<<
    async def get_practice_test(self, user: User, lesson_id: int) -> Optional[PracticeTestResponse]:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        # 1. Get lesson and check ownership
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            return None

        plan = self.plan_repo.get_by_id(user.id, lesson.plan_id)
        if not plan:
            raise HTTPException(status_code=403, detail="Not authorized to view this lesson")

        # 2. Check for existing test
        test_orm = self.plan_repo.get_practice_test(lesson_id)
        if test_orm:
            return PracticeTestResponse(
                id=test_orm.id,
                lesson_id=test_orm.lesson_id,
                questions=test_orm.content["questions"],
            )
====
    async def get_practice_test(self, user: User, lesson_id: int) -> Optional[PracticeTestResponse]:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        # 1. Get lesson and check ownership
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            return None

        plan = self.plan_repo.get_by_id(user.id, lesson.plan_id)
        if not plan:
            raise HTTPException(status_code=403, detail="Not authorized to view this lesson")

        # 2. Check for existing test
        test_orm = self.plan_repo.get_practice_test(lesson_id)
        
        # ... (generation logic) ...
        # [If test_orm is None, it generates it. I should put the last_attempt logic after generation/retrieval]
>>>>
```

Wait, I should be careful about where I insert the `last_attempt` logic.

```python
        # 2. Check for existing test
        test_orm = self.plan_repo.get_practice_test(lesson_id)
        if not test_orm:
            # 3. Generate test if missing
            # ... (omitted generation logic) ...
            test_orm = self.plan_repo.create_practice_test(lesson_id, {"questions": questions})

        # 4. Get last attempt if it exists
        last_score = self.plan_repo.get_last_test_score(user.id, lesson_id)
        last_attempt = None
        if last_score and last_score.answers:
            questions = test_orm.content["questions"]
            prev_answers = last_score.answers.get("answers", [])
            results = []
            for i, q in enumerate(questions):
                submitted = prev_answers[i] if i < len(prev_answers) else None
                is_correct = self._grade_question(q, submitted)
                results.append(
                    TestSubmissionResultItem(
                        question_index=i,
                        is_correct=is_correct,
                        user_answer=submitted,
                        correct_answer_index=q.get("correct_answer_index"),
                        correct_answer_text=q.get("correct_answer_text"),
                        explanation=q["explanation"],
                    )
                )
            
            last_attempt = TestSubmissionResponse(
                score=int((last_score.score / 100) * len(questions)),
                total=len(questions),
                results=results
            )

        return PracticeTestResponse(
            id=test_orm.id,
            lesson_id=test_orm.lesson_id,
            questions=test_orm.content["questions"],
            last_attempt=last_attempt
        )
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/lesson_service.py
git commit -m "feat: include last attempt results in get_practice_test"
```

### Task 3: Verification

- [ ] **Step 1: Run tests**

Run: `cd backend && DATABASE_URL=sqlite:///./test.db PYTHONPATH=. .venv/bin/pytest tests/test_practice_tests.py`

- [ ] **Step 2: Manual verification (if possible)**
(Since I'm in a headless environment, I'll rely on tests)

---
