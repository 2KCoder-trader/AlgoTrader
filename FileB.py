import numpy as np
from numpy.linalg import eigh, norm
import matplotlib.pyplot as plt
A = np.array([[-4,0],
              [2,1],
              [3,-2]])
# print(A.T@A)

ev, V =eigh(A.T@A)
# print(V)
print(V)
u0 = A@V[:,0]/norm(A@V[:,0])
u1 = A@V[:,1]/norm(A@V[:,1])

U = np.array([u1,u0]).T

print(np.dot(U,-1))
# print(U.T@A@V)