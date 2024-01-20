from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import TowerSection, Shell
from schemas import TowerSectionCreate
from exceptions import ShellValidationException, TowerSectionValidationException


def validate_shell_constraints(sorted_shells):
    expected_positions = set(range(1, len(sorted_shells) + 1))
    actual_positions = {shell.position for shell in sorted_shells}

    if expected_positions != actual_positions:
        raise ShellValidationException(
            "Shell positions must be sequential, unique, and start with number 1")

    for i in range(1, len(sorted_shells)):
        if sorted_shells[i - 1].top_diameter != sorted_shells[i].bottom_diameter:
            raise ShellValidationException(
                "Shell diameters must be contiguous between adjacent shells")

    for shell in sorted_shells:
        if not all(isinstance(dim, (int, float)) and dim > 0 for dim in [
            shell.height, shell.bottom_diameter, shell.top_diameter, shell.thickness, shell.steel_density
        ]):
            raise ShellValidationException(
                "Shell dimensions must be numeric positive numbers")


def create_tower_section(db: Session, tower_section_data: TowerSectionCreate):
    if not tower_section_data.shells:
        raise TowerSectionValidationException(
            "Tower section must have at least one shell")

    existing_tower_section = db.query(TowerSection).filter(
        TowerSection.part_number == tower_section_data.part_number).first()
    if existing_tower_section:
        raise TowerSectionValidationException(
            "Tower section with the same part_number already exists")

    sorted_shells = sorted(tower_section_data.shells, key=lambda x: x.position)

    validate_shell_constraints(sorted_shells)

    bottom_diameter = sorted_shells[0].bottom_diameter
    top_diameter = sorted_shells[-1].top_diameter
    length = sum(shell.height for shell in sorted_shells)

    tower_section_model = TowerSection(
        part_number=tower_section_data.part_number,
        bottom_diameter=bottom_diameter,
        top_diameter=top_diameter,
        length=length
    )

    shell_models = [Shell(**shell_data.model_dump(), section=tower_section_model)
                    for shell_data in sorted_shells]

    db.add(tower_section_model)
    db.add_all(shell_models)

    db.commit()
    db.refresh(tower_section_model)

    return tower_section_model


def modify_tower_section(db: Session, section_id: int, tower_section_data: TowerSectionCreate):
    existing_tower_section = db.query(TowerSection).filter(
        TowerSection.id == section_id).first()

    if not existing_tower_section:
        raise HTTPException(status_code=404, detail="Tower section not found")

    sorted_shells = sorted(tower_section_data.shells, key=lambda x: x.position)
    validate_shell_constraints(sorted_shells)

    existing_tower_section.part_number = tower_section_data.part_number
    existing_tower_section.bottom_diameter = sorted_shells[0].bottom_diameter
    existing_tower_section.top_diameter = sorted_shells[-1].top_diameter
    existing_tower_section.length = sum(
        shell.height for shell in sorted_shells)

    db.query(Shell).filter(Shell.section_id == section_id).delete()
    for shell_data in sorted_shells:
        shell_model = Shell(**shell_data.dict(), section_id=section_id)
        db.add(shell_model)

    db.commit()
    db.refresh(existing_tower_section)

    return existing_tower_section


def delete_tower_section(db: Session, section_id: int):
    existing_tower_section = db.query(TowerSection).filter(
        TowerSection.id == section_id).first()

    if not existing_tower_section:
        raise HTTPException(status_code=404, detail="Tower section not found")

    db.delete(existing_tower_section)
    db.commit()

    return existing_tower_section
