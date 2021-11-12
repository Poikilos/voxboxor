#!/usr/bin/env python
# voxboxor: module for using Minetest data and protocols
# Copyright (C) 2021 Jake Gustafson
# (except for other files where specified)

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
'''
voxboxor: module for using Minetest data and protocols
'''
from __future__ import print_function
import sys

def error(*args):
    if len(args) > 1:
        raise NotImplementedError("multiple args in error function")
    elif len(args) > 0:
        sys.stderr.write("{}\n".format(args[0]))
    else:
        sys.stderr.write("\n")
    sys.stderr.flush()

import from voxboxor.settings import Settings


myPath = os.path.realpath(__file__)
myPackage = os.path.split(myPath)[0]
myRepo = os.path.split(myPackage)[0]
repos = os.path.split(myRepo)[0]
me = '__init__.py'

if not os.path.isfile(os.path.join(myPackage, me)):
    raise RuntimeError('{} is not in package {}.'.format(me, myPackage))


loaded_mod_list = []

prepackaged_game_mod_list = []
prepackaged_gameid = None
new_mod_list = []

user_excluded_mod_count = 0

profile_path = None
appdata_path = None
if "windows" in platform.system().lower():
    if 'USERPROFILE' in os.environ:
        profile_path = os.environ['USERPROFILE']
        appdatas_path = os.path.join(profile_path, "AppData")
        appdata_path = os.path.join(appdatas_path, "Local")
    else:
        raise ValueError("ERROR: The USERPROFILE variable is missing"
                         " though platform.system() is {}."
                         "".format(platform.system()))
else:
    if 'HOME' in os.environ:
        profile_path = os.environ['HOME']
        appdata_path = os.path.join(profile_path, ".config")
    else:
        raise ValueError("ERROR: The HOME variable is missing"
                         " though the platform {} is not Windows."
                         "".format(platform.system()))



# settings = Settings()



if __name__ == '__main__':
    error()
    error("This is a module not an executable script.")
