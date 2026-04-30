import math

import numpy as np
from typing import List, Union
from numpy.typing import NDArray

from .standardization import standardize
from models.dtos import Constraint, LPProblem, Tableau, Operator, ObjectiveType, Optional, Snapshot, SolveStatus, SolveResponse

def lex_compare(v1: NDArray, v2: NDArray, tol: float = 1e-10) -> int:

    # Returns: -1 if v1 < v2, 0 if equal (within tolerance), 1 if v1 > v2

    for x, y in zip(v1, v2):
        diff = x - y
        if abs(diff) < tol:
            continue
        return -1 if diff < 0 else 1
    return 0


def find_leaving_var_lex(constrains: NDArray, entering: int) -> tuple:
    leaving = -1
    min_ratio_vector = None
    min_ratio = 1e18

    for i, row in enumerate(constrains):
        if row[entering] <= 0:
            continue

        # Compute ratio vector by dividing row by pivot element
        ratio_vector = row / row[entering]
        curr_ratio = ratio_vector[len(row) - 1]  # RHS ratio

        if leaving == -1:
            leaving = i
            min_ratio_vector = ratio_vector
            min_ratio = curr_ratio
        else:
            # Compare RHS first, then lexicographically if equal
            if min_ratio < curr_ratio - 1e-10:
                # Current min is strictly better
                pass
            elif abs(min_ratio - curr_ratio) < 1e-10:
                # RHS ratios are equal - compare lexicographically
                if lex_compare(ratio_vector, min_ratio_vector) < 0:
                    leaving = i
                    min_ratio_vector = ratio_vector
                    min_ratio = curr_ratio
            else:
                # This row's ratio is better
                leaving = i
                min_ratio_vector = ratio_vector
                min_ratio = curr_ratio

    return leaving, min_ratio

