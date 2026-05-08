from sqlalchemy.orm import Session
from app import models, schemas
from app.models import Place


# operation for Profects

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db : Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    #create place
    db_project = models.Project(
        name=project.name,
        description=project.description,
        start_date=project.start_date
    )
    #add place in DB
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # create and add place if their exist
    for place in project.places:
        db_place = models.Place(
            external_id = place.external.id,
            notes = place.notes,
            project_id = db_project.id
        )
        db.add(db_place)

    if project.places:
        db.commit()
        db.refresh(db_project)

    return db_project

def update_project(db: Session, db_project: models.Project, project_update: schemas.ProjectUpdate):
    #Update only those fields that were passed (not None)

    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, db_project: models.Project) -> bool:
    """
    project cannot be deleted if any of its places are already marked as visited.
    Returns False if deletion is prohibited.
    """
    for place in db_project.palces:
        if place.is_visited:
            return False

    db.delete(db_project)
    db.commit()
    return True


# Operation for Place

