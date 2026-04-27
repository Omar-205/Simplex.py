from fastapi import FastAPI

from core.standardization import standardize
from models.dtos import LPProblem

app = FastAPI()

@app.post("/solve")
async def solve(req: LPProblem):
    tableau = standardize(req)