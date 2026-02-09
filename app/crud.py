# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(title=item.title, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item

def update_item(db: Session, item_id: int, item_data: schemas.ItemCreate):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item:
        item.title = item_data.title
        item.description = item_data.description
        db.commit()
        db.refresh(item)
    return item