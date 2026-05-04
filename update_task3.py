import os

worker_settings_path = ".worktrees/redesign-learning-page/backend/app/infrastructure/queue/worker_settings.py"
lessons_path = ".worktrees/redesign-learning-page/backend/app/api/v1/endpoints/lessons.py"

# Modify worker_settings.py
with open(worker_settings_path, "r") as f:
    worker_content = f.read()

worker_content = worker_content.replace(
    "from app.tasks.recommendation_tasks import (",
    "from app.tasks.test_tasks import generate_practice_test\nfrom app.tasks.recommendation_tasks import ("
)
worker_content = worker_content.replace(
    "functions = [run_agent_task, run_hybrid_recommendation, process_material_embeddings]",
    "functions = [run_agent_task, run_hybrid_recommendation, process_material_embeddings, generate_practice_test]"
)

with open(worker_settings_path, "w") as f:
    f.write(worker_content)

# Modify lessons.py
with open(lessons_path, "r") as f:
    lessons_content = f.read()

lessons_content = lessons_content.replace(
    "from app.api.deps import get_db, get_current_active_user",
    "from app.api.deps import get_db, get_current_active_user, get_arq_pool\nfrom arq.connections import ArqRedis"
)

old_func = """@router.get("/{material_id}/test")
def get_practice_test(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_active_user),
):
    test = db.execute(select(PracticeTestORM).where(PracticeTestORM.material_id == material_id)).scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not generated yet")
    return test"""

new_func = """@router.get("/{material_id}/test")
async def get_practice_test(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_active_user),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    test = db.execute(select(PracticeTestORM).where(PracticeTestORM.material_id == material_id)).scalar_one_or_none()
    if not test:
        await arq_pool.enqueue_job("generate_practice_test", material_id)
        raise HTTPException(status_code=404, detail="Test not generated yet. Generation triggered.")
    return test"""

lessons_content = lessons_content.replace(old_func, new_func)

with open(lessons_path, "w") as f:
    f.write(lessons_content)
