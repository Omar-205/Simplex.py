from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from numpy.typing import NDArray
from pydantic import BaseModel

class Operator(str, Enum):
    LE = "<="
    GE = ">="
    EQ = "="

class ObjectiveType(str, Enum):
    MIN = "MINIMIZE"
    MAX = "MAXIMIZE"

class Constraint(BaseModel):
    coefficients: List[float]
    sign: Operator
    rhs: float

class LPProblem(BaseModel):
    n: int
    m: int
    objective: ObjectiveType
    objectiveCoeffs: List[float]
    constraints: List[Constraint]
    variableRestrictions: List[bool]

class Snapshot(BaseModel):
    matrix: List[List[float]]
    z: List[float]

    varMap: List[str]
    slackStart: int
    surplusStart: int
    artStart: int

    rowIdx: Optional[int] = None
    colIdx: Optional[int] = None
    pivot: Optional[float] = None

    enteringVar: Optional[str]
    leavingVar: Optional[str]

    basicVars: List[str]

class SolveStatus(str, Enum):
    OPTIMAL = "optimal"
    UNBOUNDED = "unbounded"
    INFEASIBLE = "infeasible"

class SolveResponse(BaseModel):
    status: SolveStatus
    snapshots: List[Snapshot]

    optimalValue: Optional[float] = None
    solution: Optional[dict[str, float]] = None


@dataclass
class Tableau:
    matrix: NDArray
    z: NDArray

    var_names: List[str]

    slack_start: int
    surplus_start: int
    art_start: int


