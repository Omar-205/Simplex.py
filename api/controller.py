from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.standardization import standardize
from models.dtos import LPProblem, SolveResponse, SolveStatus

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/solve", response_model=SolveResponse)
async def solve(req: LPProblem):
    tableau = standardize(req)

    print(req)
    print(tableau)

    # mock response for frontend testing
    return {
        "status": SolveStatus.OPTIMAL,
        "snapshots": [
            {
                "matrix": [
                    [1, 1, 1, 0, 4],
                    [1, 2, 0, 1, 6]
                ],
                "z": [-3, -2, 0, 0, 0],
                "varMap": ["x1", "x2", "s1", "s2"],
                "slackStart": 2,
                "surplusStart": 4,
                "artStart": 4,
                "rowIdx": None,
                "colIdx": None,
                "pivot": None,
                "enteringVar": None,
                "leavingVar": None,
                "basicVars": ["s1", "s2"]
            }
        ],
        "optimalValue": 12,
        "solution": {
            "x1": 4,
            "x2": 0,
            "s1": 0,
            "s2": 2
        }
    }