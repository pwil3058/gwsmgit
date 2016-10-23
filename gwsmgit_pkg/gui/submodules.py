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

from ..wsm import scm

from ..wsm.git_gui import ifce as git_ifce
from ..wsm.git import git_utils

from ..wsm.gui import actions
from ..wsm.gui import apath
from ..wsm.gui import dialogue

from ..wsm.bab import enotify
from ..wsm.bab import runext

from ..wsm.scm_gui.actions import AC_IN_SCM_PGND
from ..wsm.scm_gui import repos
from ..wsm.scm_gui import wspce

from .. import CONFIG_DIR_PATH

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

class AddSubmoduleDialog(repos.RepoSelectDialog):
    def __init__(self, parent=None):
        repos.RepoSelectDialog.__init__(self, parent=parent)
        self._browse_button.set_tooltip_text(_("Browse for a local repository to add as a submodule"))
        for subdir_path in git_utils.get_recognized_subdirs():
            self._target.append_text(subdir_path)
        self.connect("response", self._response_cb)
    @staticmethod
    def _response_cb(dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            repo = dialog.get_path()
            if not repo:
                dialog.report_failure(_("Source repository must be specified"))
                return
            with dialog.showing_busy():
                cmd = ["git", "submodule", "add", repo]
                target = dialog.get_target()
                if target:
                    cmd.append(target)
                result = git_ifce.do_action_cmd(cmd, scm.E_NEW_SCM|scm.E_FILE_CHANGES, None, [])
                if dialog.report_any_problems(result):
                    # NB if there were problems leave the dialog open and give them another go
                    return
        dialog.destroy()

class SubmodulePathMenu(Gtk.MenuItem):
    def __init__(self, label, item_activation_action):
        self._item_activation_action = item_activation_action
        Gtk.MenuItem.__init__(self, label)
        self.set_submenu(Gtk.Menu())
        self.connect("enter_notify_event", self._enter_notify_even_cb)
    def _build_submenu(self):
        _menu = Gtk.Menu()
        for submodule_path in git_utils.get_submodule_paths():
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

def generate_chdir_submodule_menu(label=_("Change Directory To")):
    return SubmodulePathMenu(label, lambda submodule_path: wspce.chdir(submodule_path))

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

actions.CLASS_INDEP_AGS[AC_IN_SCM_PGND].add_actions(
    [
        ("git_add_submodule", Gtk.STOCK_ADD, _("Add"), "",
         _("Add a new submodule to this workspace repository"),
         lambda _action: AddSubmoduleDialog().run()
        ),
    ]
)
