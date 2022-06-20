#!/usr/bin/env python
# irrcompat: voxboxor submodule translating Irrlicht from/to Minetest
# Copyright (C) 2018-2021 Jake Gustafson
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
'''
irrcompat: voxboxor submodule translating Irrlicht from/to Minetest
'''
from __future__ import print_function

import os
import sys
from datetime import datetime
import platform
import json

from voxboxor import (
    echo0,
)

UPM = 10.0  # (unused, hard-coded for speed) Engine units per game meter

# TODO: crafts (scrape list of ingredients to remove from inventory)

def irr_to_mt(irr_pos):
    '''
    Convert from engine units to Minetest meters.
    '''
    c = None
    try:
        c = len(irr_pos)
    except TypeError:
        # if isinstance(irr_pos, int):
        #     return irr_pos / 10.0
        return irr_pos / 10.0
    if c == 3:
        return (irr_pos[0] / 10.0, irr_pos[1] / 10.0, irr_pos[2] / 10.0)
    elif c == 2:
        return (irr_pos[0] / 10.0, irr_pos[1] / 10.0)
    elif c == 1:
        return (irr_pos[0] / 10.0,)
    else:
        raise ValueError("Converting Irrlicht tuples of this size is"
                         " not implemented.")
    return None


def irr_to_mt_s(irr_pos):
    '''
    Convert from engine units to Minetest meters then to a string.
    '''
    return ','.join(irr_to_mt(irr_pos))


def mt_to_irr(mt_pos):
    '''
    Convert from Minetest meters to engine units.
    '''
    c = None
    try:
        c = len(mt_pos)
    except TypeError:
        # if isinstance(mt_pos, int):
        #     return float(mt_pos) * 10.0
        return mt_pos * 10.0
    if c == 3:
        return (mt_pos[0] * 10.0, mt_pos[1] * 10.0, mt_pos[2] * 10.0)
    elif c == 2:
        return (mt_pos[0] * 10.0, mt_pos[1] * 10.0)
    elif c == 1:
        return (mt_pos[0] * 10.0,)
    else:
        raise ValueError("Converting Minetest tuples of this size is"
                         " not implemented.")
    return None


if __name__ == '__main__':
    echo0()
    echo0("This is a module not an executable script.")
