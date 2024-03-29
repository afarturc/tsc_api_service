import pytest
from sqlalchemy import create_engine
from src.database import Base, engine, SessionLocal
from src.models import TowerSection
from src.services import create_tower_section, modify_tower_section, delete_tower_section, get_tower_section_by_part_number, get_tower_sections_by_diameters
from src.schemas import TowerSectionCreate
from src.exceptions import TowerSectionValidationException, ShellValidationException

DATABASE_URL = "sqlite:///:memory:"

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def testing_engine():
    return create_engine(DATABASE_URL)


@pytest.fixture(scope="function")
def db(testing_engine):
    connection = testing_engine.connect()
    transaction = connection.begin()

    db_session = SessionLocal(bind=connection)

    Base.metadata.create_all(bind=connection)

    yield db_session

    transaction.rollback()
    connection.close()
    testing_engine.dispose()


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
    created_tower_section = create_tower_section(db, valid_tower_section)

    assert created_tower_section.part_number == "TS123"
    assert created_tower_section.bottom_diameter == 5.0
    assert created_tower_section.top_diameter == 10.0
    assert created_tower_section.length == 25.0

    assert len(created_tower_section.shells) == 2
    assert created_tower_section.shells[0].position == 1
    assert created_tower_section.shells[1].position == 2


def test_create_tower_section_duplicate_part_number(db, valid_tower_section):
    create_tower_section(db, valid_tower_section)

    with pytest.raises(TowerSectionValidationException) as e:
        create_tower_section(db, valid_tower_section)
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


def test_modify_tower_section_valid(db, valid_tower_section):
    initial_tower_section = create_tower_section(db, valid_tower_section)

    modified_tower_section_data = TowerSectionCreate(
        part_number="TS456",
        shells=[
            create_shell(1, 12.0, 6.0, 9.0, 1.2, 7.85),
            create_shell(2, 18.0, 9.0, 12.0, 1.8, 7.85),
        ],
    )
    modified_tower_section = modify_tower_section(
        db, section_id=initial_tower_section.id, tower_section_data=modified_tower_section_data)

    assert modified_tower_section.part_number == "TS456"
    assert modified_tower_section.bottom_diameter == 6.0
    assert modified_tower_section.top_diameter == 12.0
    assert modified_tower_section.length == 30.0

    assert len(modified_tower_section.shells) == 2
    assert modified_tower_section.shells[0].position == 1
    assert modified_tower_section.shells[1].position == 2


def test_modify_tower_section_not_found(db):
    with pytest.raises(Exception) as e:
        modify_tower_section(db, section_id=999, tower_section_data={})
    assert "Tower section not found" in str(e.value)


def test_delete_tower_section_valid(db, valid_tower_section):
    created_tower_section = create_tower_section(db, valid_tower_section)

    deleted_tower_section = delete_tower_section(
        db, section_id=created_tower_section.id)

    assert deleted_tower_section == created_tower_section

    assert db.query(TowerSection).get(created_tower_section.id) is None


def test_delete_tower_section_not_found(db):
    with pytest.raises(Exception) as e:
        delete_tower_section(db, section_id=999)
    assert "Tower section not found" in str(e.value)


def test_get_tower_section_by_part_number_valid(db, valid_tower_section):
    create_tower_section(db, valid_tower_section)

    result = get_tower_section_by_part_number(db, part_number="TS123")

    assert result.part_number == "TS123"
    assert result.bottom_diameter == 5.0
    assert result.top_diameter == 10.0
    assert result.length == 25.0
    assert len(result.shells) == 2


def test_get_tower_section_by_part_number_not_found(db):
    with pytest.raises(Exception) as e:
        get_tower_section_by_part_number(db, part_number="NonExistent")
    assert "Tower section not found" in str(e.value)


def test_get_tower_sections_by_diameters_with_both_diameters(db, valid_tower_section):
    create_tower_section(db, valid_tower_section)

    result = get_tower_sections_by_diameters(
        db, bottom_diameter=5.0, top_diameter=10.0)

    assert len(result) == 1
    assert result[0].part_number == "TS123"


def test_get_tower_sections_by_diameters_with_bottom_diameter(db, valid_tower_section):
    create_tower_section(db, valid_tower_section)

    result = get_tower_sections_by_diameters(db, bottom_diameter=5.0)

    assert len(result) == 1
    assert result[0].part_number == "TS123"


def test_get_tower_sections_by_diameters_with_top_diameter(db, valid_tower_section):
    create_tower_section(db, valid_tower_section)

    result = get_tower_sections_by_diameters(db, top_diameter=10.0)

    assert len(result) == 1
    assert result[0].part_number == "TS123"


def test_get_tower_sections_by_diameters_no_match(db, valid_tower_section):
    create_tower_section(db, valid_tower_section)

    with pytest.raises(Exception) as e:
        get_tower_sections_by_diameters(
            db, bottom_diameter=16.0, top_diameter=20.0)
    assert "No matching tower sections found" in str(e.value)
