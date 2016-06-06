import os
import urwid
from configtab import SimplePopupLauncher, SimplePopupDialog

class TabHostname(object):

    def __init__(self, main_loop):
        self.main_loop = main_loop
        self.name = u"Hosts Config"
        self.hosts_file = "/etc/hosts"
        self.w_entries = self.load_entries()
        self.widget = SimplePopupLauncher(self.get_entry_widget(), "Save success.")

    def load_entries(self):
        widget_lines = []
        with open(self.hosts_file) as f:
            for line in f.readlines():
                items = line.split()
                widget_items = [urwid.Edit("IP: ", items[0]), urwid.Edit("Hostname: ", items[1])]
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
        widget_items = [urwid.Edit("IP: ", ""), urwid.Edit("Hostname: ", "")]
        widget_items.append(urwid.Button("Delete", on_press=self.delete_line, user_data=widget_items))
        self.w_entries.append(widget_items)
        self.widget.original_widget = self.get_entry_widget()
        self.widget.original_widget.focus_position = len(self.w_entries)

    def save(self, button):
        f = open(self.hosts_file,"w")
        # 用with ... as f语句就不用下面的f.close了
        for entry in self.w_entries:
            if entry[0].edit_text.strip() and entry[1].edit_text.strip():
                f.write("%s %s\n" % (entry[0].edit_text, entry[1].edit_text))
        f.close()
        self.widget.open_pop_up()
