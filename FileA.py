import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.linalg import eigh, norm
import multiprocessing
module = getattr(__import__("SVD Trader"),'SVD')
# Create a sample matrix (you can replace this with your own data)
print('processing...')

df_1 = module('TSLA')
df_2 = module('RIVN')
print('finished')
# print(df_1.shape)
# print(df_2.shape)
# print(pd.concat([df_1,df_2],axis=1).shape)
# Perform SVD on the matrix A
A = pd.concat([df_2,df_1],axis=1).values
print(A)
ev, V = eigh(A.T@A)
print(V)
print(V.shape)
u = list()
for i in range(A.shape[0]):
    u.append(A@V[:,i]/norm(A@V[:,i]))

U = np.array(u[::-1]).T

# U is the left singular vectors
# S is the singular values (a 1-D array)
# VT is the right singular vectors (transposed)

# Print the results
# print("U (left singular vectors):\n", U)
diagonal_values = np.diagonal(U)
print("Diagonal values:", diagonal_values)
plt.plot([x for x in range(len(diagonal_values))],diagonal_values)
plt.show()
# print("S (singular values):\n", S)
# print("VT (right singular vectors transposed):\n", VT)