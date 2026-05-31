# Детальный технический обзор бэкенд-кода (Backend Overview with Source Code)

В этом документе собраны ключевые фрагменты исходного кода проекта **Course Advisor** с указанием путей к файлам. Он охватывает архитектурные компоненты, доменные и ORM-модели, систему аутентификации (Auth), интеграцию с ИИ (AI) и ключевые бизнес-сервисы.

---

## 1. Доменные сущности и ORM-модели базы данных (Models & Entities)

### Доменная модель пользователя (User Entity)
*   **Файл**: `backend/app/domain/identity/entities.py`
*   **Описание**: Чистый класс данных Python (`dataclass`), представляющий профиль пользователя и его предпочтения в обучении без привязки к СУБД.

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class User:
    id: Optional[int]
    email: str
    full_name: Optional[str]
    disabled: bool = False
    is_admin: bool = False
    hashed_password: Optional[str] = None
    career_goal: Optional[str] = None
    onboarding_completed: bool = False
    interests: Optional[List[str]] = None
    default_skill_level: Optional[str] = None
    default_learning_style: Optional[str] = None
    default_study_time: Optional[int] = 10
```

### ORM-модели SQLAlchemy (Database Models)
*   **Файл**: `backend/app/infrastructure/db/models.py`
*   **Описание**: Описание таблиц базы данных и связей между ними. Ниже приведены основные модели пользователей (`UserORM`) и уроков (`LessonORM`).

```python
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    disabled: Mapped[bool] = mapped_column(default=False)
    onboarding_completed: Mapped[bool] = mapped_column(default=False)
    career_goal: Mapped[str] = mapped_column(Text, nullable=True)
    interests: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Настройки по умолчанию
    default_skill_level: Mapped[str] = mapped_column(String, nullable=False, default="Beginner")
    default_learning_style: Mapped[str] = mapped_column(String, nullable=False, default="Practical")
    default_study_time: Mapped[int] = mapped_column(default=10)

