from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.simplex import solveProblem
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
    # print(tableau)
    
    # mock response for frontend testing
    return solveProblem(tableau)
    """ return{
    "status": "optimal",
    "solution": {"x1": 4, "x2": 0, "s1": 0, "s2": 2},
    "optimalValue": 12,
    "snapshots": [
        {
            "matrix": [
                [1, 1, 1, 0, 4],
                [1, 2, 0, 1, 6]
            ],
            "z": [-3, -2, 0, 0, 0],
            "varMap": ["X1", "X2", "S1", "S2"],
            "slackStart": 2,
            "surplusStart": 4,
            "artStart": 4,
            "rowIdx": None,
            "colIdx": None,
            "pivot": None,
            "enteringVar": None,
            "leavingVar": None,
            "basicVars": ["s1", "s2"]
        },
        {
            "matrix": [
                [1, 1, 1, 0, 4],
                [1, 2, 0, 1, 6]
            ],
            "z": [-3, -2, 0, 0, 0],
            "varMap": ["X1", "X2", "S1", "S2"],
            "slackStart": 2,
            "surplusStart": 4,
            "artStart": 4,
            "rowIdx": 0,
            "colIdx": 0,
            "pivot": 1,
            "enteringVar": "x1",
            "leavingVar": "s1",
            "basicVars": ["s1", "s2"]
        },
        {
            "matrix": [
                [1, 1, 1, 0, 4],
                [0, 1, -1, 1, 2]
            ],
            "z": [0, 1, 3, 0, 12],
            "varMap": ["X1", "X2", "S1", "S2"],
            "slackStart": 2,
            "surplusStart": 4,
            "artStart": 4,
            "rowIdx": None,
            "colIdx": None,
            "pivot": None,
            "enteringVar": None,
            "leavingVar": None,
            "basicVars": ["x1", "s2"]
        }
    ]
}
"""