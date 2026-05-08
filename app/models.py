from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)

    places = relationship("Place", back_populates="project", cascade="all, delete-orphan")

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, nullable=False) # ID from Art Institute API
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    notes = Column(String, nullable=True)
    is_visited = Column(Boolean, default=False)

    project = relationship("Project", back_populates="places")

