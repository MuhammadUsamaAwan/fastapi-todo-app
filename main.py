from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, status
from models import Base, Todos
from database import engine
from database import SessionLocal

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get("/todos")
async def get_todos(db: db_dependency):
    todos = db.query(Todos).all()
    return todos


@app.get("/todos/{id}")
async def get_todo(db: db_dependency, id: Annotated[int, Path(ge=0)]):
    todo = db.query(Todos).filter(Todos.id == id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todos(db: db_dependency, todo: TodoRequest):
    todo_model = Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()
    return todo


@app.put("/todos/{id}")
async def update_todos(
    db: db_dependency, id: Annotated[int, Path(ge=0)], todo: TodoRequest
):
    db_todo = db.query(Todos).filter(Todos.id == id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.priority = todo.priority
    db_todo.complete = todo.complete
    db.commit()
    return db_todo


@app.delete("/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todos(db: db_dependency, id: Annotated[int, Path(ge=0)]):
    db_todo = db.query(Todos).filter(Todos.id == id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully."}
