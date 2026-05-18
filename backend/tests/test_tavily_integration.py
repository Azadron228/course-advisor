import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.lesson_service import LessonService
from app.domain.identity.entities import User
from app.domain.recommendation.entities import LearningPlan, Lesson

@pytest.fixture
def mock_plan_repo():
    return MagicMock()

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def lesson_service(mock_plan_repo, mock_db):
    return LessonService(mock_plan_repo, mock_db)

@pytest.mark.asyncio
async def test_get_lesson_detail_uses_tavily_and_language(lesson_service, mock_plan_repo, mock_db):
    user = User(id=1, email="test@example.com", full_name="Test User")
    lesson_id = 123
    plan_id = 456
    
    # Mock lesson and plan
    mock_lesson_orm = MagicMock()
    mock_lesson_orm.id = lesson_id
    mock_lesson_orm.plan_id = plan_id
    mock_lesson_orm.title = "React Hooks"
    mock_lesson_orm.description = "Learn about useState and useEffect"
    mock_lesson_orm.content = None
    
    mock_plan_repo.get_lesson.return_value = mock_lesson_orm
    
    mock_plan = MagicMock(spec=LearningPlan)
    mock_plan.id = plan_id
    mock_plan.language = "kk" # Kazakh
    mock_plan_repo.get_by_id.return_value = mock_plan
    
    # Mock Tavily search
    with patch.object(lesson_service.search_client, "get_search_context", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = "Search result: Use hooks for state."
        
        # Mock LLM (OpenAI and LlamaOpenAI)
        with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai, \
             patch("openai.AsyncOpenAI") as mock_openai:
            
            # Setup LlamaOpenAI mock
            mock_llm_instance = MagicMock()
            mock_llama_openai.return_value = mock_llm_instance
            mock_llm_instance.acomplete = AsyncMock()
            mock_llm_instance.acomplete.return_value.text = "# React Hooks\n\nLesson content in Kazakh."
            
            # Setup OpenAI mock
            mock_client = mock_openai.return_value
            mock_client.chat.completions.create = AsyncMock()
            mock_client.chat.completions.create.return_value.choices[0].message.content = "# React Hooks\n\nLesson content in Kazakh."
            
            # Mock DB scalar
            mock_db_lesson = MagicMock()
            mock_db.scalar.return_value = mock_db_lesson
            
            result = await lesson_service.get_lesson_detail(user, lesson_id)
            
            # Assert Tavily was called with correct query
            mock_search.assert_called_once_with("React Hooks Learn about useState and useEffect")
            
            # Check which mock was used and assert prompt content
            if mock_llama_openai.called:
                call_args = mock_llm_instance.acomplete.call_args
                prompt = call_args.args[0]
            else:
                call_args = mock_client.chat.completions.create.call_args
                prompt = call_args.kwargs["messages"][0]["content"]
                
            assert "Search result: Use hooks for state." in prompt
            assert "OUTPUT LANGUAGE: You MUST provide all content in the following language: kk." in prompt
            
            # Assert content was saved
            assert mock_db_lesson.content == "# React Hooks\n\nLesson content in Kazakh."
            mock_db.commit.assert_called()

@pytest.mark.asyncio
async def test_get_practice_test_uses_language(lesson_service, mock_plan_repo, mock_db):
    user = User(id=1, email="test@example.com", full_name="Test User")
    lesson_id = 123
    plan_id = 456
    
    # Mock lesson and plan
    mock_lesson_orm = MagicMock()
    mock_lesson_orm.id = lesson_id
    mock_lesson_orm.plan_id = plan_id
    mock_lesson_orm.title = "React Hooks"
    mock_lesson_orm.description = "Learn about useState and useEffect"
    mock_lesson_orm.content = "Existing content."
    
    mock_plan_repo.get_lesson.return_value = mock_lesson_orm
    mock_plan_repo.get_practice_test.return_value = None # No existing test
    
    mock_plan = MagicMock(spec=LearningPlan)
    mock_plan.id = plan_id
    mock_plan.language = "ru" # Russian
    mock_plan_repo.get_by_id.return_value = mock_plan
    
    # Mock LLM
    with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai, \
         patch("openai.AsyncOpenAI") as mock_openai:
        
        mock_llm_instance = MagicMock()
        mock_llama_openai.return_value = mock_llm_instance
        mock_llm_instance.acomplete = AsyncMock()
        mock_llm_instance.acomplete.return_value.text = '[{"type": "multiple_choice", "question": "Что такое хук?", "options": ["A", "B"], "correct_answer_index": 0, "explanation": "..."}]'
        
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = '[{"type": "multiple_choice", "question": "Что такое хук?", "options": ["A", "B"], "correct_answer_index": 0, "explanation": "..."}]'
        
        # Mock last score
        mock_plan_repo.get_last_test_score.return_value = None
        
        result = await lesson_service.get_practice_test(user, lesson_id)
        
        # Check which mock was used and assert prompt content
        if mock_llama_openai.called:
            call_args = mock_llm_instance.acomplete.call_args
            prompt = call_args.args[0]
        else:
            call_args = mock_client.chat.completions.create.call_args
            prompt = call_args.kwargs["messages"][0]["content"]
            
        assert "OUTPUT LANGUAGE: You MUST provide all text content (questions, options, explanations) in the following language: ru." in prompt
        
        # Assert test was created
        mock_plan_repo.create_practice_test.assert_called_once()

@pytest.mark.asyncio
async def test_generate_plan_enriches_materials(mock_plan_repo, mock_db):
    from app.services.learning_plan_service import LearningPlanService
    from app.domain.recommendation.entities import Student
    
    # Mock repos
    mock_profile_repo = MagicMock()
    mock_profile_repo.get_skills.return_value = []
    mock_profile_repo.get_transcript.return_value = []
    
    # Mock LessonService and its search_client
    mock_lesson_service = MagicMock()
    mock_search_client = AsyncMock()
    mock_lesson_service.search_client = mock_search_client
    
    service = LearningPlanService(mock_profile_repo, mock_plan_repo, mock_lesson_service)
    
    user = User(id=1, email="test@example.com", full_name="Test User")
    request = MagicMock()
    request.goal = "Learn Python"
    request.skill_level = "Beginner"
    request.learning_style = "Practical"
    request.study_time = 10
    request.interests = []
    request.language = "en"
    
    # Mock generate_global_analysis
    with patch("app.services.learning_plan_service.generate_global_analysis", new_callable=AsyncMock) as mock_gen:
        from app.infrastructure.ai.analysis_agent import GlobalAnalysis, LessonPlanStep
        from app.domain.recommendation.entities import SkillGapAnalysis
        
        mock_gen.return_value = GlobalAnalysis(
            title="Python Plan",
            skill_gap_analysis=SkillGapAnalysis(overall_gap_score=0.5, domain_breakdown=[], critical_skills=[]),
            learning_path=[
                LessonPlanStep(order=1, title="Intro", description="Basics", is_external=True)
            ]
        )
        
        # Mock search results
        mock_search_client.search_educational_materials.return_value = [
            {"title": "Real Python", "description": "Good site", "url": "https://realpython.com", "type": "article"}
        ]
        
        # Mock create_plan
        mock_plan_repo.create_plan.side_effect = lambda uid, plan: plan
        
        await service.generate_plan(user, request)
        
        # Verify enrichment was called
        mock_search_client.search_educational_materials.assert_called_once()
        
        # Verify plan was saved with enriched materials
        saved_plan = mock_plan_repo.create_plan.call_args[0][1]
        assert len(saved_plan.steps[0].materials) == 1
        assert saved_plan.steps[0].materials[0].url == "https://realpython.com"
