import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(
    prefix="/api/questions",
    tags=["Questions CRUD"]
)

@router.post("", response_model=schemas.QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    """
    Create a new question. Stores choice options as a serialized JSON string.
    """
    # Check if a question with this title already exists to prevent duplicates
    existing_question = db.query(models.Question).filter(models.Question.title == question.title).first()
    if existing_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A question with this title already exists."
        )

    db_question = models.Question(
        category=question.category,
        title=question.title,
        content=question.content,
        options=json.dumps(question.options) if question.options is not None else None,
        correct_answer=question.correct_answer,
        is_active=False
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.get("", response_model=List[schemas.QuestionResponse])
def read_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of questions.
    """
    questions = db.query(models.Question).offset(skip).limit(limit).all()
    return questions


@router.get("/{question_id}", response_model=schemas.QuestionResponse)
def read_question(question_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single question by ID.
    """
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    return db_question


@router.put("/{question_id}", response_model=schemas.QuestionResponse)
def update_question(question_id: int, question_update: schemas.QuestionUpdate, db: Session = Depends(get_db)):
    """
    Update a question. Serializes options list to JSON string if provided.
    """
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )

    # Apply updates
    update_data = question_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "options":
            setattr(db_question, key, json.dumps(value) if value is not None else None)
        else:
            setattr(db_question, key, value)

    db.commit()
    db.refresh(db_question)
    return db_question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """
    Delete a question.
    """
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    db.delete(db_question)
    db.commit()
    return None
