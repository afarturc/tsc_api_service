from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Shell(Base):
    __tablename__ = "shells"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(Integer)
    height = Column(Float)
    bottom_diameter = Column(Float)
    top_diameter = Column(Float)
    thickness = Column(Float)
    steel_density = Column(Float)
    section_id = Column(Integer, ForeignKey("tower_sections.id"))

    section = relationship("TowerSection", back_populates="shells")


class TowerSection(Base):
    __tablename__ = "tower_sections"

    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String, unique=True, index=True)
    bottom_diameter = Column(Float)
    top_diameter = Column(Float)
    length = Column(Float)

    shells = relationship("Shell", back_populates="section")
