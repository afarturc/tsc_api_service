from typing import List
from pydantic import BaseModel


class ShellBase(BaseModel):
    position: int
    height: float
    bottom_diameter: float
    top_diameter: float
    thickness: float
    steel_density: float


class ShellCreate(ShellBase):
    pass


class Shell(ShellBase):
    id: int

    class Config:
        orm_mode = True


class TowerSectionBase(BaseModel):
    part_number: str


class TowerSectionCreate(TowerSectionBase):
    shells: List[ShellCreate]


class TowerSection(TowerSectionBase):
    id: int
    bottom_diameter: float
    top_diameter: float
    length: float
    shells: List[Shell] = []

    class Config:
        orm_mode = True
