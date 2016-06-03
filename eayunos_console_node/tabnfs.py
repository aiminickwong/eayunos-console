import os
import urwid
from eayunos_console_common.configtab import SimplePopupDialog

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
        f = open(self.exports_file,"w")
        for entry in self.w_entries:
            if entry[0].edit_text.strip() and entry[1].edit_text.strip():
                f.write("%s %s\n" % (entry[0].edit_text, entry[1].edit_text))
        f.close()
        os.system("service nfs start")
        os.system("exportfs -r")
        self.widget.open_pop_up()


class SimplePopupLauncher(urwid.PopUpLauncher):

    def create_pop_up(self):
        pop_up = SimplePopupDialog("Save success.")
        urwid.connect_signal(pop_up, 'close',
            lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}
