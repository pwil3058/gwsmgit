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

"""GUI bits and pieces for dealing with git submodules"""

__all__ = []
__author__ = "Peter Williams <pwil3058@gmail.com>"

import os
import re

from gi.repository import Gtk

from ..bab import scm

from ..bab.git_gui import ifce as git_ifce

from ..bab.gui import actions
from ..bab.gui import dialogue

from ..bab.lib import enotify
from ..bab.lib import runext

from ..bab.scm_gui import wspce

AC_NOT_IN_SUBMODULE, AC_IN_SUBMODULE, _AC_MASK = actions.ActionCondns.new_flags_and_mask(2)

def get_in_submodule_condns():
    if os.path.isfile(".git"):
        return actions.MaskedCondns(AC_IN_SUBMODULE, _AC_MASK)
    else:
        return actions.MaskedCondns(AC_NOT_IN_SUBMODULE, _AC_MASK)

def _update_in_submodule_condns(*args, **kwargs):
    condns = get_in_submodule_condns()
    actions.CLASS_INDEP_AGS.update_condns(condns)
    actions.CLASS_INDEP_BGS.update_condns(condns)

enotify.add_notification_cb(enotify.E_CHANGE_WD|scm.E_NEW_SCM, _update_in_submodule_condns)

_SUBMODULE_PATH_RE = re.compile(r"\s*[a-fA-F0-9]+\s+(\S+)\s+\S*")
def get_submodule_paths():
    text = runext.run_get_cmd(["git", "submodule", "status", "--recursive"], default="")
    return [_SUBMODULE_PATH_RE.match(line).groups()[0] for line in text.splitlines()]

class SubmodulePathMenu(Gtk.MenuItem):
    def __init__(self, label, item_activation_action):
        self._item_activation_action = item_activation_action
        Gtk.MenuItem.__init__(self, label)
        self.set_submenu(Gtk.Menu())
        self.connect("enter_notify_event", self._enter_notify_even_cb)
    def _build_submenu(self):
        _menu = Gtk.Menu()
        for submodule_path in get_submodule_paths():
            _menu_item = Gtk.MenuItem(submodule_path)
            _menu_item.connect("activate", self._item_activation_cb, submodule_path)
            _menu_item.show()
            _menu.append(_menu_item)
        return _menu
    def _enter_notify_even_cb(self, widget, _event):
        widget.set_submenu(self._build_submenu())
    def _item_activation_cb(self, _widget, submodule_path):
        with dialogue.main_window.showing_busy():
            result = self._item_activation_action(submodule_path)
        dialogue.main_window.report_any_problems(result)

def generate_chdir_submodule_menu():
    return SubmodulePathMenu(_("Submodules"), lambda submodule_path: wspce.chdir(submodule_path))

def chdir_to_superproject():
    sp_dir_path = git_ifce.SCM.get_superproject_root()
    if sp_dir_path:
        wspce.chdir(sp_dir_path)

actions.CLASS_INDEP_AGS[AC_IN_SUBMODULE].add_actions(
    [
        ("git_change_wd_to_superproject", Gtk.STOCK_GOTO_BOTTOM, _("Super"), "",
         _("Change current working directory to this submodule's superproject's root directory"),
         lambda _action: chdir_to_superproject()
        ),
    ]
)
