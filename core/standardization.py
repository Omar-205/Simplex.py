import numpy as np

from models.dtos import LPProblem, Operator, Tableau


def standardize(req: LPProblem):

    # handle unrestricted in z
    final_c = []
    var_names = []

    for j, coeff in enumerate(req.objectiveCoeffs):
        if not req.variableRestrictions[j]:
            final_c.extend([coeff, -coeff])
            var_names.append(f"x{j+1}_pos")
            var_names.append(f"x{j+1}_neg")
        else:
            final_c.append(coeff)
            var_names.append(f"x{j+1}")

    # build the matrix
    rows = []
    rhs_vector = []

    # 1- handle unrestricted
    for i, constraint in enumerate(req.constraints):
        row = []
        for j, coeff in enumerate(constraint.coefficients):
            if not req.variableRestrictions[j]:
                row.extend([coeff, -coeff])
            else:
                row.append(coeff)
        rows.append(row)
        rhs_vector.append(constraint.rhs)

    # 2- add slack/ surplus/ artificial vars
    num_constraints = len(req.constraints)
    num_slack = sum(c.sign == Operator.LE for c in req.constraints)
    num_surplus = sum(c.sign == Operator.GE for c in req.constraints)
    num_art = sum(c.sign in [Operator.GE, Operator.EQ] for c in req.constraints)

    slack_matrix = np.zeros((num_constraints, num_slack))
    surplus_matrix = np.zeros((num_constraints, num_surplus))
    art_matrix = np.zeros((num_constraints, num_art))

    s = e = a = 0

    for i, constraint in enumerate(req.constraints):
        if constraint.sign == Operator.LE:
            slack_matrix[i, s] = 1
            s += 1
            var_names.append(f"s{s}")

        elif constraint.sign == Operator.GE:
            surplus_matrix[i, e] = -1
            art_matrix[i, a] = 1
            e += 1
            a += 1
            var_names.append(f"e{e}")
            var_names.append(f"a{a}")

        elif constraint.sign == Operator.EQ:
            art_matrix[i, a] = 1
            a += 1
            var_names.append(f"a{a}")

    var_names.append("b")
    # assemble everything together
    rows = np.array(rows, dtype=float)
    rhs = np.array(rhs_vector).reshape((num_constraints, 1))
    full_matrix = np.hstack([rows, slack_matrix, surplus_matrix, art_matrix, rhs])

    z = np.array(final_c, dtype=float)
    num_additional = num_slack + num_surplus + num_art
    z = np.concatenate([z, np.zeros(num_additional)])

    n = len(final_c)
    return Tableau(
        matrix=full_matrix,
        z=z,
        var_names=var_names,
        slack_start=n,
        surplus_start=n + num_slack,
        art_start=n + num_slack + num_surplus)