import math

import numpy as np
from typing import List, Union
from numpy.typing import NDArray

from .standardization import standardize
from models.dtos import Constraint, LPProblem, Tableau, Operator, ObjectiveType, Optional, Snapshot, SolveStatus, SolveResponse

def maximize(  tableau: Tableau):
    constrains: NDArray = tableau.matrix
    z: NDArray = tableau.z
    snapshots = []
    snapshots.append(Snapshot(matrix=constrains.tolist(), z=z.tolist(), varMap=tableau.var_names, slackStart=tableau.slack_start
                              , surplusStart=tableau.surplus_start, artStart=tableau.art_start, basicVars=tableau.var_names[:tableau.slack_start]
                              ,colIdx=None, rowIdx=None, pivot=None, enteringVar=None, leavingVar=None))
    def reachedOptimal(a: NDArray):
        return a[0:len(a)-1].min() >= 0
    while not reachedOptimal(z):
        # finding the entering variable (col)
        print("still not oprimal")
        print("rows:")
        for row in constrains:
            print(row)
        print('z:')
        print(z)
        entering = 0
        for i, v in enumerate(z[:len(z)-1]):
            if v < z[entering]:
                entering = i
        print(f"entering: col {entering}")
        # finding the leaving variable (row) if it exists
        leaving = -1
        minRatio = 1e18
        for i, row in enumerate(constrains):
            if row[entering] <= 0:
                continue
            rowRatio = row[len(row) - 1] / row[entering] #ratio test
            if rowRatio < minRatio:
                minRatio = rowRatio
                leaving = i
        # no +ve ratios
        if(leaving == -1):
            print('unbounded')
            return False, snapshots
        print(f"leaving: row {leaving}, entering: col {entering}")
        #getting the name of the leaving variable
        leavingVarN = ''
        for i, v in enumerate(constrains[leaving]):
            if(v == 1 and z[i] == 0):
                might = True
                for j, constr in enumerate(constrains):
                    if(j == leaving): continue
                    if(constr[i]!=0): might = False
                if(not might): continue
                leavingVarN = tableau.var_names[i] 
                print(f"leaving var is {leavingVarN}")
        # getting the names of the basic variables
        basicVars = []
    
        for i in range(len(z) - 1):
            if(isBasic(i, constrains, z)):
                basicVars.append(tableau.var_names[i])
        snapshots.append(Snapshot(matrix=constrains.tolist(), z=z.tolist()
                              ,varMap=tableau.var_names, slackStart=tableau.slack_start
                              , surplusStart=tableau.surplus_start, artStart=tableau.art_start, basicVars=basicVars
                              ,colIdx=entering, rowIdx=leaving, pivot=constrains[leaving][entering], enteringVar=tableau.var_names[entering], leavingVar=leavingVarN))
        # the pivot
        constrains[leaving] = constrains[leaving] / constrains[leaving][entering]
        # updating the matix except the leaving row
        for i, row in enumerate(constrains):
            if(i == leaving):
                continue
            m = row[entering] 
            constrains[i] =  row - m * constrains[leaving]
        # updating the z-row
        m = z[entering]
        for i in range(len(z)):
            z[i] = z[i] - m * constrains[leaving][i]
        
        
            
        
    print("optimal now")
    print("rows:")
    for row in constrains:
        print(row)
    print('z:')
    print(z)
    return True, snapshots

def isBasic(i: int, constrains, z)->bool:
    if(z[i] != 0):
        return False
    ones = 0
    zeros = 0
    for constr in constrains:
        print(constr)
        if(constr[i] != 0 and constr[i] != 1 and constr[i] != -1):
            return False
        if(constr[i] == 0):
            zeros+=1
        else:
            ones +=1
    return ones == 1

def valueOf(i: int, constrains, z)->float:
    if(z[i] != 0):
        return 0
    nonZ =[]
    for constrain in constrains:
        if(constrain[i] != 0 and constrain[i] != 1 and constrain[i] != -1):
            return 0
        if (constrain[i] != 0):
            nonZ.append(constrain)
    if(len(nonZ) != 1):
        return 0
    constrain = nonZ[0]
    return constrain[i] * constrain[len(constrain) - 1]

