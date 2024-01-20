import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.services import create_tower_section
from src.schemas import TowerSectionCreate
from src.exceptions import TowerSectionValidationException, ShellValidationException

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def valid_tower_section():
    tower_section_data = TowerSectionCreate(
        part_number="TS123",
        shells=[
            create_shell(1, 10.0, 5.0, 8.0, 1.0, 7.85),
            create_shell(2, 15.0, 8.0, 10.0, 1.5, 7.85),
        ],
    )

    return tower_section_data


def create_shell(position, height, bottom_diameter, top_diameter, thickness, steel_density):
    return {
        "position": position,
        "height": height,
        "bottom_diameter": bottom_diameter,
        "top_diameter": top_diameter,
        "thickness": thickness,
        "steel_density": steel_density,
    }


def test_create_tower_section_valid(db, valid_tower_section):
    tower_section_data = valid_tower_section
    created_tower_section = create_tower_section(db, tower_section_data)

    assert created_tower_section.part_number == "TS123"
    assert created_tower_section.bottom_diameter == 5.0
    assert created_tower_section.top_diameter == 10.0
    assert created_tower_section.length == 25.0

    assert len(created_tower_section.shells) == 2
    assert created_tower_section.shells[0].position == 1
    assert created_tower_section.shells[1].position == 2


def test_create_tower_section_duplicate_part_number(db, valid_tower_section):
    tower_section_data = valid_tower_section

    with pytest.raises(TowerSectionValidationException) as e:
        create_tower_section(db, tower_section_data)
    assert "Tower section with the same part_number already exists" in str(
        e.value)


def test_create_tower_section_invalid_shell_positions(db):
    invalid_tower_section_data = TowerSectionCreate(
        part_number="TS456",
        shells=[
            create_shell(1, 10.0, 5.0, 8.0, 1.0, 7.85),
            create_shell(3, 15.0, 8.0, 10.0, 1.5, 7.85),
        ],
    )

    with pytest.raises(ShellValidationException) as e:
        create_tower_section(db, invalid_tower_section_data)
    assert "Shell positions must be sequential" in str(e.value)


def test_create_tower_section_invalid_shell_diameters(db):
    invalid_tower_section_data = TowerSectionCreate(
        part_number="TS456",
        shells=[
            create_shell(1, 10.0, 5.0, 8.0, 1.0, 7.85),
            create_shell(2, 15.0, 11.0, 10.0, 1.5, 7.85),
        ],
    )

    with pytest.raises(ShellValidationException) as e:
        create_tower_section(db, invalid_tower_section_data)
    assert "Shell diameters must be contiguous between adjacent shells" in str(
        e.value)


def test_create_tower_section_invalid_shell_dimensions(db):
    invalid_tower_section_data = TowerSectionCreate(
        part_number="TS456",
        shells=[
            create_shell(1, 10.0, 5.0, 8.0, -1.0, 7.85),
            create_shell(2, 8.0, 8.0, 10.0, 1.5, 7.85),
        ],
    )

    with pytest.raises(ShellValidationException) as e:
        create_tower_section(db, invalid_tower_section_data)
    assert "Shell dimensions must be numeric positive numbers" in str(
        e.value)


def test_create_tower_section_without_shells(db):
    invalid_tower_section_data = TowerSectionCreate(
        part_number="TS456",
        shells=[],
    )

    with pytest.raises(TowerSectionValidationException) as e:
        create_tower_section(db, invalid_tower_section_data)
    assert "Tower section must have at least one shell" in str(e.value)
