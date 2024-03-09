from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from uuid import uuid4
from typing import List
from dotenv import load_dotenv
import time
import os

load_dotenv()

app = FastAPI()

class Todo(BaseModel):
    id: str
    task: str
    is_done: bool
    created_at: int
    updated_at: int

sample_todo = Todo(
    id=str(uuid4()),
    task="Some task to be done",
    is_done=False,
    created_at=int(time.time() * 1000),
    updated_at=int(time.time() * 1000),
)

todos = [sample_todo]

def find_todo_by_id(todo_id: str):
    return next((todo for todo in todos if todo.id == todo_id), None)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}

@app.get("/todos", response_model=List[Todo])
def read_todos():
    return todos

@app.get("/todos/{id}", response_model=Todo)
def read_todo(id: str):
    todo = find_todo_by_id(id)
    if todo is None:
        raise HTTPException(status_code=404, detail="No such todo with this ID")
    return todo

@app.post("/todos", response_model=Todo)
def create_todo(task: str = Body(..., embed=True)):
    if not task:
        raise HTTPException(status_code=400, detail="No task was set")

    new_todo = Todo(
        id=str(uuid4()),
        task=task,
        is_done=False,
        created_at=int(time.time() * 1000),
        updated_at=int(time.time() * 1000),
    )

    todos.append(new_todo)
    return new_todo

@app.patch("/todos/{id}", response_model=Todo)
def update_todo(id: str, task: str = Body(...), is_done: bool = Body(...)):
    target_todo = find_todo_by_id(id)
    if target_todo is None:
        raise HTTPException(status_code=404, detail="No such todo with this ID")

    target_todo.task = task
    target_todo.is_done = is_done
    target_todo.updated_at = int(time.time() * 1000)

    return target_todo

@app.delete("/todos/{id}", response_model=Todo)
def delete_todo(id: str):
    target_todo = find_todo_by_id(id)
    if target_todo is None:
        raise HTTPException(status_code=404, detail="No such todo with this ID")

    todos.remove(target_todo)
    return target_todo

if __name__ == "__main__":
    import uvicorn

    try:
        PORT = int(os.getenv("PORT", 8000))
        HOST = os.getenv("HOST", "127.0.0.1")
    except ValueError as e:
        print(f"Error parsing PORT: {e}")
        sys.exit(1)

    uvicorn.run(app, host=HOST, port=PORT)
