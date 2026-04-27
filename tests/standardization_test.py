from core.standardization import standardize
from models.dtos import LPProblem, Constraint, Operator

print("=============Test1=================")
req = LPProblem(
    objectiveCoeffs=[3, 2],
    variableRestrictions=[True, True],
    constraints = [
        Constraint(
            coefficients=[1, 1],
            sign=Operator.LE,
            rhs=4
        ),
        Constraint(
            coefficients=[1, 0],
            sign=Operator.LE,
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