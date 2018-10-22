from mygrad.operation_base import Operation
from mygrad import Tensor
import numpy as np

__all__ = ["batchnorm"]


# TODO: Remove affine parameters from Operation
class BatchNorm(Operation):
    """
    Attributes
    ----------
    mean : numpy.ndarray
    var : numpy.ndarray

    Notes
    -----
    `mean` and `var` are bound as instance-attributes upon
    calling the batch-norm instance.
    """
    scalar_only = True

    def __call__(self, x, gamma, beta, *, eps):
        """
        y(x) = (x - E[x]) / sqrt(Var[x} + eps)
        batchnorm(x) = gamma * y(x) + beta

        Parameters
        ----------
        x : mygrad.Tensor
        gamma : Optional[mygrad.Tensor]
        beta : Optional[mygrad.Tensor]
        eps : Real
           A small non-negative number.

        Returns
        -------
        numpy.ndarray
        """
        normed_dims = tuple(i for i in range(x.ndim) if i != 1)
        keepdims_shape = tuple(1 if n != 1 else d for n, d in enumerate(x.shape))

        if gamma.size == 0:
            gamma = None
        if beta.size == 0:
            beta = None

        self.variables = tuple(i for i in (x, gamma, beta) if i is not None)
        self.gamma = gamma
        self.beta = beta

        x = x.data
        self.mean = x.mean(axis=normed_dims)
        self.var = np.einsum(x, range(x.ndim), x, range(x.ndim), [1])
        self.var /= (x.size / x.shape[1])
        self.var -= self.mean ** 2
        if eps:
            self.var += eps

        y = x - self.mean.reshape(keepdims_shape)
        y /= np.sqrt(self.var).reshape(keepdims_shape)
        self.x_norm = y

        # optional affine transformation
        if gamma is not None:
            gamma = gamma.data
            y = y * gamma.reshape(keepdims_shape)
        if beta is not None:
            beta = beta.data
            y += beta.reshape(keepdims_shape)
        return y

    def backward_var(self, grad, index, **kwargs):
        x = self.variables[0].data
        if index == 0:  # backprop through x
            normed_dims = tuple(i for i in range(x.ndim) if i != 1)
            keepdims_shape = tuple(1 if n != 1 else d for n, d in enumerate(x.shape))
            mean = self.mean.reshape(keepdims_shape)
            var = self.var.reshape(keepdims_shape)

            grad = grad - np.mean(grad, axis=normed_dims, keepdims=True)
            x_sub_Ex = x - mean
            rterm = x_sub_Ex / var
            rterm /= (x.size / x.shape[1])
            rterm *= np.reshape(np.einsum(grad, range(x.ndim),
                                          x_sub_Ex, range(x.ndim),
                                          [1]),
                                keepdims_shape)
            grad -= rterm
            grad /= np.sqrt(var)
            if self.gamma is not None:  # backprop through optional affine transformation
                gamma = self.gamma.data
                grad *= gamma.reshape(keepdims_shape)
            return grad

        elif index == 1 and self.gamma is not None:  # backprop through gamma
            return np.einsum(grad, range(x.ndim), self.x_norm, range(x.ndim), [1])

        elif (index == 1 and self.gamma is None) or index == 2:
            normed_dims = tuple(i for i in range(x.ndim) if i != 1)
            return grad.sum(axis=normed_dims)
        else:
            raise IndexError


def batchnorm(x, *, gamma=None, beta=None, eps, constant=False):
    """
    Performs batch normalization on ``x``

                 y(x) = (x - E[x]) / sqrt(Var[x] + eps)
                 batchnorm(x) = gamma * y(x) + beta

    Where E[x] and Var[x] represent the mean and variance, respectively,
    over axis-1 of ``x``. The subsequent affine transformation on ``y``
    is optional.

    Parameters
    ----------
    x : array_like, shape=(N, C, ...)
        The batch to be normalized within each entry of C

    gamma : Optional[array_like], shape=(C,)

    beta  : Optional[array_like], shape=(C,)

    eps : Real
       A small non-negative number.

    constant    constant : bool, optional (default=False)
        If True, the resulting Tensor is a constant.

    Returns
    -------
    mygrad.Tensor
        The batch-normalized data.
    """
    # pass gamma and beta as empty arrays if they are not supplied
    if gamma is None:
        gamma = np.array([])
    if beta is None:
        beta = np.array([])
    return Tensor._op(BatchNorm, x, gamma, beta, op_kwargs=dict(eps=eps), constant=constant)