""" 
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

"""
def solveProblem(tableau: Tableau):
    snapshots = []
    if(tableau.art_start == len(tableau.z) - 1):
        #no need for 2 phase
        print('no need for 2 phase')
    else :
        print('need 2 phase')
        # store the original z
        art_start = tableau.art_start
        z = tableau.z
        w = np.zeros(z.__len__()) # w row to zero out the arificial variables
        for i in range(art_start, len(z) -1):
            w[i] = 1
            tableau.z = w
        # w row - rows with artificial variables
        for constr in tableau.matrix:
            for i in range(art_start, len(z) -1):
                if(constr[i] == 1):
                    tableau.z = tableau.z - constr
                    break
        # minimize the w row
        solved, snapshots2 = maximize(tableau=tableau)
        for s in snapshots2:
            snapshots.append(s)
        # if we can't get rid of the artificial variables -> INFEASIBLE
        if(abs(tableau.z[len(z)-1]) > 5e-10):
            # no feasible solution
            print("INFEASIBLE")
            return SolveResponse(optimalValue=None, snapshots=snapshots, solution={}, status=SolveStatus.INFEASIBLE)
        # return the original z row
        tableau.z = z
        # delete the artificial row
        aas = len(z) - art_start - 1
        for i in range(aas):
            d = art_start
            print(f'z now {z}')
            print(f'deleting {d}')
            """ for j in range(len(tableau.matrix)):
                print(tableau.matrix[j])
                tableau.matrix[j] = np.delete(tableau.matrix[j], i) """
            tableau.matrix = np.delete(tableau.matrix, d, axis=1)
            tableau.z = np.delete(tableau.z, d)
            tableau.var_names.__delitem__(d)
            tableau.art_start = len(z)-1
    z = tableau.z
    solved, snapshots2 = maximize(tableau=tableau)
    for s in snapshots2:
        snapshots.append(s)

    print("snapshots")
    for sn in snapshots:
        print(sn)
    if solved:
        optimalValue = tableau.z[len(z) -1] if tableau.objective == ObjectiveType.MAX else -tableau.z[len(z) -1]
        varNames = tableau.var_names
        solutions = {}
        for i in range(len(z)):
            solutions[varNames[i]] = valueOf(i, constrains=tableau.matrix, z=tableau.z)
        print(f"solutions: {solutions}")
        print(f"optimal solution: {tableau.z[(len(z)-1)]}")
        return SolveResponse(optimalValue=optimalValue, snapshots=snapshots, solution=solutions, status=SolveStatus.OPTIMAL)
    else :
        print("UNBOUNDED")
        return SolveResponse(optimalValue=None, snapshots=snapshots, solution={}, status=SolveStatus.UNBOUNDED)
""" 
Maximize Z = x₁ + 2x₂
Subject to:
    x₁ + 2x₂ ≤ 4
    x₁ ≤ 3
    x₂ ≤ 2
    x₁, x₂ ≥ 0
"""
""" req = LPProblem(n=2, m=2, objective=ObjectiveType.MAX, 
                objectiveCoeffs=[40.0, 30.0],
                constraints=[
                    Constraint(coefficients=[1, 1.0],sign=Operator.LE, rhs=12.0), 
                    Constraint(coefficients=[2, 1.0], sign=Operator.GE, rhs=16.0)
                ],
                variableRestrictions=[True, True] ) """
""" req = LPProblem(n=2, m=3, objective=ObjectiveType.MAX, 
                objectiveCoeffs=[2, 1],
                constraints=[
                Constraint(coefficients=[1, 1.0],sign=Operator.GE, rhs=3), 
                Constraint(coefficients=[1.0, 0], sign=Operator.LE, rhs=4),
                Constraint(coefficients=[1.0, -1.0], sign=Operator.EQ, rhs=1),
                # Constraint(coefficients=[1.0, 0], sign=Operator.LE, rhs=3),
                ],
                variableRestrictions=[False, True] ) """
req = LPProblem(n=3, m=3, objective=ObjectiveType.MAX,
                objectiveCoeffs=[2345678.0, 3456789.0, 1234567.0],
                constraints=[
                    Constraint(coefficients=[12345.0, 23456.0, 34567.0], sign=Operator.LE, rhs=1000000.0),
                    Constraint(coefficients=[98765.0, 87654.0, 76543.0], sign=Operator.GE, rhs=500000.0),
                    Constraint(coefficients=[11111.0, 22222.0, 33333.0], sign=Operator.LE, rhs=2000000.0)
                ],
                variableRestrictions=[True, True, True])
#print(req)
tableau = standardize(req)
print(tableau)
solveProblem(tableau)


