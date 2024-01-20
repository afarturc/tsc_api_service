from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine
from models import Base
from services import create_tower_section, modify_tower_section, delete_tower_section, get_tower_section_by_part_number, get_tower_sections_by_diameters
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
        return create_tower_section(db, tower_section_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error occurred: {str(e)}")


@app.put("/tower_sections/{section_id}", response_model=TowerSectionSchema)
def modify_tower_section_endpoint(section_id: int, tower_section_data: TowerSectionCreate, db: Session = Depends(get_db)):
    try:
        return modify_tower_section(db, section_id, tower_section_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error occurred: {str(e)}")


@app.delete("/tower_sections/{section_id}", response_model=TowerSectionSchema)
def delete_tower_section_endpoint(section_id: int, db: Session = Depends(get_db)):
    try:
        deleted_section = delete_tower_section(db, section_id)
        return deleted_section
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error occurred: {str(e)}")


@app.get("/tower_sections/{part_number}", response_model=TowerSectionSchema)
def get_tower_section_by_part_number_endpoint(part_number: str, db: Session = Depends(get_db)):
    try:
        retrieved_section = get_tower_section_by_part_number(db, part_number)
        return retrieved_section
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error occurred: {str(e)}")


@app.get("/tower_sections", response_model=List[TowerSectionSchema])
def get_tower_sections_by_diameters_endpoint(
    db: Session = Depends(get_db),
    bottom_diameter: float = Query(
        None, ge=0, description="Minimum bottom diameter"),
    top_diameter: float = Query(None, ge=0, description="Maximum top diameter")
):
    try:
        retrieved_sections = get_tower_sections_by_diameters(
            db, bottom_diameter, top_diameter)
        return retrieved_sections
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error occurred: {str(e)}")
