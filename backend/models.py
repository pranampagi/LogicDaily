import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    User model representing individuals competing in LogicDaily.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")


class Question(Base):
    """
    Question model representing logic challenges.
    The category can be 'mathematics', 'logical', or 'verbal'.
    The 'options' field stores a JSON-serialized list of strings for multiple-choice questions.
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)  # 'mathematics', 'logical', 'verbal'
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # Store JSON-serialized array of choices
    correct_answer = Column(String, nullable=False)  # The raw string of the correct choice
    is_active = Column(Boolean, default=False, nullable=False, index=True)  # If it is the daily active challenge
    activated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    submissions = relationship("Submission", back_populates="question", cascade="all, delete-orphan")


class Submission(Base):
    """
    Submission model tracking user answers and performance.
    """
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False, index=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="submissions")
    question = relationship("Question", back_populates="submissions")
