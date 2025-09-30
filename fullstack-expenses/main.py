from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Allow frontend JS to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Expense(BaseModel):
    category: str
    amount: float
    note: str = ""

expenses: List[Expense] = []

@app.post("/add")
def add_expense(expense: Expense):
    expenses.append(expense)
    return {"status": "success", "expense": expense}

@app.get("/list")
def list_expenses():
    total = sum(e.amount for e in expenses)
    return {"expenses": expenses, "total": total}

