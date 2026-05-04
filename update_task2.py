import os

entities_path = ".worktrees/redesign-learning-page/backend/app/domain/catalog/entities.py"
router_path = ".worktrees/redesign-learning-page/backend/app/api/router.py"
init_path = ".worktrees/redesign-learning-page/backend/app/api/v1/__init__.py"

# Update entities.py
with open(entities_path, "a") as f:
    f.write("""

@dataclass
class PracticeTest:
    id: int
    material_id: int
    content: dict
    created_at: str

@dataclass
class UserTestScore:
    id: int
    user_id: int
    material_id: int
    score: int
    attempts: int
    completed_at: str
""")

# Update router.py
with open(router_path, "r") as f:
    router_content = f.read()

router_content = router_content.replace(
    "from app.api.v1.endpoints import auth, recommendations, parser, admin, users, learning_plan, dashboard, courses",
    "from app.api.v1.endpoints import auth, recommendations, parser, admin, users, learning_plan, dashboard, courses, lessons"
)
router_content += 'api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])\n'

with open(router_path, "w") as f:
    f.write(router_content)

# Update __init__.py
with open(init_path, "r") as f:
    init_content = f.read()

init_content = init_content.replace(
    "from .endpoints import auth, recommendations, parser, admin, users, courses, dashboard, learning_plan",
    "from .endpoints import auth, recommendations, parser, admin, users, courses, dashboard, learning_plan, lessons"
)
init_content = init_content.replace(
    ']',
    '    "lessons",\n]'
)

with open(init_path, "w") as f:
    f.write(init_content)
