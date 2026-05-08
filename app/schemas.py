from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import date

from pydantic_core.core_schema import none_schema

from app.models import Place


#SCHEMA FOR PLACES

class PlaceBase(BaseModel):
    notes: Optional[str] = None

class PlaceCreate(BaseModel):
    external_id: int = Field(... , discription="ID place from Art Institute API")

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None

class PlaceResponse(BaseModel):
    id: int
    external_id: int
    project_id: int
    is_visited: bool

    model_config = ConfigDict(from_attributes=True) # allow Pydantic read date from models SQLAlchemy

# SCHEMA FOR PROJECTS

class ProjectBase(BaseModel):
    name: str = Field(... , min_length=1, max_length=150)
    description: Optional[str]= None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    places: List[PlaceCreate] = Field(default=[],max_length=10)

    @field_validator('places')
    @classmethod
    def check_unique_places(cls, places_list):
        """Prevent adding the same external_id to the same project"""
        external_ids = [place.external_id for place in places_list]
        if len(external_ids) != len(set(external_ids)):
            raise ValueError("the same external id")
        return places_list

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    descrition: Optional[str] = None
    start_date: Optional[date] = None

class ProjectResponse(ProjectBase):
    id: int
    is_completed: bool
    places: List[PlaceResponse] = []

    model_config = ConfigDict(from_attributes=True)

