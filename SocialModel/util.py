import numpy as np
from np import linalg
import math

# With help from orthonormal sets pseudocode written by David Eberly
# https://www.geometrictools.com/Documentation/OrthonormalSets.pdf

# limiting to 3-D case for right now
# TODO configurable eigenvalues? (until then, we can just set eigenvalues to 0 and stack...)
def calculate_transition_matrix_3d(pi_1):
    v1 = np.array([1.,1.,1.])/ma# length N in future...
    pi_2 = np.array([-1.,1,0.])# perpendicular to 1 1 1 and also unit length
    #pi_3 = np.cross(v1,pi_2) # guarantee not linearly dependent on pi_2 to avoid weirdness
    pi_3 = np.array([-1,-1,2.])
    # somewhat arbitrary values for 2nd and 3rd eigenvalues
    # eig_1 = 1. by definition
    L = np.diag([1.,0.1,0.01])
    U_inv = np.stack((pi_1,pi_2,pi_3))
    P = np.dot(np.linalg.inv(U_inv),np.dot(L,U_inv))
    return P
