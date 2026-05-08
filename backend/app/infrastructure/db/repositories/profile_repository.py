from typing import List
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.infrastructure.db.models import UserSkillORM, UserTranscriptORM
from app.domain.recommendation.entities import UserSkill, TranscriptEntry


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_skills(self, user_id: int) -> List[UserSkill]:
        orms = self.db.scalars(select(UserSkillORM).where(UserSkillORM.user_id == user_id)).all()
        return [
            UserSkill(
                skill_name=o.skill_name,
                mastery_level=o.mastery_level,
                category=o.category,
            )
            for o in orms
        ]

    def set_skills(self, user_id: int, skills: List[UserSkill]):
        # Clear existing skills
        self.db.execute(delete(UserSkillORM).where(UserSkillORM.user_id == user_id))

        # Add new skills
        for s in skills:
            orm = UserSkillORM(
                user_id=user_id,
                skill_name=s.skill_name,
                mastery_level=s.mastery_level,
                category=s.category,
            )
            self.db.add(orm)

        self.db.commit()

    def get_transcript(self, user_id: int) -> List[TranscriptEntry]:
        orms = self.db.scalars(
            select(UserTranscriptORM).where(UserTranscriptORM.user_id == user_id)
        ).all()
        return [
            TranscriptEntry(subject_name=o.subject_name, credits=o.credits, mark=o.mark)
            for o in orms
        ]

    def set_transcript(self, user_id: int, entries: List[TranscriptEntry]):
        # Clear existing transcript
        self.db.execute(delete(UserTranscriptORM).where(UserTranscriptORM.user_id == user_id))

        # Add new entries
        for e in entries:
            orm = UserTranscriptORM(
                user_id=user_id,
                subject_name=e.subject_name,
                credits=e.credits,
                mark=e.mark,
            )
            self.db.add(orm)

        self.db.commit()
