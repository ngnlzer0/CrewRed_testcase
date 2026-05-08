from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, crud, external_api
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Endpoints for Projects

@app.post("/projects/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db) ):
    #Before creating, check if all places exist in the Art Institute API
    for place in project.places:
        exists = await external_api.verify_place_exists(place.external_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Place with external_id {place.external_id} not found in Art Institute API."
            )

    return crud.create_project(db=db, project=project)

@app.get("/projects/", response_model= schemas.ProjectResponse)
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projects(db,skip=skip, limit=limit)

@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.update_project(db=db, db_project=db_project, project_update=project_update)

@app.delete("/projects/{project_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    success = crud.delete_project(db=db, db_project=db_project)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The project cannot be deleted because it contains visited places."
        )
    return None


# Endpoints for Place


@app.post("/projects/{project_id}/places/", response_model=schemas.PlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place_to_project(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(db_project.places) >= 10:
        raise HTTPException(status_code=400, detail="A project cannot contain more than 10 places.")

    # Verification: uniqueness of the place within the project
    existing_ids = [p.external_id for p in db_project.places]
    if place.external_id in existing_ids:
        raise HTTPException(status_code=400, detail="This place already add for this project.")

    # Check: Does a place exist in the Art Institute API
    exists = await external_api.verify_place_exists(place.external_id)
    if not exists:
        raise HTTPException(status_code=400, detail="place not found in Art Institute API.")

    return crud.add_place_to_project(db=db, place=place, project_id=project_id)


@app.put("/places/{place_id}", response_model=schemas.PlaceResponse)
def update_place(place_id: int, place_update: schemas.PlaceUpdate, db: Session = Depends(get_db)):
    db_place = crud.get_place(db, place_id=place_id)
    if db_place is None:
        raise HTTPException(status_code=404, detail="place not found")

    return crud.update_place(db=db, db_place=db_place, place_update=place_update)


@app.get("/places/{place_id}", response_model=schemas.PlaceResponse)
def get_place(place_id: int, db: Session = Depends(get_db)):
    db_place = crud.get_place(db, place_id=place_id)
    if db_place is None:
        raise HTTPException(status_code=404, detail="place not found")
    return db_place
