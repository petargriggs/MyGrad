import hypothesis.extra.numpy as hnp
import hypothesis.strategies as st
import numpy as np
from hypothesis import given, settings
from mygrad.tensor_base import Tensor
from numpy.testing import assert_allclose

from ..custom_strategies import adv_integer_index, basic_indices, arbitrary_indices
from ..wrappers.uber import backprop_test_factory, fwdprop_test_factory


@settings(deadline=None)
@given(
    a=hnp.arrays(
        shape=hnp.array_shapes(max_side=4, max_dims=10),
        dtype=float,
    ),
    data=st.data(),
)
def test_arbitrary_indices_strategy(a, data):
    shape = a.shape
    index = data.draw(arbitrary_indices(shape))

    # if index does not comply with numpy indexing
    # rules, numpy will raise an error
    a[index]


def test_getitem():
    x = Tensor([1, 2, 3])
    a, b, c = x
    f = 2 * a + 3 * b + 4 * c
    f.backward()

    assert a.data == 1
    assert b.data == 2
    assert c.data == 3
    assert f.data == 20

    assert_allclose(a.grad, np.array(2))
    assert_allclose(b.grad, np.array(3))
    assert_allclose(c.grad, np.array(4))
    assert_allclose(x.grad, np.array([2, 3, 4]))


def get_item(*arrs, index, constant=False):
    o = arrs[0][index]
    if isinstance(o, Tensor):
        o._constant = constant
    return o


def basic_index_wrap(*arrs):
    return basic_indices(arrs[0].shape)


def adv_index_int_wrap(*arrs):
    return adv_integer_index(arrs[0].shape)


def adv_index_bool_wrap(*arrs):
    return hnp.arrays(shape=arrs[0].shape, dtype=bool)


def arb_index_wrap(*arrs):
    return arbitrary_indices(arrs[0].shape)


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=6, max_dims=4)},
    kwargs=dict(index=basic_index_wrap),
)
def test_getitem_basicindex_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=6, max_dims=4)},
    kwargs=dict(index=basic_index_wrap),
    vary_each_element=True,
)
def test_getitem_basicindex_bkwdprop():
    pass


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=6, max_dims=4)},
    kwargs=dict(index=adv_index_int_wrap),
)
def test_getitem_advindex_int_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=6, max_dims=4)},
    kwargs=dict(index=adv_index_int_wrap),
    vary_each_element=True,
)
def test_getitem_advindex_int_bkwdprop():
    pass


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=6, max_dims=4)},
    kwargs=dict(index=adv_index_bool_wrap),
)
def test_getitem_advindex_bool_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=6, max_dims=4)},
    kwargs=dict(index=adv_index_bool_wrap),
    vary_each_element=True,
)
def test_getitem_advindex_bool_bkwdprop():
    pass


# test broadcast-compatible int-arrays
rows = np.array([0, 3], dtype=np.intp)
columns = np.array([0, 2], dtype=np.intp)


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (4, 3)},
    kwargs=dict(index=np.ix_(rows, columns)),
)
def test_getitem_broadcast_index_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (4, 3)},
    kwargs=dict(index=np.ix_(rows, columns)),
    vary_each_element=True,
)
def test_getitem_broadcast_index_bkprop():
    pass


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (3, 2, 4, 3)},
    kwargs=dict(index=(Ellipsis, 2, 0)),
)
def test_getitem_ellipsis_index_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (3, 2, 4, 3)},
    kwargs=dict(index=(Ellipsis, 2, 0)),
    vary_each_element=True,
)
def test_getitem_ellipsis_index_bkprop():
    pass


rows1 = np.array([False, True, False, True])
columns1 = [0, 2]


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (4, 3)},
    kwargs=dict(index=np.ix_(rows1, columns1)),
)
def test_getitem_bool_int_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (4, 3)},
    kwargs=dict(index=np.ix_(rows1, columns1)),
    vary_each_element=True,
)
def test_getitem_bool_int_bkprop():
    pass


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (4, 3)},
    kwargs=dict(index=(slice(1, 2), [1, 2])),
)
def test_getitem_basic_w_adv_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: (4, 3)},
    kwargs=dict(index=(slice(1, 2), [1, 2])),
    vary_each_element=True,
)
def test_getitem_basic_w_adv_bkprop():
    pass


@fwdprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=4, max_dims=8)},
    kwargs=dict(index=arb_index_wrap),
)
def test_getitem_arbitraryindex_fwdprop():
    pass


@settings(deadline=None)
@backprop_test_factory(
    mygrad_func=get_item,
    true_func=get_item,
    num_arrays=1,
    index_to_arr_shapes={0: hnp.array_shapes(max_side=4, max_dims=8)},
    kwargs=dict(index=arb_index_wrap),
    vary_each_element=True,
)
def test_getitem_arbitraryindex_bkwdprop():
    pass
