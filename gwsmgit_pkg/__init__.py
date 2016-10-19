#  Copyright 2016 Peter Williams <pwil3058@gmail.com>
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License only.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; if not, write to:
#  The Free Software Foundation, Inc., 51 Franklin Street,
#  Fifth Floor, Boston, MA 02110-1301 USA

"""Python package providing support for gwsm_git program"""

__all__ = []
__author__ = "Peter Williams <pwil3058@gmail.com>"
__version__ = "0.0"

import os

HOME = os.path.expanduser("~")
APP_NAME = "gwsm_git"
CONFIG_DIR_PATH = os.path.join(HOME, ".config", APP_NAME + os.extsep + "d")
LOCAl_CONFIG_DIR_NAME = "." + APP_NAME + ".d"

if not os.path.exists(CONFIG_DIR_PATH):
    os.makedirs(CONFIG_DIR_PATH, 0o775)

ISSUES_URL = "<https://github.com/pwil3058/gwsmgit/issues>"
