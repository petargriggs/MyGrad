from .multivar_operations import MultiVarOperation
import numpy as np


class Abs(MultiVarOperation):
    def __call__(self, a):
        self.variables = (a,)
        return np.abs(a.data)
    
    def backward_var(self, grad, index, **kwargs):
        a = self.variables[index]
        a.backward(grad * np.piecewise(a.data, [a.data < 0, a.data == 0, a.data > 0], [-1, 0, 1]), **kwargs)