class LessonORM(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("learning_plans.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="upcoming")
    is_external: Mapped[bool] = mapped_column(default=False)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_resources: Mapped[List[dict]] = mapped_column(JSON, nullable=False, default=list)

    plan: Mapped["LearningPlanORM"] = relationship("LearningPlanORM", back_populates="lessons")
```

---

## 2. Безопасность и Аутентификация (Security & Auth)

### Функции криптографии и токенов (Security Helpers)
*   **Файл**: `backend/app/core/security.py`
*   **Описание**: Хеширование паролей при помощи `pwdlib` и создание JWT-токенов доступа с помощью `PyJWT`.

```python
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from pwdlib import PasswordHash
from .config import settings

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

### Защитная зависимость авторизации (Auth Dependency)
*   **Файл**: `backend/app/api/deps.py`
*   **Описание**: FastAPI зависимость (`Depends`) для извлечения, декодирования JWT и проверки текущего активного пользователя из БД.

```python
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.infrastructure.db.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise credentials_exception
        token_data = TokenData(email=sub)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception
        
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user
```

### Эндпоинты авторизации (Auth Endpoints)
*   **Файл**: `backend/app/api/v1/endpoints/auth.py`
*   **Описание**: Вход по логину/паролю (выдача JWT) и регистрация новых пользователей.

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.schemas.auth import UserCreate, UserPublic, Token
from app.core.security import get_password_hash, create_access_token
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.api.deps import get_db

router = APIRouter()

@router.post("/register", response_model=UserPublic)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_exists = user_repo.get_by_email(user_in.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        id=None, email=user_in.email, full_name=user_in.full_name, hashed_password=hashed_password
    )
    created_user = user_repo.create(new_user)
    return created_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 3. Интеграция с искусственным интеллектом (AI Integration)

### 1. Интеллектуальный ReAct-агент (Advisor ReAct Agent)
*   **Файл**: `backend/app/infrastructure/ai/agent.py`
*   **Описание**: Создание агента `LlamaIndex` с системным промптом, историей диалога и внешними инструментами поиска.

```python
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import LLM
from llama_index.core.tools import FunctionTool
from app.infrastructure.ai.tavily_search import TavilySearch
from app.infrastructure.ai.prompts.manager import PromptManager

search_client = TavilySearch()

async def search_external_resources(query: str) -> str:
    """Инструмент поиска образовательных материалов через Tavily API"""
    try:
        materials = await search_client.search_educational_materials(query, max_results=5)
        results = []
        for res in materials:
            results.append(f"- [{res['title']}]({res['url']}): {res['description'][:200]}")
        return "\n".join(results) if results else "No external resources found."
    except Exception as e:
        return f"Error searching for external resources: {str(e)}"

def get_advisor_agent(
    llm: LLM,
    transcript_summary: str = "No transcript provided.",
    current_skills: str = "No skills provided.",
    user = None,
    learning_plan = None,
) -> ReActAgent:
    # Инициализация поискового инструмента, который агент вызывает при необходимости
    tools = [FunctionTool.from_defaults(async_fn=search_external_resources)]

    user_context = ""
    if user:
        user_context += f"- User: {user.full_name or user.email}\n"
        if user.career_goal:
            user_context += f"- Career Goal: {user.career_goal}\n"

    plan_context = ""
    if learning_plan:
        plan_context += f"- Current Learning Plan Goal: {learning_plan.goal}\n"
        steps_str = "\n".join([f"  {s.order}. {s.title}: {s.description}" for s in learning_plan.steps])
        plan_context += f"- Plan Steps:\n{steps_str}\n"

    system_prompt = PromptManager.get_advisor_system_prompt(
        user_context=user_context,
        transcript_summary=transcript_summary,
        current_skills=current_skills,
        plan_context=plan_context,
    )

    return ReActAgent(tools=tools, llm=llm, system_prompt=system_prompt)
```

### 2. Генератор глобального анализа пробелов в знаниях (Global Analysis Agent)
*   **Файл**: `backend/app/infrastructure/ai/analysis_agent.py`
*   **Описание**: Генерация комплексной структуры учебного плана на базе Pydantic-схемы с парсингом неформатированного JSON от LLM.

```python
import re
import logging
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.llms import LLM
from app.infrastructure.ai.prompts.manager import PromptManager
from app.domain.recommendation.entities import Student

logger = logging.getLogger(__name__)

async def generate_global_analysis(
    llm: LLM, student: Student, courses: list, goal_msg: str, language: str = "en"
):
    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)

    parser = PydanticOutputParser(GlobalAnalysis)
    prompt_template_str = PromptManager.get_global_analysis_prompt(
        language=language,
        transcript_summary=transcript_summary,
        current_skills=current_skills,
        goal_msg=goal_msg,
        schema=parser.format(""),
    )

    response = await llm.acomplete(prompt_template_str)
    raw_output = response.text.strip()

    # Очистка выдачи от markdown-блоков ```json ... ```
    raw_output = re.sub(r"^```json\s*", "", raw_output, flags=re.MULTILINE)
    raw_output = re.sub(r"```\s*$", "", raw_output, flags=re.MULTILINE)

    # Поиск валидных границ JSON
    start = raw_output.find("{")
    end = raw_output.rfind("}")
    if start != -1 and end != -1:
        raw_output = raw_output[start : end + 1]

    # Фильтрация непечатных символов
    raw_output = "".join(c for c in raw_output if ord(c) >= 32 or c in "\n\r\t")

    try:
        return parser.parse(raw_output)
    except Exception:
        # Вторая попытка с удалением лишних запятых
        clean_output = re.sub(r",\s*\}", "}", raw_output)
        clean_output = re.sub(r",\s*\]", "]", clean_output)
        return parser.parse(clean_output)
```

---

## 4. Ключевые сервисы (Core Services)

### 1. Генерация учебных планов (Learning Plan Service)
*   **Файл**: `backend/app/services/learning_plan_service.py`
*   **Описание**: Генерация полной траектории обучения и наполнение её уроков ссылками из интернета.

```python
import asyncio
from app.domain.recommendation.entities import Student, LearningPlan, Lesson, ModelProvider
from app.infrastructure.ai.model_factory import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis

class LearningPlanService:
    def __init__(self, profile_repo, plan_repo, lesson_service):
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo
        self.lesson_service = lesson_service

    async def generate_plan(self, user, request=None) -> LearningPlan:
        if user.id is None:
            raise ValueError("User ID cannot be None")

        # Сбор исходных данных о навыках и оценках
        skills = self.profile_repo.get_skills(user.id)
        transcript = self.profile_repo.get_transcript(user.id)

        student = Student(
            id=str(user.id),
            name=user.full_name or "Student",
            transcript=transcript,
            current_skills=[s.skill_name for s in skills],
        )

        llm = get_model(ModelProvider.AUTO)
        goal = request.goal if request else (user.career_goal or "General Growth")
        language = request.language if request and hasattr(request, "language") else "en"

        goal_msg = f"Goal: {goal}. Style: Practical."

        # Генерация плана через ИИ
        parsed = await generate_global_analysis(llm, student, [], goal_msg, language)
        final_title = parsed.title if hasattr(parsed, "title") else goal

        learning_path = []
        for step in parsed.learning_path:
            learning_path.append(
                Lesson(
                    order=step.order,
                    title=step.title,
                    description=step.description,
                    is_external=step.is_external,
                    status="upcoming",
                    materials=[],
                )
            )

        if learning_path:
            learning_path.sort(key=lambda x: x.order)
            learning_path[0].status = "current" # делаем первый урок активным

            # Обогащение уроков ссылками на статьи/видео через Tavily Search (параллельно)
            enrich_tasks = [
                self._enrich_lesson_materials(lesson, language) 
                for lesson in learning_path
            ]
            await asyncio.gather(*enrich_tasks)

        # Сохранение в БД
        self.plan_repo.deactivate_all_plans(user.id)
        initial_plan = LearningPlan(
            id=None,
            goal=final_title,
            steps=learning_path,
            is_active=True,
            language=language,
        )
        saved_plan = self.plan_repo.create_plan(user.id, initial_plan)
        self.plan_repo.db.commit()
        return saved_plan
```

### 2. Динамическая генерация лекций и AI-оценка тестов (Lesson Service)
*   **Файл**: `backend/app/services/lesson_service.py`
*   **Описание**: Генерация контента урока в формате Markdown/LaTeX по запросу и умная проверка свободных ответов с прощающим сравнением синонимов через LLM.

```python
import logging
from fastapi import HTTPException
from sqlalchemy import select
from app.infrastructure.db.models import LessonORM

logger = logging.getLogger(__name__)

class LessonService:
    def __init__(self, plan_repo, db):
        self.plan_repo = plan_repo
        self.db = db

    async def get_lesson_detail(self, user, lesson_id: int):
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            return None

        # Если лекция ещё не была сгенерирована ИИ, делаем это при первом открытии
        if not lesson.content:
            logger.info(f"Generating content for lesson {lesson_id} in real time")
            search_query = f"{lesson.title} {lesson.description}"
            search_context = await self.search_client.get_search_context(search_query)

            prompt = f"""You are an expert academic educator. Generate a comprehensive lesson in strict Markdown format.
Use KaTeX/LaTeX for math: Inline: $x+y$, Block: $$ x^2 $$.
OUTPUT LANGUAGE: {plan_language}.
Title: {lesson.title}
Description: {lesson.description}
Context: {search_context}
"""
            import openai
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()

            # Сохранение сгенерированного текста лекции в БД
            lesson_orm = self.db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
            if lesson_orm:
                lesson_orm.content = content
                self.db.commit()

        return self.plan_repo.get_lesson_with_materials(user.id, lesson.plan_id, lesson_id)

    async def _review_typing_answer_with_ai(self, question: dict, user_answer: str) -> bool:
        """Интеллектуальная оценка ответов со свободным вводом (Short Answer)"""
        if not user_answer or not user_answer.strip():
            return False

        prompt = f"""You are an expert grading assistant. Review if the student's answer is factually correct.
Question: {question.get('question')}
Correct Answer: {question.get('correct_answer_text')}
Student's Answer: {user_answer}

Consider synonyms, spelling variations, or minor typos as correct.
Output ONLY "YES" if correct, or "NO" if incorrect.
"""
        from app.infrastructure.ai.model_factory import get_model
        llm = get_model()
        response = await llm.acomplete(prompt)
        result = response.text.strip().upper()
        
        return "YES" in result
```

### 3. Потоковый чат-ассистент (Chat Service SSE Streaming)
*   **Файл**: `backend/app/services/chat_service.py`
*   **Описание**: Асинхронный генератор сообщений (SSE) для мгновенной посимвольной выдачи ответов ИИ в интерфейс пользователя с сохранением истории.

```python
import re
from typing import AsyncGenerator
from llama_index.core.base.llms.types import ChatMessage as LLMChatMessage, MessageRole
from llama_index.core.agent.workflow.workflow_events import AgentStream
from app.infrastructure.ai.model_factory import get_model
from app.infrastructure.ai.agent import get_advisor_agent

class ChatService:
    async def stream_chat(self, user, request) -> AsyncGenerator[str, None]:
        # Сбор контекста профиля
        skills = self.profile_repo.get_skills(user.id)
        transcript = self.profile_repo.get_transcript(user.id)
        active_plan = self.plan_repo.get_active_plan(user.id)

        session_id = request.session_id
        session = self.chat_repo.get_session(user.id, session_id)

        # Подготовка истории диалога для ИИ
        chat_messages = []
        for m in session.messages:
            role = MessageRole.USER if m.role == "user" else MessageRole.ASSISTANT
            chat_messages.append(LLMChatMessage(role=role, content=m.content))

        llm = get_model()
        agent = get_advisor_agent(
            llm,
            transcript_summary=", ".join([e.subject_name for e in transcript]),
            current_skills=", ".join([s.skill_name for s in skills]),
            user=user,
            learning_plan=active_plan,
        )

        handler = agent.run(user_msg=request.message, chat_history=chat_messages)

        full_response = ""
        final_answer_started = False
        
        # Стриминг событий
        async for event in handler.stream_events():
            if isinstance(event, AgentStream):
                if getattr(event, "thinking_delta", None):
                    continue # Пропускаем внутренние рассуждения (CoT)

                delta = event.delta
                full_response += delta

                # Фильтруем вывод, отдавая пользователю только "Final Answer"
                if not final_answer_started:
                    if re.search(r"(?:^|\n)Final Answer:", full_response):
                        final_answer_started = True
                        parts = re.split(r"(?:^|\n)Final Answer:", full_response)
                        part = parts[-1].lstrip()
                        if part:
                            yield part
                else:
                    yield delta

        # Сохранение нового вопроса и ответа в СУБД SQLite/PostgreSQL и кэш Redis
        clean_response = full_response
        if re.search(r"(?:^|\n)Final Answer:", clean_response):
            clean_response = re.split(r"(?:^|\n)Final Answer:", clean_response)[-1].strip()

        self.chat_repo.add_message(session_id, "user", request.message)
        self.chat_repo.add_message(session_id, "assistant", clean_response)
        await self.chat_history.add_message(user.email, "user", request.message)
        await self.chat_history.add_message(user.email, "assistant", clean_response)
```