def maximize(  tableau: Tableau):
    print(tableau.basic_vars)
    constrains: NDArray = tableau.matrix
    z: NDArray = tableau.z
    snapshots = []
    # snapshots.append(Snapshot(matrix=constrains.tolist(), z=z.tolist(), varMap=tableau.var_names, slackStart=tableau.slack_start
    #                           , surplusStart=tableau.surplus_start, artStart=tableau.art_start, basicVars=tableau.basic_vars
    #                           ,colIdx=None, rowIdx=None, pivot=None, enteringVar=None, leavingVar=None))
    def reachedOptimal(a: NDArray):
        return a[0:len(a)-1].min() >= 0
    while not reachedOptimal(z):
        # finding the entering variable (col)
        print("still not optimal")
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
        leaving, minRatio = find_leaving_var_lex(constrains, entering)
        # leaving = -1
        # minRatio = 1e18
        # for i, row in enumerate(constrains):
        #     if row[entering] <= 0:
        #         continue
        #     rowRatio = row[len(row) - 1] / row[entering] #ratio test
        #     if rowRatio < 0:
        #         continue
        #     if rowRatio < minRatio:
        #         minRatio = rowRatio
        #         leaving = i
            # elif rowRatio == minRatio:
            #     if tableau.var_names.index(tableau.basic_vars[i]) < tableau.var_names.index(
            #             tableau.basic_vars[leaving]):
            #         leaving = i
        # no +ve ratios
        if(leaving == -1):
            print('unbounded')
            return False, snapshots
        print(f"leaving: row {leaving}, entering: col {entering}")
        leavingVarN = tableau.basic_vars[leaving]
        snapshots.append(Snapshot(matrix=constrains.tolist(), z=z.tolist()
                              ,varMap=tableau.var_names, slackStart=tableau.slack_start
                              , surplusStart=tableau.surplus_start, artStart=tableau.art_start, basicVars=tableau.basic_vars
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

        tableau.basic_vars[leaving] = tableau.var_names[entering]

    snapshots.append(Snapshot(matrix=constrains.tolist(), z=z.tolist()
                              , varMap=tableau.var_names, slackStart=tableau.slack_start
                              , surplusStart=tableau.surplus_start, artStart=tableau.art_start, basicVars=tableau.basic_vars
                              , colIdx=None, rowIdx=None, pivot=None,
                              enteringVar=None, leavingVar=None))


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
        # if(constrain[i] != 0 and constrain[i] != 1 and constrain[i] != -1):
        if (constrain[i] != 0 and constrain[i] != 1):
            return 0
        if (constrain[i] != 0):
            nonZ.append(constrain)
    if(len(nonZ) != 1):
        return 0
    constrain = nonZ[0]
    # return constrain[i] * constrain[len(constrain) - 1]
    return constrain[len(constrain) - 1]


def merge_unrestricted_vars(solution: dict, var_restrictions: list[bool]) -> dict:
    if var_restrictions is None:
        return solution
    merged = {}
    for i, is_restricted in enumerate(var_restrictions):
        var_name = f"x{i+1}"
        if is_restricted:
            if var_name in solution:
                merged[var_name] = solution[var_name]
        else:
            print("here")
            pos_name = f"x{i+1}_pos"
            neg_name = f"x{i+1}_neg"
            pos_val = solution.get(pos_name, 0)
            neg_val = solution.get(neg_name, 0)
            print(pos_val, neg_val)
            merged[var_name] = pos_val - neg_val

        print(merged)

    for var_name, val in solution.items():
        if var_name.startswith(('s', 'e', 'a')):
            merged[var_name] = val

    return merged


def solveProblem(tableau: Tableau):
    snapshots = []
    if(tableau.art_start == len(tableau.z) - 1):
        #no need for 2 phase
        print('no need for 2 phase')
        snapshots.append(Snapshot(
            matrix=tableau.matrix.tolist(),
            z=tableau.z.tolist(),
            varMap=tableau.var_names,
            slackStart=tableau.slack_start,
            surplusStart=tableau.surplus_start,
            artStart=tableau.art_start,
            basicVars=tableau.basic_vars,
            colIdx=None,
            rowIdx=None,
            pivot=None,
            enteringVar=None,
            leavingVar=None,
            phase=2
        ))
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

        snapshots.append(Snapshot(
            matrix=tableau.matrix.tolist(),
            z=w.tolist(),
            varMap=tableau.var_names,
            slackStart=tableau.slack_start,
            surplusStart=tableau.surplus_start,
            artStart=tableau.art_start,
            basicVars=tableau.basic_vars,
            colIdx=None,
            rowIdx=None,
            pivot=None,
            enteringVar=None,
            leavingVar=None,
            phase=1
        ))
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
        print("Before")
        print(tableau.z)
        var_map = {name: i for i, name in enumerate(tableau.var_names)}
        for i, name in enumerate(tableau.basic_vars):
            row = tableau.matrix[i]
            tableau.z = tableau.z - row * z[var_map[name]]
        print("After")
        print(tableau.z)
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
            z = np.delete(z, d)
            tableau.var_names.__delitem__(d)
            tableau.art_start = len(z)-1

        snapshots.append(Snapshot(
            matrix=tableau.matrix.tolist(),
            z=z.tolist(),
            varMap=tableau.var_names,
            slackStart=tableau.slack_start,
            surplusStart=tableau.surplus_start,
            artStart=tableau.art_start,
            basicVars=tableau.basic_vars,
            colIdx=None,
            rowIdx=None,
            pivot=None,
            enteringVar=None,
            leavingVar=None,
            phase=2
        ))
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
        solutions = merge_unrestricted_vars(solutions, tableau.variable_restrictions)
        print(f"solutions: {solutions}")
        print(f"optimal solution: {tableau.z[(len(z)-1)]}")
        return SolveResponse(optimalValue=optimalValue, snapshots=snapshots, solution=solutions, status=SolveStatus.OPTIMAL)
    else :
        print("UNBOUNDED")
        return SolveResponse(optimalValue=None, snapshots=snapshots, solution={}, status=SolveStatus.UNBOUNDED)




