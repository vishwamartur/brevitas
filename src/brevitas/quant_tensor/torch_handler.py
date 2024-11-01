# Copyright (C) 2023, Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause

import functools
import math
from typing import Callable
import warnings

import torch
from torch import Tensor
import torch.nn.functional as F

from brevitas.function.ops import max_int
from brevitas.function.ops_ste import ceil_ste
from brevitas.utils.torch_utils import compute_channel_view_shape

INT_QUANT_TENSOR_FN_HANDLER = {}
FLOAT_QUANT_TENSOR_FN_HANDLER = {}
QUANT_TENSOR_FN_HANDLER = {}


def implements(torch_function):

    @functools.wraps(torch_function)
    def decorator(func):
        QUANT_TENSOR_FN_HANDLER[torch_function] = func
        return func

    return decorator


def quant_invariant_handler(fn, inp, *args, **kwargs):
    out_value = fn(inp.value, *args, **kwargs)
    return inp.set(value=out_value)


@implements(torch.flatten)
def flatten_handler(inp, *args, **kwargs):
    return inp.flatten(*args, **kwargs)


@implements(torch.reshape)
def reshape_handler(inp, *args, **kwargs):
    return inp.reshape(*args, **kwargs)


@implements(torch.transpose)
def transpose_handler(inp, *args, **kwargs):
    return inp.transpose(*args, **kwargs)


@implements(F.pad)
def pad_handler(*args, **kwargs):
    # TODO check padding value is legal
    return quant_invariant_handler(F.pad, *args, **kwargs)


@implements(F.relu)
def relu_qt_handler(*args, **kwargs):
    return quant_invariant_handler(F.relu, *args, **kwargs)


@implements(F.relu6)
def relu6_qt_handler(*args, **kwargs):
    return quant_invariant_handler(F.relu6, *args, **kwargs)


@implements(F.hardtanh)
def hardtanh_qt_handler(*args, **kwargs):
    return quant_invariant_handler(F.hardtanh, *args, **kwargs)


@implements(F.alpha_dropout)
def alpha_dropout_handler(*args, **kwargs):
    return quant_invariant_handler(F.alpha_dropout, *args, **kwargs)


@implements(F.dropout)
def dropout_handler(*args, **kwargs):
    return quant_invariant_handler(F.dropout, *args, **kwargs)


@implements(F.dropout2d)
def dropout2d_handler(*args, **kwargs):
    return quant_invariant_handler(F.dropout2d, *args, **kwargs)


@implements(F.dropout3d)
def dropout3d_handler(*args, **kwargs):
    return quant_invariant_handler(F.dropout3d, *args, **kwargs)


@implements(F.max_pool1d)
def max_pool1d(*args, **kwargs):
    return quant_invariant_handler(F.max_pool1d, *args, **kwargs)


@implements(F.max_pool2d)
def max_pool2d_handler(*args, **kwargs):
    return quant_invariant_handler(F.max_pool2d, *args, **kwargs)


@implements(F.max_pool3d)
def max_pool3d_handler(*args, **kwargs):
    return quant_invariant_handler(F.max_pool3d, *args, **kwargs)


@implements(F.adaptive_max_pool1d)
def adaptive_max_pool1d_handler(*args, **kwargs):
    return quant_invariant_handler(F.adaptive_max_pool1d, *args, **kwargs)


@implements(F.adaptive_max_pool2d)
def adaptive_max_pool2d_handler(*args, **kwargs):
    return quant_invariant_handler(F.adaptive_max_pool2d, *args, **kwargs)


@implements(F.adaptive_max_pool3d)
def adaptive_max_pool3d_handler(*args, **kwargs):
    return quant_invariant_handler(F.adaptive_max_pool3d, *args, **kwargs)


@implements(F.interpolate)
def interpolate_handler(
        inp,
        size=None,
        scale_factor=None,
        mode='nearest',
        align_corners=None,
        recompute_scale_factor=None,
        **kwargs):  # support newer kwargs added in recent pytorch versions
    if mode == 'nearest' or mode == 'nearest_exact':
        return quant_invariant_handler(
            F.interpolate,
            inp,
            size=size,
            scale_factor=scale_factor,
            mode=mode,
            align_corners=align_corners,
            recompute_scale_factor=recompute_scale_factor,
            **kwargs)
    else:
        return F.interpolate(
            inp.value,
            size=size,
            scale_factor=scale_factor,
            mode=mode,
            align_corners=align_corners,
            recompute_scale_factor=recompute_scale_factor,
            **kwargs)


@implements(F.pixel_shuffle)
def pixel_shuffle_handler(*args, **kwargs):
    return quant_invariant_handler(F.pixel_shuffle, *args, **kwargs)


@implements(F.pixel_unshuffle)
def pixel_unshuffle_handler(*args, **kwargs):
    return quant_invariant_handler(F.pixel_unshuffle, *args, **kwargs)
