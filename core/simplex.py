import numpy as np
from typing import List, Union
from numpy.typing import NDArray

def maximize(constrains: NDArray, z: NDArray):
    def reachedOptimal(a: NDArray):
        return a[0:len(a)-1].min() >= 0
    while not reachedOptimal(z):
        # finding the entering variable (col)
        
        entering = 0
        for i, v in enumerate(z):
            if v < z[entering]:
                entering = i
        print(f"entering: col {entering}")
        # finding the leaving variable (row) if it exists
        leaving = -1
        minRatio = 100
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
            return False
        print(f"leaving: row {leaving}, entering: col {entering}")
        # the pivot
        pivot = constains[leaving][entering]
        constrains[leaving] = constrains[leaving] / pivot
        # updating the matix except the leaving row
        for i, row in enumerate(constains):
            if(i == leaving):
                continue
            m = row[entering] 
            constains[i] =  row - m * constains[leaving]
        # updating the z-row
        m = z[entering]
        for i in range(len(z)):
            z[i] = z[i] - m * constains[leaving][i] * pivot
        
        print("constrains: ")
        print(constains)
        print("z:")
        print(z)
        return True
        
		



# constains = np.array([
#     [1/5, 1, 2/5, 0, 1/5, 6],
#     [2, 0, -4, 1, 1, 70]
# ])
constains = np.array([
    [1, 0, 0, 1, 5],
    [0, -1, 1, -5, 5]
])
# z = np.array([5.0, 2, 3, 0, 0, 100])
# z = np.array([-5.0, -2, -3, 0, 0, 0])
z = np.array([-30, 4, -4, 0, 0])
maximize(constains,z)
  
