import numpy as np

from models.dtos import LPProblem, ObjectiveType, Operator, Tableau

def flip(sign: Operator):
    if sign == Operator.LE:
        return Operator.GE
    elif sign == Operator.GE:
        return Operator.LE
    else:
        return Operator.EQ

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

    # 2- handel neg b
    for i, b in enumerate(rhs_vector):
        if b < 0:
            rows[i] = [-x for x in rows[i]]
            rhs_vector[i] *= -1
            req.constraints[i].sign = flip(req.constraints[i].sign)
    # 3- add slack/ surplus/ artificial vars
    num_constraints = len(req.constraints)
    n = len(final_c)
    num_slack = sum(c.sign == Operator.LE for c in req.constraints)
    num_surplus = sum(c.sign == Operator.GE for c in req.constraints)
    num_art = sum(c.sign in [Operator.GE, Operator.EQ] for c in req.constraints)
    num_additional = num_slack + num_surplus + num_art

    var_names.extend([""] * num_additional)

    slack_start = n
    surplus_start = n + num_slack
    art_start = n + num_slack + num_surplus

    slack_matrix = np.zeros((num_constraints, num_slack))
    surplus_matrix = np.zeros((num_constraints, num_surplus))
    art_matrix = np.zeros((num_constraints, num_art))

    s = e = a = 0

    basic_vars = [""] * num_constraints

    for i, constraint in enumerate(req.constraints):
        if constraint.sign == Operator.LE:
            slack_matrix[i, s] = 1
            var_names[slack_start + s] = f"s{s+1}"
            basic_vars[i] = f"s{s+1}"
            s += 1

        elif constraint.sign == Operator.GE:
            surplus_matrix[i, e] = -1
            art_matrix[i, a] = 1
            var_names[surplus_start + e] = f"e{e+1}"
            var_names[art_start + a] = f"a{a+1}"
            basic_vars[i] = f"a{a+1}"
            e += 1
            a += 1


        elif constraint.sign == Operator.EQ:
            art_matrix[i, a] = 1
            var_names[art_start + a] = f"a{a+1}"
            basic_vars[i] = f"a{a+1}"
            a += 1

    var_names.append("b")
    # assemble everything together
    rows = np.array(rows, dtype=float)
    rhs = np.array(rhs_vector).reshape((num_constraints, 1))
    full_matrix = np.hstack([rows, slack_matrix, surplus_matrix, art_matrix, rhs])

    z = np.array(final_c, dtype=float)
    z = np.concatenate([z, np.zeros(num_additional)])

    if(req.objective == ObjectiveType.MAX):
        z = z * -1
    z = np.append(z, 0)
    """ print(z)
    print(full_matrix[0]) """
    assert len(z) == len(full_matrix[0])
    return Tableau(
        matrix=full_matrix,
        z=z,
        var_names=var_names,
        basic_vars=basic_vars,
        slack_start=slack_start,
        surplus_start=surplus_start,
        art_start=art_start,
        objective=req.objective,
        variable_restrictions=req.variableRestrictions,
    )