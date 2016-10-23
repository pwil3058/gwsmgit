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

"""<DOCSTRING GOES HERE>"""

__all__ = []
__author__ = "Peter Williams <pwil3058@gmail.com>"

import os

from gi.repository import Gtk

from .. import APP_NAME

from ..wsm import scm_gui
from ..wsm import git_gui

from ..wsm.gui import actions
from ..wsm.gui import console
from ..wsm.gui import dialogue
from ..wsm.gui import icons
from ..wsm.gui import recollect
from ..wsm.gui import terminal

from ..wsm.bab.decorators import singleton
from ..wsm.bab import enotify
from ..wsm.bab import utils

from ..wsm.scm_gui import do_opn as scm_do_opn

from . import submodules

recollect.define("main_window", "last_geometry", recollect.Defn(str, "900x600+100+100"))
recollect.define("main_window", "vpaned_position", recollect.Defn(int, 300))
recollect.define("main_window", "hpaned_position", recollect.Defn(int, 500))
recollect.define("main_window", "fthpaned_position", recollect.Defn(int, 300))

@singleton
class MainWindow(dialogue.MainWindow, actions.CAGandUIManager, enotify.Listener, scm_gui.actions.WDListenerMixin, scm_do_opn.DoOpnMixin):
    UI_DESCR = """
    <ui>
        <menubar name="appn_left_menubar">
            <menu name="appn_cwd" action="actions_wd_menu">
              <menuitem action="scm_change_wd"/>
              <menuitem action="scm_initialize_curdir"/>
              <menuitem action="scm_clone_repo"/>
              <menuitem action="actions_quit"/>
            </menu>
            <menu name="appn_wspce" action="actions_wspce_menu">
              <menuitem action="scm_create_new_workspace"/>
            </menu>
            <menu name="appn_submodules" action="actions_submodules_menu">
              <menuitem action="git_add_submodule"/>
            </menu>
        </menubar>
        <menubar name="appn_right_menubar">
            <menu name="appn_config" action="config_menu">
              <menuitem action="allocate_xtnl_editors"/>
              <menuitem action="config_auto_update"/>
            </menu>
        </menubar>
        <toolbar name="appn_main_toolbar">
             <toolitem action="git_change_wd_to_superproject"/>
           <separator/>
             <toolitem action="git_wd_diff_dialog"/>
             <toolitem action="git_commit_staged_changes"/>
             <toolitem action="git_amend_last_commit"/>
           <separator/>
             <toolitem action="git_branch_current_head"/>
             <toolitem action="git_tag_current_head"/>
           <separator/>
             <toolitem action="git_stash_current_state"/>
           <separator/>
             <toolitem action="git_fetch_from_remote"/>
             <toolitem action="scm_pull_from_default_repo"/>
             <toolitem action="scm_push_to_default_repo"/>
           <separator/>
        </toolbar>
    </ui>
    """
    def __init__(self):
        scm_gui.ifce.init()
        dialogue.MainWindow.__init__(self)
        self.parse_geometry(recollect.get("main_window", "last_geometry"))
        self.set_icon_from_file(icons.APP_ICON_FILE)
        self.connect("destroy", Gtk.main_quit)
        self.connect("configure-event", self._configure_event_cb)
        self._update_title()
        actions.CAGandUIManager.__init__(self)
        enotify.Listener.__init__(self)
        scm_gui.actions.WDListenerMixin.__init__(self)
        self.ui_manager.add_ui_from_string(MainWindow.UI_DESCR)
        vbox = Gtk.VBox()
        self.add(vbox)
        mbar_box = Gtk.HBox()
        lmenu_bar = self.ui_manager.get_widget("/appn_left_menubar")
        workspace_menu = self.ui_manager.get_widget("/appn_left_menubar/appn_wspce")
        workspace_menu.get_submenu().insert(scm_gui.wspce.generate_chdir_to_workspace_menu(), 0)
        submodule_menu = self.ui_manager.get_widget("/appn_left_menubar/appn_submodules")
        submodule_menu.get_submenu().insert(submodules.generate_chdir_submodule_menu(), 0)
        mbar_box.pack_start(lmenu_bar, expand=True, fill=True, padding=0)
        mbar_box.pack_end(self.ui_manager.get_widget("/appn_right_menubar"), expand=False, fill=True, padding=0)
        vbox.pack_start(mbar_box, expand=False, fill=True, padding=0)
        toolbar = self.ui_manager.get_widget("/appn_main_toolbar")
        toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        vbox.pack_start(toolbar, expand=False, fill=True, padding=0)
        vpaned = Gtk.VPaned()
        vpaned.set_position(recollect.get("main_window", "vpaned_position"))
        vbox.pack_start(vpaned, expand=True, fill=True, padding=0)
        hpaned = Gtk.HPaned()
        hpaned.set_position(recollect.get("main_window", "hpaned_position"))
        vpaned.add1(hpaned)
        fthpaned = Gtk.HPaned()
        fthpaned.set_position(recollect.get("main_window", "fthpaned_position"))
        wdtree = git_gui.wd.WDFileTreeWidget()
        indextree = git_gui.index.IndexFileTreeWidget()
        fthpaned.add1(wdtree)
        fthpaned.add2(indextree)
        hpaned.add1(fthpaned)
        vpaned.connect("notify", self._paned_notify_cb, "vpaned_position")
        hpaned.connect("notify", self._paned_notify_cb, "hpaned_position")
        fthpaned.connect("notify", self._paned_notify_cb, "fthpaned_position")
        nbook = Gtk.Notebook()
        nbook.popup_enable()
        branches_list = git_gui.branches.BranchList()
        nbook.append_page(branches_list, Gtk.Label(label=_("Branches")))
        nbook.append_page(git_gui.tags.TagList(), Gtk.Label(label=_("Tags")))
        nbook.append_page(git_gui.stashes.StashList(), Gtk.Label(label=_("Stashes")))
        nbook.append_page(git_gui.remotes.RemotesList(), Gtk.Label(label=_("Remotes")))
        nbook.append_page(git_gui.log.LogList(), Gtk.Label(label=_("Log")))
        hpaned.add2(nbook)
        if terminal.AVAILABLE:
            nbook = Gtk.Notebook()
            nbook.popup_enable()
            nbook.append_page(console.LOG, Gtk.Label(label=_("Transaction Log")))
            nbook.append_page(terminal.Terminal(), Gtk.Label(label=_("Terminal")))
            nbook.append_page(terminal.Terminal(False), Gtk.Label(label=_("Unbound Terminal")))
            if terminal.GITSOME_AVAILABLE:
                nbook.append_page(terminal.GitsomeTerminal(), Gtk.Label(label=_("Gitsome Terminal")))
            nbook.set_current_page(1)
            vpaned.add2(nbook)
        else:
            vpaned.add2(console.LOG)
        self.add_notification_cb(enotify.E_CHANGE_WD, self._change_pgnd_ncb)
        self.show_all()
    def _update_title(self):
        self.set_title("{}: {}".format(APP_NAME, utils.path_rel_home(os.getcwd())))
    def _change_pgnd_ncb(self, **kwargs):
        self._update_title()
    def _configure_event_cb(self, widget, event):
        recollect.set("main_window", "last_geometry", "{0.width}x{0.height}+{0.x}+{0.y}".format(event))
    def _paned_notify_cb(self, widget, parameter, oname=None):
        if parameter.name == "position":
            recollect.set("main_window", oname, str(widget.get_position()))

actions.CLASS_INDEP_AGS[actions.AC_DONT_CARE].add_actions(
    [
        ("config_menu", None, _("Configuration")),
        ("actions_wd_menu", None, _("Working Directory")),
        ("actions_wspce_menu", None, _("Workspaces")),
        ("actions_submodules_menu", None, _("Submodules")),
        ("actions_quit", Gtk.STOCK_QUIT, _("Quit"), "",
         _("Quit"),
         lambda _action: Gtk.main_quit()
        ),
    ])
