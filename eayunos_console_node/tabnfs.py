#coding=utf-8

import os
import urwid
from eayunos_console_common.configtab import SimplePopupLauncher, SimplePopupDialog


class TabNFS(object):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"NFS Config"
        self.exports_file = "/etc/exports"
        self.w_entries = self.load_entries()
        self.widget = SimplePopupLauncher(self.get_entry_widget())

    def load_entries(self):
        widget_lines = []
        with open(self.exports_file) as f:
            for line in f.readlines():
                if not line.strip():
                    continue
                items = line.split()
                widget_items = [urwid.Edit("Path: ", items[0]), urwid.Edit("Param: ", items[1])]
                widget_items.append(urwid.Button("Delete", on_press=self.delete_line, user_data=widget_items))
                widget_lines.append(widget_items)
        return widget_lines

    def delete_line(self, button, line):
        self.w_entries.remove(line)
        self.widget.original_widget = self.get_entry_widget()
        self.widget.original_widget.focus_position = max(0, len(self.w_entries)-1)

    def get_entry_widget(self):
        pile = urwid.Pile([
            urwid.Columns(entry) for entry in self.w_entries
        ])
        pile.contents.append((urwid.Button("New", on_press=self.new), ('pack', None)))
        pile.contents.append((urwid.Button("Save", on_press=self.save), ('pack', None)))
        return pile

    def new(self, button):
        widget_items = [urwid.Edit("Path: ", ""), urwid.Edit("Param: ", "*(rw)")]
        widget_items.append(urwid.Button("Delete", on_press=self.delete_line, user_data=widget_items))
        self.w_entries.append(widget_items)
        self.widget.original_widget = self.get_entry_widget()
        self.widget.original_widget.focus_position = len(self.w_entries)

    def save(self, button):
        self.widget.set_wait(True)
        self.widget.set_popup_text("Saving and applying nfs config...")
        self.widget.open_pop_up()
        f = open(self.exports_file,"w")
        for entry in self.w_entries:
            path = entry[0].edit_text.strip()
            param = entry[1].edit_text.strip()
            if path and param:
                os.system("chkconfig nfs-server on &>/dev/null")
                f.write("%s %s\n" % (path, param))
                os.system("mkdir -p %s" % path)
                os.system("chown -R vdsm:kvm %s" % path)
        f.close()
        os.system("service nfs start &>/dev/null")
        os.system("exportfs -r")
        self.widget.set_wait(False)
        self.widget.set_popup_text("Save success.")
        self.widget.open_pop_up()
