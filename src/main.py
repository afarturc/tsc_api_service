from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine
from models import Base
from services import create_tower_section
from schemas import TowerSectionCreate, TowerSection as TowerSectionSchema

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/tower_sections/", response_model=TowerSectionSchema)
def add_tower_section(tower_section_data: TowerSectionCreate, db: Session = Depends(get_db)):
    try:
        # Add any additional validation logic here if needed
        return create_tower_section(db, tower_section_data)
    except HTTPException as e:
        raise e  # Re-raise FastAPI's HTTPException to maintain proper status codes and details
    except Exception as e:
        # Handle specific exceptions or log the error as needed
        raise HTTPException(
            status_code=500, detail=f"Error occurred: {str(e)}")
