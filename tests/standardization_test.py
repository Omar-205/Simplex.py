from core.standardization import standardize
from models.dtos import LPProblem, Constraint, Operator, ObjectiveType

print("=============Test1=================")
req = LPProblem(
    n=2,
    m=2,
    objective="MAXIMIZE",
    objectiveCoeffs=[3, 2],
    variableRestrictions=[True, True],
    constraints = [
        Constraint(
            coefficients=[1, 1],
            sign="=",
            rhs=4
        ),
        Constraint(
            coefficients=[1, 0],
            sign="<=",
            rhs=2
        )
    ],
)

t = standardize(req)
print("Var names:")
print(t.var_names)
print("Matrix:")
print(t.matrix)

print("Z:")
print(t.z)

print("Slack start:", t.slack_start)
print("Surplus start:", t.surplus_start)
print("Art start:", t.art_start)

print("========================")

print("=============Test2=================")
req = LPProblem(
    n=4,
    m=3,
    objective=ObjectiveType.MAX,
    objectiveCoeffs=[-3, 1, 3, -1],
    variableRestrictions=[True, True, True, True],
    constraints = [
        Constraint(
            coefficients=[1, 2, -1, 1],
            sign=Operator.EQ,
            rhs=0
        ),
        Constraint(
            coefficients=[2, -2, 3, 3],
            sign=Operator.EQ,
            rhs=9
        ),
        Constraint(
            coefficients=[1, -1, 2, -1],
            sign=Operator.EQ,
            rhs=6
        )
    ],
)

t = standardize(req)
print("Var names:")
print(t.var_names)
print("Matrix:")
print(t.matrix)

print("Z:")
print(t.z)

print("Slack start:", t.slack_start)
print("Surplus start:", t.surplus_start)
print("Art start:", t.art_start)

print("========================")


print("=============Test3=================")
req = LPProblem(
    n=2,
    m=2,
    objective=ObjectiveType.MAX,
    objectiveCoeffs=[30, -4],
    variableRestrictions=[True, False],
    constraints = [
        Constraint(
            coefficients=[5, -1],
            sign=Operator.LE,
            rhs=30
        ),
        Constraint(
            coefficients=[1, 0],
            sign=Operator.LE,
            rhs=5
        )
    ],
)

t = standardize(req)
print("Var names:")
print(t.var_names)
print("Matrix:")
print(t.matrix)

print("Z:")
print(t.z)

print("Slack start:", t.slack_start)
print("Surplus start:", t.surplus_start)
print("Art start:", t.art_start)

print("========================")