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

"""Make a menu for launching other git related GUIs (if present)"""

__all__ = []
__author__ = "Peter Williams <pwil3058@gmail.com>"

import shutil

from gi.repository import Gtk

from ..bab import runext

from ..gtx import actions
from ..gtx import dialogue

def launch_friend(friend_name):
    friend_exec = shutil.which(friend_name)
    if friend_exec:
        return runext.run_cmd_in_bgnd(friend_exec)
    else:
        return dialogue.main_window.inform_user(_("\"{}\" could not be found.").format(friend_name))

def _make_friend_action(friend_name):
    name = "git_launch_{}".format(friend_name)
    label = _("Launch: {}").format(friend_name)
    ttip = _("Launch \"{}\" in the current working directory.").format(friend_name)
    # TODO: try to find the friend's icon and use it instead of stock execute
    icon = Gtk.STOCK_EXECUTE
    return (name, icon, label, "", ttip, lambda _action: launch_friend(friend_name))

actions.CLASS_INDEP_AGS[actions.AC_DONT_CARE].add_actions(
    [("git_friends_menu", None, _("Friends")),] + \
    [_make_friend_action(fnm) for fnm in ["gitg", "gitk", "git-dag", "git-cola"]]
)
